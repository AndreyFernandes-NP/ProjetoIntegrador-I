"""
validator.py
------------
Validação de qualidade dos DataFrames após limpeza/transformação.

Não altera dados, serve apenas pra reporta problemas ou interrompe a pipeline.
"""

import pandas as pd
from src.core.cleaner import normalize_column_list

class ValidationError(Exception):
    """Erro lançado quando a validação de qualidade falha."""
    pass

def validate_required_columns(df: pd.DataFrame, columns: list[str], nome: str) -> list[str]:
    errors = []
    missing = [col for col in columns if col not in df.columns]

    if missing:
        errors.append(f"[{nome}] Colunas obrigatórias ausentes: {missing}")

    return errors

def validate_not_null(df: pd.DataFrame, columns: list[str], nome: str) -> list[str]:
    errors = []

    for col in columns:
        if col not in df.columns:
            continue

        qtd = df[col].isna().sum()
        if qtd > 0:
            pct = qtd / len(df) * 100 if len(df) else 0
            errors.append(f"[{nome}] Coluna '{col}' possui {qtd} nulos ({pct:.1f}%)")

    return errors

def validate_unique(df: pd.DataFrame, columns: list[str], nome: str) -> list[str]:
    errors = []

    for col in columns:
        if col not in df.columns:
            continue

        qtd = df[col].duplicated().sum()
        if qtd > 0:
            errors.append(f"[{nome}] Coluna '{col}' possui {qtd} valores duplicados")

    return errors

def validate_numeric(df: pd.DataFrame, columns: list[str], nome: str) -> list[str]:
    errors = []

    for col in columns:
        if col not in df.columns:
            continue

        if not pd.api.types.is_numeric_dtype(df[col]):
            errors.append(f"[{nome}] Coluna '{col}' deveria ser numérica, mas está como {df[col].dtype}")

    return errors

def validate_generic(df: pd.DataFrame, nome: str) -> list[str]:
    """
    Validações genéricas, não assumem semântica de colunas.
    """
    warnings = []

    if df.empty:
        warnings.append(f"[{nome}] DataFrame está vazio")

    duplicated_rows = df.duplicated().sum()

    if duplicated_rows > 0:
        warnings.append(f"[{nome}] DataFrame ainda possui {duplicated_rows} linhas duplicadas")

    unnamed_cols = [col for col in df.columns if str(col).startswith("Unnamed")]

    if unnamed_cols:
        warnings.append(f"[{nome}] Colunas possivelmente inválidas encontradas: {unnamed_cols}")

    return warnings

def validate_quality(df: pd.DataFrame, nome: str, fonte_cfg: dict, fail_on_error: bool = True) -> None:
    """
    Executa validações genéricas e validações configuradas no sources.yaml.
    
    Não altera o DataFrame.
    """
    errors = []
    warnings = []

    quality_cfg = fonte_cfg.get("qualidade") or {}

    cols_obrigatorias = normalize_column_list(quality_cfg.get("cols_obrigatorias", []))
    cols_nao_nulas = normalize_column_list(quality_cfg.get("cols_nao_nulas", []))
    cols_unicas = normalize_column_list(quality_cfg.get("cols_unicas", []))
    cols_numericas = normalize_column_list(quality_cfg.get("cols_numericas", []))

    # Validação genérica, segura para todos
    warnings.extend(validate_generic(df, nome))

    # Validações específicas, somente se declaradas no YAML
    errors.extend(validate_required_columns(df, cols_obrigatorias, nome))
    errors.extend(validate_not_null(df, cols_nao_nulas, nome))
    errors.extend(validate_unique(df, cols_unicas, nome))
    errors.extend(validate_numeric(df, cols_numericas, nome))

    for warning in warnings:
        print(f"[Aviso] {warning}")

    if errors:
        print(f"[Erro] '{nome}' falhou na validação:")

        for error in errors:
            print(f"- {error}")

        if fail_on_error:
            raise ValidationError(f"Validação de qualidade falhou para '{nome}'")

    else:
        print(f"[Qualidade] '{nome}' passou na validação")