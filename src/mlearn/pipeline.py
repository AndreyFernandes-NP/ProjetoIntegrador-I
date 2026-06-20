import argparse
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))

import pandas as pd
import yaml

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler, RobustScaler, MaxAbsScaler
from sklearn.decomposition import PCA, KernelPCA

from src.config import PATHS
from src.mlearn.registry import create_supervised_model, create_unsupervised_model
from src.data.generator import DatasetGenerator
from src.core.calculator import calculate_ids, load_ids_config
from src.mlearn.fine_tuning import (SUPERVISED_TUNING_SETTINGS, explore_tuning_for_supervised_model, save_supervised_tuning_exploration_results,
                                    UNSUPERVISED_TUNING_SETTINGS, explore_tuning_for_unsupervised_model, save_unsupervised_tuning_results,
                                    PCA_TUNING_SETTINGS, explore_tuning_for_pca, save_pca_tuning_results)

CONFIG_PATH = PATHS.config / "models.yaml"
PROC_DIR = PATHS.data_processed

SCALER_REGISTRY = {
    "StandardScaler": StandardScaler,
    "MinMaxScaler": MinMaxScaler,
    "RobustScaler": RobustScaler,
    "MaxAbsScaler": MaxAbsScaler
}

PCA_REGISTRY = {
    "PCA": PCA,
    "KernelPCA": KernelPCA,
}

def load_dataframe(path: Path) -> pd.DataFrame:
    if not path.exists():
        raise FileNotFoundError(f"Arquivo de dataset não encontrado: {path}")

    df = pd.read_csv(path, sep=";", encoding="utf-8")

    return df

