# Metodologia

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](../../data/README.md), [`docs/`](../README.md)
- **Visão geral**: [`../README.md`](../README.md)
- **Planejamento**: [`../project/CRONOGRAMA.md`](../project/CRONOGRAMA.md), [`../project/ESCOPO.md`](../project/ESCOPO.md), [`../project/OBJETIVOS.md`](../project/OBJETIVOS.md)
- **Dados**: [`../data/DICIONARIO_DE_DADOS.md`](../data/DICIONARIO_DE_DADOS.md), [`../data/FONTES_DE_DADOS.md`](../data/FONTES_DE_DADOS.md), [`../data/TRATAMENTO_DE_DADOS.md`](../data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura & Pipeline**: [`../architecture/ARQUITETURA.md`](../architecture/ARQUITETURA.md), [`../architecture/PIPELINE.md`](../architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](HIPOTESES.md), [`METODOLOGIA.md`](METODOLOGIA.md)

## Visão geral

O projeto segue uma metodologia inspirada no **CRISP-DM** (*Cross Industry Standard Process for Data Mining*), adaptada à realidade acadêmica e ao conjunto de dados públicos do estado de São Paulo.

A metodologia orienta a condução do trabalho em etapas claras e iterativas: entendimento do problema, compreensão dos dados, preparação da base, análise exploratória, modelagem e avaliação.

## Etapas adotadas no projeto

### 1. Entendimento do problema

Nesta etapa, o grupo estabeleceu o recorte do projeto, a hipótese central e os objetivos analíticos.

O foco está em investigar como vulnerabilidade social e infraestrutura urbana impactam a pressão sobre os serviços públicos de saúde nos municípios paulista, seus viéses e problemática.

### 2. Entendimento dos dados

São avaliadas as bases públicas locais quanto a:

- pertinência ao problema de saúde e vulnerabilidade
- qualidade e limpeza necessárias
- granularidade municipal e temporal
- compatibilidade entre fontes
- potencial de integração em uma base única

### 3. Preparação dos dados

A preparação atual do projeto inclui:

- leitura e organização das tabelas brutas
- limpeza e padronização de colunas
- validação de nomes de municípios e códigos IBGE
- integração de datasets por município
- geração de bases processadas e clusterizadas

### 4. Análise exploratória

A análise exploratória realizada tem por objetivo:

- compreender distribuições e tendências nos indicadores
- identificar padrões espaciais e grupos de municípios
- avaliar relações entre vulnerabilidade, infraestrutura e saúde
- detectar anomalias, dados faltantes e inconsistências
- apoiar a escolha de variáveis para modelagem

### 5. Modelagem

Com a base analítica consolidada, são testadas abordagens de machine learning para apoiar a previsão de pressão sobre o sistema de saúde.

A modelagem considera:

- variável-alvo ainda em refinamento
- seleção de variáveis preditoras relevantes
- experimentos com algoritmos supervisionados e não supervisionados
- avaliação de performance e estabilidade dos modelos

### 6. Avaliação dos resultados

A avaliação dos resultados é feita com base em:

- consistência com o problema pesquisado
- qualidade da base e dos indicadores
- capacidade explicativa das análises exploratórias
- desempenho de modelos e robustez das previsões
- limitações metodológicas e dos dados disponíveis

## Estratégia de trabalho

A execução do projeto é iterativa e incremental, permitindo ajustes nas etapas conforme evolução das análises e disponibilidade de dados.

Essa estratégia favorece refinamentos sucessivos em documentação, preparação de dados e modelagem.
