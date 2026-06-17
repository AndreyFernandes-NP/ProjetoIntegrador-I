from __future__ import annotations

from typing import Any, cast

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.base import clone
from sklearn.model_selection import KFold, RandomizedSearchCV, ParameterGrid
from sklearn.metrics import (r2_score, mean_absolute_error, mean_squared_error,
                             silhouette_score, calinski_harabasz_score, davies_bouldin_score)
from sklearn.cluster import estimate_bandwidth
from sklearn.decomposition import PCA, KernelPCA

UNSUPERVISED_TUNING_SETTINGS = {
    "show_top": 10,
    "save_results": True,
    "max_candidates": None,
    "random_state": 42,
}

SUPERVISED_TUNING_SETTINGS = {
    "n_iter": 100,
    "cv_splits": 5,
    "scoring": "r2",
    "show_top": 10,
    "evaluate_external_top": 10,
    "save_results": True,
}

PCA_TUNING_SETTINGS = {
    "show_top": 15,
    "save_results": True,
    "random_state": 42,
    # PCA Linear
    "variance_thresholds": [0.80, 0.85, 0.90, 0.95, 0.99],
}

UNSUPERVISED_TUNING_REGISTRY: dict[str, dict[str, list[Any]]] = {
    "KMeans": {
        "n_clusters": [2, 3, 4, 5, 6, 7, 8, 10, 12],
        "init": ["k-means++"],
        "n_init": [10, 20],
        "max_iter": [300, 500],
    },

    "DBSCAN": {
        "eps": [0.2, 0.3, 0.5, 0.75, 1.0, 1.25, 1.5, 2.0],
        "min_samples": [3, 5, 8, 10, 12, 15],
    },

    "MeanShift": {
        "bin_seeding": [True, False],
        "cluster_all": [True, False],
    },

    "GaussianMixture": {
        "n_components": [2, 3, 4, 5, 6, 7, 8, 10, 12],
        "covariance_type": ["full", "tied", "diag", "spherical"],
        "max_iter": [100, 300],
        "n_init": [1, 3, 5],
    },

    "AgglomerativeClustering": {
        "n_clusters": [2, 3, 4, 5, 6, 7, 8, 10, 12],
        "linkage": ["ward", "complete", "average"],
    }
}

SUPERVISED_TUNING_REGISTRY: dict[str, dict[str, list[Any]]] = {
    "GradientBoostingRegressor": {
        "n_estimators": [100, 200, 300, 400, 500],
        "learning_rate": [0.05, 0.07, 0.1, 0.12, 0.15, 0.2, 0.25, 0.4, 0.6],
        "max_depth": [1, 2, 3, 4, 5],
        "min_samples_split": [2, 5, 10, 20],
        "min_samples_leaf": [1, 3, 5, 10, 20],
        "subsample": [0.6, 0.75, 0.85, 1.0],
        "max_features": [None, "sqrt", 0.5, 0.75],
        "loss": ["squared_error", "absolute_error", "huber"],
    },

    "HistGradientBoostingRegressor": {
        "max_iter": [100, 200, 300, 400, 500],
        "learning_rate": [0.05, 0.07, 0.1, 0.12, 0.15, 0.2, 0.25, 0.4, 0.6, 0.8],
        "max_leaf_nodes": [7, 15, 31, 63],
        "min_samples_leaf": [5, 10, 15, 20, 30],
        "l2_regularization": [0.0, 0.001, 0.01, 0.1, 1.0],
        "max_bins": [64, 128, 255],
        "early_stopping": [True],
        "validation_fraction": [0.05, 0.10, 0.15, 0.20, 0.25],
        "n_iter_no_change": [10, 20, 30],
    },
}

PCA_TUNING_REGISTRY: dict[str, dict[str, list[Any]]] = {
    "PCA": {
        "n_components": [2, 3, 4, 5, 8, 10, 12, 15, 20, 25, 30],
        "svd_solver": ["auto", "full"],
    },

    "KernelPCA": {
        "n_components": [5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30],
        "kernel": ["rbf"],
        "gamma": [None, 0.001, 0.01, 0.05],
        "degree": [2, 3]
    }
}

def as_float(value: Any) -> float:
    return float(cast(Any, value))

def as_numpy(X) -> np.ndarray:
    if isinstance(X, pd.DataFrame):
        return X.to_numpy(dtype=float)
    
    return np.asarray(X, dtype=float)

def get_model_estimator(model):
    if hasattr(model, "model"):
        return model.model

    if hasattr(model, "estimator"):
        return model.estimator

    raise AttributeError(f"[Erro] Modelo '{model.name}' não possui os atributos 'model' ou 'estimator' com o estimador do sklearn interno.")

def regression_metrics(y_true, y_pred) -> dict[str, float]:
    y_true = pd.Series(y_true).reset_index(drop=True)
    y_pred = pd.Series(y_pred).reset_index(drop=True)

    return {
        "external_r2": r2_score(y_true, y_pred),
        "external_mae": mean_absolute_error(y_true, y_pred),
        "external_rmse": float(np.sqrt(mean_squared_error(y_true, y_pred))),
    }

def count_clusters(labels: np.ndarray, ignore_noise: bool = True) -> int:
    unique_labels = set(labels)

    if ignore_noise and -1 in unique_labels:
        unique_labels.remove(-1)
    
    return len(unique_labels)

