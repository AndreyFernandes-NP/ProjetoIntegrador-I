# Arquitetura do Projeto

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](../../data/README.md), [`docs/`](../README.md)
- **Planejamento**: [`CRONOGRAMA.md`](../project/CRONOGRAMA.md), [`ESCOPO.md`](../project/ESCOPO.md), [`OBJETIVOS.md`](../project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](../data/DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](../data/FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](../data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura & Pipeline**: [`ARQUITETURA.md`](ARQUITETURA.md), [`PIPELINE.md`](PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](../analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](../analysis/HIPOTESES.md), [`METODOLOGIA.md`](../analysis/METODOLOGIA.md)

## Visão geral

A arquitetura do projeto define como os dados, o código e os resultados são organizados para dar suporte à análise de indicadores sociais, infraestrutura urbana e pressão sobre a saúde pública em municípios de São Paulo.

O foco está em uma estrutura leve e modular, que permita:

- ingestão e tratamento de dados variados
- composição de uma base analítica integrada
- experimentação com modelos de machine learning
- geração de relatórios e visualizações reproduzíveis

A arquitetura atual é centrada em um repositório local com código Python em `src/`, dados em `data/`, notebooks em `notebooks/` e resultados em `reports/`.

## Componentes principais

### 1. Dados (`data/`)

A camada de dados é organizada em três subdiretórios:

- `raw/`: dados brutos importados das fontes originais
- `clean/`: bases tratadas e normalizadas
- `processed/`: bases finais prontas para análise e modelagem
- `mapping/`: arquivos de apoio para integração, como códigos do IBGE

Essa separação garante que os dados originais permaneçam preservados e que as etapas de tratamento sejam rastreáveis.

### 2. Código fonte (`src/`)

O código é organizado em módulos com responsabilidades claras:

- `src/core/`: lógica de pipeline, limpeza, transformação, integração e validação de dados
- `src/data/`: geração e manipulação de dados auxiliares
- `src/mlearn/`: componentes de machine learning, registro de modelos e fluxo de treinamento
- `src/config/`: configurações e arquivos de suporte para fontes, modelos e dados
- `src/ui/`: interface de execução ou scripts de interação
- `src/__main__.py`: ponto de entrada do projeto quando executado como pacote

### 3. Documentação (`docs/`)

A documentação está dividida em blocos lógicos:

- `docs/project/`: escopo, cronograma e objetivos do projeto
- `docs/data/`: dicionário, fontes e tratamento dos dados
- `docs/analysis/`: abordagem analítica, hipóteses e metodologia
- `docs/architecture/`: arquitetura e pipeline do projeto

### 4. Notebooks e experimentos (`notebooks/`)

Os notebooks hospedam análises exploratórias e visualizações interativas, permitindo experimentação sem alterar o código fonte principal.

A pasta também serve como ambiente de documentação dinâmica para resultados intermediários e testes rápidos.

### 5. Relatórios e resultados (`reports/`)

Os relatórios armazenam resultados exportados de modelos e métricas de avaliação, com foco em transparência dos experimentos e reprodutibilidade das análises.

Atualmente, a pasta `reports/ml/` contém previsões e métricas de modelos supervisionados e não supervisionados.

## Fluxo de execução

A arquitetura segue um fluxo de alto nível composto por:

1. coleta de dados brutos em `data/raw/`
2. limpeza, padronização e mapeamento em `data/clean/`
3. integração e criação de bases analíticas em `data/processed/`
4. análise exploratória em `notebooks/` e/ou `src/`
5. modelagem e validação em `src/mlearn/`
6. geração de resultados em `reports/`

Esse fluxo é descrito de forma complementar em `docs/architecture/PIPELINE.md`.

## Diretrizes arquiteturais

As decisões de arquitetura foram tomadas para garantir:

- modularidade entre dados, processamento e modelagem
- preservação dos dados brutos
- reprodutibilidade do pipeline analítico
- fácil navegação entre código, dados e documentação
- suporte a evoluções futuras sem refatorações extensivas

## Considerações sobre ferramentas

O projeto é desenvolvido principalmente em Python e utiliza:

- ambiente virtual local (`env/`)
- dependências listadas em `requirements.txt`
- edição e execução de scripts em `src/`
- notebooks para exploração experimental

A arquitetura não depende de ferramentas externas complexas, priorizando a execução local e a manutenção do repositório como fonte única de verdade.

## Limitações e próximos passos

A arquitetura ainda está em maturação, e os resultados obtidos não foram satisfatórios. As principais melhorias previstas incluem:

- documentar melhor o fluxo de execução do pipeline
- harmonizar scripts de transformação com notebooks de análise
- consolidar o uso de `src/mlearn/` para experimentos e modelos finais
- definir critérios mais claros para a geração de artefatos em `reports/`
- aplicar estratégias para a natureza de nossos dados visando uma melhor eficácia e generalização do modelo de predição final
