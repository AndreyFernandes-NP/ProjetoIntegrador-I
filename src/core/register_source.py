"""
register_source.py
------------------
Registra uma nova fonte de dados no sources.yaml automaticamente.

Lê o CSV, inspeciona as colunas e gera o bloco de configuração como template.

Uso:
    python src/pipeline/register_source.py data/raw/novo_arquivo.csv
    python src/pipeline/register_source.py data/raw/novo_arquivo.csv --nome meu_nome_customizado
    python src/pipeline/register_source.py data/raw/novo_arquivo.csv --dry-run
"""

import argparse
import sys
from pathlib import Path

from ruamel.yaml import YAML

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

yaml_rt = YAML()
yaml_rt.preserve_quotes = True
yaml_rt.indent(mapping=2, sequence=4, offset=2)

from src.config import PATHS
from src.core.transformer import careful_load_csv

CONFIG_PATH = PATHS.config / "sources.yaml"

# Utilities

# Esse load config é específico para o register_source, não deve ser usado em outros lugares
def load_config(path: Path) -> dict:
    if not path.exists():
        return {"fontes": []}

    with open(path, "r", encoding="utf-8") as f:
        config = yaml_rt.load(f)

    if config is None:
        config = {"fontes": []}

    config.setdefault("fontes", [])

    return config

def save_config(path: Path, config: dict) -> None:
    with open(path, "w", encoding="utf-8") as f:
        yaml_rt.dump(config, f)

def existing_name(config: dict | None, nome: str) -> bool:
    if not isinstance(config, dict):
        return False

    fontes = config.get("fontes") or []

    return any(isinstance(fonte, dict) and fonte.get("nome") == nome for fonte in fontes)

def existing_file(config: dict | None, arquivo: str) -> bool:
    if not isinstance(config, dict):
        return False
    
    fontes = config.get("fontes") or []

    return any(isinstance(fonte, dict) and fonte.get("arquivo") == arquivo for fonte in fontes)

def ensure_fontes_list(config: dict | None) -> dict:
    if not isinstance(config, dict):
        config = {}

    if not isinstance(config.get("fontes"), list):
        config["fontes"] = []

    return config

def inspect_csv(caminho: Path) -> dict:
    """Lê o CSV e retorna metadados: colunas, tipos, % de nulos."""

    df = careful_load_csv(caminho)

    colunas_info = {}
    for col in df.columns:
        nulos_pct = round(df[col].isnull().mean() * 100, 1)
        colunas_info[col] = {
            "tipo": str(df[col].dtype),
            "nulos_pct": nulos_pct,
        }

    return {
        "encoding": df._mgr.blocks[0].values.dtype,
        "separador": ";",
        "total_colunas": len(df.columns),
        "colunas_info": colunas_info,
    }

# Geração do bloco de config

def generate_block(nome: str, arquivo: str) -> dict:
    return {
        "nome": nome,
        "arquivo": arquivo,
        "merge": False, # default: não faz merge automático assim que criado, evitar problemas de chave e etc
        "colunas_uteis": [],
        "notas": "",
        "transformacoes": None,
        "qualidade": None
    }

def create_template(nome: str, arquivo: str) -> None:
    config = load_config(CONFIG_PATH)
    config = ensure_fontes_list(config)

    if existing_name(config, nome):
        print(f"[Aviso] A fonte '{nome}' já existe no sources.yaml. Template não criado.")
        return

    if existing_file(config, arquivo):
        print(f"[Aviso] O arquivo '{arquivo}' já está registrado. Template não criado.")
        return

    block = generate_block(nome, arquivo)
    config["fontes"].append(block)
    save_config(CONFIG_PATH, config)

    print(f"[OK] Fonte '{nome}' adicionada ao sources.yaml.")

def debug_inspection(nome: str, inspecao: dict) -> None:
    print(f"\n{'─' * 55}")
    print(f"Inspeção: {nome} ({inspecao['total_colunas']} colunas)")
    print(f"{'─' * 55}")
    print(f"Encoding  : {inspecao['encoding']}")
    print(f"Separador : {repr(inspecao['separador'])}")
    print()
    print(f"{'Coluna':<35} {'Tipo':<12} {'Nulos %':>7}")
    print(f"{'─'*35} {'─'*12} {'─'*7}")
    for col, info in inspecao["colunas_info"].items():
        nulos_str = f"{info['nulos_pct']}%" if info["nulos_pct"] > 0 else "—"
        print(f"{col:<35} {info['tipo']:<12} {nulos_str:>7}")

# Entrypoint

def main():
    parser = argparse.ArgumentParser(description="Registra nova fonte no sources.yaml")
    parser.add_argument("arquivo", type=str, help="Caminho para o arquivo CSV (ex: data/raw/novo.csv)")
    parser.add_argument("--nome", type=str, default=None, help="Nome da fonte (padrão: inferido do nome do arquivo)")
    parser.add_argument("--dry-run", action="store_true", help="Mostra o bloco que seria adicionado, sem salvar")
    args = parser.parse_args()

    caminho = Path(args.arquivo)
    if not caminho.is_absolute():
        caminho = PATHS.root / caminho

    if not caminho.exists():
        print(f"[Erro] Arquivo não encontrado: {caminho}")
        sys.exit(1)

    nome = args.nome or caminho.stem
    arquivo = caminho.name

    config = load_config(CONFIG_PATH)

    if existing_name(config, nome):
        print(f"[Aviso] A fonte '{nome}' já existe no sources.yaml. Nenhuma alteração feita.")
        print(f"Se quiser sobrescrever, edite o arquivo manualmente.")
        sys.exit(0)

    if existing_file(config, arquivo):
        print(f"[Aviso] O arquivo '{arquivo}' já está registrado com outro nome. Nenhuma alteração feita.")
        sys.exit(0)

    print(f"Lendo arquivo: {caminho.relative_to(PATHS.root)}")
    inspecao = inspect_csv(caminho)
    #debug_inspection(nome, inspecao)

    bloco = generate_block(nome, arquivo)

    print(f"\n{'─' * 55}")
    print("Bloco que será adicionado ao sources.yaml:")
    print(yaml_rt.dump(bloco))

    if args.dry_run:
        print("[dry-run] sources.yaml NÃO foi modificado.")
        return

    resposta = input("Confirmar adição? [s/N] ").strip().lower()
    if resposta != "s":
        print("Cancelado - Nenhuma alteração feita.")
        return

    config["fontes"].append(bloco)
    save_config(CONFIG_PATH, config)

    print(f"\n[OK] Fonte '{nome}' adicionada ao sources.yaml.")

if __name__ == "__main__":
    main()