def count_noise(labels: np.ndarray) -> int:
    return int(np.sum(labels == -1))

def valid_cluster(labels: np.ndarray, n_samples: int) -> bool:
    n_clusters = count_clusters(labels, ignore_noise=True)

    return 2 <= n_clusters < n_samples

def limit_components(candidates: list[int], max_components: int) -> list[int]:
    valid = []

    for n in candidates:
        if 1 <= int(n) <= max_components:
            valid.append(int(n))

    return list(dict.fromkeys(valid))

def fit_get_labels(estimator, X):
    """
    Treina um clone do estimador e retorna as labels.

    Suporta:
    - fit_predict
    - labels_
    - predict
    """

    candidate = clone(estimator)

    if hasattr(candidate, "fit_predict"):
        labels = candidate.fit_predict(X)
    else:
        candidate.fit(X)
    
        if hasattr(candidate, "labels_"):
            labels = candidate.labels_
        elif hasattr(candidate, "predict"):
            labels = candidate.predict(X)
        else:
            raise AttributeError(f"[Erro] Estimator {type(candidate).__name__} não possui fit_predict, labels_ ou predict. Certeza que chamou a função pro modelo correto? (na verdade, isso sequer é um modelo?)")
    
    return candidate, np.asarray(labels)

def build_unsupervised_param_grid(model_type: str, X) -> dict[str, list[Any]]:
    base_grid = UNSUPERVISED_TUNING_REGISTRY.get(model_type)

    if not base_grid:
        return {}

    if model_type != "MeanShift":
        return base_grid

    bandwidths = estimate_meanshift_bandwidth_candidates(X)

    grid = dict(base_grid)
    grid["bandwidth"] = bandwidths

    return grid

def estimate_meanshift_bandwidth_candidates(X) -> list[float | None]:
    quantiles = [0.1, 0.2, 0.3, 0.4, 0.5]

    bandwidths: list[float | None] = [None]

    for q in quantiles:
        try:
            bw = estimate_bandwidth(
                X,
                quantile=q,
                n_samples=min(500, len(X)),
            )

            if bw is not None and bw > 0:
                bandwidths.append(float(bw))

        except Exception:
            continue

    unique: list[float | None] = []

    for bw in bandwidths:
        if bw not in unique:
            unique.append(bw)

    return unique

def explore_tuning_for_unsupervised_model(model, X, settings: dict[str, Any] | None = None) -> pd.DataFrame | None:
    """
    Executa uma exploração de hiperparâmetros para um modelo não supervisionado, a fim de encontrar o melhor agrupamento.

    Importante:
    - Não altera model.hyperparameters.
    - Usa clone(estimator).
    - Usa refit=False.

    Retorna um DataFrame com os resultados da exploração.
    """
    settings = settings or UNSUPERVISED_TUNING_SETTINGS

    estimator = get_model_estimator(model)
    model_type = model.tipo

    param_grid = build_unsupervised_param_grid(model_type, X)

    if not param_grid:
        print(f"[ML Exploration] Nenhum espaço definido para tipo '{model_type}'. Pulando '{model.name}'...")
        return None
    
    max_candidates = settings.get("max_candidates")
    show_top = int(settings.get("show_top", 10))

    candidates = list(ParameterGrid(param_grid))

    if max_candidates is not None:
        candidates = candidates[: int(max_candidates)]
    
    print(f"\n[ML Exploration] Rodando exploração para '{model.name}' | tipo={model_type} | candidatos={len(candidates)}")

    rows = []

    for i, params in enumerate(candidates, start=1):
        try:
            candidate = clone(estimator)
            candidate.set_params(**params)

            fitted, labels = fit_get_labels(candidate, X)

            metrics = cluster_metrics(X, labels)

            inertia = getattr(fitted, "inertia_", None)
            bic = None
            aic = None

            if model_type == "GaussianMixture":
                try:
                    bic = float(fitted.bic(X))
                    aic = float(fitted.aic(X))
                except Exception:
                    bic = None
                    aic = None
            
            row = {
                "model": model.name,
                "tipo": model_type,
                "candidate": i,
                "params": params,
                "n_clusters": metrics["n_clusters"],
                "n_noise": metrics["n_noise"],
                "silhouette": metrics["silhouette"],
                "calinski_harabasz": metrics["calinski_harabasz"],
                "davies_bouldin": metrics["davies_bouldin"],
                "inertia": float(inertia) if inertia is not None else None,
                "bic": bic,
                "aic": aic,
            }

            rows.append(row)
        
        except Exception as e:
            rows.append({
                "model": model.name,
                "tipo": model_type,
                "candidate": i,
                "params": params,
                "n_clusters": None,
                "n_noise": None,
                "silhouette": None,
                "calinski_harabasz": None,
                "davies_bouldin": None,
                "inertia": None,
                "bic": None,
                "aic": None,
                "error": str(e),
            })
    
    results = pd.DataFrame(rows)
    results = rank_unsupervised_results(results)

    print_unsupervised_tuning_summary(model_name=model.name, model_type=model_type, results=results, show_top=show_top)
    plot_unsupervised_metric_curves(model_name=model.name, model_type=model_type, results=results)

    return results

