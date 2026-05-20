"""
transformer.py
--------------
Transformações de fontes de dados automaticamente com base em configurações/condições.

Roda após a limpeza genérica e antes do merge final.
"""

import sys
from pathlib import Path

import pandas as pd
import unicodedata

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.config import PATHS
from cleaner import normalize_column_mapping, normalize_column_name, normalize_column_list

CONFIG_PATH = PATHS.config / "sources.yaml"
MAPPING_DIR   = PATHS.data_mapping

encodings = ["utf-8", "utf-8-sig", "latin1", "iso-8859-1", "cp1252"]
na_values = ['nan', '?', 'null', '0', '-']
separators = [";", ","]

# Loading Utils

def has_replacement_char(df: pd.DataFrame) -> bool:
    return any("�" in str(col) for col in df.columns)

def careful_load_csv(path: Path, sep: str | None = None) -> pd.DataFrame:
    errors = []

    for encoding in encodings:
        for separator in separators:
            try:
                df = pd.read_csv(path, sep=separator, encoding=encoding, low_memory=False, na_values=na_values)

                if len(df.columns) <= 1:
                    errors.append(f"encoding={encoding}, sep={repr(separator)} → apenas {len(df.columns)} coluna(s)")
                    continue

                if has_replacement_char(df):
                    errors.append(f"encoding={encoding}, sep={repr(separator)} → caractere inválido nas colunas: {list(df.columns)}")
                    continue

                #print(f"[load] '{path.name}' lido com encoding={encoding}, sep={repr(separator)}")
                return df

            except UnicodeDecodeError as e:
                errors.append(f"encoding={encoding}, sep={repr(separator)} → UnicodeDecodeError: {e}")

            except pd.errors.ParserError as e:
                errors.append(f"encoding={encoding}, sep={repr(separator)} → ParserError: {e}")

            except Exception as e:
                errors.append(f"encoding={encoding}, sep={repr(separator)} → {type(e).__name__}: {e}")

    raise ValueError(f"Não foi possível ler '{path.name}' sem corromper colunas.\n"+ "\n".join(errors[-20:]))

# Text Utils

def purge_unicode(texto: str) -> str:
    if pd.isna(texto):
        return texto
    return ''.join(c for c in unicodedata.normalize('NFKD', str(texto)) if not unicodedata.combining(c))

def purge_numbers(serie: pd.Series) -> pd.Series:
    """Remove dígitos, strip e uppercase. Ex: '59932824 MUNICÍPIO' → 'MUNICIPIO'."""
    return (
        serie.astype("string")
        .str.replace(r"\d+", "", regex=True)
        .str.strip()
        .apply(purge_unicode)
        .str.upper()
    )

# Condições de transformação

def infer_numeric_columns(df, threshold=0.9):

    cols = df.select_dtypes(include=["object", "string"]).columns

    for col in cols:

        converted = pd.to_numeric(df[col], errors="coerce")

        ratio = converted.notna().mean()

        if ratio >= threshold:

            if (converted.dropna() % 1 == 0).all():
                df[col] = converted.astype("Int64")
            else:
                df[col] = converted.astype("Float64")

            print(f"[tipo] '{col}' → {df[col].dtype}")

    return df

