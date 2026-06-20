"""
merger.py
---------
Une os arquivos *-clean.csv da pasta data/clean/ em um DataFrame consolidado.

Configuração esperada no sources.yaml:

merge:
  chave: municipio
  como: left
  saida: main_dataframe.csv

fontes:
  - nome: nome_da_fonte
    merge: true
    colunas_uteis: []

Uso:
    python src/core/merger.py
    python src/core/merger.py --dry-run     # mostra resultado sem salvar
    python src/core/merger.py --how left    # tipo de join (left/inner/outer)
"""

import argparse
import sys
from pathlib import Path
from typing import Literal

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.config import PATHS
from src.core.cleaner import normalize_column_list
from src.core.transformer import careful_load_csv, apply_purge

CONFIG_PATH = PATHS.config / "sources.yaml"
CLEAN_DIR = PATHS.data_clean
MAP_DIR = PATHS.data_mapping
PROC_DIR = PATHS.data_processed

MergeHow = Literal["left", "right", "inner", "outer"]

# Config

def load_merge_config(path: Path) -> dict:
    """
    Carrega o sources.yaml inteiro.

    Retorna sempre um dict minimamente válido.
    """
    default = {
        "merge": {
            "chave": "municipio",
            "como": "left",
            "saida": "main_dataframe.csv",
        },
        "fontes": [],
    }

    if not path.exists():
        print(f"[Aviso] Config não encontrada em: {path}")
        return default

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        print("[Aviso] sources.yaml inválido ou vazio. Usando configuração padrão.")
        return default

    config.setdefault("merge", {})
    config.setdefault("fontes", [])

    config["merge"].setdefault("chave", default["merge"]["chave"])
    config["merge"].setdefault("como", default["merge"]["como"])
    config["merge"].setdefault("saida", default["merge"]["saida"])

    return config

def get_mergeable_sources(config: dict) -> list[dict]:
    """
    Retorna apenas fontes que devem participar do merge.

    Por padrão, merge=True.
    """
    fontes = config.get("fontes", [])

    return [fonte for fonte in fontes if fonte.get("merge", True)]

# Leitura dos clean CSVs

def load_clean(nome: str) -> pd.DataFrame | None:
    caminho = CLEAN_DIR / f"{nome}-clean.csv"

    if not caminho.exists():
        print(f"[Aviso] '{nome}-clean.csv' não encontrado em clean/. Pulando.")
        return None

    df = careful_load_csv(caminho)

    print(f"[Carregado] '{nome}' — {len(df)} linhas x {len(df.columns)} colunas")

    return df

def load_map(nome: str) -> pd.DataFrame | None:
    caminho = MAP_DIR / f"{nome}.csv"

    if not caminho.exists():
        print(f"[Aviso] '{nome}.csv' não encontrado em mapping/. Pulando.")
        return None

    df = careful_load_csv(caminho)

    print(f"[Carregado] '{nome}' — {len(df)} linhas x {len(df.columns)} colunas")

    return df

def apply_useful(df: pd.DataFrame, fonte: dict, chave_merge: str) -> pd.DataFrame:
    """
    Aplica whitelist de colunas se colunas_uteis estiver preenchido.

    Garante que a chave de merge seja mantida.
    """
    colunas_uteis = normalize_column_list(fonte.get("colunas_uteis", []))

    if not colunas_uteis:
        return df

    colunas = list(dict.fromkeys([chave_merge, *colunas_uteis]))

    existentes = [col for col in colunas if col in df.columns]
    ausentes = [col for col in colunas if col not in df.columns]

    if ausentes:
        print(f"[Aviso] '{fonte['nome']}' — colunas_uteis ausentes: {ausentes}")

    return df[existentes]

# Validações básicas do merge

def validate_how(how: str | None) -> MergeHow:
    permitidos: set[MergeHow] = {'left', 'right', 'inner', 'outer'}

    if how in permitidos:
        return how
    
    print(f"[Aviso] Tipo de merge inválido: '{how}'. Usando 'left'.")
    return 'left'

def validate_key(df: pd.DataFrame, nome: str, chave_merge: str) -> bool:
    if chave_merge not in df.columns:
        print(f"[Aviso] chave '{chave_merge}' não encontrada em '{nome}'. Pulando.")
        return False

    return True

def debug_merge(df: pd.DataFrame, nome_esq: str, nome_dir: str) -> None:
    print(f"[Merge] '{nome_esq}' + '{nome_dir}' " f"→ {len(df)} linhas x {len(df.columns)} colunas")