def explore_tuning_for_supervised_model(model, X_train, y_train, random_state: int = 42, settings: dict[str, Any] | None = None,
                             X_external=None, y_external=None) -> pd.DataFrame | None:
    """
    Executa uma exploração de hiperparâmetros para um modelo supervisionado.

    Importante:
    - Não altera model.hyperparameters.
    - Usa clone(estimator).
    - Usa refit=False.

    Retorna um DataFrame com os resultados da exploração. Se X_external/y_external forem enviados,
    avalia os melhores candidatos também no DF externo.
    """

    settings = settings or SUPERVISED_TUNING_SETTINGS

    param_distributions = SUPERVISED_TUNING_REGISTRY.get(model.tipo)

    if not param_distributions:
        print(f"[ML Exploration] Nenhum espaço definido para tipo '{model.tipo}'. Pulando '{model.name}'...")
        return None

    n_iter = int(settings.get("n_iter", 50))
    cv_splits = int(settings.get("cv_splits", 5))
    scoring = settings.get("scoring", "r2")
    show_top = int(settings.get("show_top", 10))
    evaluate_external_top = int(settings.get("evaluate_external_top", show_top))

    cv = KFold(n_splits=cv_splits, shuffle=True, random_state=random_state)

    estimator = get_model_estimator(model)

    search = RandomizedSearchCV(
        estimator=clone(estimator),
        param_distributions=param_distributions,
        n_iter=n_iter,
        scoring=scoring,
        cv=cv,
        n_jobs=-1,
        random_state=random_state,
        return_train_score=True,
        refit=False,
        verbose=1,
    )

    print(f"\n[ML Exploration] Rodando exploração para '{model.name}' | tipo={model.tipo} | n_iter={n_iter} | cv={cv_splits} | scoring={scoring}")

    search.fit(X_train, y_train)

    results = pd.DataFrame(search.cv_results_)
    results["model"] = model.name
    results["tipo"] = model.tipo

    view_cols = [
        "model",
        "tipo",
        "rank_test_score",
        "mean_train_score",
        "std_train_score",
        "mean_test_score",
        "std_test_score",
        "params",
    ]

    results_view = (results[view_cols].sort_values("rank_test_score").reset_index(drop=True))

    if X_external is not None and y_external is not None:
        results_view = evaluate_external_top_candidates(
            base_estimator=estimator,
            results=results_view,
            X_train=X_train,
            y_train=y_train,
            X_external=X_external,
            y_external=y_external,
            top_n=evaluate_external_top,
        )

    print_tuning_summary(model_name=model.name, results=results_view, show_top=show_top, has_external=X_external is not None and y_external is not None)
    plot_tuning_top_results(model_name=model.name, results=results_view, show_top=show_top)
    plot_tuning_train_vs_validation(model_name=model.name, results=results_view, show_top=show_top)

    if X_external is not None and y_external is not None:
        plot_cv_vs_external(model_name=model.name, results=results_view, show_top=show_top)

    return results_view

def explore_tuning_for_pca(X, pca_cfg: dict[str, Any], df_name: str = "main_dataset", settings: dict[str, Any] | None = None) -> pd.DataFrame | dict[str, pd.DataFrame] | None:
    settings = settings or PCA_TUNING_SETTINGS
    pca_type = pca_cfg.get("tipo", None)

    if not pca_type:
        print("[PCA Exploration] Campo 'tipo' não encontrado na config do PCA.")
        return None

    search_space = PCA_TUNING_REGISTRY.get(pca_type)

    if search_space is None:
        print(f"[PCA Exploration] Tipo de PCA não suportado no registry: {pca_type}")
        return None

    X_array = as_numpy(X)

    if X_array.ndim != 2 or X_array.shape[1] == 0:
        print(f"[Aviso] X precisa ter pelo menos uma feature, pulando.")
        return None

    print(f"[PCA Exploration] Iniciando exploração do '{pca_type}' no dataset '{df_name}' [shape={X_array.shape}]")

    base_hyperparameters = pca_cfg.get("hyperparameters", {}) or {}

    if pca_type == "PCA":
        return explore_linear_pca(X=X_array, df_name=df_name, search_space=search_space, settings=settings)

    if pca_type == "KernelPCA":
        return explore_kernel_pca(X=X_array, df_name=df_name, search_space=search_space, settings=settings)
    

