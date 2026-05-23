"""
calculator.py
------------
Calcula o IDS (Índice de Desenvolvimento de Saúde) de um município a partir de seus indicadores de saúde presentes no DataFrame.

O IDS é uma métrica composta que reflete o desenvolvimento de saúde de um município, considerando diversos indicadores como quantidade de estabelecimentos de saúde e instalações, acesso a serviços de saúde, tipo e quantidade de serviços realizados, infraestrutura, entre outros. Uma nova coluna 'ids' é adicionada ao DataFrame, representando o valor do IDS para cada município.
"""

import sys
from pathlib import Path

import pandas as pd
import numpy as np
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.config import PATHS

CONFIG_PATH = PATHS.config / "sources.yaml"

IDS_CONFIG = {
    "populacao_col": "populacao",

    "pesos_finais": {
        "infraestrutura": 0.25,
        "serviços": 0.40,
        "vulnerabilidade": 0.20,
        "renda": 0.15,
    },

    "infraestrutura": {
        "tipo": "densidade_ponderada",
        "normalizacao": "robust_minmax",
        "por_habitantes": 10000,
        "colunas": {}
    },

    "vulnerabilidade": {
        "tipo": "media_ponderada_populacional",
        "colunas": {}
    },

    "serviços": {
        "tipo": "cobertura_adaptativa",
        "alpha": 0.5,
        "por_habitantes": 10000,

        # Aqui o valor peso é a importância do serviço no S_total.
        "colunas": {},

        # Referência estadual baseada no próprio dataframe.
        "taxa_base": "median_dataframe"
    },

    "renda": {
        "tipo": "log_per_capita",
        "normalizacao": "robust_minmax",
        "coluna_valor": "receita_anual"
    }
}

# Funções de Cálculo

def safe_divide(num: pd.Series, den: pd.Series) -> pd.Series:
    """
    Divide duas Series evitando inf e NaN causados por divisão por zero.
    """
    resultado = num / den
    resultado = resultado.replace([np.inf, -np.inf], np.nan)
    return resultado.fillna(0.0)

def minmax_normalize(series: pd.Series) -> pd.Series:
    """
    Normalização min-max simples.
    """
    minimo = series.min()
    maximo = series.max()

    if pd.isna(minimo) or pd.isna(maximo) or maximo == minimo:
        return pd.Series(0.0, index=series.index)

    return ((series - minimo) / (maximo - minimo)).clip(0, 1)

def robust_minmax_normalize(series: pd.Series, q_min: float = 0.05, q_max: float = 0.95) -> pd.Series:
    """
    Normalização min-max robusta usando percentis.
    Evita que outliers distorçam demais nossa escala.
    """
    minimo = series.quantile(q_min)
    maximo = series.quantile(q_max)

    if pd.isna(minimo) or pd.isna(maximo) or maximo == minimo:
        return pd.Series(0.0, index=series.index)

    return ((series - minimo) / (maximo - minimo)).clip(0, 1)

def normalize_series(series: pd.Series, metodo: str = "robust_minmax") -> pd.Series:
    match metodo:
        case "minmax":
            return minmax_normalize(series)
        case "robust_minmax":
             return robust_minmax_normalize(series)
        case "none":
            return series
        case _:
            raise ValueError(f"[Erro] Método de normalização desconhecido: {metodo}")

def weighted_sum(df: pd.DataFrame, colunas_pesos: dict[str, float]) -> pd.Series:
    """
    Soma ponderada vetorizada:

    EX:
    score_i = coluna_a_i * peso_a + coluna_b_i * peso_b + ...
    """
    score = pd.Series(0.0, index=df.index)

    for coluna, peso in colunas_pesos.items():
        if coluna not in df.columns:
            print(f"[Aviso] Coluna não encontrada no dataframe: {coluna}. Pulando soma.")
            continue

        score += df[coluna].fillna(0.0) * peso

    return score

