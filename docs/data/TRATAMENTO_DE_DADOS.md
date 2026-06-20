# Tratamento de Dados

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](../../data/README.md), [`docs/`](../README.md)
- **Planejamento**: [`CRONOGRAMA.md`](../project/CRONOGRAMA.md), [`ESCOPO.md`](../project/ESCOPO.md), [`OBJETIVOS.md`](../project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](TRATAMENTO_DE_DADOS.md)
- **Arquitetura & Pipeline**: [`ARQUITETURA.md`](../architecture/ARQUITETURA.md), [`PIPELINE.md`](../architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](../analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](../analysis/HIPOTESES.md), [`METODOLOGIA.md`](../analysis/METODOLOGIA.md)

## Visão geral

Esta seção documenta, de forma resumida, os tratamentos iniciais aplicados às bases do projeto.

O objetivo é registrar as principais transformações realizadas até o momento para facilitar reprodutibilidade, entendimento do fluxo e manutenção futura.

## Tratamentos aplicados

Este documento descreve os tratamentos implementados pelo pipeline (veja `src/core/pipeline.py`) e as regras declarativas do `src/config/sources.yaml` que orientam transformações, validação e merge.

1) Leitura robusta

- O carregamento de CSV usa uma função cuidadosa que tenta múltiplos encodings e separadores (`transformer.careful_load_csv`).
- Encodings testados (ex.): `utf-8`, `cp1252`, `latin1`.

2) Limpeza genérica (`clean`)

- Normalização de nomes de colunas: lowercase, remoção de acentos, substituição de espaços por `_` quando aplicável.
- Limpeza de strings: `strip()`, remoção de caracteres não imprimíveis e conversão de valores vazios.
- Remoção de duplicatas e linhas claramente inválidas.
- Normalização de chaves de município (remoção de códigos embutidos e padronização textual) — passo implementado como `purge` quando configurado.

3) Transformações declarativas por fonte (`transform`)

As transformações por coluna são dirigidas pelo bloco `transformacoes` em `src/config/sources.yaml`. Os tipos suportados incluem:

- `tipo: mapa_ibge` — mapeia códigos IBGE para nomes de município usando `codigos_ibge_sp.csv` (parâmetros `mapa_ref`, `col_chave`, `col_valor`).
- `tipo: purge` — limpeza textual específica (remoção de dígitos, espaços extra, uppercase/strip).
- `cast` — conversão de tipos suportados (`Int64`, `float64`, `str`, `datetime`).
- `rename` — renomeia colunas para nomes estáveis no dataset.
- `convert_to_column` — pivota colunas categóricas em múltiplas colunas (one-hot-like) usando `index` (chave, ex.: `municipio`) e `values` (lista de métricas a extrair). Suporta `prefixo` para nomes gerados.

Exemplo (do YAML):

	municipio:
		tipo: purge

	grupo_ipvs:
		convert_to_column: true
		index: municipio
		values: ['n_pessoas', 'n_domicilios', 'n_setores']

4) Regras de qualidade e validação (`validate_quality`)

- Validações per-fonte dirigidas por `sources.yaml`:
	- `cols_obrigatorias`
	- `cols_unicas`
	- `cols_nao_nulas`
	- `cols_numericas`
- Validações gerais: DataFrame vazio, colunas `Unnamed`, detecção de duplicatas.
- O pipeline pode operar em `--dry-run` para executar validações sem salvar os CSVs limpos.

5) Salvamento intermediário

- DataFrames validados são salvos em `data/clean/{nome}-clean.csv` usando `save_csv()`.

6) Inicialização de colunas IDS por fonte

- Após salvar as fontes limpas, o pipeline chama `append_dimensions()` (em `src/core/calculator.py`) para ler os blocos `ids` de cada fonte e preencher `IDS_CONFIG` com as colunas e pesos declarados no YAML.

7) Merge sequencial e produção da base processada

- O `run_merge()` (em `src/core/merger.py`) aplica merge sequencial baseado em `merge.chave` e `merge.como` definidos em `sources.yaml`.
- As `colunas_uteis` em cada fonte definem uma whitelist para inclusão no merge final, evitando inflar o dataset com colunas irrelevantes.

8) Cálculo do IDS (`calculate_ids`)

- Depois do merge, `calculate_ids()` utiliza `IDS_CONFIG` para calcular as quatro dimensões (`infraestrutura`, `serviços`, `vulnerabilidade`, `renda`).
- Operadores usados: `weighted_sum`, `safe_divide`, `normalize_series` (ex.: `robust_minmax`), `log1p` para renda per capita.

9) Geração de dataset de validação sintético

- `src/data/generator.py` usa o bloco `validation` do `sources.yaml` para gerar amostras sintéticas balanceadas pelos percentis do IDS, aplicar ruído e preservar estrutura de colunas.

10) Opções operacionais

- `--dry-run`: roda validações sem salvar os CSVs tratados.
- `--skip-transform`: executa somente a limpeza genérica sem aplicar `transformacoes`.

## Arquivos e funções principais

- `src/core/cleaner.py` → `clean()`
- `src/core/transformer.py` → `transform()`, `careful_load_csv()`, `load_refs()`
- `src/core/validator.py` → `validate_quality()`
- `src/core/merger.py` → `run_merge()`, `load_merge_config()`
- `src/core/calculator.py` → `append_dimensions()`, `calculate_ids()`
- `src/data/generator.py` → `DatasetGenerator`

## Recomendações operacionais

- Mantenha o `src/config/sources.yaml` sincronizado com a origem dos CSVs; ele é a documentação viva das transformações.
- Use `--dry-run` para validar novas fontes antes de escrever em `data/clean/`.
- Ao adicionar novas fontes, preencha blocos `transformacoes`, `qualidade` e `ids` para garantir integração e uso no cálculo do IDS.

## Comandos úteis

```bash
python -m src.core.pipeline        # executa limpeza + transformação + merge + cálculo de IDS
python -m src.__main__             # menu interativo
```
