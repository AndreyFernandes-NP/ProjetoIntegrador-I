# Hipóteses

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](../../data/README.md), [`docs/`](../README.md)
- **Visão geral**: [`../README.md`](../README.md)
- **Planejamento**: [`../project/CRONOGRAMA.md`](../project/CRONOGRAMA.md), [`../project/ESCOPO.md`](../project/ESCOPO.md), [`../project/OBJETIVOS.md`](../project/OBJETIVOS.md)
- **Dados**: [`../data/DICIONARIO_DE_DADOS.md`](../data/DICIONARIO_DE_DADOS.md), [`../data/FONTES_DE_DADOS.md`](../data/FONTES_DE_DADOS.md), [`../data/TRATAMENTO_DE_DADOS.md`](../data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura & Pipeline**: [`../architecture/ARQUITETURA.md`](../architecture/ARQUITETURA.md), [`../architecture/PIPELINE.md`](../architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](HIPOTESES.md), [`METODOLOGIA.md`](METODOLOGIA.md)

## Visão geral

Este documento registra as hipóteses analíticas do projeto, fundamentadas no problema de pesquisa e nas bases públicas municipais selecionadas.

As hipóteses orientam a análise exploratória, a construção da base analítica integrada, os testes estatísticos e a modelagem preditiva.

## Hipótese principal

Municípios com maior vulnerabilidade social e piores condições de infraestrutura urbana apresentam maior pressão sobre os serviços públicos de saúde e como alguns municípios subvertem essa necessidade.

## Hipóteses secundárias

### Hipótese 1: Vulnerabilidade social e concentração de riscos

Municípios com piores indicadores sociais e de pobreza apresentam concentrações de fatores que amplificam vulnerabilidades: receita baixa ou desigual, saúde precária e infraestrutura inadequada.

### Hipótese 2: Receita desigual para baixa receita

Municípios com uma receita muito alta porém uma infraestrutura ruim e/ou poucos serviços de saúde denunciam negligência de seus governantes com a população e o investimento de seu capital no próprio município.

### Hipótese 3: Interação entre vulnerabilidade e infraestrutura

A combinação de vulnerabilidade social elevada e infraestrutura urbana/hospitalar inadequada está associada a cenários críticos de demanda sobre serviços de saúde.

### Hipótese 4: Potencial preditivo de indicadores integrados

A integração de indicadores sociais, urbanos e de saúde permite construir modelos preditivos capazes de identificar municípios com maior propensão a pressão sobre a rede hospitalar.

### Hipótese 5: Padrões territoriais

Existem padrões territoriais e regionais no estado de São Paulo que agrupam municípios com vulnerabilidade similar e pressão semelhante sobre serviços de saúde.

## Papel das hipóteses no projeto

As hipóteses neste documento são diretrizes analíticas, não conclusões prévias. Elas são testadas da seguinte forma:

- análise exploratória dos dados municipais
- testes de correlação entre indicadores
- modelagem supervisionada e não supervisionada
- validação com dados de validação e amostras independentes

A confirmação, rejeição ou refinamento também depende da:

- qualidade e cobertura das bases utilizadas
- compatibilidade temporal e metodológica entre dados
- resultados dos testes estatísticos e preditivos
- análise crítica das limitações dos dados
