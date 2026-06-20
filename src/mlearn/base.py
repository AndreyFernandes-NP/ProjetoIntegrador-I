from abc import ABC, abstractmethod
from typing import Any

import pandas as pd

class MLModel(ABC):
    """
    Classe base para todos os modelos de machine learning.

    Guarda informações definidas no YAML como:
    - nome
    - tipo
    - features
    - drop_cols
    - hyperparameters
    - métricas
    - predições
    """

    def __init__(self, model_name: str, model_type: str, config: dict, global_config: dict | None = None) -> None:
        self.name = model_name
        self.tipo = model_type
        self.config = config
        self.global_config = global_config or {}

        self.features: list[str] = config.get("features") or []
        self.selected_features: list[str] = []
        self.drop_cols: list[str] = config.get("drop_cols") or []
        self.hyperparameters: dict[str, Any] = config.get("hyperparameters") or {}
        self.notes: str = config.get("notas", "")

        self.model: Any = None
        self.scaler: Any = None
        self.pca: Any = None
        self.metrics: dict[str, Any] = {}
        self.predictions: pd.DataFrame | None = None
        self.labels_: Any = None

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
    
    @abstractmethod
    def fit_predict(self, X_scaled):
        raise NotImplementedError

    def get_result_row(self) -> dict:
        """
        Retorna uma linha padronizada para salvar em CSV depois.
        """
        return {
            "nome": self.name,
            "tipo": self.tipo,
            "n_features": len(self.features) if self.features else None,
            "notas": self.notes,
            **self.metrics,
        }