def explore_linear_pca(X: np.ndarray, df_name: str, search_space: dict[str, list[Any]], settings: dict[str, Any]) -> dict[str, pd.DataFrame]:
    random_state = int(settings.get("random_state", 42))

    n_samples, n_features = X.shape
    max_components = min(n_samples, n_features)

    print(f"[PCA Exploration] Máximo de componentes possíveis: {max_components}")

    full_pca = PCA(n_components=max_components, random_state=random_state)
    full_pca.fit(X)

    explained = full_pca.explained_variance_ratio_
    cumulative = np.cumsum(explained)

    variance_df = pd.DataFrame({
        "component": np.arange(1, len(explained) + 1),
        "explained_variance_ratio": explained,
        "cumulative_variance": cumulative,
    })

    thresholds = settings.get("variance_thresholds", [0.80, 0.90, 0.95, 0.99])

    threshold_rows = []

    for threshold in thresholds:
        n_required = int(np.searchsorted(cumulative, threshold) + 1)

        threshold_rows.append({
            "dataset": df_name,
            "threshold": threshold,
            "n_components_required": n_required,
            "reached_variance": float(cumulative[n_required - 1]),
        })

    thresholds_df = pd.DataFrame(threshold_rows)

    n_components_candidates = limit_components(
        search_space.get("n_components", []),
        max_components=max_components,
    )

    param_grid = {key: value for key, value in search_space.items() if key != "n_components"}
    param_grid["n_components"] = n_components_candidates

    candidates = list(ParameterGrid(param_grid))

    rows = []

    for i, params in enumerate(candidates, start=1):
        try:
            final_params = dict(params)

            pca = PCA(**final_params, random_state=random_state,)

            X_transformed = pca.fit_transform(X)
            X_reconstructed = pca.inverse_transform(X_transformed)

            reconstruction_mse = mean_squared_error(X, X_reconstructed)
            retained_variance = float(np.sum(pca.explained_variance_ratio_))

            rows.append({
                "dataset": df_name,
                "pca_type": "PCA",
                "candidate": i,
                "n_components": final_params.get("n_components"),
                "svd_solver": final_params.get("svd_solver"),
                "retained_variance": retained_variance,
                "reconstruction_mse": float(reconstruction_mse),
                "params": final_params,
            })

        except Exception as e:
            rows.append({
                "dataset": df_name,
                "pca_type": "PCA",
                "candidate": i,
                "params": params,
                "error": str(e),
            })

    candidates_df = pd.DataFrame(rows)
    candidates_df = rank_linear_pca_results(candidates_df)

    print_linear_pca_summary(thresholds_df=thresholds_df, candidates_df=candidates_df, show_top=int(settings.get("show_top", 15)))
    plot_pca_cumulative_variance(df_name=df_name, variance_df=variance_df, thresholds=thresholds)
    plot_pca_reconstruction_error(df_name=df_name, candidates_df=candidates_df)

    return {
        "variance": variance_df,
        "thresholds": thresholds_df,
        "candidates": candidates_df,
    }

def explore_kernel_pca(X: np.ndarray, df_name: str, search_space: dict[str, list[Any]], settings: dict[str, Any]) -> pd.DataFrame:
    random_state = int(settings.get("random_state", 42))

    n_samples, n_features = X.shape
    max_components = min(n_samples, n_features)

    n_components_candidates = limit_components(search_space.get("n_components", []), max_components=max_components)

    param_grid = dict(search_space)
    param_grid["n_components"] = n_components_candidates

    candidates = list(ParameterGrid(param_grid))

    print(f"[KernelPCA Exploration] Candidatos: {len(candidates)}")

    rows = []

    for i, params in enumerate(candidates, start=1):
        try:
            final_params = clean_kernel_pca_params(dict(params))

            kpca = KernelPCA(**final_params, random_state=random_state)

            X_transformed = kpca.fit_transform(X)

            reconstruction_mse = None

            if final_params.get("fit_inverse_transform", False):
                try:
                    X_reconstructed = kpca.inverse_transform(X_transformed)
                    reconstruction_mse = float(mean_squared_error(X, X_reconstructed))
                except Exception:
                    reconstruction_mse = None

            transformed_variance = float(np.var(X_transformed, axis=0).sum())

            eigenvalue_sum = None
            eigenvalue_ratio_proxy = None

            if hasattr(kpca, "eigenvalues_"):
                eigenvalues = np.asarray(kpca.eigenvalues_, dtype=float)
                eigenvalue_sum = float(np.sum(eigenvalues))

                if eigenvalue_sum > 0: eigenvalue_ratio_proxy = float(np.sum(eigenvalues) / eigenvalue_sum)
            
            energy_info = calculate_kernel_pca_energy_ratio(X=X, kernel=final_params.get("kernel"), 
                                                            n_components=final_params.get("n_components"), gamma=final_params.get("gamma"), 
                                                            degree=final_params.get("degree", 3), max_full_components=100)

            rows.append({
                "dataset": df_name,
                "pca_type": "KernelPCA",
                "candidate": i,
                "n_components": final_params.get("n_components"),
                "kernel": final_params.get("kernel"),
                "gamma": final_params.get("gamma"),
                "degree": final_params.get("degree"),
                "kernel_energy_ratio": energy_info["kernel_energy_ratio"],
                "kernel_energy_percent": energy_info["kernel_energy_percent"],
                "total_kernel_energy": energy_info["total_kernel_energy"],
                "transformed_variance": transformed_variance,
                "eigenvalue_sum": eigenvalue_sum,
                "eigenvalue_ratio_proxy": eigenvalue_ratio_proxy,
                "params": final_params,
            })

        except Exception as e:
            rows.append({
                "dataset": df_name,
                "pca_type": "KernelPCA",
                "candidate": i,
                "params": params,
                "error": str(e),
            })

    results = pd.DataFrame(rows)
    results = rank_kernel_pca_results(results)

    print_kernel_pca_summary(results=results, show_top=int(settings.get("show_top", 15)))
    plot_kernel_pca_results(df_name=df_name, results=results, show_top=int(settings.get("show_top", 15)))

    return results

