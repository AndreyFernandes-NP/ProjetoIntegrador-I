from __future__ import annotations

import sys
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

from src.config import PATHS

CONFIG_DIR = PATHS.config
PROC_DIR = PATHS.data_processed

class DatasetGenerator:
    """
    Gera um dataset sintético a partir de dados reais de um dataframe base.

    A lógica principal é:
    - usar a coluna de IDS para classificar cada linha como low/medium/high;
    - sortear algumas linhas originais;
    - aplicar ruído percentual nos valores numéricos;
    - trocar o nome do município por um nome sintético;
    - preservar a estrutura das colunas do dataset original.
    """

    def __init__(self, df_base: pd.DataFrame, config: dict[str, Any]) -> None:
        self.df_base = df_base.copy()
        self.config = config

        self.n_rows = config.get("n_rows", 100)
        self.enabled = bool(config.get("enabled", True))
        self.rng = np.random.default_rng()

        columns_cfg = config.get("columns", {})
        self.ids_col = columns_cfg.get("ids", "ids")
        self.municipality_col = columns_cfg.get("municipality", "municipio")

        generation_cfg = config.get("generation", {})
        self.noise_factor = float(generation_cfg.get("noise_factor", 0.1))
        self.preserve_zero_probability = float(generation_cfg.get("preserve_zero_probability", 0.90))
        self.clip_to_original_range = bool(generation_cfg.get("clip_to_original_range", True))
        self.sample_with_replacement = bool(generation_cfg.get("sample_with_replacement", True))
        self.null_strategy = generation_cfg.get("null_strategy", "sample_column")

        sampling_cfg = config.get("sampling", {})
        self.sampling_mode = sampling_cfg.get("mode", "balanced")
        self.ids_distribution = sampling_cfg.get("ids_distribution", {"low": 0.33, "medium": 0.34, "high": 0.33})

        names_cfg = config.get("names", {})
        self.base_names_path = names_cfg.get("base_names_path", "muni_nomes.txt")
        self.surnames_path = names_cfg.get("surnames_path", "muni_sobrenomes.txt")
        self.connector_probability = float(names_cfg.get("connector_probability", 0.40))
        self.connectors = names_cfg.get("connectors", ["DE", "DA", "DO", "DAS", "DOS"])

        self.base_names = self._load_words(self.base_names_path)
        self.surnames = self._load_words(self.surnames_path)
        self.used_names: set[str] = set()

        self._validate_config()
        self._prepare_base_dataframe()

    def generate(self) -> pd.DataFrame:
        """
        Gera um dataframe sintético com n_rows linhas.

        Cada linha sintética nasce de uma linha real aleatoriamente.
        """
        if not self.enabled:
            print("[DatasetGenerator] Geração desabilitada. Retornando dataframe vazio.")
            return pd.DataFrame(columns=self.df_base.columns)
        
        n_rows = self.n_rows if self.n_rows > 0 else len(self.df_base)
        
        if n_rows <= 0:
            raise ValueError("n_rows precisa ser maior que zero.")
        
        if self.sampling_mode == "balanced":
            sampled_rows = self._sample_balanced(n_rows)
        elif self.sampling_mode == "random":
            sampled_rows = self._sample_randomly(n_rows)
        else:
            raise ValueError(f"Modo de amostragem desconhecido: {self.sampling_mode}")

        synthetic_rows = [self._generate_synthetic_row(row) for _, row in sampled_rows.iterrows()]

        df_synthetic = pd.DataFrame(synthetic_rows)

        return self._order_columns(df_synthetic)

    def save(self, df: pd.DataFrame, output_path: str | Path) -> None:
        output_path = PROC_DIR / output_path
        df.to_csv(output_path, index=False, encoding="utf-8-sig")

    def _validate_config(self) -> None:
        if self.ids_col not in self.df_base.columns:
            raise ValueError(f"Coluna de IDS '{self.ids_col}' não encontrada no dataframe base.")

        if self.municipality_col not in self.df_base.columns:
            raise ValueError(f"Coluna de município '{self.municipality_col}' não encontrada no dataframe base.")

        if not 0 <= self.noise_factor <= 1:
            raise ValueError("generation.noise_factor precisa estar entre 0 e 1.")

        if not 0 <= self.preserve_zero_probability <= 1:
            raise ValueError("generation.preserve_zero_probability precisa estar entre 0 e 1.")
        
        if self.sampling_mode == "balanced":
            distribution_sum = sum(self.ids_distribution.values())

            if not np.isclose(distribution_sum, 1.0):
                raise ValueError(f"A soma das proporções em sampling.ids_distribution precisa ser 1.0. Soma atual: {distribution_sum}")

    def _prepare_base_dataframe(self) -> None:
        """
        Prepara o dataframe base criando a coluna de classe derivada do IDS.
        """
        self.df_base[self.ids_col] = pd.to_numeric(self.df_base[self.ids_col], errors="coerce")

        self.df_base = self.df_base.dropna(subset=[self.ids_col]).reset_index(drop=True)

        if self.df_base.empty:
            raise ValueError("O dataframe base está vazio após processar a coluna de IDS. Verifique os dados e a configuração.")
    
    def _sample_randomly(self, n_rows: int) -> pd.DataFrame:
        """
        Sorteia n_rows linhas aleatoriamente do dataframe base.
        """
        if not self.sample_with_replacement and n_rows > len(self.df_base):
            raise ValueError("n_rows é maior que a quantidade de linhas reais disponíveis. Ative generation.sample_with_replacement ou reduza n_rows.")
        
        sampled_indices = self.rng.choice(self.df_base.index.to_numpy(), size=n_rows, replace=self.sample_with_replacement)

        return self.df_base.loc[sampled_indices].reset_index(drop=True)
    
    def _sample_balanced(self, n_rows: int) -> pd.DataFrame:
        """
        Sorteia n_rows linhas do dataframe base tentando manter a distribuição de classes do IDS.

        Exemplo: se IDS tem 30% low, 50% medium e 20% high, o dataset sintético também terá essa proporção.
        """
        ids = self.df_base[self.ids_col]

        q_low = ids.quantile(0.33)
        q_high = ids.quantile(0.67)
        
        groups = {
            "low": self.df_base[ids <= q_low],
            "medium": self.df_base[(ids > q_low) & (ids < q_high)],
            "high": self.df_base[ids >= q_high],
        }

        counts = self._calculate_sampling_counts(n_rows)

        sampled_parts: list[pd.DataFrame] = []

        for group, count in counts.items():
            candidates = groups[group]

            if candidates.empty:
                print(f"[Aviso] Não há linhas com classe '{group}' para amostrar.")
                continue

            replace = self.sample_with_replacement or count > len(candidates)

            sampled_indices = self.rng.choice(candidates.index.to_numpy(), size=count, replace=replace)
            sampled_parts.append(self.df_base.loc[sampled_indices])
        
        sampled = pd.concat(sampled_parts, ignore_index=True)
        random_state: int = int(self.rng.integers(0, 1_000_000))

        sampled = sampled.sample(frac=1, random_state=random_state).reset_index(drop=True)

        return sampled
    
    def _calculate_sampling_counts(self, n_rows: int) -> dict[str, int]:
        counts = {
            group_name: int(np.floor(n_rows * ratio)) for group_name, ratio in self.ids_distribution.items()
        }

        missing = n_rows - sum(counts.values())

        if missing > 0:
            sorted_groups = sorted(self.ids_distribution, key=self.ids_distribution.get, reverse=True)

            for group_name in sorted_groups[:missing]:
                counts[group_name] += 1
        
        return counts

    def _generate_synthetic_row(self, sampled: pd.Series) -> dict[str, Any]:
        row: dict[str, Any] = {}

        for col in self.df_base.columns:
            if col == self.ids_col:
                continue

            value = sampled[col]

            if col == self.municipality_col:
                row[col] = self._generate_municipality_name()
                continue
            
            if self._is_numeric_column(col):
                row[col] = self._perturb_numeric_value(col, value)
                continue

            row[col] = self._handle_non_numeric_value(col, value)
        
        return row

    def _is_numeric_column(self, col: str) -> bool:
        return pd.api.types.is_numeric_dtype(self.df_base[col])

    def _perturb_numeric_value(self, col: str, value: Any) -> int | float | None:
        """
        Aplica um ruído percentual uniforme no valor.

        Exemplo:
        - noise_factor = 0.10
        - valor = 100
        - novo valor fica entre 90 e 110
        """
        series = pd.to_numeric(self.df_base[col], errors="coerce").dropna()

        if series.empty:
            return None

        if pd.isna(value):
            numeric_value = self._handle_null_numeric_value(series)
        else:
            numeric_value = float(value)

        if numeric_value == 0:
            numeric_value = self._handle_zero_value(series)

        multiplier = self.rng.uniform(1 - self.noise_factor, 1 + self.noise_factor)

        new_value = numeric_value * multiplier

        if self.clip_to_original_range:
            new_value = float(np.clip(new_value, float(series.min()), float(series.max())))

        if self._is_integer_like(series):
            return int(round(new_value))

        return round(float(new_value), 6)
    
    def _handle_null_numeric_value(self, series: pd.Series) -> float:
        if self.null_strategy == "sample_column":
            return float(self.rng.choice(series.to_numpy()))
        
        if self.null_strategy == "zero":
            return 0.0
        
        return np.nan

    def _handle_zero_value(self, series: pd.Series) -> float:
        """
        Decide o que fazer quando o valor original é zero.

        Por padrão, preserva zero na maioria das vezes.
        Caso não preserve, pega um valor real não-zero da mesma coluna.
        """
        keep_zero = self.rng.random() < self.preserve_zero_probability

        if keep_zero:
            return 0.0

        non_zero_values = series[series != 0]

        if non_zero_values.empty:
            return 0.0

        return float(self.rng.choice(non_zero_values.to_numpy()))
    
    def _handle_non_numeric_value(self, col: str, value: Any) -> Any:
        if not pd.isna(value):
            return value
        
        if self.null_strategy != "sample_column":
            return None
        
        series = self.df_base[col].dropna()

        if series.empty:
            return None
        
        return self.rng.choice(series.to_numpy())

    def _generate_municipality_name(self, attempt: int = 0) -> str:
        if attempt > 10:
            raise RuntimeError("Não foi possível gerar nomes únicos suficientes. Adicione mais nomes aos arquivos de nomes/sobrenomes.")

        for _ in range(10_000):
            first = self._pick_word(self.base_names)
            surname = self._pick_word(self.surnames)

            if self.rng.random() < self.connector_probability:
                connector = self.rng.choice(self.connectors)
                name = f"{first} {connector} {surname}"
            else:
                name = f"{first} {surname}"

            if name not in self.used_names:
                self.used_names.add(name)
                return name

        self.used_names.clear()
        return self._generate_municipality_name(attempt + 1)

    def _pick_word(self, words: list[str]) -> str:
        if not words:
            raise ValueError("A lista de nomes está vazia. Verifique os arquivos configurados.")

        idx = int(self.rng.integers(0, len(words)))
        return words[idx]

    def _load_words(self, path: str | Path) -> list[str]:
        file_path = CONFIG_DIR / path

        if not file_path.exists():
            raise FileNotFoundError(f"Arquivo de nomes não encontrado: {file_path}")

        words = [line.strip().upper() for line in file_path.read_text(encoding="utf-8").splitlines() if line.strip()]

        if not words:
            raise ValueError(f"Arquivo de nomes vazio: {file_path}")

        return words

    def _is_integer_like(self, series: pd.Series) -> bool:
        clean = pd.to_numeric(series, errors="coerce").dropna()

        if clean.empty:
            return False

        return bool(np.all(np.equal(np.mod(clean, 1), 0)))

    def _order_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        cols = list(df.columns)
        
        if self.municipality_col in cols:
            cols.remove(self.municipality_col)
            cols.insert(0, self.municipality_col)

        return df[cols]