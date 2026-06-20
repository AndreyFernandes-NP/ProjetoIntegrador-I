# Organização da pasta de dados

Esta pasta reúne os arquivos de dados usados no projeto, contém fontes brutas, versões limpas intermediárias, bases processadas prontas para análise e alguns relatórios/resultados gerados pelo pipeline e pelos experimentos de ML.

## Estrutura

```text
data/
├── raw/                    # arquivos originais baixados das fontes
├── clean/                  # saídas intermediárias após limpeza e transformações por fonte
├── processed/              # bases consolidadas prontas para análise/modelagem
├── data_cleaner+merger.py  # utilitário legado (documentado abaixo)
└── README.md
```

## Visão geral das pastas

- `raw/`
	- Armazena os CSVs originais tal como baixados das fontes (DATASUS, IBGE, Seade, Secretaria da Fazenda).
	- Mantenha esses arquivos imutáveis para fins de auditoria e reprocessamento.

- `clean/`
	- Contém os arquivos resultantes após a execução de `src/core/pipeline.py` (ou do utilitário legado). Arquivos seguem o padrão `{fonte}-clean.csv`.
	- Essas versões já aplicaram `clean()` e `transform()` (quando não executado em `--skip-transform`).

- `processed/`
	- Contém a base consolidada `main_dataframe.csv` (merge final), datasets de validação (`validation_dataset.csv`, `validation_samples.csv`) e variações (ex.: `main_dataframe_clusterizado.csv`).
	- Usadas diretamente por notebooks, scripts analíticos e pela pasta `reports/`.

## Principais datasets brutos (`raw/`)

Resumo das fontes encontradas no repositório e seu papel principal (descrição resumida; para detalhes veja `docs/data/FONTES_DE_DADOS.md`):

- `municipios.csv` — tabela auxiliar de códigos IBGE, nomes, coordenadas e atributos administrativos (base para `mapa_ibge`).
- `estabelecimentos_saude.csv` — CNES: tipos e contagens de estabelecimentos por município (fonte de infraestrutura).
- `inst_hospitalares_sp.csv` — quantidade de instituições hospitalares por município (CNES subset/derivado).
- `ipvs_esp.csv` — IPVS (Fundação Seade / IBGE): distribuição de pessoas/domicílios por classe de vulnerabilidade.
- `sia_cnv_qgsp.csv` — SIA: procedimentos ambulatoriais e volume por município (fonte de serviços).
- `sih_cnv_spgsp.csv` — SIH: internações e procedimentos hospitalares por município.
- `tabela30_SP_internacao.csv` — tabelas Tabnet/DATASUS com detalhamento de internações por tipo (suporte exploratório).
- `finbra_2022SP.csv` — Finbra: receitas municipais e dados financeiros (fonte de renda / capacidade econômica).
- `healthcare_final_latlon.csv` — CNES cruzado com geolocalização (latitude/longitude) para análises espaciais.

> Observação: a lista acima corresponde aos arquivos presentes em `data/raw/` no momento; novas fontes podem ser adicionadas e devem ser documentadas em `docs/data/FONTES_DE_DADOS.md`.

## Principais saídas processadas (`processed/`)

- `main_dataframe.csv`
	- Merge consolidado de fontes com as colunas úteis definidas em `src/config/sources.yaml`.
	- Contém colunas usadas no cálculo do `IDS` e nas pipelines de ML (features + `ids`).

- `main_dataframe_clusterizado.csv` (quando gerado)
	- Versão do dataset com colunas de cluster/labels provenientes de algoritmos não supervisionados.

- `validation_dataset.csv`, `validation_samples.csv`
	- Datasets sintéticos gerados por `src/data/generator.py` seguindo as regras em `src/config/sources.yaml` (`validation` block).
	- Usados para validação externa e testes de predição dos modelos treinados.

## Relatórios e outputs (gerados em `reports/`)

- `reports/ml/ml_supervised_metrics.csv` — métricas agregadas dos modelos supervisionados (MAE, RMSE, R2, etc.).
- `reports/ml/ml_supervised_prediction_metrics.csv` — métricas de performance das predições em datasets de validação.
- `reports/ml/ml_unsupervised_metrics.csv` — métricas de clusterização (silhouette, calinski_harabasz, davies_bouldin).
- `reports/ml/{model_name}_predictions.csv` — predições individuais por modelo.
- `reports/ml/pca_tuning/` — resultados de exploração de parâmetros de PCA.

Esses relatórios são gerados por `src/mlearn/pipeline.py` ao executar `run_all()` ou `run_pipeline()`.

## Como regenerar dados e relatórios

- Executar pipeline de dados (limpeza, transformação, merge, IDS):

```bash
python -m src.core.pipeline
```

- Executar pipeline completo de Machine Learning (treino, tuning, validação):

```bash
python -m src.mlearn.pipeline
```

- Gerar apenas modelos supervisionados:

```bash
python -m src.mlearn.pipeline supervised_pipeline
```

Recomendações:

- Rode `python -m src.core.pipeline --dry-run` ao adicionar uma nova fonte para validar transformações antes de escrever em `data/clean/`.
- Ao incluir novas fontes, atualize `src/config/sources.yaml` com `transformacoes`, `qualidade` e bloco `ids` para garantir participação no cálculo do IDS.

## Boas práticas e convenções

- Mantenha os arquivos em `data/raw/` imutáveis: reprocessamentos devem gerar novos arquivos em `data/clean/`.
- Nome dos arquivos limpos: `{nome}-clean.csv`.
- Evite editar `data/processed/` manualmente: gere via pipeline para manter rastreabilidade.
