import pandas as pd
import numpy as np

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score


# =========================
# LOAD DATA
# =========================
df = pd.read_csv("data/processed/main_dataframe.csv", sep=";")


FEATURES = ["ids", "receita_anual", "populacao"]


def run_kmeans_analysis(df_input: pd.DataFrame, k: int = 4, label: str = ""):
    print("\n" + "=" * 60)
    print(f"K-MEANS ANALYSIS {label}")
    print("=" * 60)

    df = df_input.copy()

    # =========================
    # PREPROCESSING
    # =========================
    X = df[FEATURES].copy()

    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    kmeans = KMeans(n_clusters=k, random_state=42, n_init=10)

    df["cluster"] = kmeans.fit_predict(X_scaled)

    # =========================
    # QUALITY METRIC
    # =========================
    silhouette = silhouette_score(X_scaled, df["cluster"])
    print(f"\n📊 Silhouette Score: {silhouette:.4f}")

    # =========================
    # CLUSTER PROFILING
    # =========================
    profile = (
        df.groupby("cluster")[FEATURES]
        .agg(["mean", "median", "min", "max"])
        .round(2)
    )

    print("\n📌 Cluster profiling:")
    print(profile)

    # =========================
    # CLUSTER SIZES
    # =========================
    print("\n📦 Cluster sizes:")
    print(df["cluster"].value_counts().sort_index())

    # =========================
    # 🔥 NEW: IMPROVED CLUSTER SCORING
    # =========================
    cluster_profile = df.groupby("cluster")[FEATURES].mean().copy()

    # log para reduzir impacto de escala absurda
    cluster_profile["receita_anual"] = np.log1p(cluster_profile["receita_anual"])
    cluster_profile["populacao"] = np.log1p(cluster_profile["populacao"])

    # z-score (normalização comparável entre variáveis)
    cluster_norm = (cluster_profile - cluster_profile.mean()) / cluster_profile.std()

    # score composto (interpretação de desenvolvimento)
    cluster_profile["score"] = (
        cluster_norm["ids"] * 0.5 +
        cluster_norm["receita_anual"] * 0.3 +
        cluster_norm["populacao"] * 0.2
    )

    ranking = cluster_profile.sort_values("score", ascending=False).reset_index()

    ranking["rank"] = range(1, len(ranking) + 1)

    print("\n🏆 Cluster ranking (score composto):")
    print(ranking[["cluster", "score", "rank"]])

    # =========================
    # MERGE RANK BACK
    # =========================
    df = df.merge(ranking[["cluster", "rank"]], on="cluster", how="left")

    # =========================
    # LABELING (INTERPRETAÇÃO FINAL)
    # =========================
    cluster_labels = {}

    for _, row in ranking.iterrows():
        cluster_id = row["cluster"]
        rank = row["rank"]

        if rank == 1:
            cluster_labels[cluster_id] = "Estruturado"
        elif rank == 2:
            cluster_labels[cluster_id] = "Moderado"
        elif rank == 3:
            cluster_labels[cluster_id] = "Em risco"
        else:
            cluster_labels[cluster_id] = "Crítico"

    df["cluster_label"] = df["cluster"].map(cluster_labels)

    print("\n🏷️ Cluster labels:")
    print(cluster_labels)

    return df


# =========================
# COM SÃO PAULO
# =========================
df_with_sp = run_kmeans_analysis(df, k=4, label="(COM SÃO PAULO)")


# =========================
# SEM SÃO PAULO
# =========================
df_without_sp = run_kmeans_analysis(
    df[df["municipio"] != "SAO PAULO"],
    k=4,
    label="(SEM SÃO PAULO)"
)


# =========================
# SAVE RESULT
# =========================
df_without_sp.to_csv(
    "data/processed/main_dataframe_clusterizado.csv",
    sep=";",
    index=False
)