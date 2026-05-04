"""
pipeline.py
-----------
Orquestrador principal: roda cleaner → transformer em sequência para cada fonte,

salvando o resultado final em data/clean/*-clean.csv.

Uso:
    python src/pipeline/pipeline.py                              # todas as fontes
    python src/pipeline/pipeline.py --fonte inst_hospitalares_sp # só uma fonte
    python src/pipeline/pipeline.py --dry-run                    # valida sem salvar
    python src/pipeline/pipeline.py --skip-transform             # só limpeza
"""

import argparse
import sys
from pathlib import Path

import pandas as pd
import yaml

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.config import PATHS
from cleaner import clean
from validator import validate_quality
from register_source import create_template
from transformer import load_refs, transform, careful_load_csv
from merger import run_merge, load_merge_config

CONFIG_PATH = PATHS.config / "sources.yaml"
RAW_DIR     = PATHS.data_raw
CLEAN_DIR   = PATHS.data_clean

# Utils

def get_csv() -> list[dict]:
    caminho = RAW_DIR
    files = []

    for arquivo in caminho.glob("*.csv"):
        files.append({"nome": arquivo.stem, "arquivo": arquivo.name})

    return files

def get_cleaned_csv() -> list[dict]:
    caminho = CLEAN_DIR
    files = []

    for arquivo in caminho.glob("*.csv"):
        files.append({"nome": arquivo.stem.removesuffix("-clean"), "arquivo": arquivo.name})

    return files

def get_fonte_cfg(config: dict | None, nome: str) -> dict:
    if not isinstance(config, dict):
        return {}

    fontes = config.get("fontes") or []

    return next((f for f in fontes if isinstance(f, dict) and f.get("nome") == nome), {})

def load_config(path: Path) -> dict:
    default = {
        "merge": {},
        "fontes": [],
    }

    if not path.exists():
        return default

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        return default

    if not isinstance(config.get("fontes"), list):
        config["fontes"] = []

    if not isinstance(config.get("merge"), dict):
        config["merge"] = {}

    return config

def load_raw_csv(fonte: dict) -> pd.DataFrame:
    caminho = RAW_DIR / fonte["arquivo"]
    if not caminho.exists():
        raise FileNotFoundError(f"Arquivo não encontrado: {caminho}")
    return careful_load_csv(caminho)

def save_csv(df: pd.DataFrame, nome: str) -> Path:
    CLEAN_DIR.mkdir(parents=True, exist_ok=True)
    destino = CLEAN_DIR / f"{nome}-clean.csv"
    df.to_csv(destino, index=False, encoding="utf-8", sep=";")
    return destino

# Pipeline Principal

def process_csv(fonte: dict, fonte_cfg: dict, dfs_ref: dict, dry_run: bool = False, skip_transform: bool = False) -> None:
    nome = fonte["nome"]
    arquivo = fonte["arquivo"]

    print(f"\n{'─' * 55}")
    print(f"Processando: {nome}")

    if not fonte_cfg:
        print(f"[Aviso] Configurações não encontradas para '{nome}'.")
        fonte_cfg = {}

    df_raw = load_raw_csv(fonte)
    print(f"[Raw] {len(df_raw)} linhas x {len(df_raw.columns)} colunas")

    # Etapa 1: limpeza genérica
    df = clean(df_raw, nome)
    print(f"[Clean] {len(df)} linhas x {len(df.columns)} colunas")

    # Etapa 1.1: criação de template do item no sources.yaml (se não existir)
    if not fonte_cfg:
        create_template(nome, arquivo)
        
    # Etapa 2: transformações específicas (mapeamento, cast, purge)
    if not skip_transform:
        df = transform(df, fonte_cfg, dfs_ref)
        print(f"[Transform] concluído para '{nome}'")
    
    # Etapa 3: validação de qualidade
    validate_quality(df, nome, fonte_cfg, fail_on_error=not dry_run)

    if not dry_run:
        destino = save_csv(df, nome)
        print(f"[Salvo] {destino.relative_to(PATHS.root)}")

# Entrypoint

def pipeline(force_save: bool = False):
    parser = argparse.ArgumentParser(description="Pipeline: limpeza + transformação de dados")
    parser.add_argument("--fonte", type=str, default=None,
                        help="Nome da fonte para processar (padrão: todas)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Executa sem salvar arquivos")
    parser.add_argument("--skip-transform", action="store_true",
                        help="Pula a etapa de transformação (só limpeza)")
    args = parser.parse_args()

    todas_fontes = get_csv()
    config = load_config(CONFIG_PATH)

    if not todas_fontes:
        print("[Erro] Nenhum arquivo .csv encontrado na pasta raw.")
        return
    
    fontes_clean = get_cleaned_csv()

    if force_save:
        fontes_run = todas_fontes
    else:
        fontes_run = [fonte for fonte in todas_fontes if not any(f["nome"] == fonte["nome"] for f in fontes_clean)]

    if args.fonte:
        fontes_run = [f for f in todas_fontes if f["nome"] == args.fonte]
        if not fontes_run:
            print(f"[Erro] Fonte '{args.fonte}' não encontrada na config.")
            return

    # Pré-carrega DFs de referência (ex: codigos_ibge_sp)
    dfs_ref = load_refs()
    erros = []
    for fonte in fontes_run:
        try:
            fonte_cfg = get_fonte_cfg(config, fonte["nome"])
            # process_csv contém etapas 1,2,3
            process_csv(fonte, fonte_cfg, dfs_ref, dry_run=args.dry_run, skip_transform=args.skip_transform)
        except Exception as e:
            print(f"[Erro] {fonte['nome']}: {e}")
            erros.append(fonte["nome"])

    print(f"\n{'═' * 55}")
    ok = len(fontes_run) - len(erros)
    print(f"Concluído: {ok}/{len(fontes_run)} fontes processadas com sucesso.")
    if erros:
        print(f"Com erro: {erros}")
        return
    print(f"{'═' * 55}")

    # Etapa 4: merge final
    merge_config = load_merge_config(CONFIG_PATH)
    merged = run_merge(config=merge_config)

    if merged is not None:
        print(f"\n[Merge] Merge final concluído com {len(merged)} linhas x {len(merged.columns)} colunas.")

if __name__ == "__main__":
    pipeline(force_save=True)
