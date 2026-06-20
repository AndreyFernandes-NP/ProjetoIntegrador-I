# Escopo do Projeto

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](../../data/README.md), [`docs/`](../README.md)
- **Visão geral**: [`../README.md`](../README.md)
- **Planejamento**: [`CRONOGRAMA.md`](CRONOGRAMA.md), [`ESCOPO.md`](ESCOPO.md), [`OBJETIVOS.md`](OBJETIVOS.md)
- **Dados**: [`../data/DICIONARIO_DE_DADOS.md`](../data/DICIONARIO_DE_DADOS.md), [`../data/FONTES_DE_DADOS.md`](../data/FONTES_DE_DADOS.md), [`../data/TRATAMENTO_DE_DADOS.md`](../data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura & Pipeline**: [`../architecture/ARQUITETURA.md`](../architecture/ARQUITETURA.md), [`../architecture/PIPELINE.md`](../architecture/PIPELINE.md)
- **Análise**: [`../analysis/ABORDAGEM_ANALITICA.md`](../analysis/ABORDAGEM_ANALITICA.md), [`../analysis/HIPOTESES.md`](../analysis/HIPOTESES.md), [`../analysis/METODOLOGIA.md`](../analysis/METODOLOGIA.md)

## Visão geral

Este projeto tem como objetivo analisar dados públicos do estado de São Paulo para investigar a relação entre vulnerabilidade social, infraestrutura urbana e pressão sobre os serviços públicos de saúde. A proposta busca identificar padrões e correlações entre condições urbanas adversas e possíveis sinais de maior demanda ou sobrecarga na rede de atendimento em diferentes municípios.

## Problema

Municípios com maior vulnerabilidade social e condições mais precárias de infraestrutura urbana podem apresentar maior pressão sobre os serviços públicos de saúde.

O projeto parte da necessidade de entender essa relação com base em dados públicos, permitindo apoiar análises comparativas e futuras estratégias de tomada de decisão.

## Recorte atual

Nesta etapa, o projeto está concentrado em:

- municípios do estado de São Paulo
- indicadores de vulnerabilidade social
- indicadores de infraestrutura urbana
- indicadores relacionados à rede e à pressão sobre serviços de saúde
- análise com base em dados públicos disponíveis

## O que está dentro do escopo

- levantamento e seleção de bases públicas
- padronização e tratamento dos dados
- integração entre bases compatíveis
- análise exploratória
- identificação de correlações
- preparação de base analítica
- desenvolvimento inicial de abordagem preditiva supervisionada

## O que está fora do escopo neste momento

- análise causal definitiva
- expansão para outros estados
- análise de serviços públicos além da área da saúde
- uso de dados privados ou sensíveis
- implantação real de solução em ambiente governamental ou hospitalar
- construção de sistema completo de produção

## Escopo expandido

A seguir há uma versão ampliada do escopo com objetivos específicos, entregáveis, critérios de sucesso, premissas e riscos iniciais.

**Objetivos específicos**
- Consolidar e documentar um pipeline reprodutível para transformar `data/raw/` → `data/clean/` → `data/processed/`.
- Implementar o cálculo do `IDS` em `src/core/calculator.py` e documentar suas suposições e parâmetros.
- Gerar um conjunto de features por município para alimentar modelos supervisionados que prevejam o `ids`.
- Produzir relatórios e visualizações que evidenciem correlações entre vulnerabilidade, infraestrutura, serviços e renda.

**Entregáveis (mínimos viáveis)**
- `data/processed/main_dataframe.csv` com colunas utilizadas pelo IDS e features selecionadas.
- Documentação: `docs/architecture/PIPELINE.md`, `docs/data/DICIONARIO_DE_DADOS.md`, `docs/data/TRATAMENTO_DE_DADOS.md`, `docs/data/FONTES_DE_DADOS.md`.
- Relatórios ML: `reports/ml/ml_supervised_metrics.csv`, `reports/ml/ml_supervised_prediction_metrics.csv`, `reports/ml/ml_unsupervised_metrics.csv`.
- Código reproducível: scripts em `src/core/` e `src/mlearn/` com configurações em `src/config/*.yaml`.

**Critérios de sucesso**
- Pipeline executável localmente que gera `main_dataframe.csv` sem intervenção manual (passos documentados).
- IDS reproduzível e documentado, com os pesos e colunas herdadas de `src/config/sources.yaml`.
- Modelos supervisionados treináveis e avaliáveis com métricas registradas em `reports/ml/`.
- Documentação mínima completa para entrega (README, docs, dicionário de dados e pipeline).

**Premissas**
- Fontes públicas permanecem acessíveis e com estrutura estável durante o período do projeto.
- A granularidade por município é suficiente para consolidar indicadores e treinar modelos.
- Recursos computacionais locais são suficientes para execução dos experimentos de ML planejados (ou será feita seleção de modelos para reduzir custo).

**Restrições**
- Não usar dados pessoais sensíveis ou qualquer base que viole privacidade.
- O escopo temporal está limitado às bases de 2022 (quando aplicável), salvo atualização documentada.

**Riscos conhecidos**
- Mudanças no layout das fontes (colunas/encodings) podem quebrar transformações declarativas; mitigação: testes com `--dry-run` e logs de validação.
- Quantidade de features (colunas) é exorbitante em comparação ao número de dados disponíveis (apenas 640 linhas para treinamento).
- A própria natureza dos dados contém valores ausentes e que não podem ser modificados por representarem a realidade.

**Recomendações operacionais**
- Ao adicionar uma nova fonte, atualize `src/config/sources.yaml` com `transformacoes`, `qualidade` e `ids` para inclusão automática no pipeline.
- Use `python -m src.core.pipeline --dry-run` antes de persistir arquivos em `data/clean/`.
- Versione grandes CSVs processados em um sistema de arquivos dedicado ou anexe um hash/manifest para rastreabilidade.
