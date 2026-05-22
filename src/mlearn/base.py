from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

class MLModel(ABC):
    """
    Classe base para todos os modelos de machine learning.

    Guarda informações definidas no YAML como:
    - name
    - tipo
    - features
    - drop_cols
    - hyperparameters
    - métricas
    - predições
    """

    def __init__(self, name: str, type: str, config: dict, global_config: dict | None = None) -> None:
        self.name = name
        self.type = type
        self.config = config
        self.global_config = global_config or {}

        self.features: list[str] = config.get("features") or []
        self.drop_cols: list[str] = config.get("drop_cols") or []
        self.hyperparameters: dict[str, Any] = config.get("hyperparameters") or {}
        self.notes: str = config.get("notas", "")

        self.model: Any = None
        self.metrics: dict[str, Any] = {}
        self.predictions: pd.DataFrame | None = None

    @abstractmethod
    def build_model(self) -> Any:
        """
        Cria o modelo real, ex: LinearRegression(), RandomForestRegressor().
        """
        raise NotImplementedError

    @abstractmethod
    def fit(self, X_train, y_train=None) -> None:
        raise NotImplementedError

    @abstractmethod
    def predict(self, X_test):
        raise NotImplementedError

    def get_result_row(self) -> dict:
        """
        Retorna uma linha padronizada para salvar em CSV depois.
        """
        return {
            "name": self.name,
            "tipo": self.type,
            "n_features": len(self.features) if self.features else None,
            "notas": self.notes,
            **self.metrics,
        }