def load_models_config(path: Path) -> dict:
    default = {
        "dataset_config": {},
        "ml_supervised": {},
        "ml_unsupervised": {},
    }

    if not path.exists():
        return default

    with open(path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    if not isinstance(config, dict):
        return default
    
    if not isinstance(config.get("ml_supervised"), dict):
        config["dataset_config"] = {}
    
    if not isinstance(config.get("ml_supervised"), dict):
        config["ml_supervised"] = {}
    
    if not isinstance(config.get("ml_unsupervised"), dict):
        config["ml_unsupervised"] = {}

    return config

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

        self.global_cfg = self.config.get("global_config") or {}
        self.dataset_cfg = self.global_cfg.get("dataset") or {}
        self.preprocessing_cfg = self.global_cfg.get("preprocessing") or {}
        self.unsupervised_cfg = config.get("ml_unsupervised") or {}
        self.supervised_cfg = config.get("ml_supervised") or {}
        
        self.unsup_enabled = bool(self.unsupervised_cfg.get("enabled", False))
        self.sup_enabled = bool(self.supervised_cfg.get("enabled", False))

        self.unsup_tuning_exp = bool(self.unsupervised_cfg.get("fine-tuning_exploration", False))
        self.sup_tuning_exp = bool(self.supervised_cfg.get("fine-tuning_exploration", False))

        self.sup_split_cfg = self.supervised_cfg.get("split") or {}

        self.df: pd.DataFrame | None = None

        self.unsupervised_models = []
        self.unsupervised_results: list[dict] = []
        self.unsupervised_exploration_results: list[pd.DataFrame] = []

        self.supervised_models = []
        self.supervised_results: list[dict] = []
        self.supervised_prediction_results: list[dict] = []
        self.supervised_exploration_results: list[pd.DataFrame] = []

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
        target = self.dataset_cfg.get("target_col")

        if not target:
            raise ValueError("Campo dataset_config.target_col não definido em 'models.yaml'.")

        return target

    def get_global_features(self) -> list[str]:
        return self.dataset_cfg.get("features") or []

    def get_sup_test_size(self) -> float:
        return self.sup_split_cfg.get("global_test_size", 0.2)
    
    def get_sup_random_state(self) -> int:
        return self.sup_split_cfg.get("global_random_state", 42)

    # Feature selection
    def select_features_for_model(self, model) -> tuple[pd.DataFrame, pd.Series]:
        df = self.get_dataframe()
        target = self.get_global_target()

        if target not in df.columns:
            raise ValueError(f"Target '{target}' não encontrado no DataFrame.")

        global_features = self.get_global_features()
        model_features = model.features or []
        drop_cols = model.drop_cols or []

        features = global_features + model_features

        if features:
            selected_cols = list(dict.fromkeys(features))
        else:
            selected_cols = [col for col in df.columns if col != target and pd.api.types.is_numeric_dtype(df[col])]
            print(f"[Aviso] Modelo '{model.name}' sem features definidas, usando seleção automática: {selected_cols}")

        selected_cols = [col for col in selected_cols if col not in drop_cols]

        missing = [col for col in selected_cols if col not in df.columns]

        if missing:
            print(f"[Aviso] Modelo '{model.name}' possui features ausentes no DataFrame: {missing}")

        selected_cols = [col for col in selected_cols if col in df.columns]

        X = df[selected_cols].copy()
        y = df[target].copy()

        model.selected_features = selected_cols

        return X, y

    # Preprocessing
    def preprocess_X(self, X: pd.DataFrame) -> pd.DataFrame:
        return X.fillna(0) # TODO/FASE 2: implementar preprocessamento mais robusto depois pra modelos conseguirem lidar melhor com dados reais

    def maybe_scale(self, X_train, X_test, model):
        scale = self.preprocessing_cfg.get("scale", False)

        if not scale:
            return X_train, X_test

        scaler_name = self.preprocessing_cfg.get("scaler", "StandardScaler")
        scaler_cls = SCALER_REGISTRY.get(scaler_name, StandardScaler)
        model.set_scaler(scaler_cls())

        print(f"[ML] Aplicando scaler '{scaler_cls.__name__}' aos dados de treino e teste...")

        X_train_scaled = model.scaler.fit_transform(X_train)
        X_test_scaled = model.scaler.transform(X_test) if X_test is not None else None

        return X_train_scaled, X_test_scaled
    
    def maybe_reduce(self, pca_config, X_train, X_test, model):
        if not pca_config:
            print(f"[Aviso] Nenhuma configuração recebida, pulando etapa de PCA.")
            return X_train, X_test
        
        pca = pca_config.get("enabled", False)

        if not pca:
            return X_train, X_test

        pca_name = pca_config.get("tipo", "PCA")
        pca_params = pca_config.get("hyperparameters", {})
        pca_cls = PCA_REGISTRY.get(pca_name, "PCA")
        model.set_pca(self.select_pca(pca_name, **pca_params))

        print(f"[ML] Aplicando redução '{pca_cls.__name__}' aos dados de treino e teste...")

        if not model.pca:
            print(f"[Aviso] PCA não pôde ser aplicado, continuando...")
            return X_train, X_test
        
        X_train_reduced = model.pca.fit_transform(X_train)
        X_test_reduced = model.pca.transform(X_test) if X_test is not None else None

        return X_train_reduced, X_test_reduced
    
    def select_pca(self, pca_type: str, **hyperparameters):
        pca_class = PCA_REGISTRY.get(pca_type)

        if pca_class is None:
            print(f"[Erro] Tipo de PCA selecionado inválido: {pca_type}")
            return None

        return pca_class(**hyperparameters)

    # Model creation
    def build_unsupervised_models(self) -> None:
        models_cfg = self.unsupervised_cfg.get("models") or []

        created_models = [
            create_unsupervised_model(model_cfg=model_cfg, global_config=self.unsupervised_cfg)
            for model_cfg in models_cfg
        ]

        self.unsupervised_models = [model for model in created_models if model is not None]

        invalid_count = len(created_models) - len(self.unsupervised_models)
        if invalid_count:
            print(f"[ML] {invalid_count} modelo(s) inválido(s) ignorado(s).")
        
        print(f"[ML] {len(self.unsupervised_models)} modelo(s) não supervisionado(s) instanciado(s).")

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
    def setup_unsupervised(self) -> None:
        if not self.unsupervised_cfg:
            print("[ML] Nenhuma configuração ml_unsupervised encontrada.")
            return None

        self.build_unsupervised_models()

    def setup_supervised(self) -> None:
        if not self.supervised_cfg:
            print("[ML] Nenhuma configuração ml_supervised encontrada.")
            return None

        self.build_supervised_models()
    
    def run_unsupervised(self, model) -> bool:
        try:
            X, _ = self.select_features_for_model(model)
            X = self.preprocess_X(X)
            print(f"[ML] Dados preparados para modelo '{model.name}'. Quantidade de Features: {X.shape[1]}")

            pca_config = self.unsupervised_cfg.get('pca', None)
            X_train, _ = self.maybe_scale(X, None, model)
            X_train, _ = self.maybe_reduce(pca_config, X, None, model)
            print(f"[ML] Pré-processamento concluído para modelo '{model.name}', escalonamento aplicado?: {self.preprocessing_cfg.get('scale', False)}")

            if pca_config:
                print(f"[ML] Redução aplicada?: {pca_config.get('enabled', False)}")
            
            print(f"[ML] Treinando e avaliando modelo '{model.name}'...")
            result = model.run(X_train=X_train)

            self.unsupervised_results.append(result)

            print(
                f"[ML] {model.name} concluído "
                f"| Silhouette={model.metrics.get('silhouette'):.4f} "
                f"| Calinski-Harabasz={model.metrics.get('calinski_harabasz'):.4f} "
                f"| Davies-Bouldin={model.metrics.get('davies_bouldin'):.4f}"
            )
        except Exception as e:
            print(f"[Erro] Falha ao executar modelo não supervisionado '{model.name}': {e}")
            return False

        return True

    def run_supervised(self, model) -> bool:
        try:
            X, y = self.select_features_for_model(model)
            X = self.preprocess_X(X)
            print(f"[ML] Dados preparados para modelo '{model.name}'. Quantidade de Features: {X.shape[1]} | Target: {y.name}")

            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.get_sup_test_size(), random_state=self.get_sup_random_state())

            print(f"[ML] Dados divididos para modelo '{model.name}': {X_train.shape[0]} treino, {X_test.shape[0]} teste")

            pca_config = self.supervised_cfg.get('pca', None)
            X_train, X_test = self.maybe_scale(X_train, X_test, model)
            X_train, X_test = self.maybe_reduce(pca_config, X_train, X_test, model)

            print(f"[ML] Pré-processamento concluído para modelo '{model.name}', escalonamento aplicado?: {self.preprocessing_cfg.get('scale', False)}")

            if pca_config:
                print(f"[ML] Redução aplicada?: {pca_config.get('enabled', False)}")

            print(f"[ML] Treinando e avaliando modelo '{model.name}'...")
            result = model.run(X_train=X_train, X_test=X_test, y_train=y_train, y_test=y_test)

            self.supervised_results.append(result)

            print(
                f"[ML] {model.name} concluído "
                f"| R²={model.metrics.get('r2'):.4f} "
                f"| MAE={model.metrics.get('mae'):.4f}"
            )
        except Exception as e:
            print(f"[Erro] Falha ao executar modelo supervisionado '{model.name}': {e}")
            return False

        return True
    
    def predict_with_model(self, model, df_external: pd.DataFrame, has_target: bool = False) -> pd.DataFrame | None:
        target = self.get_global_target()
        features = getattr(model, "selected_features", None) or (self.get_global_features() + model.features)

        features = list(dict.fromkeys(features))

        missing = [col for col in features if col not in df_external.columns]

        if missing:
            print(f"[Erro] Dados externos para modelo '{model.name}' estão faltando features: {missing}")
            return None
        
        X_external = df_external[features].copy()
        X_external = self.preprocess_X(X_external)
        X_external = model.scaler.transform(X_external)

        if model.pca:
            X_external = model.pca.transform(X_external)

        y_pred = model.predict_external(X_external)
        y_pred = pd.Series(y_pred, index=df_external.index, name=f"{model.name}_pred")
        y_pred = y_pred.clip(lower=0, upper=1)

        result = pd.DataFrame(index=df_external.index)

        if "municipio" in df_external.columns:
            result["municipio"] = df_external["municipio"]
        
        result[f"{model.name}_pred"] = y_pred.round(3)

        if has_target and target in df_external.columns:
            y_true = df_external[target]

            result[f"{model.name}_true"] = df_external[target]

            metrics = model.evaluate(y_true, y_pred)
            
            validation_result = {
                "model": model.name,
                "tipo": model.tipo,
                "target": target,
                "n_rows": len(df_external),
                "r2": metrics["r2"],
                "mae": metrics["mae"],
                "rmse": metrics["rmse"],
            }

            self.supervised_prediction_results.append(validation_result)

            print(
                f"[ML] Validação externa de '{model.name}' concluído "
                f"| R²={metrics['r2']:.4f} "
                f"| MAE={metrics['mae']:.4f} "
                f"| RMSE={metrics['rmse']:.4f}"
            )
        
        elif has_target and target not in df_external.columns:
            print(f"[Aviso] 'has_target' é True, mas coluna de target '{target}' não encontrada nos dados externos para modelo '{model.name}'. Métricas de validação não serão calculadas.")

        return result
    
    def run_unsupervised_tuning_exploration(self) -> None:
        if not self.unsup_tuning_exp:
            print("[ML Exploration] A exploração de fine-tuning não supervisionada está desativada, continuando...")
            return

        print("\n[ML Exploration] Iniciando exploração de hiperparâmetros de modelos supervisionados...")

        self.unsupervised_tuning_results = []

        for model in self.unsupervised_models:
            try:
                print(f"[ML Exploration] Preparando dados para '{model.name}'...")

                X, _ = self.select_features_for_model(model)
                X = self.preprocess_X(X)

                if X.shape[1] == 0:
                    print(f"[Aviso] Modelo '{model.name}' ficou sem features. Pulando exploração.")
                    continue
                
                pca_config = self.unsupervised_cfg.get('pca', None)
                X_scaled, _ = self.maybe_scale(X, None, model)
                X_reduced, _ = self.maybe_reduce(pca_config, X_scaled, None, model)

                result = explore_tuning_for_unsupervised_model(model=model, X=X_reduced, settings=UNSUPERVISED_TUNING_SETTINGS)

                if result is not None:
                    self.unsupervised_tuning_results.append(result)

            except Exception as e:
                print(f"[Erro] Falha ao explorar '{model.name}': {e}")

        if UNSUPERVISED_TUNING_SETTINGS.get("save_results", True):
            output = PATHS.reports_ml / "ml_unsupervised_tuning_exploration.csv"

            save_unsupervised_tuning_results(results_list=self.unsupervised_tuning_results, output_path=output, sep=";")
    
    def run_supervised_tuning_exploration(self, validation_df: pd.DataFrame | None = None, has_target: bool = False) -> None:
        if not self.sup_tuning_exp:
            print("[ML Exploration] A exploração de fine-tuning supervisionada está desativada, continuando...")
            return
        
        print("\n[ML Exploration] Iniciando exploração de hiperparâmetros de modelos supervisionados...")

        self.supervised_exploration_results = []
        target = self.get_global_target()

        for model in self.supervised_models:
            try:
                print(f"[ML Exploration] Preparando dados para '{model.name}'...")

                X, y = self.select_features_for_model(model)
                X = self.preprocess_X(X)

                X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=self.get_sup_test_size(), random_state=self.get_sup_random_state())

                pca_config = self.supervised_cfg.get('pca', None)
                X_train, X_test = self.maybe_scale(X_train, X_test, model)
                X_train, X_test = self.maybe_reduce(pca_config, X_train, X_test, model)

                X_external = None
                y_external = None

                if validation_df is not None and has_target and target in validation_df.columns:
                    missing = [col for col in model.selected_features if col not in validation_df.columns]

                    if missing:
                        print(f"[Aviso] Validação externa ignorada para '{model.name}'. Features faltando: {missing}")
                    else:
                        X_external = validation_df[model.selected_features].copy()
                        X_external = self.preprocess_X(X_external)

                        if self.preprocessing_cfg.get("scale", False):
                            X_external = model.scaler.transform(X_external) if model.scaler else X_external
                        
                        y_external = validation_df[target].copy()

                result = explore_tuning_for_supervised_model(model=model, X_train=X_train, y_train=y_train, random_state=self.get_sup_random_state(), 
                                                  settings=SUPERVISED_TUNING_SETTINGS, X_external=X_external, y_external=y_external)

                if result is not None:
                    self.supervised_exploration_results.append(result)

            except Exception as e:
                print(f"[Erro] Falha ao explorar '{model.name}': {e}")
        
        if SUPERVISED_TUNING_SETTINGS.get("save_results", False):
            output = PATHS.reports_ml / "ml_supervised_tuning_exploration.csv"

            save_supervised_tuning_exploration_results(results_list=self.supervised_exploration_results, output_path=output, sep=";")
    
    def run_pca_tuning_exploration(self) -> None:
        pca_cfg = self.preprocessing_cfg.get("pca") or {}
        pca_tuning_exp = pca_cfg.get("fine-tuning_exploration", False)

        if not pca_tuning_exp:
            print("[ML Exploration] A exploração de fine-tuning de PCA está desativada, continuando...")
            return

        models = []

        if hasattr(self, "supervised_models"):
            models.extend(self.supervised_models)

        if hasattr(self, "unsupervised_models"):
            models.extend(self.unsupervised_models)

        if not models:
            print("[PCA Exploration] Nenhum modelo disponível para resolver features.")
            return

        model = models[0]

        X, _ = self.select_features_for_model(model)
        X = self.preprocess_X(X)

        if X.shape[1] == 0:
            print("[PCA Exploration] X não possui features, encerrando exploração...")
            return

        X_scaled, _ = self.maybe_scale(X, None, model)

        results = explore_tuning_for_pca(X=X_scaled, pca_cfg=pca_cfg, df_name="main_dataframe", settings=PCA_TUNING_SETTINGS,)

        if PCA_TUNING_SETTINGS.get("save_results", True):
            save_pca_tuning_results(results=results, output_dir=PATHS.reports_ml / "pca_tuning", sep=";")
    
    # Save
    def save_unsupervised_results(self, results_df: pd.DataFrame) -> None:
        if results_df.empty:
            print("[ML] Nenhum resultado não supervisionado para salvar.")
            return

        output = PATHS.reports_ml / "ml_unsupervised_metrics.csv"

        results_df.to_csv(output, sep=";", index=False, encoding="utf-8")
        print(f"[ML] Métricas não supervisionadas salvas em {output.relative_to(PATHS.root)}")

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
        self.setup_unsupervised()
        print("[ML] Modelos Não Supervisionados configurados. Modelos para executar:", [model.name for model in self.unsupervised_models])

        self.setup_supervised()
        print("[ML] Modelos Supervisionados configurados. Modelos para executar:", [model.name for model in self.supervised_models])

        unsupervised_status = {}
        for model in self.unsupervised_models:
            print(f"\n[ML] Executando modelo não supervisionado: {model.name} ({model.tipo})")
            unsupervised_status[model.name] = self.run_unsupervised(model)
        
        print(f"\n[ML] Execução de modelos não supervisionados concluída. Status dos modelos: {unsupervised_status}")
        results = pd.DataFrame(self.unsupervised_results)

        self.save_unsupervised_results(results)

        supervised_status = {}
        for model in self.supervised_models:
            print(f"\n[ML] Executando modelo supervisionado: {model.name} ({model.tipo})")
            supervised_status[model.name] = self.run_supervised(model)
        
        print(f"\n[ML] Execução dos modelos supervisionados concluída. Status dos modelos: {supervised_status}")
        results = pd.DataFrame(self.supervised_results)

        self.save_supervised_results(results)
        self.save_predictions()

