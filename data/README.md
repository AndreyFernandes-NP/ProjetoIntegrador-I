# Organização da pasta de dados

Esta pasta reúne os arquivos de dados utilizados no projeto, incluindo bases brutas, versões tratadas e saídas intermediárias geradas ao longo do pipeline.

## Estrutura

```text
data/
├── clean/
├── processed/
├── raw/
├── data_cleaner+merger.py
└── README.md
```

## Descrição das pastas

`raw/`
Armazena os arquivos originais obtidos a partir das fontes públicas utilizadas no projeto.

Esses arquivos devem ser preservados o máximo possível em seu estado original, servindo como referência para reprocessamento e auditoria das transformações realizadas.

`clean/`
Contém versões limpas ou parcialmente tratadas das bases originais.

Esses arquivos representam saídas intermediárias após etapas iniciais de padronização, correção ou ajuste de colunas e valores.

`processed/`
Reservada para bases mais consolidadas, preparadas para análise exploratória, integração entre indicadores e futuras etapas de modelagem.

`amogus/`
A pasta mais suspeita desse projeto, pro que será que ela serve?

## Script auxiliar

`data_cleaner+merger.py`

Script inicial utilizado para tratamento e mesclagem de bases CSV, incluindo etapas como:

- leitura com suporte a diferentes encodings
- remoção de valores ausentes
- padronização de nomes de municípios
- conversão de tipos numéricos
- merge com base auxiliar de códigos IBGE

## Observações

A organização desta pasta poderá ser refinada ao longo do projeto, conforme novas bases forem incorporadas e o pipeline de dados se tornar mais estruturado.

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](README.md), [`docs/`](../docs/README.md)
- **Projeto**: [`CRONOGRAMA.md`](../docs/project/CRONOGRAMA.md), [`ESCOPO.md`](../docs/project/ESCOPO.md), [`OBJETIVOS.md`](../docs/project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](../docs/data/DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](../docs/data/FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](../docs/data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura**: [`ARQUITETURA.md`](../docs/architecture/ARQUITETURA.md), [`PIPELINE.md`](../docs/architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](../docs/analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](../docs/analysis/HIPOTESES.md), [`METODOLOGIA.md`](../docs/analysis/METODOLOGIA.md)