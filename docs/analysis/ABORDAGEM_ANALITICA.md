# Abordagem Analítica

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](../../data/README.md), [`docs/`](../README.md)
- **Projeto**: [`CRONOGRAMA.md`](../project/CRONOGRAMA.md), [`ESCOPO.md`](../project/ESCOPO.md), [`OBJETIVOS.md`](../project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](../data/DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](../data/FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](../data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura**: [`ARQUITETURA.md`](../architecture/ARQUITETURA.md), [`PIPELINE.md`](../architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](HIPOTESES.md), [`METODOLOGIA.md`](METODOLOGIA.md)

## Visão geral

A abordagem analítica do projeto será desenvolvida de forma progressiva, partindo da organização e compreensão das bases públicas até a construção de uma análise preditiva inicial.

O objetivo não é apenas reunir dados, mas estruturar uma base analítica capaz de sustentar interpretações consistentes sobre a relação entre vulnerabilidade social, infraestrutura urbana e pressão sobre os serviços públicos de saúde.

## Etapas da abordagem

### 1. Seleção e organização das bases

Inicialmente, serão reunidas bases públicas relevantes para o problema do projeto, priorizando fontes com:

- aderência ao tema
- recorte compatível com o estado de São Paulo
- granularidade municipal
- potencial de integração entre si

### 2. Padronização e integração

Após a coleta, os dados passarão por tratamento e padronização, com foco em:

- uniformização de nomes de municípios
- uso de códigos oficiais quando aplicável
- ajuste de tipos de dados
- compatibilização entre diferentes formatos de base

Essa etapa é essencial para permitir comparações consistentes entre os indicadores selecionados.

### 3. Análise exploratória dos indicadores

A análise exploratória buscará:

- compreender a distribuição dos dados
- observar diferenças entre municípios
- identificar tendências iniciais
- detectar inconsistências, valores extremos e limitações
- orientar a escolha de variáveis mais relevantes

### 4. Definição da base analítica

Com os dados integrados e analisados, será consolidada uma base analítica com os indicadores considerados mais relevantes para o problema estudado.

Essa base servirá como referência para análises comparativas, correlações e testes preditivos.

### 5. Modelagem supervisionada inicial

O projeto prevê a aplicação inicial de um modelo supervisionado, com a finalidade de apoiar a identificação de municípios com maior propensão a cenários de pressão sobre os serviços de saúde.

Nesta etapa, ainda serão definidos com maior precisão:

- a variável-alvo
- as variáveis preditoras
- o tipo mais adequado de problema analítico
- os critérios de avaliação do modelo

### 6. Interpretação dos resultados

Os resultados serão interpretados com foco em:

- coerência com a hipótese principal
- utilidade analítica dos indicadores escolhidos
- limitações dos dados utilizados
- contribuição da modelagem para a compreensão do problema

## Diretrizes da análise

A abordagem do projeto seguirá algumas diretrizes principais:

- priorizar bases públicas e verificáveis
- manter o recorte municipal como unidade inicial de análise
- evitar conclusões causais indevidas
- documentar limitações e decisões metodológicas
- construir resultados progressivamente, sem antecipar promessas além do que os dados sustentam

## Limitações esperadas

Algumas limitações já são previstas nesta etapa:

- disponibilidade desigual de indicadores entre bases
- necessidade de padronização adicional
- possível diferença de granularidade entre fontes
- definição ainda em andamento da variável-alvo
- necessidade de validação do potencial real de predição

## Observações

Este documento poderá ser atualizado conforme a base analítica for amadurecida e as decisões de modelagem se tornarem mais específicas.