def apply_ibge(df: pd.DataFrame, coluna: str, cfg_col: dict, dfs_ref: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Mapeia os valores da coluna usando um DF de referência.

    Por padrão usa codigos_ibge_sp com cod_ibge → municipio.
    """
    # Em teoria era pro no sources.yaml definirmos mais de um mapa se necessário pra conveniência, só que eu deixo isso pro andrey do futuro resolver
    ref_nome = cfg_col.get("mapa_ref",   "codigos_ibge_sp")
    col_chave = cfg_col.get("col_chave",  "cod_ibge")
    col_valor = cfg_col.get("col_valor",  "municipio")

    df_ref = dfs_ref.get("codigos_ibge_sp")
    if df_ref is None:
        print(f"[Aviso] DF de referência '{ref_nome}' não carregado. Pulando mapa.")
        return df

    if col_chave not in df_ref.columns or col_valor not in df_ref.columns:
        print(f"[Aviso] Colunas '{col_chave}'/'{col_valor}' não encontradas em '{ref_nome}'.")
        return df

    mapa = df_ref.set_index(col_chave)[col_valor]
    df[coluna] = df[coluna].map(mapa)
    df[coluna] = df[coluna].astype(str).apply(purge_unicode).str.upper()
    print(f"[Mapa] '{coluna}' mapeado via '{ref_nome}'")

    return df

def apply_purge(df: pd.DataFrame, coluna: str) -> pd.DataFrame:
    df[coluna] = purge_numbers(df[coluna])
    print(f"[Purge] '{coluna}' → dígitos removidos, strip, uppercase")
    return df

def apply_rename(df: pd.DataFrame, coluna: str, novo_nome: str) -> pd.DataFrame:
    if coluna not in df.columns:
        return df
    df = df.rename(columns={coluna: novo_nome})
    print(f"[Rename] '{coluna}' → '{novo_nome}'")
    return df

def apply_cast(df: pd.DataFrame, coluna: str, dtype: str) -> pd.DataFrame:
    if coluna not in df.columns:
        return df

    try:
        dtype = dtype.lower()

        match dtype:
            case "int" | "int64" | "float" | "float64":
                s_original = df[coluna]

                s = (s_original.astype("string").str.strip().str.replace(".", "", regex=False).str.replace(",", ".", regex=False))

                num = pd.to_numeric(s, errors="coerce")
                falhas = s_original[num.isna() & s_original.notna()]

                if not falhas.empty:
                    print(f"[Aviso] Alguns valores de '{coluna}' não puderam ser convertidos:")
                    print(falhas.unique()[:20])

                if dtype in ["int", "int64"]:
                    if (num.dropna() % 1 == 0).all():
                        df[coluna] = num.astype("Int64")
                    else:
                        df[coluna] = num.astype("float64")
                else:
                    df[coluna] = num.astype("float64")

            case "str" | "string":
                df[coluna] = df[coluna].astype("string")

            case "datetime":
                df[coluna] = pd.to_datetime(df[coluna], errors="coerce")

            case _:
                print(f"[Aviso] Tipo de cast desconhecido '{dtype}' para '{coluna}'. Pulando cast.")
            
    except Exception as e:
        print(f"[Aviso] cast '{coluna}' para {dtype} falhou: {e}")

    return df

def convert_category_to_columns(df: pd.DataFrame,category_col: str,cfg_col: dict,default_index: str = "municipio") -> pd.DataFrame:
    """
    Transforma uma coluna categórica em múltiplas colunas.

    Ex:
    municipio | tipo      | total
    A         | hospital  | 5
    A         | clinica   | 10

    vira:
    municipio | saude_hospital_total | saude_clinica_total
    A         | 5                    | 10
    """

    index_col = normalize_column_name(cfg_col.get("index", default_index))
    category_col = normalize_column_name(category_col)
    values = normalize_column_list(cfg_col.get("values"))
    prefixo = f"{prefixo_base}_" if (prefixo_base := cfg_col.get("prefixo")) else ""

    aggfunc = cfg_col.get("aggfunc", "sum")
    fill_value = cfg_col.get("fill_value", 0)

    if index_col not in df.columns:
        print(f"[Aviso] Coluna índice '{index_col}' não encontrada. Pivot pulado.")
        return df

    if category_col not in df.columns:
        print(f"[Aviso] Coluna categórica '{category_col}' não encontrada. Pivot pulado.")
        return df

    if not values:
        values = [col for col in df.columns if col not in {index_col, category_col} and pd.api.types.is_numeric_dtype(df[col])]

    values = [col for col in values if col in df.columns]

    if not values:
        print(f"[Aviso] Nenhuma coluna numérica válida encontrada para pivot em '{category_col}'.")
        return df

    df_wide = df.pivot_table(index=index_col, columns=category_col, values=values, aggfunc=aggfunc, fill_value=fill_value,)

    df_wide.columns = [normalize_column_name(f"{prefixo}{categoria}_{valor}") for valor, categoria in df_wide.columns]
    df_wide = df_wide.reset_index()

    return df_wide

# Transformação Principal

def transform(df: pd.DataFrame, config: dict, dfs_ref: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """
    Aplica transformações genéricas e específicas para uma fonte.

    Parâmetros
    ----------
    df       : DataFrame limpo (saída do cleaner)
    dfs_ref  : dicionário com DFs de referência já carregados {nome: DataFrame}
    """

    df = infer_numeric_columns(df)
    transformacoes = normalize_column_mapping(config.get("transformacoes")) or {}

    for coluna, cfg_col in transformacoes.items():
        if not cfg_col:
            continue

        if not isinstance(cfg_col, dict):
            print(f"[Aviso] Config inválida para '{coluna}'. Esperado dict, veio {type(cfg_col).__name__}. Pulando.")
            continue

        if cfg_col.get("convert_to_column"):
            df = convert_category_to_columns(df, coluna, cfg_col,)
            continue

        tipo = cfg_col.get("tipo")
        rename = cfg_col.get("rename")
        cast = cfg_col.get("cast")

        if coluna not in df.columns:
            print(f"[Aviso] Coluna '{coluna}' não encontrada no DataFrame. Pulando transformação.")
            print(f"[Debug] Colunas disponíveis: {list(df.columns)}")
            continue

        if tipo:
            match tipo:
                case "mapa_ibge":
                    df = apply_ibge(df, coluna, cfg_col, dfs_ref)

                case "purge":
                    df = apply_purge(df, coluna)

                case _:
                    print(f"[Aviso] Tipo desconhecido '{tipo}' para '{coluna}'. Pulando.")

        if cast:
            df = apply_cast(df, coluna, cast)

        if rename:
            rename_norm = normalize_column_name(rename)
            df = apply_rename(df, coluna, rename_norm)

    return df

# Carregamento de DFs de referência

def load_refs() -> dict[str, pd.DataFrame]:
    """
    Pré-carrega DFs que podem ser usados como referência de mapeamento.

    Por ora carrega o codigos_ibge_sp direto do mapping.
    """

    nome_refs = ["codigos_ibge_sp"]  # expandir conforme necessário
    refs = {}

    for fonte in nome_refs:
        caminho = MAPPING_DIR / f"{fonte}.csv"

        if not caminho.exists():
            print(f"[Aviso] DF de referência '{fonte}' não encontrado em {caminho}.")
            continue

        refs[fonte] = careful_load_csv(caminho)
        print(f"[Ref] '{fonte}' carregado de {caminho.relative_to(PATHS.root)}")

    return refs


def main():
    #import argparse

    #parser = argparse.ArgumentParser(description="Transformer da pipeline de dados")
    #parser.add_argument("--fonte", type=str, default=None, help="Nome da fonte (padrão: todas)")
    #parser.add_argument("--dry-run", action="store_true", help="Executa sem salvar")
    #args = parser.parse_args()

    pass

if __name__ == "__main__":
    main()