def cluster_metrics(X, labels: np.ndarray) -> dict[str, float | int | None]:
    n_samples = len(labels)
    n_clusters = count_clusters(labels, ignore_noise=True)
    n_noise = count_noise(labels)

    metrics: dict[str, float | int | None] = {
        "n_clusters": n_clusters,
        "n_noise": n_noise,
        "silhouette": None,
        "calinski_harabasz": None,
        "davies_bouldin": None,
    }

    if not valid_cluster(labels, n_samples):
        return metrics
    
    try:
        metrics["silhouette"] = float(silhouette_score(X, labels))
    except Exception:
        metrics["silhouette"] = None
    
    try:
        metrics["calinski_harabasz"] = float(calinski_harabasz_score(X, labels))
    except Exception:
        metrics["calinski_harabasz"] = None

    try:
        metrics["davies_bouldin"] = float(davies_bouldin_score(X, labels))
    except Exception:
        metrics["davies_bouldin"] = None
    
    return metrics

def rank_unsupervised_results(results: pd.DataFrame) -> pd.DataFrame:
    results = results.copy()

    results["silhouette_rank_value"] = results["silhouette"].fillna(-9999)
    results["davies_rank_value"] = results["davies_bouldin"].fillna(9999)
    results["calinski_rank_value"] = results["calinski_harabasz"].fillna(-9999)

    results = results.sort_values(
        by=[
            "silhouette_rank_value",
            "davies_rank_value",
            "calinski_rank_value",
        ],
        ascending=[
            False,
            True,
            False,
        ],
    ).reset_index(drop=True)

    results["rank"] = range(1, len(results) + 1)

    return results.drop(columns=["silhouette_rank_value", "davies_rank_value", "calinski_rank_value"], errors="ignore")

def evaluate_external_top_candidates(base_estimator, results: pd.DataFrame, X_train, y_train, X_external, y_external, top_n: int = 10) -> pd.DataFrame:
    results = results.copy()

    results["external_r2"] = np.nan
    results["external_mae"] = np.nan
    results["external_rmse"] = np.nan
    results["generalization_gap_cv_external"] = np.nan

    top_n = min(top_n, len(results))

    print(f"[ML Exploration] Avaliando top {top_n} configurações no DataFrame externo de validação/predição...")

    for idx in range(top_n):
        params = cast(dict[str, Any], results.at[idx, "params"])

        candidate = clone(base_estimator)
        candidate.set_params(**params)
        candidate.fit(X_train, y_train)

        y_pred = candidate.predict(X_external)
        y_pred = pd.Series(y_pred, index=y_external.index).clip(lower=0, upper=1)

        metrics = regression_metrics(y_external, y_pred)
        mean_test_score = as_float(results.loc[idx, "mean_test_score"])
        external_r2 = float(metrics["external_r2"])

        results.loc[idx, "external_r2"] = metrics["external_r2"]
        results.loc[idx, "external_mae"] = metrics["external_mae"]
        results.loc[idx, "external_rmse"] = metrics["external_rmse"]
        results.loc[idx, "generalization_gap_cv_external"] = mean_test_score - external_r2

    return results

