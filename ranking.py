import pandas as pd
import matplotlib.pyplot as plt
from sklearn.cluster import KMeans
from sklearn.preprocessing import StandardScaler


# Leitura do CSV
df = pd.read_csv("data/processed/main_dataframe.csv", sep=";" )

# TESTES DO RANKING
# TOP 10 melhores ids
# print(df.sort_values("ids").head(10))

#TOP 10 piores ids
# print(df.sort_values("ids", ascending=False).head(10))


# =========================
# Quartis // Divisão dos municípios em 4 grupos iguais baseando-se no IDS
# =========================

df["categoria"] = pd.qcut(
    df["ids"],
    q=4,
    labels=[
        "Crítico",
        "Em risco",
        "Moderado",
        "Estruturado"
    ]
)

# Municipios por categoria
print("\nQuantidade por categoria:\n")
print(df["categoria"].value_counts())



### K-MEANS

print("\n=========================")
print("K-MEANS COM SÃO PAULO")
print("=========================\n")

# Variáveis utilizadas
X = df[[
    "ids",
    "receita_anual",
    "populacao"
]]

# Normalização
scaler = StandardScaler()
X_scaled = scaler.fit_transform(X)

# Modelo K-Means
kmeans = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

# Criar clusters
df["cluster"] = kmeans.fit_predict(X_scaled)

print(df["cluster"].value_counts())

print("\nMédia das variáveis por cluster:\n")
print(
    df.groupby("cluster")[[
        "ids",
        "receita_anual",
        "populacao"
    ]].mean()
)


print("\n=========================")
print("K-MEANS SEM SÃO PAULO")
print("=========================\n")

df_sem_sp = df[df["municipio"] != "SAO PAULO"].copy()

X_sem_sp = df_sem_sp[[
    "ids",
    "receita_anual",
    "populacao"
]]

scaler_sem_sp = StandardScaler()
X_scaled_sem_sp = scaler_sem_sp.fit_transform(X_sem_sp)

kmeans_sem_sp = KMeans(
    n_clusters=4,
    random_state=42,
    n_init=10
)

df_sem_sp["cluster"] = kmeans_sem_sp.fit_predict(X_scaled_sem_sp)

print(df_sem_sp["cluster"].value_counts())

print("\nMédia das variáveis por cluster:\n")
print(
    df_sem_sp.groupby("cluster")[[
        "ids",
        "receita_anual",
        "populacao"
    ]].mean()
)



# Municipios por Cluster
print("\nMunicípios por cluster:\n")

for i in range(4):
    print(f"\nCLUSTER {i}\n")
    print(
        df_sem_sp[df_sem_sp["cluster"] == i][
            ["municipio", "ids"]
        ].head(10)
    )


# Salvar CSV

df_sem_sp.to_csv(
    "data/processed/main_dataframe_classificacao_com_cluster.csv",
    sep=";",
    index=False
)


# Visualização gráfica (COM SÃO PAULO)

# Cria o gráfico
plt.figure(figsize=(8, 5))

df["cluster"].value_counts().sort_index().plot(kind="bar")

# Títulos do gráfico
plt.title("Distribuição dos Clusters (Com São Paulo)")
plt.xlabel("Cluster")
plt.ylabel("Quantidade de Municípios")

# Melhorar layout
plt.xticks(rotation=0)

# Mostra o gráfico em si
plt.show()


# Visualização gráfica (SEM SÃO PAULO)

plt.figure(figsize=(8, 5))

df_sem_sp["cluster"].value_counts().sort_index().plot(kind="bar")

plt.title("Distribuição dos Clusters (Sem São Paulo)")
plt.xlabel("Cluster")
plt.ylabel("Quantidade de Municípios")

plt.xticks(rotation=0)

plt.show()


# =========================
# SCATTER PLOT (COM SÃO PAULO)
# =========================

plt.figure(figsize=(18, 12))

# Cria o Scatter Plot
plt.scatter(
    df["receita_anual"],
    df["ids"],
    c=df["cluster"]
)

# Escala logarítmica
plt.xscale("log")

# Adicionar nome dos municípios
for _, row in df.iterrows():
    plt.text(
        row["receita_anual"],
        row["ids"],
        row["municipio"],
        fontsize=7
    )

# Títulos
plt.title("Clusters dos Municípios (Com São Paulo)")
plt.xlabel("Receita Anual (escala log)")
plt.ylabel("IDS")

# Mostra o gráfico
plt.show()

# =========================
# SCATTER PLOT (SEM SÃO PAULO)
# =========================

plt.figure(figsize=(18, 12))

plt.scatter(
    df_sem_sp["receita_anual"],
    df_sem_sp["ids"],
    c=df_sem_sp["cluster"]
)

plt.xscale("log")

for _, row in df_sem_sp.iterrows():
    plt.text(
        row["receita_anual"],
        row["ids"],
        row["municipio"],
        fontsize=7
    )

plt.title("Clusters dos Municípios (Sem São Paulo)")
plt.xlabel("Receita Anual (escala log)")
plt.ylabel("IDS")

plt.show()