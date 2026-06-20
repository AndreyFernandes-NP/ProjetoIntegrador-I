# Objetivos do Projeto

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](../../data/README.md), [`docs/`](../README.md)
- **Visão geral**: [`../README.md`](../README.md)
- **Planejamento**: [`CRONOGRAMA.md`](CRONOGRAMA.md), [`ESCOPO.md`](ESCOPO.md), [`OBJETIVOS.md`](OBJETIVOS.md)
- **Dados**: [`../data/DICIONARIO_DE_DADOS.md`](../data/DICIONARIO_DE_DADOS.md), [`../data/FONTES_DE_DADOS.md`](../data/FONTES_DE_DADOS.md), [`../data/TRATAMENTO_DE_DADOS.md`](../data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura & Pipeline**: [`../architecture/ARQUITETURA.md`](../architecture/ARQUITETURA.md), [`../architecture/PIPELINE.md`](../architecture/PIPELINE.md)
- **Análise**: [`../analysis/ABORDAGEM_ANALITICA.md`](../analysis/ABORDAGEM_ANALITICA.md), [`../analysis/HIPOTESES.md`](../analysis/HIPOTESES.md), [`../analysis/METODOLOGIA.md`](../analysis/METODOLOGIA.md)

## Objetivo geral

Analisar a relação entre vulnerabilidade social, infraestrutura urbana e pressão sobre os serviços públicos de saúde nos municípios do estado de São Paulo.

O foco é construir um pipeline de dados reprodutível que transforme fontes públicas em uma base analítica confiável e em métricas de apoio à decisão.

## Objetivos específicos

- identificar, documentar e validar bases públicas relevantes para o problema do projeto
- limpar, padronizar e transformar cada fonte com regras declarativas em `src/config/sources.yaml`
- integrar as bases por município usando chaves de referência como `cod_ibge` e `municipio`
- estruturar e documentar o cálculo do IDS nas quatro dimensões: infraestrutura, serviços, vulnerabilidade e renda
- preparar uma base analítica consolidada em `data/processed/main_dataframe.csv`
- realizar análise exploratória e gerar relatórios que evidenciem padrões e relações entre indicadores
- treinar, avaliar e comparar modelos supervisionados e não supervisionados
- gerar datasets de validação sintética para testar robustez e generalização

## Metas de entrega

- `data/processed/main_dataframe.csv` preparado e documentado
- `data/processed/validation_dataset.csv` gerado e reproduzível
- `docs/architecture/PIPELINE.md` com o fluxo real do pipeline
- `docs/data/DICIONARIO_DE_DADOS.md` com dimensões do IDS e exemplos de features
- `docs/data/FONTES_DE_DADOS.md` com contexto das fontes e su papel no projeto
- `docs/data/TRATAMENTO_DE_DADOS.md` com o detalhamento das transformações e validações
- `reports/ml/ml_supervised_metrics.csv` e outros relatórios de ML gerados por execução automatizada

## Indicadores de sucesso

- pipeline de dados executável localmente com um comando único
- cálculo do IDS consistente com a configuração de pesos em `src/config/sources.yaml`
- base analítica estável para modelagem supervisionada
- modelos avaliados com métricas registradas em `reports/ml/`
- documentação alinhada com o código e o workflow real
- validação sintética disponível para medir desempenho fora do conjunto original

## Resultado esperado

Ao final do projeto, espera-se obter:

- uma base organizada e tratada para análise de saúde pública em SP;
- um índice de desenvolvimento de saúde (`ids`) calculado e documentado;
- uma análise exploratória que identifique relações entre vulnerabilidade, capacidade de infraestrutura, oferta de serviços e outras informações importantes;
- uma abordagem preditiva inicial apoiada por métricas de desempenho e relatórios de validação;
- uma documentação completa que permita reconstruir o pipeline e entender as decisões de tratamento e modelagem.

## Considerações extras

- o projeto prioriza dados públicos e transparência de processamento;
- não se espera uma solução final de produção, mas um protótipo analítico robusto e reproduzível;
- ganhos potenciais incluem suporte a decisões locais e mapeamento de áreas com maior pressão sobre os serviços de saúde.