def rank_linear_pca_results(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty or "reconstruction_mse" not in df.columns:
        return df

    df = df.copy()

    df["reconstruction_rank_value"] = df["reconstruction_mse"].fillna(np.inf)
    df["variance_rank_value"] = df["retained_variance"].fillna(-np.inf)

    df = df.sort_values(by=["reconstruction_rank_value", "variance_rank_value"], ascending=[True, False]).reset_index(drop=True)
    df["rank"] = np.arange(1, len(df) + 1)

    return df.drop(columns=["reconstruction_rank_value", "variance_rank_value"], errors="ignore")

def rank_kernel_pca_results(df: pd.DataFrame) -> pd.DataFrame:
    if df.empty:
        return df

    df = df.copy()

    if "reconstruction_mse" not in df.columns:
        df["reconstruction_mse"] = np.nan

    if "transformed_variance" not in df.columns:
        df["transformed_variance"] = np.nan

    df["reconstruction_rank_value"] = df["reconstruction_mse"].fillna(np.inf)
    df["variance_rank_value"] = df["transformed_variance"].fillna(-np.inf)

    df = df.sort_values(by=["reconstruction_rank_value", "variance_rank_value"], ascending=[True, False]).reset_index(drop=True)
    df["rank"] = np.arange(1, len(df) + 1)

    return df.drop(columns=["reconstruction_rank_value", "variance_rank_value"], errors="ignore")

def clean_kernel_pca_params(params: dict[str, Any]) -> dict[str, Any]:
    clean = dict(params)

    kernel = clean.get("kernel")

    if kernel in {"linear", "cosine"}:
        clean.pop("gamma", None)

    if kernel != "poly":
        clean.pop("degree", None)

    return clean

def calculate_kernel_pca_energy_ratio(X, kernel: str | None, n_components: int | None, 
                                      gamma=None, degree: int = 3, coef0: float = 1.0, 
                                      max_full_components: int | None = None) -> dict:
    max_components = min(X.shape[0], X.shape[1])

    if max_full_components is not None:
        max_components = min(max_components, max_full_components)

    params = {
        "n_components": max_components,
        "kernel": kernel,
        "fit_inverse_transform": False,
    }

    if kernel in {"rbf", "poly", "sigmoid"} and gamma is not None:
        params["gamma"] = gamma

    if kernel == "poly":
        params["degree"] = degree
        params["coef0"] = coef0

    kpca_full = KernelPCA(**params)
    kpca_full.fit(X)

    eigenvalues = np.asarray(kpca_full.eigenvalues_, dtype=float)
    eigenvalues = np.clip(eigenvalues, a_min=0.0, a_max=None)

    total_energy = eigenvalues.sum()

    if total_energy <= 0:
        return {
            "kernel_energy_ratio": None,
            "kernel_energy_percent": None,
            "total_kernel_energy": float(total_energy),
        }

    selected_energy = eigenvalues[:n_components].sum()
    ratio = selected_energy / total_energy

    return {
        "kernel_energy_ratio": float(ratio),
        "kernel_energy_percent": float(ratio * 100),
        "total_kernel_energy": float(total_energy),
    }

def print_unsupervised_tuning_summary(model_name: str, model_type: str, results: pd.DataFrame, show_top: int = 10) -> None:
    if results.empty:
        print(f"[ML Exploração] Nenhum resultado para '{model_name}'.")
        return

    print(f"\n[ML Exploration] Top {show_top} configurações para '{model_name}':")

    cols = [
        "rank",
        "n_clusters",
        "n_noise",
        "silhouette",
        "calinski_harabasz",
        "davies_bouldin",
    ]

    if model_type in {"KMeans", "MiniBatchKMeans"}:
        cols.append("inertia")

    if model_type == "GaussianMixture":
        cols.extend(["bic", "aic"])

    cols.append("params")

    available_cols = [col for col in cols if col in results.columns]

    print(results[available_cols].head(show_top).to_string(index=False))

    best = results.iloc[0]

    print(f"\n[ML Exploração] Sugestão exploratória para '{model_name}':")
    print(f"Clusters: {best.get('n_clusters')}")
    print(f"Noise: {best.get('n_noise')}")
    print(f"Silhouette: {best.get('silhouette')}")
    print(f"Calinski-Harabasz: {best.get('calinski_harabasz')}")
    print(f"Davies-Bouldin: {best.get('davies_bouldin')}")

    if model_type in {"KMeans", "MiniBatchKMeans"}:
        print(f"Inertia: {best.get('inertia')}")

    if model_type == "GaussianMixture":
        print(f"BIC: {best.get('bic')}")
        print(f"AIC: {best.get('aic')}")

    print("Parâmetros sugeridos:")
    print(best.get("params"))

def print_tuning_summary(model_name: str, results: pd.DataFrame, show_top: int = 10, has_external: bool = False) -> None:
    if results.empty:
        print(f"[ML Exploration] Nenhum resultado para '{model_name}'.")
        return

    print(f"\n[ML Exploration] Top {show_top} configurações para '{model_name}':")
    
    cols = [
        "rank_test_score",
        "mean_train_score",
        "mean_test_score",
        "std_test_score"
    ]

    if has_external:
        cols += [
            "external_r2",
            "external_mae",
            "external_rmse",
            "generalization_gap_cv_external"
        ]
    
    cols += ["params"]

    print(results[cols].head(show_top).to_string(index=False))

    best_cv = results.iloc[0]

    print(f"\n[ML Exploration] Melhor por CV para '{model_name}':")
    print(f"R² médio CV: {best_cv['mean_test_score']:.4f}")
    print(f"R² médio treino: {best_cv['mean_train_score']:.4f}")
    print(f"Gap treino-validação: {(best_cv['mean_train_score'] - best_cv['mean_test_score']):.4f}")

    if has_external and not results["external_r2"].dropna().empty:
        external_sorted = results.dropna(subset=["external_r2"]).sort_values("external_r2", ascending=False)
        best_external = external_sorted.iloc[0]

        print(f"\n[ML Exploration] Melhor no DataFrame externo para '{model_name}':")
        print(f"R² externo: {best_external['external_r2']:.4f}")
        print(f"MAE externo: {best_external['external_mae']:.4f}")
        print(f"RMSE externo: {best_external['external_rmse']:.4f}")
        print(f"R² médio CV dessa config: {best_external['mean_test_score']:.4f}")
        print(f"Gap CV - externo: {best_external['generalization_gap_cv_external']:.4f}")
        print("Parâmetros sugeridos pela validação externa:")
        print(best_external["params"])
    
    print("\nParâmetros sugeridos por CV:")
    print(best_cv["params"])

    return

def print_linear_pca_summary(thresholds_df: pd.DataFrame, candidates_df: pd.DataFrame, show_top: int = 15) -> None:
    print("\n[PCA Exploration] Componentes necessários por variância:")
    print(thresholds_df.to_string(index=False))

    if candidates_df.empty:
        return

    cols = [
        "rank",
        "n_components",
        "svd_solver",
        "retained_variance",
        "reconstruction_mse",
        "params",
    ]

    available_cols = [col for col in cols if col in candidates_df.columns]

    print(f"\n[PCA Exploration] Top {show_top} candidatos PCA:")
    print(candidates_df[available_cols].head(show_top).to_string(index=False))

    best = candidates_df.iloc[0]

    print("\n[PCA Exploration] Sugestão exploratória PCA:")
    print(f"n_components: {best.get('n_components')}")
    print(f"retained_variance: {best.get('retained_variance')}")
    print(f"reconstruction_mse: {best.get('reconstruction_mse')}")
    print("params:")
    print(best.get("params"))

def plot_unsupervised_metric_curves(model_name: str, model_type: str, results: pd.DataFrame) -> None:
    if results.empty:
        return

    if model_type in {"KMeans", "MiniBatchKMeans"}:
        plot_kmeans_elbow_and_scores(model_name, results)
        return

    plot_metric_by_rank(model_name=model_name, results=results, metric="silhouette", title_metric="Silhouette Score")
    plot_metric_by_rank(model_name=model_name, results=results, metric="davies_bouldin", title_metric="Davies-Bouldin")

def print_kernel_pca_summary(results: pd.DataFrame, show_top: int = 15) -> None:
    if results.empty:
        print("[KernelPCA Exploration] Nenhum resultado.")
        return

    cols = [
        "rank",
        "n_components",
        "kernel",
        "gamma",
        "degree",
        "kernel_energy_ratio",
        "kernel_energy_percent",
        "total_kernel_energy",
        "transformed_variance",
        "params",
    ]

    available_cols = [col for col in cols if col in results.columns]

    print(f"\n[KernelPCA Exploration] Top {show_top} candidatos:")
    print(results[available_cols].head(show_top).to_string(index=False))

    best = results.iloc[0]

    print("\n[KernelPCA Exploration] Sugestão exploratória KernelPCA:")
    print(f"n_components: {best.get('n_components')}")
    print(f"kernel: {best.get('kernel')}")
    print(f"gamma: {best.get('gamma')}")
    print(f"degree: {best.get('degree')}")
    print(f"kernel_energy_ratio: {best.get('kernel_energy_ration')}")
    print(f"kernel_energy_percent: {best.get('kernel_energy_percent')}")
    print(f"total_kernel_energy: {best.get('total_kernel_energy')}")
    print(f"transformed_variance: {best.get('transformed_variance')}")
    print("params:")
    print(best.get("params"))

def plot_kmeans_elbow_and_scores(model_name: str, results: pd.DataFrame) -> None:
    if "params" not in results.columns:
        return

    df = results.copy()

    df["n_clusters_param"] = df["params"].apply(lambda p: p.get("n_clusters") if isinstance(p, dict) else None)
    df = df.dropna(subset=["n_clusters_param"])

    if df.empty:
        return

    elbow_df = (df.dropna(subset=["inertia"]).sort_values("n_clusters_param"))

    if not elbow_df.empty:
        plt.figure(figsize=(9, 5))
        plt.plot(elbow_df["n_clusters_param"], elbow_df["inertia"],marker="o")
        plt.xlabel("n_clusters")
        plt.ylabel("Inertia")
        plt.title(f"Elbow Method - {model_name}")
        plt.tight_layout()
        plt.show()

    score_df = (df.dropna(subset=["silhouette"]).sort_values("n_clusters_param"))

    if not score_df.empty:
        plt.figure(figsize=(9, 5))
        plt.plot(score_df["n_clusters_param"], score_df["silhouette"], marker="o")
        plt.xlabel("n_clusters")
        plt.ylabel("Silhouette Score")
        plt.title(f"Silhouette por n_clusters - {model_name}")
        plt.tight_layout()
        plt.show()

def plot_metric_by_rank(model_name: str, results: pd.DataFrame, metric: str, title_metric: str, show_top: int = 20) -> None:
    if metric not in results.columns:
        return

    df = results.head(show_top).copy()
    df = df.dropna(subset=[metric])

    if df.empty:
        return

    plt.figure(figsize=(10, 5))
    plt.plot(df["rank"], df[metric], marker="o")
    plt.xlabel("Rank exploratório")
    plt.ylabel(title_metric)
    plt.title(f"{title_metric} por rank - {model_name}")
    plt.tight_layout()
    plt.show()

def plot_tuning_top_results(model_name: str, results: pd.DataFrame, show_top: int = 10) -> None:
    if results.empty:
        return

    top = results.head(show_top).copy()
    top = top.sort_values("mean_test_score", ascending=True)

    labels = [f"rank {int(rank)}" for rank in top["rank_test_score"]]

    plt.figure(figsize=(10, 5))
    plt.barh(labels, top["mean_test_score"])
    plt.xlabel("R² médio em validação cruzada")
    plt.ylabel("Configuração")
    plt.title(f"Top {show_top} configurações - {model_name}")
    plt.tight_layout()
    plt.show()

    return

def plot_tuning_train_vs_validation(model_name: str, results: pd.DataFrame, show_top: int = 10) -> None:
    if results.empty:
        return

    top = results.head(show_top).copy()

    labels = [f"rank {int(rank)}" for rank in top["rank_test_score"]]
    x = range(len(top))

    plt.figure(figsize=(10, 5))
    plt.plot(x, top["mean_train_score"], marker="o", label="Treino")
    plt.plot(x, top["mean_test_score"], marker="o", label="Validação CV")
    plt.xticks(x, labels, rotation=45)
    plt.ylabel("R² médio")
    plt.title(f"Treino vs Validação - {model_name}")
    plt.legend()
    plt.tight_layout()
    plt.show()

    return

def plot_cv_vs_external(model_name: str, results: pd.DataFrame, show_top: int = 10) -> None:
    if results.empty or "external_r2" not in results.columns:
        return
    
    top = results.head(show_top).copy()
    top = top.dropna(subset=["external_r2"])

    if top.empty:
        return
    
    labels = [f"rank {int(rank)}" for rank in top["rank_test_score"]]
    x = range(len(top))

    plt.figure(figsize=(10, 5))
    plt.plot(x, top["mean_test_score"], marker="o", label="CV")
    plt.plot(x, top["external_r2"], marker="o", label="R² Externo")
    plt.xticks(x, labels, rotation=45)
    plt.ylabel("R²")
    plt.title(f"CV vs DataFrame externo - {model_name}")
    plt.legend()
    plt.tight_layout()
    plt.show()

    return

def plot_pca_cumulative_variance(df_name: str, variance_df: pd.DataFrame, thresholds: list[float]) -> None:
    plt.figure(figsize=(9, 5))
    plt.plot(variance_df["component"], variance_df["cumulative_variance"], marker="o")

    for threshold in thresholds:
        plt.axhline(y=threshold, linestyle="--", label=f"{int(threshold * 100)}%")

    plt.xlabel("Número de componentes")
    plt.ylabel("Variância acumulada")
    plt.title(f"PCA - Variância acumulada - {df_name}")
    plt.legend()
    plt.tight_layout()
    plt.show()

def plot_pca_reconstruction_error(df_name: str, candidates_df: pd.DataFrame) -> None:
    if candidates_df.empty or "reconstruction_mse" not in candidates_df.columns:
        return

    df = candidates_df.dropna(subset=["reconstruction_mse"])
    df = df.sort_values("n_components")

    if df.empty:
        return

    plt.figure(figsize=(9, 5))
    plt.plot(df["n_components"], df["reconstruction_mse"], marker="o")
    plt.xlabel("n_components")
    plt.ylabel("Reconstruction MSE")
    plt.title(f"PCA - Erro de reconstrução - {df_name}")
    plt.tight_layout()
    plt.show()

def plot_kernel_pca_results(df_name: str, results: pd.DataFrame, show_top: int = 15) -> None:
    if results.empty:
        return

    df = results.head(show_top).copy()

    if "reconstruction_mse" in df.columns:
        mse_df = df.dropna(subset=["reconstruction_mse"])

        if not mse_df.empty:
            labels = [f"{row.kernel}, n={row.n_components}" for row in mse_df.itertuples()]

            plt.figure(figsize=(11, 5))
            plt.barh(labels[::-1], mse_df["reconstruction_mse"].iloc[::-1])
            plt.xlabel("Reconstruction MSE")
            plt.ylabel("Configuração")
            plt.title(f"KernelPCA - Reconstruction MSE - {df_name}")
            plt.tight_layout()
            plt.show()

    if "transformed_variance" in df.columns:
        var_df = df.dropna(subset=["transformed_variance"])

        if not var_df.empty:
            labels = [f"{row.kernel}, n={row.n_components}" for row in var_df.itertuples()]

            plt.figure(figsize=(11, 5))
            plt.barh(labels[::-1], var_df["transformed_variance"].iloc[::-1])
            plt.xlabel("Variância no espaço transformado")
            plt.ylabel("Configuração")
            plt.title(f"KernelPCA - Variância transformada - {df_name}")
            plt.tight_layout()
            plt.show()

def save_unsupervised_tuning_results(results_list: list[pd.DataFrame], output_path, sep: str = ";") -> None:
    if not results_list:
        print("[ML Exploratório] Nenhum resultado não supervisionado exploratório para salvar.")
        return

    df = pd.concat(results_list, ignore_index=True)

    df.to_csv(output_path, sep=sep, index=False, encoding="utf-8")

    print(f"[ML Exploração] Resultados não supervisionados exploratórios salvos em {output_path}")

def save_supervised_tuning_exploration_results(results_list: list[pd.DataFrame], output_path, sep: str = ";") -> None:
    if not results_list:
        print("[ML Exploration] Nenhum resultado supervisionado exploratório para salvar.")
        return
    
    df = pd.concat(results_list, ignore_index=True)

    df.to_csv(output_path, sep=sep, index=False, encoding="utf-8")

    print(f"[ML Exploration] Resultados supervisionados exploratórios salvos em {output_path}")

def save_pca_tuning_results(results: pd.DataFrame | dict[str, pd.DataFrame] | None, output_dir, sep: str = ";") -> None:
    if results is None:
        print("[PCA Exploration] Nenhum resultado para salvar.")
        return

    output_dir.mkdir(parents=True, exist_ok=True)

    if isinstance(results, pd.DataFrame):
        output = output_dir / "ml_pca_tuning_results.csv"
        results.to_csv(output, sep=sep, index=False, encoding="utf-8")
        print(f"[PCA Exploration] Resultado salvo em {output}")
        return

    for name, df in results.items():
        if df is None or df.empty:
            continue

        output = output_dir / f"ml_pca_tuning_{name}.csv"
        df.to_csv(output, sep=sep, index=False, encoding="utf-8")
        print(f"[PCA Exploration] Resultado salvo em {output}")
