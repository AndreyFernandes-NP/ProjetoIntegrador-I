# Dicionário de Dados

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](../../data/README.md), [`docs/`](../README.md)
- **Projeto**: [`CRONOGRAMA.md`](../project/CRONOGRAMA.md), [`ESCOPO.md`](../project/ESCOPO.md), [`OBJETIVOS.md`](../project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](TRATAMENTO_DE_DADOS.md)
- **Arquitetura**: [`ARQUITETURA.md`](../architecture/ARQUITETURA.md), [`PIPELINE.md`](../architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](../analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](../analysis/HIPOTESES.md), [`METODOLOGIA.md`](../analysis/METODOLOGIA.md)

## Visão geral

Este documento descreve os principais campos das bases atualmente utilizadas no projeto.

Os tipos e descrições abaixo representam o estágio atual do trabalho e poderão ser refinados conforme as bases forem expandidas e tratadas.

---

## Base: instalações hospitalares

**Arquivos relacionados:**
- `inst_hospitalares_sp-raw.csv`
- `inst_hospitalares_sp-clean.csv`

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `municipio` | texto | Nome do município do estado de São Paulo |
| `quantidade` | inteiro | Quantidade registrada de instalações hospitalares associadas ao município |

**Observações:**
- na versão bruta, o campo `municipio` pode conter código e nome no mesmo valor
- na versão limpa, o campo foi padronizado para manter apenas o nome do município

---

## Base: IPVS / vulnerabilidade social

**Arquivos relacionados:**
- `ipvs_esp-raw.csv`
- `ipvs_esp-merge.csv`

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `cod_ibge` | texto ou inteiro | Identificador do município; na base tratada passa a representar o nome do município após o merge |
| `grupo_ipvs` | texto | Classificação do grupo de vulnerabilidade social |
| `n_pessoas` | inteiro | Quantidade de pessoas associadas ao grupo de vulnerabilidade |
| `n_domicilios` | inteiro | Quantidade de domicílios associados ao grupo de vulnerabilidade |
| `n_setores` | inteiro | Quantidade de setores associados ao grupo de vulnerabilidade |

**Observações:**
- o campo `cod_ibge` na base tratada deve ser renomeado futuramente para algo mais claro, como `municipio`, para evitar ambiguidade
- o campo `grupo_ipvs` representa categorias qualitativas de vulnerabilidade

---

## Base: tabela auxiliar de códigos IBGE

**Arquivo relacionado:**
- `codigos_ibge_sp.csv`

| Campo | Tipo esperado | Descrição |
|---|---|---|
| `cod_ibge` | inteiro | Código IBGE do município |
| `municipio` | texto | Nome do município |
| `area_km` | texto ou numérico | Área do município em quilômetros quadrados |
| `cod_ra` | inteiro | Código da região administrativa |
| `ra` | texto | Nome da região administrativa |
| `cod_rm` | inteiro | Código da região metropolitana |
| `rm` | texto | Nome da região metropolitana |
| `cod_drs` | inteiro | Código do departamento regional de saúde |
| `drs` | texto | Nome do departamento regional de saúde |
| `cod_r_saude` | inteiro | Código da regional de saúde |
| `r_saude` | texto | Nome da regional de saúde |

## Campos-chave atuais

Os campos mais relevantes para integração entre bases, neste momento, são:

- `cod_ibge`
- `municipio`

## Pontos de atenção

- alguns campos mudam de significado entre a base bruta e a base tratada
- nomes de municípios podem exigir padronização adicional

## Observações

Este dicionário deverá evoluir conforme novas bases, variáveis e transformações forem incorporadas ao projeto.