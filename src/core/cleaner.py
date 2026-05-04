"""
cleaner.py
----------
Lógica de limpeza aplicada a qualquer DataFrame da pipeline.

Obs: Adicionar novas funções de limpeza se precisar ao longo do projeto.
"""
import re
import unicodedata
from typing import Any

import pandas as pd

# Função de purge específica para esse arquivo .py, diferente do purge do transformer.
def purge_unicode_text(texto: object) -> str:
    """
    Remove acentos de valores de células.
    
    Sempre retorna string.
    """
    if texto is None:
        return ""

    return "".join(c for c in unicodedata.normalize("NFKD", str(texto)) if not unicodedata.combining(c))

def purge_unicode_value(valor: Any) -> Any:
    """
    Remove acentos de valores de células.

    Preserva nulos.
    """
    if pd.isna(valor):
        return valor

    return "".join(c for c in unicodedata.normalize("NFKD", str(valor)) if not unicodedata.combining(c))

def warn_broken_columns(df: pd.DataFrame, nome: str) -> None:
    broken_markers = ["�", "¿", "½", "¼", "¾", "Ã", "Â"]

    broken_cols = [
        col for col in df.columns
        if any(marker in str(col) for marker in broken_markers)
    ]

    if broken_cols:
        print(f"[Aviso] '{nome}' possui possíveis colunas com encoding quebrado:")
        for col in broken_cols:
            print(f"- {col}")

# Limpeza genérica - aplicada a todos os Dataframes, independente da fonte
def clean_strings(df: pd.DataFrame) -> pd.DataFrame:
    """Strip de espaços em colunas de texto."""

    cols_str = df.select_dtypes(include=["object", "string"]).columns
    df[cols_str] = (df[cols_str].apply(lambda col: col.str.strip()).replace(r"^\s*$", pd.NA, regex=True))

    return df

def normalize_column_name(nome: object) -> str:
    """
    Normaliza nomes de colunas e nomes vindos do YAML.
    """
    nome_normalizado = purge_unicode_text(nome)

    nome_normalizado = (nome_normalizado.replace("\ufeff", "").strip().lower())

    nome_normalizado = re.sub(r"^\d+\s*", "", nome_normalizado)
    nome_normalizado = re.sub(r"\s*/\s*", " / ", nome_normalizado)
    nome_normalizado = re.sub(r"\s+", " ", nome_normalizado)

    return nome_normalizado.strip()

def normalize_columns(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df.columns = [normalize_column_name(col) for col in df.columns]
    return df

def normalize_column_list(colunas: list | None) -> list[str]:
    """
    Normaliza uma lista de nomes de colunas vinda do YAML.
    """
    if not colunas:
        return []
    return [normalize_column_name(col)for col in colunas]

def normalize_column_mapping(mapping: dict | None) -> dict:
    """
    Normaliza as chaves de um dict onde as chaves são nomes de colunas.

    Ex:
    transformacoes:
      Município:
        tipo: purge

    vira:
    {
        "municipio": {"tipo": "purge"}
    }
    """
    if not isinstance(mapping, dict):
        return {}

    return {normalize_column_name(col): regras for col, regras in mapping.items()}

def get_null_amount(df: pd.DataFrame, nome: str) -> pd.DataFrame:
    """Imprime um relatório de colunas com valores nulos (não remove)."""
    nulos = df.isnull().sum()
    nulos = nulos[nulos > 0]

    if not nulos.empty:
        pct = (nulos / len(df) * 100).round(1)
        print(f"[nulos] '{nome}' — colunas com valores ausentes:") # debug
        for col in nulos.index:
            print(f"- {col}: {nulos[col]} ({pct[col]}%)") # debug

    return df

# Função principal da pipeline de limpeza

def clean(df: pd.DataFrame, nome: str) -> pd.DataFrame:
    """
    Aplica o pipeline de limpeza genérica completo a um DataFrame.

    Parâmetros
    ----------
    df     : DataFrame bruto carregado do CSV
    nome   : string com o nome da fonte de dados

    Retorna
    -------
    DataFrame limpo.
    """
    df = df.copy()
    warn_broken_columns(df, nome)
    df = normalize_columns(df)
    df = clean_strings(df)
    df.drop_duplicates(inplace=True)
    df = get_null_amount(df, nome)

    return df
