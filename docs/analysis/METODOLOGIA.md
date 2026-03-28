# Metodologia

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](data/README.md), [`docs/`](docs/README.md)
- **Projeto**: [`CRONOGRAMA.md`](docs/project/CRONOGRAMA.md), [`ESCOPO.md`](docs/project/ESCOPO.md), [`OBJETIVOS.md`](docs/project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](docs/data/DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](docs/data/FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](docs/data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura**: [`ARQUITETURA.md`](docs/architecture/ARQUITETURA.md), [`PIPELINE.md`](docs/architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](docs/analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](docs/analysis/HIPOTESES.md), [`METODOLOGIA.md`](docs/analysis/METODOLOGIA.md)

## Visão geral

O projeto será conduzido com base em uma abordagem de análise de dados inspirada no **CRISP-DM** (*Cross Industry Standard Process for Data Mining*), adaptada à realidade e ao escopo acadêmico do trabalho.

A escolha dessa metodologia se deve à sua organização em etapas claras, que permitem estruturar o problema, compreender os dados, preparar a base analítica, desenvolver modelos e avaliar resultados de forma progressiva.

## Etapas adotadas no projeto

### 1. Entendimento do problema

Nesta etapa, o grupo define o problema central do projeto, o recorte adotado, a hipótese principal e os objetivos da análise.

O foco atual está em investigar a relação entre vulnerabilidade social, infraestrutura urbana e pressão sobre os serviços públicos de saúde nos municípios do estado de São Paulo.

### 2. Entendimento dos dados

Nesta fase, são identificadas e avaliadas as bases públicas disponíveis para o projeto, observando aspectos como:

- aderência ao problema estudado
- qualidade dos dados
- granularidade
- compatibilidade entre fontes
- possibilidade de integração por município

### 3. Preparação dos dados

A preparação dos dados envolve:

- leitura e organização das bases
- tratamento de inconsistências
- padronização de nomes e colunas
- compatibilização de chaves
- integração entre datasets
- geração de uma base analítica inicial

### 4. Análise exploratória

A análise exploratória será utilizada para:

- compreender a distribuição dos indicadores
- identificar padrões iniciais
- observar possíveis correlações
- detectar anomalias, inconsistências e limitações
- apoiar decisões sobre variáveis e modelagem

### 5. Modelagem

Após a consolidação da base analítica, o projeto prevê o uso inicial de modelos supervisionados com finalidade preditiva, buscando apoiar a identificação de cenários de maior pressão sobre os serviços de saúde.

A escolha final dos algoritmos dependerá da definição da variável-alvo, da qualidade dos dados e do comportamento observado nas etapas anteriores.

### 6. Avaliação dos resultados

Os resultados serão avaliados com base em:

- coerência com o problema proposto
- qualidade da base construída
- capacidade explicativa das análises
- desempenho preliminar dos modelos
- limitações metodológicas e dos dados utilizados

## Estratégia de trabalho

A condução do projeto seguirá uma organização simples e iterativa, com refinamento progressivo das análises, da documentação e das decisões metodológicas ao longo do semestre.

Essa abordagem permite que o grupo adapte o andamento do trabalho de acordo com a disponibilidade de dados, a compatibilidade entre fontes e os resultados obtidos em cada etapa.

## Observações

Esta metodologia poderá ser refinada ao longo do projeto, principalmente nas etapas de modelagem e avaliação, conforme o avanço das análises e a definição mais precisa da variável-alvo.