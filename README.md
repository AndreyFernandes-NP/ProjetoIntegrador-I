# Projeto Integrador I (PUC-SP)

Este repositório contém o desenvolvimento do Projeto Integrador I da Pós-Graduação em Inteligência Artificial da **PUC-SP**. O projeto investiga a relação entre vulnerabilidade social, infraestrutura urbana e pressão sobre os serviços públicos de saúde no estado de São Paulo, com análise e abordagem preditiva.

## Objetivo

Analisar se municípios com maior vulnerabilidade social e piores condições de infraestrutura urbana tendem a apresentar menor ocorrências de serviços públicos de saúde, e como eles possivelmente subvertem essa necessidade. Além da análise correlacional, o projeto construiu um modelo preditivo que apoia a identificação de municípios com maior tendência de pressão através do indicador de IDS.

## Hipótese

Municípios com maior vulnerabilidade social e infraestrutura urbana mais precária tendem a apresentar maior pressão sobre os serviços públicos de saúde e como isso é subvertido por alguns deles.

## Mapa de documentação do repositório

- **Pastas**: [`data/`](data/README.md), [`docs/`](docs/README.md)
- **Visão geral**: [`docs/README.md`](docs/README.md)
- **Planejamento**: [`docs/project/CRONOGRAMA.md`](docs/project/CRONOGRAMA.md), [`docs/project/ESCOPO.md`](docs/project/ESCOPO.md), [`docs/project/OBJETIVOS.md`](docs/project/OBJETIVOS.md)
- **Dados**: [`docs/data/DICIONARIO_DE_DADOS.md`](docs/data/DICIONARIO_DE_DADOS.md), [`docs/data/FONTES_DE_DADOS.md`](docs/data/FONTES_DE_DADOS.md), [`docs/data/TRATAMENTO_DE_DADOS.md`](docs/data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura & Pipeline**: [`docs/architecture/ARQUITETURA.md`](docs/architecture/ARQUITETURA.md), [`docs/architecture/PIPELINE.md`](docs/architecture/PIPELINE.md)
- **Análise**: [`docs/analysis/ABORDAGEM_ANALITICA.md`](docs/analysis/ABORDAGEM_ANALITICA.md), [`docs/analysis/HIPOTESES.md`](docs/analysis/HIPOTESES.md), [`docs/analysis/METODOLOGIA.md`](docs/analysis/METODOLOGIA.md)

## Escopo atual

O trabalho atual está concentrado em:

- coleta e integração de bases públicas do estado de São Paulo
- limpeza, padronização e enriquecimento dos dados
- construção de uma base processada para análise e modelagem
- análise exploratória de indicadores sociais, demográficos e de saúde
- desenvolvimento e validação de modelos de machine learning
- geração de relatórios e métricas de desempenho de modelos

## Requisitos

- Python 3.x
- `requirements.txt`
- Ambiente Virtual [Recomendado]

## Estrutura do repositório

```text
ProjetoIntegrador-I/
├── data/
│   ├── clean/
│   │   ├── estabelecimentos_saude-clean.csv
│   │   ├── finbra_2022SP-clean.csv
│   │   ├── healthcare_final_latlon-clean.csv
│   │   ├── inst_hospitalares_sp-clean.csv
│   │   ├── ipvs_esp-clean.csv
│   │   ├── municipios-clean.csv
│   │   ├── sia_cnv_qgsp-clean.csv
│   │   └── sih_cnv_spgsp-clean.csv
│   ├── mapping/
│   │   └── codigos_ibge_sp.csv
│   ├── processed/
│   │   ├── main_dataframe.csv
│   │   ├── main_dataframe_clusterizado.csv
│   │   ├── validation_dataset.csv
│   │   └── validation_samples.csv
│   └── raw/
│       ├── estabelecimentos_saude.csv
│       ├── finbra_2022SP.csv
│       ├── healthcare_final_latlon.csv
│       ├── inst_hospitalares_sp.csv
│       ├── ipvs_esp.csv
│       ├── municipios.csv
│       ├── sia_cnv_qgsp.csv
│       ├── sih_cnv_spgsp.csv
│       └── tabela30_SP_internacao.csv
├── docs/
│   ├── analysis/
│   ├── architecture/
│   ├── data/
│   └── project/
├── notebooks/
├── reports/
│   └── ml/
│       ├── Extra Trees Regressor_predictions.csv
│       ├── Gradient Boosting Regressor_predictions.csv
│       ├── Hist Gradient Boosting Regressor_predictions.csv
│       ├── Random Forest Regressor_predictions.csv
│       ├── ml_supervised_metrics.csv
│       ├── ml_supervised_prediction_metrics.csv
│       ├── ml_supervised_tuning_exploration.csv
│       ├── ml_unsupervised_metrics.csv
│       └── pca_tuning/
├── src/
│   ├── config/
│   │   ├── models.yaml
│   │   ├── muni_nomes.txt
│   │   ├── muni_sobrenomes.txt
│   │   └── sources.yaml
│   ├── core/
│   │   ├── calculator.py
│   │   ├── cleaner.py
│   │   ├── merger.py
│   │   ├── pipeline.py
│   │   ├── register_source.py
│   │   ├── transformer.py
│   │   └── validator.py
│   ├── data/
│   │   └── generator.py
│   ├── mlearn/
│   │   ├── base.py
│   │   ├── fine_tuning.py
│   │   ├── pipeline.py
│   │   ├── registry.py
│   │   ├── supervised.py
│   │   └── unsupervised.py
│   ├── ui/
│   └── __main__.py
├── grouping_notebook.ipynb
├── grouping_visualization.py
├── requirements.txt
├── README.md
└── LICENSE
```

## Setup local

1. **Clone o repositório**
   ```bash
   git clone https://github.com/AndreyFernandes-NP/ProjetoIntegrador-I.git
   cd ProjetoIntegrador-I
   ```
2. **Crie um virtual environment**
   ```bash
   python -m venv env
   ```
3. **Ative o ambiente virtual**
   ```bash
   env/Scripts/activate.bat
   ```
4. **Instale as dependências**
   ```bash
   pip install -r requirements.txt
   ```
5. **Execute nosso programa**
   ```bash
   python -m src
   ```

## Organização do projeto

A documentação e o desenvolvimento são organizados em frentes principais:

- `docs/`: documentação do projeto, dados, arquitetura, pipeline e análise
- `data/`: dados brutos, limpos, mapeamentos e bases processadas
- `src/`: código de pipeline, transformação, validação e modelos de ML
- `reports/`: resultados e métricas de experimentos
- `notebooks/`: análises exploratórias e visualizações
