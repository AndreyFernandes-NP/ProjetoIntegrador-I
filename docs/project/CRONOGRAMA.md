# Cronograma do Projeto

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](../../data/README.md), [`docs/`](../README.md)
- **Planejamento**: [`CRONOGRAMA.md`](CRONOGRAMA.md), [`ESCOPO.md`](ESCOPO.md), [`OBJETIVOS.md`](OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](../data/DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](../data/FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](../data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura & Pipeline**: [`ARQUITETURA.md`](../architecture/ARQUITETURA.md), [`PIPELINE.md`](../architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](../analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](../analysis/HIPOTESES.md), [`METODOLOGIA.md`](../analysis/METODOLOGIA.md)

## Visão geral

O cronograma do projeto está organizado de forma gradual, acompanhando as etapas de definição, coleta, tratamento, análise e documentação.

## Etapas principais

### 1. Planejamento inicial
- definição do problema
- definição da hipótese
- definição dos objetivos
- organização do repositório e da documentação inicial

### 2. Levantamento de dados
- busca por bases públicas relevantes
- avaliação de compatibilidade entre fontes
- definição das chaves de integração
- organização dos dados brutos

### 3. Preparação dos dados
- limpeza e padronização
- tratamento de inconsistências
- integração entre datasets
- criação da base analítica inicial

### 4. Análise dos dados
- análise exploratória
- geração de visualizações
- investigação de correlações
- identificação de padrões e limitações

### 5. Modelagem
- definição da variável-alvo
- preparação para modelo supervisionado
- testes iniciais de abordagem preditiva
- avaliação preliminar dos resultados

### 6. Entrega final
- consolidação da documentação
- revisão dos resultados
- github com código revisionado
- finalização da documentação
- preparação da apresentação
- organização da entrega final

## Cronograma detalhado (status atual)

Este cronograma resume marcos, responsáveis e entregáveis com base no estado atual do repositório.

| Marco | Descrição | Responsável | Prazo estimado | Status | Entregáveis |
|---|---|---:|---:|---|---|
| Planejamento inicial | Definição de problema, hipóteses e objetivos | Equipe | concluído | Concluído | `docs/analysis/*`, `docs/project/*` |
| Levantamento de dados | Coleta de bases públicas (DATASUS, IBGE, Seade, Finbra) | Equipe | concluído | Concluído | `data/raw/*`, `docs/data/FONTES_DE_DADOS.md` |
| Preparação dos dados | Limpeza, transformações e merge configuráveis via YAML | Equipe | concluído | Concluído | `data/clean/*`, `data/processed/main_dataframe.csv` |
| Cálculo do IDS | Implementação das 4 dimensões e agregação em `ids` | Andrey/Beatriz | concluído | Concluído | `src/core/calculator.py`, `data/processed/main_dataframe.csv` |
| Documentação da pipeline | Documentar fluxo real do código e execução | Hiago/Gabriel | concluído | Concluído | `docs/architecture/PIPELINE.md` |
| Dicionário e fontes | Agrupar variáveis por dimensão e detalhar fontes | Equipe | concluído | Concluído | `docs/data/DICIONARIO_DE_DADOS.md`, `docs/data/FONTES_DE_DADOS.md` |
| Tratamento detalhado | Descrever transformações aplicadas e regras YAML | Andrey | concluído | Concluído | `docs/data/TRATAMENTO_DE_DADOS.md` |
| ML: experimentos e relatórios | Treino, tuning, exploração e geração de relatórios | Equipe | concluído | Concluído | `reports/ml/*.csv`, `src/mlearn/pipeline.py` |
| Validação externa | Geração de dataset sintético e validação cruzada | Andrey/Pedro | concluído | Concluído | `data/processed/validation_dataset.csv`, `reports/ml/ml_supervised_prediction_metrics.csv` |
| Entrega final e apresentação | Consolidação final dos ativos para entrega | Equipe | concluído | Concluído | Apresentação, README final, código organizado |