def calculate_infra(df: pd.DataFrame, config: dict[str, Any], populacao: pd.Series) -> pd.Series:
    """
    Função para calcular um índice básico de Infraestrutura, utilizado pro cálculo de IDS.

    Parâmetros
    ----------
    df          : Dataframe limpo, processado e mesclado.
    config      : configuração do IDS para definição de valores e tipos.
    populacao   : valor da nossa coluna de população.
    """

    colunas = config["colunas"]
    p_hab = config.get("por_habitantes", 10000)
    normalizacao = config.get("normalizacao", "robust_minmax")
    
    F_infra = weighted_sum(df, colunas)

    dens_infra = safe_divide(F_infra, populacao / p_hab)
    I_infra = normalize_series(dens_infra, normalizacao)

    return I_infra

def calculate_vul(df: pd.DataFrame, config: dict[str, Any], populacao: pd.Series) -> tuple[pd.Series, pd.Series]:
    """
    Função para que calculamos o valor do nosso índice de vulnerabilidade social dos municípios.
    
    Utilizado pro cálculo de IDS.

    Parâmetros
    ----------
    df          : Dataframe limpo, processado e mesclado.
    config      : configuração do IDS para definição de valores e tipos.
    populacao   : valor da nossa coluna de população.
    """

    colunas = config["colunas"]
    nec_bruta = weighted_sum(df, colunas)

    N_med = safe_divide(nec_bruta, populacao)
    N_med = N_med.clip(0, 1)

    I_vuln = 1 - N_med

    return I_vuln, N_med

def calculate_services(df: pd.DataFrame, config: dict[str, Any], populacao: pd.Series, N_med: pd.Series) -> pd.Series:
    """
    Função para calcularmos o índice de prestação de serviços de saúde de um município, com base na importância dos serviços utilizados pro cálculo.

    Utilizado pro cálculo de IDS.

    Parâmetros
    ----------
    df          : Dataframe limpo, processado e mesclado.
    config      : configuração do IDS para definição de valores e tipos.
    populacao   : valor da nossa coluna de população.
    N_med       : necessidade/vulnerabilidade média do município. (obtido de calculate_vul())
    """

    colunas = config["colunas"]
    alpha = config.get("alpha", 0.5)
    p_hab = config.get("por_habitantes", 10000)
    taxa_base = config.get("taxa_base", "median_dataframe")

    S_total = weighted_sum(df, colunas)

    serv_por_base = safe_divide(S_total, populacao / p_hab)

    match taxa_base:
        case "median_dataframe":
            tb_valor = serv_por_base.median()
        case "mean_dataframe":
            tb_valor = serv_por_base.mean()
        case int() | float():
            tb_valor = float(taxa_base)
        case _:
            raise ValueError(f"[Erro] Valor de 'taxa_base' inválido: {taxa_base}")

    meta = (tb_valor * (populacao / p_hab) * (1 + alpha * N_med))

    cobertura = safe_divide(S_total, meta)
    I_serv = cobertura.clip(upper=1)

    return I_serv

def calculate_income(df: pd.DataFrame, config: dict[str, Any], populacao: pd.Series) -> pd.Series:
    """
    Função para o cáluclo do índice de renda/economia de um município com base em sua receita anual e população total.
    
    Utilizado pro cálculo de IDS.

    Parâmetros
    ----------
    df          : Dataframe limpo, processado e mesclado.
    config      : configuração do IDS para definição de valores e tipos.
    populacao   : valor da nossa coluna de população.
    """

    coluna_valor = config["coluna_valor"]
    normalizacao = config.get("normalizacao", "robust_minmax")

    if coluna_valor not in df.columns:
        print(f"[Aviso] Coluna '{coluna_valor}' não encontrada no DataFrame. Índice de renda será zero.")
        return pd.Series(0.0, index=df.index)
    
    renda_pc = safe_divide(df[coluna_valor], populacao)
    log_renda = pd.Series(np.log1p(renda_pc), index=renda_pc.index, name="log_renda", dtype="float64")

    I_renda = normalize_series(log_renda, normalizacao)

    return I_renda

# Setup das colunas do IDS_CONFIG

