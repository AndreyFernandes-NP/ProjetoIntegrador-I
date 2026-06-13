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

def as_float(value: Any) -> float:
    return float(cast(Any, value))

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

def plot_unsupervised_metric_curves(model_name: str, model_type: str, results: pd.DataFrame) -> None:
    if results.empty:
        return

    if model_type in {"KMeans", "MiniBatchKMeans"}:
        plot_kmeans_elbow_and_scores(model_name, results)
        return

    plot_metric_by_rank(model_name=model_name, results=results, metric="silhouette", title_metric="Silhouette Score")
    plot_metric_by_rank(model_name=model_name, results=results, metric="davies_bouldin", title_metric="Davies-Bouldin")

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