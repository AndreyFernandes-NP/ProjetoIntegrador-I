import pandas as pd
import matplotlib.pyplot as plt

from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler
from sklearn.metrics import silhouette_score
from sklearn.decomposition import PCA


# Leitura do dataset
df = pd.read_csv(
    "data/processed/main_dataframe.csv",
    sep=";"
)

FEATURES = [
    "ids",
    "receita_anual",
    "populacao"
]


def run_kmeans_analysis(
    df_input: pd.DataFrame,
    k: int = 4,
    label: str = ""
):
    print("\n" + "=" * 50)
    print(f"Analise K-MEANS {label}")
    print("=" * 50)

    df = df_input.copy()

    # Seleciona apenas as features do clustering
    X = df[FEATURES].copy()

    # Normalização
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # Treinamento
    kmeans = KMeans(
        n_clusters=k,
        random_state=42,
        n_init=10
    )

    df["cluster"] = kmeans.fit_predict(X_scaled)

    # Qualidade dos clusters
    silhouette = silhouette_score(
        X_scaled,
        df["cluster"]
    )

    print(f"\n📊 Silhouette Score: {silhouette:.4f}")

    # Perfil estatístico dos clusters
    profile = (
        df.groupby("cluster")[FEATURES]
        .agg(["mean", "median", "min", "max"])
        .round(2)
    )

    print("\n📌 Cluster profiling:")
    print(profile)

    # Tamanho dos clusters
    print("\n📦 Cluster sizes:")
    print(
        df["cluster"]
        .value_counts()
        .sort_index()
    )

    # Exemplos de municípios em cada cluster
    print("\n📍 Exemplos de municípios por cluster:")

    for cluster_id in sorted(df["cluster"].unique()):

        print("\n" + "-" * 50)
        print(f"CLUSTER {cluster_id}")
        print("-" * 50)

        dados_cluster = df[df["cluster"] == cluster_id][
            [
                "municipio",
                "ids",
                "receita_anual",
                "populacao"
            ]
        ]

        melhores = (dados_cluster.sort_values(by=["ids", "receita_anual"],ascending=False).head(10))

        piores = (dados_cluster.sort_values(by=["ids", "receita_anual"],ascending=True).head(1))

        print("\n🏆 TOP 10 IDS")
        print(melhores.to_string(index=False))

        print("\n⚠️ PIOR IDS")
        print(piores.to_string(index=False))

    return df


# =========================
# COM SÃO PAULO
# =========================
df_with_sp = run_kmeans_analysis(
    df,
    k=4,
    label="(COM SÃO PAULO)"
)


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

# PARTE GRÁFICA
# Gráfico 1 (barras)
plt.figure(figsize=(9, 7))

ax = (
    df_without_sp["cluster"]
    .value_counts()
    .sort_index()
    .plot(kind="bar")
)

plt.title("Distribuição dos Municípios por Cluster")
plt.xlabel("Cluster")
plt.ylabel("Quantidade de Municípios")
plt.xticks(rotation=0)
plt.grid(axis="y", linestyle="--", alpha=0.5)

for barra in ax.patches:
    altura = barra.get_height()

    ax.annotate(
        f"{int(altura)}",
        (
            barra.get_x() + barra.get_width() / 2,
            altura
        ),
        ha="center",
        va="bottom",
        fontsize=10
    )

# Gráfico 2 (scatterplot)
plt.tight_layout()
plt.show()

plt.figure(figsize=(16, 9))

scatter = plt.scatter(
    df_without_sp["receita_anual"],
    df_without_sp["ids"],
    c=df_without_sp["cluster"],
    alpha=0.7
)

plt.xscale("log")

# Mostrar os 10 melhores municípios de cada cluster
for cluster in sorted(df_without_sp["cluster"].unique()):

    top10 = (
        df_without_sp[df_without_sp["cluster"] == cluster]
        .nlargest(10, "ids")
    )

    for _, row in top10.iterrows():
        plt.annotate(
            row["municipio"],
            (row["receita_anual"], row["ids"]),
            fontsize=7,
            alpha=0.8
        )


    bottom = (
        df_without_sp[df_without_sp["cluster"] == cluster]
        .nsmallest(1, "ids")
    )


    for _, row in bottom.iterrows():
        plt.annotate(
            row["municipio"],
            (row["receita_anual"], row["ids"]),
            fontsize=7,
            color="red"
        )

plt.title("Clusters dos Municípios Paulistas")
plt.xlabel("Receita Anual (escala log)")
plt.ylabel("IDS")
plt.colorbar(scatter, label="Cluster")

plt.tight_layout()
plt.show()