# Projeto Integrador I (PUC-SP)

Este repositório contém o desenvolvimento do Projeto Integrador I da Pós-Graduação em Inteligência Artificial da **PUC-SP**. O projeto tem como foco a análise de dados públicos do estado de São Paulo para investigar a relação entre vulnerabilidade social, infraestrutura urbana e pressão sobre os serviços públicos de saúde.

## Objetivo

Analisar se municípios com maior vulnerabilidade social e piores condições de infraestrutura urbana tendem a apresentar maior pressão sobre os serviços públicos de saúde no estado de São Paulo. Além da análise correlacional, o projeto também busca construir uma abordagem preditiva supervisionada capaz de apoiar a identificação de municípios com maior tendência de pressão sobre a rede hospitalar, contribuindo para a tomada de decisão e o planejamento de estratégias de atendimento.

## Hipótese

A hipótese central do projeto é que municípios com maior vulnerabilidade social e estrutura urbana mais precária tendem a apresentar maior pressão sobre os serviços públicos de saúde.

## Mapa de Documentação do Repositório

- **Projeto**: [`CRONOGRAMA.md`](docs/project/CRONOGRAMA.md), [`ESCOPO.md`](docs/project/ESCOPO.md), [`OBJETIVOS.md`](docs/project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](docs/data/DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](docs/data/FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](docs/data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura**: [`ARQUITETURA.md`](docs/architecture/ARQUITETURA.md), [`PIPELINE.md`](docs/architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](docs/analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](docs/analysis/HIPOTESES.md), [`METODOLOGIA.md`](docs/analysis/METODOLOGIA.md)

## Escopo atual

Nesta etapa, o projeto está concentrado em:

- levantamento e integração de bases públicas do estado de São Paulo
- padronização e tratamento dos dados
- análise exploratória dos indicadores selecionados
- identificação de correlações entre vulnerabilidade, infraestrutura e saúde
- preparação da base para análises estatísticas e modelos preditivos
- desenvolvimento inicial de modelos supervisionados para apoio à análise preditiva

## Requisitos

- Python 3.x
- Bibliotecas listadas em `requirements.txt`
- Ambiente Virtual [Recomendado]

## Estrutura do repositório

```text
ProjetoIntegrador-I/
├── data/
|   ├── clean/
|   |   ├── inst_hospitalares_sp-clean.csv
|   |   └── ipvs_esp-merge.csv
|   ├── processed/
|   ├── raw/
|   |   ├── codigos_ibge_sp.csv
|   |   ├── inst_hospitalares_sp-raw.csv
|   |   └── ipvs_esp-raw.csv
|   └── data_cleaner+merger.py
├── docs/
|   ├── analysis/
|   |   ├── ABORDAGEM_ANALITICA.md
|   |   ├── HIPOTESES.md
|   |   └── METODOLOGIA.md
|   ├── architecture/
|   |   ├── ARQUITETURA.md
|   |   └── PIPELINE.md
|   ├── data/
|   |   ├── DICIONARIO_DE_DADOS.md
|   |   ├── FONTES_DE_DADOS.md
|   |   └── TRATAMENTO_DE_DADOS.md
|   └── project/
|       ├── CRONOGRAMA.md
|       ├── ESCOPO.md
|       └── OBJETIVOS.md
├── notebooks/
├── src/
├── requirements.txt
└── README.md
```
> A estrutura do repositório poderá ser expandida ao longo do projeto para acomodar documentação, scripts de processamento, análises e resultados.

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
3. **Instale as dependencias**
   ```bash
   pip install -r requirements.txt
    ```
****

## Organização do projeto

A documentação complementar do projeto será mantida na pasta docs, incluindo informações sobre:

- escopo e objetivos
- fontes de dados
- arquitetura do projeto
- pipeline de dados
- dicionário de dados
- metodologia e análise

## Observações

Este projeto está em desenvolvimento e pode passar por mudanças de escopo, estrutura e documentação ao longo da evolução das análises.