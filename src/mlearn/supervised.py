import numpy as np
import pandas as pd

from sklearn.linear_model import LinearRegression
from sklearn.neighbors import KNeighborsRegressor
from sklearn.svm import SVR
from sklearn.tree import DecisionTreeRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score

from src.mlearn.base import MLModel


class BaseSupervisedModel(MLModel):
    """
    Classe base para modelos supervisionados.
    """

    def fit(self, X_train, y_train=None) -> None:
        if y_train is None:
            print(f"[Erro] Modelo supervisionado '{self.name}' precisa de y_train.")
            return None

        self.model = self.build_model()
        self.model.fit(X_train, y_train)

    def predict(self, X_test):
        if self.model is None:
            print(f"[Erro] Modelo '{self.name}' ainda não foi treinado.")
            return None

        return self.model.predict(X_test)
    
    def predict_external(self, X_external):
        # É a mesma função de predict, mas pra deixar claro que é pra dados externos (e, talvez fazer validações específicas aqui no futuro)
        if self.model is None:
            print(f"[Erro] Modelo '{self.name}' ainda não foi treinado.")
            return None

        return self.model.predict(X_external)

    def evaluate(self, y_true, y_pred) -> dict:
        self.metrics = {
            "mae": mean_absolute_error(y_true, y_pred),
            "rmse": np.sqrt(mean_squared_error(y_true, y_pred)),
            "r2": r2_score(y_true, y_pred),
        }

        return self.metrics

    def run(self, X_train, X_test, y_train, y_test) -> dict:
        self.fit(X_train, y_train)

        y_pred = self.predict(X_test)

        self.evaluate(y_test, y_pred)

        self.predictions = pd.DataFrame({
            "y_true": y_test,
            "y_pred": y_pred,
        })

        return self.get_result_row()


class LinearRegressionModel(BaseSupervisedModel):
    def build_model(self):
        return LinearRegression(**self.hyperparameters)

class KNNRegressorModel(BaseSupervisedModel):
    def build_model(self):
        return KNeighborsRegressor(**self.hyperparameters)

class SVRModel(BaseSupervisedModel):
    def build_model(self):
        return SVR(**self.hyperparameters)

class DecisionTreeRegressorModel(BaseSupervisedModel):
    def build_model(self):
        return DecisionTreeRegressor(**self.hyperparameters)

class RandomForestRegressorModel(BaseSupervisedModel):
    def build_model(self):
        return RandomForestRegressor(**self.hyperparameters)

class GradientBoostingRegressorModel(BaseSupervisedModel):
    def build_model(self):
        return GradientBoostingRegressor(**self.hyperparameters)