def run_pipeline(config: dict) -> None:
    print("[ML] Configurando pipeline...")
    ml_pipeline = MachineLearningPipeline(config)
    print("[ML] Pipeline configurada. Iniciando execução...")
    ml_pipeline.run_all()

    print("[ML] Gerando dataset de validação...")
    generator = DatasetGenerator(load_dataframe(PROC_DIR / "main_dataframe.csv"))

    validation_df = generator.generate()
    load_ids_config()
    validation_df = calculate_ids(validation_df)
    generator.save(validation_df)

    print("[ML] Rodando exploração de hiperparâmetros com comparação externa...")
    ml_pipeline.run_unsupervised_tuning_exploration()
    ml_pipeline.run_supervised_tuning_exploration(validation_df=validation_df, has_target=True)
    ml_pipeline.run_pca_tuning_exploration()

    print("[ML] Realizando validação cruzada com dataset sintético...")
    for model in ml_pipeline.supervised_models:
        print(f"\n[ML] Validando modelo '{model.name}' com dataset sintético...")
        ml_pipeline.predict_with_model(model, validation_df, has_target=True)
    
    df_validation_metrics = pd.DataFrame(ml_pipeline.supervised_prediction_results)

    pred_output = PATHS.reports_ml / "ml_supervised_prediction_metrics.csv"
    df_validation_metrics.to_csv(pred_output, sep=";", index=False, encoding="utf-8")

if __name__ == "__main__":
    print("[ML] Iniciando pipeline de Machine Learning...")
    config = load_models_config(CONFIG_PATH)
    run_pipeline(config)