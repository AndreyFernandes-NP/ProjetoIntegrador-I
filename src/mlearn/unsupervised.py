import numpy as np
import pandas as pd

from sklearn.cluster import KMeans, DBSCAN, MeanShift, AgglomerativeClustering
from sklearn.mixture import GaussianMixture
from sklearn.metrics import silhouette_score, calinski_harabasz_score, davies_bouldin_score

from src.mlearn.base import MLModel


class BaseUnsupervisedModel(MLModel):
    """
    Classe base para modelos não supervisionados.
    """
    def ensure_model(self) -> None:
        if self.model is None:
            self.model = self.build_model()

    def fit(self, X_train, y_train=None) -> None:
        if X_train is None:
            print(f"[Erro] Modelo não supervisionado '{self.name}' precisa de dados de treinamento.")
            return None

        self.ensure_model()     
        self.model.fit(X_train)
        
        if hasattr(self.model, "labels_"):
            self.labels_ = self.model.labels_

    def fit_predict(self, X_scaled) -> None:
        if X_scaled is None:
            print(f"[Erro] Modelo não supervisionado '{self.name}' precisa de dados para fit_predict.")
            return None
        
        self.ensure_model()
        self.labels_ = self.model.fit_predict(X_scaled)
            
    def evaluate(self, X_scaled, labels) -> dict:
        self.metrics = {
            "silhouette": silhouette_score(X_scaled, labels),
            "calinski_harabasz": calinski_harabasz_score(X_scaled, labels),
            "davies_bouldin": davies_bouldin_score(X_scaled, labels),
        }

        return self.metrics

    def run(self, X_train) -> dict | None:
        if X_train is None:
            print(f"[Erro] Modelo não supervisionado '{self.name}' precisa de dados de treinamento.")
            return None
        
        self.ensure_model()
        has_fit = hasattr(self.model, "fit")
        has_predict = hasattr(self.model, "predict")
        has_fit_predict = hasattr(self.model, "fit_predict")

        if has_fit and has_predict:
            self.fit(X_train)
        elif has_fit_predict:
            self.fit_predict(X_train)
        else:
            self.fit(X_train)

        self.evaluate(X_train, self.labels_)

        return self.get_result_row()
    
    def set_scaler(self, scaler) -> None:
        self.scaler = scaler if scaler else None

class KMeansModel(BaseUnsupervisedModel):
    def build_model(self):
        return KMeans(**self.hyperparameters)

class DBSCANModel(BaseUnsupervisedModel):
    def build_model(self):
        return DBSCAN(**self.hyperparameters)

class MeanShiftModel(BaseUnsupervisedModel):
    def build_model(self):
        return MeanShift(**self.hyperparameters)

class AgglomerativeClusteringModel(BaseUnsupervisedModel):
    def build_model(self):
        return AgglomerativeClustering(**self.hyperparameters)

class GaussianMixtureModel(BaseUnsupervisedModel):
    def build_model(self):
        return GaussianMixture(**self.hyperparameters)
