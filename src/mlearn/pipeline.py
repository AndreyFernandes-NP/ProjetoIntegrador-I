import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pandas as pd

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler

from src.config import PATHS
from src.mlearn.registry import create_supervised_model
from src.core.pipeline import load_config

CONFIG_PATH = PATHS.config / "sources.yaml"

SCALER_REGISTRY = {
    "StandardScaler": StandardScaler,
    "MinMaxScaler": MinMaxScaler,
    "RobustScaler": RobustScaler,
    "MaxAbsScaler": MaxAbsScaler
}

class MachineLearningPipeline:
    """
    Pipeline principal de Machine Learning.

    Responsável por:
    - instanciar classes de modelos
    - preparar features/target
    - executar modelos
    - salvar métricas e predições
    """

    def __init__(self, config: dict) -> None:
        self.config = config

        self.supervised_cfg = config.get("ml_supervised") or {}
        self.enabled = bool(self.supervised_cfg.get("enabled", False))
        self.dataset_cfg = self.supervised_cfg.get("dataset") or {}
        self.split_cfg = self.supervised_cfg.get("split") or {}
        self.preprocessing_cfg = self.supervised_cfg.get("preprocessing") or {}

        self.df: pd.DataFrame | None = None

        self.supervised_models = []
        self.supervised_results: list[dict] = []

    # Dataset
    def load_dataset(self) -> pd.DataFrame:
        dataset_file = self.dataset_cfg.get("arquivo", "main_dataframe.csv")

        path = PATHS.data_processed / dataset_file

        if not path.exists():
            raise FileNotFoundError(f"Dataset não encontrado: {path}")

        self.df = pd.read_csv(path, sep=";", encoding="utf-8")

        print(f"[ML] Dataset carregado: {path.relative_to(PATHS.root)} ({len(self.df)} linhas x {len(self.df.columns)} colunas)")

        return self.df

    def get_dataframe(self) -> pd.DataFrame:
        if self.df is None:
            return self.load_dataset()

        return self.df
    
    # Supervised config
    def get_global_target(self) -> str:
        target = self.dataset_cfg.get("global_target")

        if not target:
            raise ValueError("Campo ml_supervised.dataset.global_target não definido em 'sources.yaml'.")

        return target

    def get_global_features(self) -> list[str]:
        return self.dataset_cfg.get("global_features") or []

    def get_test_size(self) -> float:
        return self.split_cfg.get("global_test_size", 0.2)
    
    def get_random_state(self) -> int:
        return self.split_cfg.get("global_random_state", 42)

    # Feature selection
    def select_features_for_model(self, model) -> tuple[pd.DataFrame, pd.Series]:
        df = self.get_dataframe()
        target = self.get_global_target()

        if target not in df.columns:
            raise ValueError(f"Target '{target}' não encontrado no DataFrame.")

        features = self.get_global_features() + model.features
        drop_cols = model.drop_cols

        if features:
            selected_cols = features
        else:
            selected_cols = [col for col in df.columns if col != target and col not in drop_cols and pd.api.types.is_numeric_dtype(df[col])]
            print(f"[Aviso] Modelo '{model.name}' sem features definidas, usando seleção automática: {selected_cols}")

        missing = [col for col in selected_cols if col not in df.columns]

        if missing:
            print(f"[Aviso] Modelo '{model.name}' possui features ausentes no DataFrame: {missing}")

        X = df[selected_cols].copy()
        y = df[target].copy()

        model.features = selected_cols

        return X, y

    # Preprocessing
    def preprocess_X(self, X: pd.DataFrame) -> pd.DataFrame:
        return X.fillna(0) # TODO/FASE 2: implementar preprocessamento mais robusto depois pra modelos conseguirem lidar melhor com dados reais

    def maybe_scale(self, X_train, X_test):
        scale = self.preprocessing_cfg.get("global_scale", False)

        if not scale:
            return X_train, X_test

        scaler_name = self.preprocessing_cfg.get("global_scaler", "StandardScaler")
        scaler_cls = SCALER_REGISTRY.get(scaler_name, StandardScaler)

        print(f"[ML] Aplicando scaler '{scaler_cls.__name__}' aos dados de treino e teste...")

        scaler = scaler_cls()
        X_train_scaled = scaler.fit_transform(X_train)
        X_test_scaled = scaler.transform(X_test)

        return X_train_scaled, X_test_scaled

    # Model creation
    def build_supervised_models(self) -> None:
        models_cfg = self.supervised_cfg.get("models") or []

        created_models = [
            create_supervised_model(model_cfg=model_cfg, global_config=self.supervised_cfg)
            for model_cfg in models_cfg
        ]

        self.supervised_models = [model for model in created_models if model is not None]

        invalid_count = len(created_models) - len(self.supervised_models)
        if invalid_count:
            print(f"[ML] {invalid_count} modelo(s) inválido(s) ignorado(s).")

        print(f"[ML] {len(self.supervised_models)} modelo(s) supervisionado(s) instanciado(s).")

    # Execution
    def setup_supervised(self) -> None:
        if not self.supervised_cfg:
            print("[ML] Nenhuma configuração ml_supervised encontrada.")
            return None

        self.build_supervised_models()

    def run_supervised(self, model) -> bool:
        try:
            X, y = self.select_features_for_model(model)
            X = self.preprocess_X(X)
            print(f"[ML] Dados preparados para modelo '{model.name}'. Features: {X.columns.tolist()}\n[ML] Target: {y.name}")

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.get_test_size(), random_state=self.get_random_state())

            print(f"[ML] Dados divididos para modelo '{model.name}': {X_train.shape[0]} treino, {X_test.shape[0]} teste")

            X_train, X_test = self.maybe_scale(X_train, X_test)
            print(f"[ML] Pré-processamento concluído para modelo '{model.name}', escala aplicada: {self.preprocessing_cfg.get('global_scale', False)}")

            print(f"[ML] Treinando e avaliando modelo '{model.name}'...")
            result = model.run(X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test)

            self.supervised_results.append(result)

            print(
                f"[ML] {model.name} concluído "
                f"| R²={model.metrics.get('r2'):.4f} "
                f"| MAE={model.metrics.get('mae'):.4f}"
            )
        except Exception as e:
            print(f"[Erro] Falha ao executar modelo '{model.name}': {e}")
            return False

        return True
    
    def predict_with_model(self, model, df_external: pd.DataFrame, has_target: bool = False) -> pd.DataFrame | None:
        target = self.get_global_target()
        features = model.features

        missing = [col for col in features if col not in df_external.columns]

        if missing:
            print(f"[Erro] Dados externos para modelo '{model.name}' estão faltando features: {missing}")
            return None
        
        X_external = df_external[features].copy()
        X_external = self.preprocess_X(X_external)

        y_pred = model.predict_external(X_external)
        result = pd.DataFrame()

        if "municipio" in df_external.columns:
            result["municipio"] = df_external["municipio"]
        
        result[f"{model.name}_pred"] = y_pred

        if has_target and target in df_external.columns:
            result[f"{model.name}_true"] = df_external[target]
        
        return result
    
    # Save
    def save_supervised_results(self, results_df: pd.DataFrame) -> None:
        if results_df.empty:
            print("[ML] Nenhum resultado supervisionado para salvar.")
            return

        output = PATHS.reports_ml / "ml_supervised_metrics.csv"

        results_df.to_csv(output, sep=";", index=False, encoding="utf-8")
        print(f"[ML] Métricas supervisionadas salvas em {output.relative_to(PATHS.root)}")

    def save_predictions(self) -> None:
        for model in self.supervised_models:
            if model.predictions is None:
                continue

            output = PATHS.reports_ml / f"{model.name}_predictions.csv"

            model.predictions.to_csv(output, sep=";", index=False, encoding="utf-8",)
            print(f"[ML] Predições salvas: {output.relative_to(PATHS.root)}")

    def run_all(self) -> None:
        self.setup_supervised()
        print("[ML] Modelos configurados. Modelos para executar:", [model.name for model in self.supervised_models])

        models_status = {}
        for model in self.supervised_models:
            print(f"\n[ML] Executando modelo: {model.name} ({model.tipo})")
            models_status[model.name] = self.run_supervised(model)
        
        print(f"\n[ML] Execução concluída. Status dos modelos: {models_status}")
        results = pd.DataFrame(self.supervised_results)

        self.save_supervised_results(results)
        self.save_predictions()

def run_pipeline(config: dict) -> None:
    print("[ML] Configurando pipeline...")
    ml_pipeline = MachineLearningPipeline(config)
    print("[ML] Pipeline configurada. Iniciando execução...")
    ml_pipeline.run_all()

if __name__ == "__main__":
    print("[ML] Iniciando pipeline de Machine Learning...")
    config = load_config(CONFIG_PATH)
    run_pipeline(config)