def append_dimensions(config: dict) -> None:
    """
    Atualiza IDS_CONFIG com colunas vindas do YAML.

    Espera uma estrutura mais ou menos assim:

    ids:
      infraestrutura:
        hospitais_totais: 1.0
        clinicas_totais: 0.3

      serviços:
        atendimentos_basicos: 1.0
        equipes_saude_familia: 0.8

      vulnerabilidade:
        baixissima vulnerabilidade_n_pessoas: 0.0
        muito baixa vulnerabilidade_n_pessoas: 0.1

      renda:
        coluna_valor: rendimento_anual
    """
    ids = config.get("ids", {})

    if not ids:
        return

    for nome_dimensao, valores in ids.items():
        if nome_dimensao not in IDS_CONFIG:
            print(f"[Aviso] Dimensão '{nome_dimensao}' não reconhecida para IDS. Pulando.")
            continue

        if nome_dimensao == "renda":
            if isinstance(valores, dict) and "coluna_valor" in valores:
                IDS_CONFIG["renda"]["coluna_valor"] = valores["coluna_valor"]
            continue

        if "colunas" not in IDS_CONFIG[nome_dimensao]:
            continue

        if not isinstance(valores, dict):
            print(f"[Aviso] A dimensão '{nome_dimensao}' deve ser um dict no formato {{coluna: peso}}.")
            continue

        IDS_CONFIG[nome_dimensao]["colunas"].update(valores)

def load_ids_config(config: dict) -> None:
    """
    Carrega as colunas e pesos do IDS_CONFIG a partir do YAML.
    """
    fonte_cfg = config.get("fontes", {})
    for fonte in fonte_cfg:
        append_dimensions(fonte)
    
    return None

# Cálculo do IDS

def calculate_ids(df: pd.DataFrame, keep_intermeds: bool = False) -> pd.DataFrame:
    """
    Calcula o IDS (Índice de Desenvolvimento de Saúde) de um município a partir de seus indicadores de saúde presentes no DataFrame.

    Os indicadores são agrupados/reduzidos em 4 dimensões (infraestrutura, vulnerabilidade, serviços, renda) e ponderados de acordo com a configuração definida no YAML. O resultado é uma nova coluna 'ids' no DataFrame, representando o valor do IDS para cada município.

    Parâmetros
    ----------
    df              : Dataframe limpo, processado e mesclado, contendo as colunas exatas para cada cálculo.
    keep_intermeds  : Se True, mantém colunas intermediárias de cada dimensão (I_infra, I_vuln, N_med, I_serv, I_renda) para análise posterior. Caso contrário, retorna apenas a coluna final 'ids'.
    """

    df_ids = df.copy()
    populacao = IDS_CONFIG["populacao_col"]

    if populacao not in df_ids.columns:
        print(f"[Erro] Coluna de população não encontrada: {populacao}. Cálculo de IDS não pode ser realizado.")
        return df_ids

    populacao = df_ids[populacao]
    pesos_finais = IDS_CONFIG["pesos_finais"]

    I_infra = calculate_infra(df_ids, IDS_CONFIG["infraestrutura"], populacao)
    I_vuln, N_med = calculate_vul(df_ids, IDS_CONFIG["vulnerabilidade"], populacao)
    I_serv = calculate_services(df_ids, IDS_CONFIG["serviços"],populacao,N_med)
    I_renda = calculate_income(df_ids, IDS_CONFIG["renda"], populacao)

    IDS = (
        I_infra * pesos_finais.get("infraestrutura", 0.0)
        + I_serv * pesos_finais.get("serviços", 0.0)
        + I_vuln * pesos_finais.get("vulnerabilidade", 0.0)
        + I_renda * pesos_finais.get("renda", 0.0)
    )

    df_ids["ids"] = IDS.clip(0, 1).round(3)

    if keep_intermeds:
        df_ids["I_infra"] = I_infra
        df_ids["N_med"] = N_med
        df_ids["I_vuln"] = I_vuln
        df_ids["I_serv"] = I_serv
        df_ids["I_renda"] = I_renda

    return df_ids

def main():
    #import argparse

    #parser = argparse.ArgumentParser(description="Transformer da pipeline de dados")
    #parser.add_argument("--fonte", type=str, default=None, help="Nome da fonte (padrão: todas)")
    #parser.add_argument("--dry-run", action="store_true", help="Executa sem salvar")
    #args = parser.parse_args()

    pass

if __name__ == "__main__":
    main()
