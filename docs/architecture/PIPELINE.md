# Pipeline do Projeto

## Mapa de Documentação do Repositório

- **Pastas**: [`..data/`](../../data/README.md), [`docs/`](../README.md)
- **Visão geral**: [`../README.md`](../README.md)
- **Planejamento**: [`../project/CRONOGRAMA.md`](../project/CRONOGRAMA.md), [`../project/ESCOPO.md`](../project/ESCOPO.md), [`../project/OBJETIVOS.md`](../project/OBJETIVOS.md)
- **Dados**: [`../data/DICIONARIO_DE_DADOS.md`](../data/DICIONARIO_DE_DADOS.md), [`../data/FONTES_DE_DADOS.md`](../data/FONTES_DE_DADOS.md), [`../data/TRATAMENTO_DE_DADOS.md`](../data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura & Pipeline**: [`ARQUITETURA.md`](ARQUITETURA.md), [`PIPELINE.md`](PIPELINE.md)
- **Análise**: [`../analysis/ABORDAGEM_ANALITICA.md`](../analysis/ABORDAGEM_ANALITICA.md), [`../analysis/HIPOTESES.md`](../analysis/HIPOTESES.md), [`../analysis/METODOLOGIA.md`](../analysis/METODOLOGIA.md)

## Visão geral

Este documento descreve a pipeline implementada no código do projeto. A jornada cobre desde os dados brutos (`data/raw/`) até a criação da base final em `data/processed/`, geração do IDS e a execução de modelos de machine learning e validação.

A pipeline atual foi desenhada para ser reproduzível, transparente e compatível com o volume e o escopo de um projeto acadêmico. O pipeline funciona de forma integrada com as configurações declaradas em `src/config/sources.yaml` e `src/config/models.yaml`.

## Visão da jornada de dados

1. ingestão de dados brutos nas fontes em `data/raw/`
2. leitura e limpeza genérica de cada arquivo
3. transformações específicas definidas em `src/config/sources.yaml`
4. validação de qualidade por fonte
5. escrita de arquivos limpos em `data/clean/`
6. merge sequencial e criação de base analítica em `data/processed/main_dataframe.csv`
7. cálculo do IDS e inclusão da métrica no dataset final
8. geração de dataset de validação sintético
9. execução de modelos de ML supervisonados e não supervisionados
10. geração de métricas, previsões e relatórios em `reports/`

## Principais scripts e pontos de entrada

- `src/core/pipeline.py`: pipeline principal de ingestão, limpeza, transformação, validação, merge e cálculo de IDS.
- `src/core/cleaner.py`: funções de limpeza genérica aplicadas a todos os datasets.
- `src/core/transformer.py`: transformações específicas por fonte com base em `sources.yaml`.
- `src/core/merger.py`: merge sequencial dos arquivos limpos em um único dataset.
- `src/core/calculator.py`: cálculo do Índice de Desenvolvimento de Saúde (IDS).
- `src/data/generator.py`: geração de dataset sintético de validação.
- `src/mlearn/pipeline.py`: execução dos pipelines de ML supervisionado e não supervisionado.
- `src/config/sources.yaml`: configuração de fontes, transformações, qualidade, merge e IDS.
- `src/config/models.yaml`: configuração de dataset, pré-processamento e modelos de ML.
- `src/__main__.py`: menu interativo para executar pipeline e modelos.

## Pipeline de dados detalhada

### 1. Coleta e armazenamento

Os arquivos originais são mantidos em `data/raw/` e não são modificados. Cada CSV é lido com `transformer.careful_load_csv`, que testa diferentes encodings e separadores para evitar erros de leitura.

### 2. Limpeza genérica

A função `clean()` em `src/core/cleaner.py` executa a limpeza básica de cada fonte:

- normaliza nomes de colunas (lowercase, remoção de acentos, remoção de espaços extras)
- limpa strings, retirando espaços e convertendo células vazias para nulo
- remove duplicatas
- detecta colunas com possíveis erros de encoding
- imprime relatório de valores nulos para cada coluna

### 3. Transformação por fonte

A função `transform()` em `src/core/transformer.py` aplica transformações específicas definidas em `src/config/sources.yaml`.

Suporta:

- `tipo: mapa_ibge`: mapeia códigos IBGE para nome de município usando `codigos_ibge_sp.csv`
- `tipo: purge`: remove dígitos e normaliza textos (uppercase)
- `rename`: renomeia colunas
- `cast`: converte colunas para `Int64`, `Float64`, `str` ou `datetime`
- `convert_to_column`: transforma coluna categórica em várias colunas via pivot
- inferência automática de colunas numéricas

Essas transformações permitem harmonizar diferentes fontes para que possam ser integradas posteriormente.

### 4. Validação de qualidade

Após transformação, `src/core/validator.py` valida cada DataFrame com base nas regras definidas em `sources.yaml`:

- `cols_obrigatorias`
- `cols_nao_nulas`
- `cols_unicas`
- `cols_numericas`

Também aplica validações genéricas:

- verifica DataFrames vazios
- identifica linhas duplicadas
- detecta colunas `Unnamed`

A pipeline pode falhar quando há erros de validação (exceto em `--dry-run`).

### 5. Produção de dados limpos

Os DataFrames validados são salvos em `data/clean/` no formato `nome-da-fonte-clean.csv`. Essa camada representa a etapa de preparação de dados, preservando a separação entre bruto e tratado.

### 6. Merge e base processada

Depois de processar as fontes, `src/core/pipeline.py` chama `run_merge()` em `src/core/merger.py`.

O merge usa:

- fonte base `codigos_ibge_sp` para garantir consistência geográfica
- chave de merge definida em `sources.yaml` (ex: `municipio`)
- join do tipo `left` por padrão
- whitelist `colunas_uteis` para limitar colunas por fonte

A junção é feita sequencialmente, evitando duplicação de colunas já presentes, e mantendo a chave de merge como referência principal.

O resultado final do merge é salvo em `data/processed/main_dataframe.csv`.

### 7. Cálculo do IDS

Após o merge, `src/core/pipeline.py` invoca `calculate_ids()` em `src/core/calculator.py`.

O IDS é calculado a partir de quatro dimensões:

- `infraestrutura`
- `serviços`
- `vulnerabilidade`
- `renda`

Cada dimensão é configurada em `sources.yaml` com colunas e pesos específicos.

O cálculo do IDS passa por:

- normalização robusta (`robust_minmax`) de infraestrutura e renda
- média ponderada populacional para vulnerabilidade
- cobertura adaptativa de serviços considerando necessidade média e taxa base
- soma ponderada final com pesos definidos em `IDS_CONFIG`

O valor final é normalizado para [0, 1] e salvo na coluna `ids`.

## Pipeline de modelos e validação

### 8. Configuração de ML

A configuração de machine learning está em `src/config/models.yaml`.

Ela define:

- `dataset.arquivo`: dataset processado usado para ML
- `dataset.features`: lista de colunas a serem usadas como features
- `dataset.target_col`: coluna alvo (`ids`)
- `preprocessing.scale`: se o scaler deve ser aplicado
- `preprocessing.scaler`: tipo de scaler
- `ml_supervised.enabled`: habilita modelos supervisionados
- `ml_supervised.pca`: controla uso de PCA em supervisado
- `ml_supervised.models`: lista de modelos e hiperparâmetros
- `ml_unsupervised.enabled`: habilita modelos de clusterização
- `ml_unsupervised.pca`: controla uso de PCA em não supervisionado
- `ml_unsupervised.models`: lista de algoritmos de agrupamento

### 9. Pipeline de ML

O pipeline de ML em `src/mlearn/pipeline.py` realiza:

- carregamento do dataset processado de `data/processed/`
- seleção de features globais e específicas por modelo
- preenchimento de valores faltantes com zero
- divisão de treino/teste para modelos supervisionados
- escalonamento opcional com `StandardScaler` ou outros scalers
- redução opcional de dimensionalidade via PCA/KernelPCA
- treinamento e avaliação de modelos

Para modelos supervisionados, o fluxo é:

1. `train_test_split`
2. `fit()` no modelo
3. `predict()` em `X_test`
4. avaliação com `MAE`, `RMSE` e `R²`
5. salvamento de predições e métricas

Para modelos não supervisionados, o fluxo é:

1. treinamento em `X_train`
2. obtenção de rótulos ou clusters
3. avaliação com `silhouette`, `calinski_harabasz` e `davies_bouldin`
4. salvamento de métricas

### 10. Registro de modelos

Os modelos são instanciados a partir de registries em `src/mlearn/registry.py`.

Modelos suportados atualmente:

- Supervisionados: `LinearRegression`, `Lasso`, `Ridge`, `KNNRegressor`, `SVR`, `DecisionTreeRegressor`, `RandomForestRegressor`, `GradientBoostingRegressor`, `ExtraTreesRegressor`, `HistGradientBoostingRegressor`
- Não supervisionados: `KMeans`, `DBSCAN`, `MeanShift`, `AgglomerativeClustering`, `GaussianMixture`

Cada modelo herda comportamentos comuns para treino, predição e avaliação.

### 11. Geração de dataset de validação sintético

Ao final da execução de ML, o projeto gera um dataset sintético com `src/data/generator.py`.

O `DatasetGenerator`:

- classifica linhas reais em `low`, `medium` e `high` a partir do IDS
- amostra linhas reais aleatoriamente ou de forma balanceada
- aplica ruído percentual aos valores numéricos
- preserva zeros com probabilidade configurável
- recria nomes de municípios sintéticos usando listas de nomes e sobrenomes
- salva o resultado em `data/processed/`

Essa base sintética é usada para validação externa dos modelos e para comparar previsões em um cenário de dados gerados.

### 12. Validação cruzada e exploração

O pipeline de ML também executa explorações de hiperparâmetros quando habilitado.

- `run_unsupervised_tuning_exploration()` testa parâmetros de modelos não supervisionados
- `run_supervised_tuning_exploration()` testa parâmetros de modelos supervisionados
- `run_pca_tuning_exploration()` testa configurações de redução de dimensionalidade

Os resultados dessas explorações são salvos em `reports/ml/` e subpastas de `pca_tuning/`.

### 13. Resultados e relatórios

O pipeline salva:

- `reports/ml/ml_supervised_metrics.csv`
- `reports/ml/ml_supervised_prediction_metrics.csv`
- `reports/ml/ml_unsupervised_metrics.csv`
- predições individuais por modelo em `reports/ml/{model_name}_predictions.csv`
- resultados de exploração de hiperparâmetros em `reports/ml/ml_supervised_tuning_exploration.csv` e `reports/ml/ml_unsupervised_tuning_exploration.csv`

## Observações sobre a pipeline

- a pipeline assume que a configuração de fontes em `src/config/sources.yaml` está atualizada e completa
- a base de merge parte de `codigos_ibge_sp` como referência geográfica
- o cálculo do IDS depende da coluna `populacao` e dos pesos definidos em `calculator.py`
- o pré-processamento de ML atualmente é simples (`fillna(0)`) e pode ser refinado em fases futuras
- o menu em `src/__main__.py` permite executar pipeline de dados e de modelos de forma interativa

## Como executar

- `python -m src.core.pipeline` → executa a pipeline completa de dados, incluindo merge e cálculo de IDS
- `python -m src.mlearn.pipeline` → executa todos os modelos e validações configurados em `src/config/models.yaml`
- `python -m src.__main__` → abre o menu interativo do sistema IDS