def fill_missing_numeric(df: pd.DataFrame, chave_merge: str) -> pd.DataFrame:
    cols_numeric = [col for col in df.columns if col != chave_merge and pd.api.types.is_numeric_dtype(df[col])]
    
    for col in cols_numeric:
        df[col] = df[col].fillna(0)

        if (df[col] % 1 == 0).all():
            df[col] = df[col].astype("Int64")

    return df

# Lógica principal de merge

def init_df(chave_merge: str) -> tuple[pd.DataFrame | None, str]:
    nome = "codigos_ibge_sp"
    fonte = {"colunas_uteis": [chave_merge]}

    df = load_map(nome)
    if df is not None:
        print(f"[Base] '{nome}' definido como DataFrame base")

        df = apply_useful(df, fonte, chave_merge)
        df = apply_purge(df, chave_merge)

        if not validate_key(df, nome, chave_merge):
            print(f"[Aviso] DF de referência '{nome}' não possui a chave de merge '{chave_merge}'. Ignorando referência.")
            return None, ""
        
        return df, nome
    
    return None, ""

def sequence_merge(fontes_merge: list[dict], chave_merge: str, how: MergeHow) -> pd.DataFrame | None:
    """
    Faz merge sequencial usando a mesma chave global definida em:

    merge:
      chave: municipio
    """
    df_base, nome_base = init_df(chave_merge)

    for fonte in fontes_merge:
        nome = fonte["nome"]
        df = load_clean(nome)

        if df is None:
            continue

        df = apply_useful(df, fonte, chave_merge)

        if not validate_key(df, nome, chave_merge):
            continue

        if df_base is None:
            df_base = df
            nome_base = nome
            print(f"[Base] '{nome}' definido como DataFrame base")
            continue

        # Evita colunas duplicadas, mantendo a chave.
        colunas_novas = [col for col in df.columns if col == chave_merge or col not in df_base.columns]

        if colunas_novas == [chave_merge]:
            print(f"[Aviso] '{nome}' não possui colunas novas para adicionar. Pulando.")
            continue

        df_base = df_base.merge(df[colunas_novas], on=chave_merge, how=how)
        debug_merge(df_base, nome_base, nome)

    return df_base

def run_merge(config: dict, how_override: MergeHow | None = None) -> tuple[pd.DataFrame | None, Path]:
    """
    Executa o merge usando o dict de configuração já carregado.

    Usar o load_merge_config ao invés de outros loads por maior segurança.
    """
    merge_cfg = config.get("merge", {})

    chave_merge = merge_cfg.get("chave", "municipio")
    how = validate_how(how_override or merge_cfg.get("como", 'left'))
    arquivo_saida = merge_cfg.get("saida", "main_dataframe.csv")

    fontes = config.get("fontes", [])
    fontes_merge = get_mergeable_sources(config)

    ignoradas = [fonte["nome"] for fonte in fontes if not fonte.get("merge", True)]
    if ignoradas:
        print(f"[Merger] Fontes ignoradas (merge: false): {ignoradas}")

    print(f"\n[Merger] Iniciando merge de {len(fontes_merge)} fonte(s)")
    print(f"[Merger] Chave: '{chave_merge}' | Join: '{how}' | Saída: '{arquivo_saida}'")
    print(f"{'─' * 55}")

    df_merged = sequence_merge(fontes_merge, chave_merge, how)
    if df_merged is None:
        print("\n[Erro] Nenhum dado para mesclar. Verifique se a pipeline foi executada.")
        return None, Path()
    
    df_merged = fill_missing_numeric(df_merged, chave_merge)

    print(f"\n{'─' * 55}")
    print(f"[Resultado] {len(df_merged)} linhas x {len(df_merged.columns)} colunas")
    print(f"[Colunas]   {list(df_merged.columns)}")

    PROC_DIR.mkdir(parents=True, exist_ok=True)

    destino = PROC_DIR / arquivo_saida

    return df_merged, destino

# Entrypoint

def main() -> None:
    parser = argparse.ArgumentParser(description="Merger: une arquivos clean em um CSV processado")
    parser.add_argument("--dry-run", action="store_true", help="Mostra resultado sem salvar")
    parser.add_argument("--how", type=str, default=None, choices=["left", "right", "inner", "outer"], help="Sobrescreve o tipo de join definido no sources.yaml")

    args = parser.parse_args()

    config = load_merge_config(CONFIG_PATH)
    run_merge(config=config, how_override=args.how)

if __name__ == "__main__":
    main()