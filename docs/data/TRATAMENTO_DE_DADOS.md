# Tratamento de Dados

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](data/README.md), [`docs/`](docs/README.md)
- **Projeto**: [`CRONOGRAMA.md`](docs/project/CRONOGRAMA.md), [`ESCOPO.md`](docs/project/ESCOPO.md), [`OBJETIVOS.md`](docs/project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](docs/data/DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](docs/data/FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](docs/data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura**: [`ARQUITETURA.md`](docs/architecture/ARQUITETURA.md), [`PIPELINE.md`](docs/architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](docs/analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](docs/analysis/HIPOTESES.md), [`METODOLOGIA.md`](docs/analysis/METODOLOGIA.md)

## Visão geral

Esta seção documenta, de forma resumida, os tratamentos iniciais aplicados às bases do projeto.

O objetivo é registrar as principais transformações realizadas até o momento para facilitar reprodutibilidade, entendimento do fluxo e manutenção futura.

## Tratamentos já aplicados

### 1. Leitura com suporte a múltiplos encodings

Para reduzir falhas na leitura dos arquivos CSV, foi adotada uma tentativa sequencial com diferentes encodings.

**Encodings considerados:**
- `utf-8`
- `cp1252`
- `latin1`

### 2. Remoção inicial de valores ausentes

Foi aplicada remoção de registros com valores ausentes nas bases utilizadas na etapa inicial.

**Observação:**
Esse critério ainda poderá ser revisado no futuro, dependendo da importância analítica dos campos ausentes.

### 3. Padronização de municípios

Foi realizada padronização de nomes de municípios para facilitar junções entre bases.

**Exemplos de tratamento:**
- remoção de códigos numéricos misturados ao nome do município
- conversão para texto
- remoção de acentos
- conversão para letras maiúsculas

### 4. Conversão de tipos numéricos

Campos quantitativos foram convertidos para formato inteiro quando aplicável.

**Campos já tratados:**
- `quantidade`
- `n_pessoas`
- `n_domicilios`
- `n_setores`

### 5. Merge com base auxiliar de códigos

Foi utilizada uma base auxiliar de códigos IBGE para mapear municípios e permitir compatibilização entre datasets.

**Objetivo do merge:**
- transformar códigos em nomes padronizados de município
- facilitar comparações entre bases com formatos diferentes de chave

## Script atual

O tratamento inicial foi centralizado em um script Python de limpeza e mesclagem de dados.

**Arquivo atual:**
- `data_cleaner+merger.py`

## Limitações atuais do tratamento

- o processo ainda está em estágio inicial
- parte da limpeza foi feita para viabilizar testes exploratórios, não como pipeline final
- a estratégia de remoção de nulos ainda pode ser refinada
- ainda será necessário documentar melhor regras de transformação por base
- alguns nomes de colunas serão ajustados para maior clareza semântica

## Melhorias previstas

- separar limpeza e merge em etapas distintas
- padronizar nomes de colunas entre bases
- registrar logs de transformação
- criar saídas intermediárias por etapa
- definir melhor as chaves finais de integração
- revisar tratamento de valores ausentes e inconsistências

## Observações

Este documento deverá acompanhar a evolução do pipeline de dados e ser atualizado sempre que novos tratamentos forem incorporados.