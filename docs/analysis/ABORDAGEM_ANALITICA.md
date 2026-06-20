# Abordagem Analítica

## Mapa de Documentação do Repositório

- **Pastas**: [`..data/`](../../data/README.md), [`docs/`](../README.md)
- **Visão geral**: [`../README.md`](../README.md)
- **Planejamento**: [`../project/CRONOGRAMA.md`](../project/CRONOGRAMA.md), [`../project/ESCOPO.md`](../project/ESCOPO.md), [`../project/OBJETIVOS.md`](../project/OBJETIVOS.md)
- **Dados**: [`../data/DICIONARIO_DE_DADOS.md`](../data/DICIONARIO_DE_DADOS.md), [`../data/FONTES_DE_DADOS.md`](../data/FONTES_DE_DADOS.md), [`../data/TRATAMENTO_DE_DADOS.md`](../data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura & Pipeline**: [`../architecture/ARQUITETURA.md`](../architecture/ARQUITETURA.md), [`../architecture/PIPELINE.md`](../architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](HIPOTESES.md), [`METODOLOGIA.md`](METODOLOGIA.md)

## Contextualização geral

O Projeto Integrador I investiga como variáveis de vulnerabilidade social, infraestrutura urbana e indicadores de saúde interagem na rede pública do estado de São Paulo.

O objetivo é construir uma base analítica integrada que permita identificar padrões territoriais, estudar a pressão sobre os serviços de saúde e oferecer subsídios iniciais para modelos preditivos e análises de risco municipal.

A análise considera dados municipais de diferentes domínios, incluindo saúde hospitalar, infraestrutura, indicadores socioeconômicos e variáveis geográficas, para criar uma base confiável para nossa exploração e modelagem.

## Etapas da abordagem

### 1. Seleção e organização das bases

Agregação de fontes públicas relevantes com:

- recorte em municípios de São Paulo
- dados de saúde, vulnerabilidade social e infraestrutura urbana
- granularidade municipal adequadas para comparação
- potencial de integração entre diferentes domínios de informação

### 2. Padronização e integração

Tratamento dos dados com foco em:

- normalização de nomes de municípios e códigos IBGE
- uniformização de formatos de colunas e tipos de dados
- limpeza de inconsistências
- harmonização entre diferentes bases e períodos

### 3. Análise exploratória

A exploração dos dados busca:

- mapear distribuições e variações municipais
- identificar clusters e padrões territoriais
- verificar relações iniciais entre infraestrutura e saúde
- avaliar qualidade dos dados e possíveis vieses
- apoiar a seleção de indicadores para modelagem

### 4. Definição da base analítica

Consolidação de uma base analítica integrada com os indicadores mais relevantes para o problema estudado.

Essa base será utilizada em análises estatísticas, correlações, visualizações e testes de hipóteses.

### 5. Modelagem e validação

Desenvolvimento e validação de abordagens de machine learning para apoiar a identificação de municípios com maior probabilidade de pressão sobre a rede hospitalar.

Nesta fase serão refinados:

- variável-alvo
- variáveis preditoras
- abordagem de modelagem (regressão e clusterização)
- métricas de avaliação e validação

### 6. Interpretação dos resultados

A interpretação possui foco em:

- aderência à hipótese de vulnerabilidade e pressão sobre a saúde
- insights práticos para gestão e planejamento de saúde pública
- limitações e incertezas dos dados
- potencial de uso dos modelos em cenários municipais

## Diretrizes da análise

O projeto segue os princípios de:

- uso de dados públicos e fontes verificáveis
- recorte municipal como unidade de estudo
- transparência metodológica
- documentação de decisões e limitações
- evolução incremental dos resultados

## Limitações

Enfrentamos as seguintes limitações durante o desenvolvimento:

- disponibilidade desigual de indicadores entre bases
- necessidade de padronização e harmonização dos dados
- diferenças temporais e metodológicas entre fontes
- definição em evolução da variável-alvo
- necessidade de validação do potencial preditivo
- muitos valores ausentes por causa da natureza dos dados
