# Pipeline do Projeto

## Mapa de Documentação do Repositório

- **Projeto**: [`CRONOGRAMA.md`](docs/project/CRONOGRAMA.md), [`ESCOPO.md`](docs/project/ESCOPO.md), [`OBJETIVOS.md`](docs/project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](docs/data/DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](docs/data/FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](docs/data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura**: [`ARQUITETURA.md`](docs/architecture/ARQUITETURA.md), [`PIPELINE.md`](docs/architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](docs/analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](docs/analysis/HIPOTESES.md), [`METODOLOGIA.md`](docs/analysis/METODOLOGIA.md)

## Visão geral

O pipeline do projeto descreve o fluxo básico de trabalho adotado para transformar dados públicos brutos em uma base analítica utilizável para exploração, comparação e modelagem.

A proposta atual prioriza um fluxo simples, reprodutível e compatível com o estágio acadêmico do projeto.

## Fluxo geral

O fluxo do projeto pode ser resumido nas seguintes etapas:

1. obtenção das bases públicas
2. armazenamento dos arquivos brutos
3. limpeza e padronização inicial
4. integração entre bases compatíveis
5. geração de dados limpos e processados
6. análise exploratória
7. preparação para modelagem supervisionada
8. avaliação e documentação dos resultados

## Etapas do pipeline

### 1. Obtenção dos dados

As bases são coletadas a partir de fontes públicas e oficiais, de acordo com o recorte do projeto.

Neste momento, o pipeline considera principalmente:

- dados de municípios do IBGE
- dados de instalações hospitalares do DATASUS
- dados de vulnerabilidade social do IPVS

### 2. Armazenamento inicial

Após a coleta, os arquivos são armazenados na pasta `data/raw/`, preservando os dados originais para referência e reprocessamento futuro.

Essa separação permite manter uma distinção clara entre fonte original e dados tratados.

### 3. Limpeza e padronização

Na etapa de preparação inicial, são aplicados tratamentos como:

- leitura com encodings compatíveis
- remoção ou ajuste de valores inconsistentes
- padronização de nomes de municípios
- conversão de tipos numéricos
- remoção de elementos indesejados em campos textuais

Essa fase tem como objetivo viabilizar integração e comparação entre bases.

### 4. Integração entre bases

Após a limpeza, as bases compatíveis passam por junção com base em chaves disponíveis, como:

- código IBGE
- nome padronizado do município

Essa etapa permite consolidar diferentes indicadores em uma estrutura mais adequada para análise conjunta.

### 5. Geração de saídas tratadas

Os resultados das transformações são armazenados em diretórios como:

- `data/clean/`
- `data/processed/`

Esses arquivos representam versões intermediárias ou consolidadas dos dados, prontas para uso analítico.

### 6. Análise exploratória

Com a base tratada, o projeto segue para análise exploratória por meio de notebooks e scripts, buscando:

- compreender a distribuição dos indicadores
- comparar municípios
- identificar padrões e possíveis relações
- detectar limitações e inconsistências restantes

### 7. Preparação para modelagem

A partir da análise exploratória, será construída uma base analítica mais consolidada para:

- definição de variáveis preditoras
- definição da variável-alvo
- testes com modelos supervisionados
- comparação inicial de abordagens

### 8. Avaliação e documentação

Os resultados obtidos ao longo do pipeline serão documentados na pasta `docs/` e, quando aplicável, em notebooks e relatórios do projeto.

Essa etapa garante que decisões, limitações e avanços permaneçam registrados de forma organizada.

## Representação resumida do fluxo

```text
Fontes públicas oficiais
        ↓
data/raw/
        ↓
limpeza e padronização
        ↓
integração entre bases
        ↓
data/clean/ e data/processed/
        ↓
notebooks e análises exploratórias
        ↓
base analítica
        ↓
modelagem supervisionada inicial
        ↓
documentação e resultados
```

## Ferramentas associadas ao pipeline
O pipeline atual utiliza, ou prevê utilizar, as seguintes ferramentas:

- Python para scripts de limpeza, transformação e integração
- Jupyter Notebook para exploração e análise
- Google Colab para testes e experimentos complementares
- GitHub para versionamento e centralização do projeto

# Limitações atuais
O pipeline ainda se encontra em evolução e poderá sofrer ajustes em função de:

- novas bases incorporadas ao projeto
- mudanças na estratégia de integração
- refinamento da variável-alvo
- amadurecimento da etapa de modelagem

# Observações
O pipeline foi desenhado para atender às necessidades atuais do projeto sem adotar soluções de orquestração ou processamento distribuído, que seriam desnecessárias para o escopo e volume de dados trabalhados neste momento.