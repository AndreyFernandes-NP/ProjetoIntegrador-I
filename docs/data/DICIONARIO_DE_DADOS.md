# Dicionário de Dados

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](../../data/README.md), [`docs/`](../README.md)
- **Planejamento**: [`CRONOGRAMA.md`](../project/CRONOGRAMA.md), [`ESCOPO.md`](../project/ESCOPO.md), [`OBJETIVOS.md`](../project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](TRATAMENTO_DE_DADOS.md)
- **Arquitetura & Pipeline**: [`ARQUITETURA.md`](../architecture/ARQUITETURA.md), [`PIPELINE.md`](../architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](../analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](../analysis/HIPOTESES.md), [`METODOLOGIA.md`](../analysis/METODOLOGIA.md)

## Visão geral

Este documento descreve os campos principais das bases que alimentam o cálculo do IDS (Índice de Desenvolvimento de Saúde) e as quatro dimensões usadas para compor esse índice.

A quantidade de features é extensa, então o foco abaixo é dar contexto por dimensão com algumas colunas representativas.

---

## Dimensão 1: Infraestrutura

A dimensão de infraestrutura captura a capacidade física da rede de saúde em cada município. Ela reúne colunas relacionadas a estabelecimentos, hospitais e unidades de atendimento.

**Exemplos de colunas representativas:**

- `hospital_estadual`
- `hospital_federal`
- `hospital_municipal`
- `hospital_particular`
- `clinica_estadual`
- `clinica_federal`
- `clinica_municipal`
- `clinica_particular`
- `consultorio_total`
- `pronto_atendimento_total`
- `unidade_movel_total`

**Fontes principais:**

- `estabelecimentos_saude.csv`
- `inst_hospitalares_sp.csv`

**Observação:**
- A infraestrutura é calculada como densidade ponderada por população, usando pesos atribuídos a cada tipo de estabelecimento.

---

## Dimensão 2: Serviços

A dimensão de serviços mede a oferta de procedimentos de saúde e a capacidade de atendimento, incluindo exames, tratamentos e ações coletivas.

**Exemplos de colunas representativas:**

- `vigilancia em saude`
- `consultas / atendimentos / acompanhamentos`
- `diagnostico em vigilancia epidemiologica e ambiental`
- `diagnostico em laboratorio clinico`
- `coleta de material`
- `tratamentos clinicos (outras especialidades)`
- `diagnostico por ultrasonografia`
- `diagnostico por radiologia`
- `fisioterapia`
- `tratamentos odontologicos`
- `diagnostico por teste rapido`
- `terapias especializadas`
- `diagnostico por tomografia`
- `diagnostico por ressonancia magnetica`
- `pequenas cirurgias e cirurgias de pele, tecido subcutaneo e mucosa`

**Fontes principais:**

- `sia_cnv_qgsp.csv`
- `healthcare_final_latlon.csv`

**Observação:**
- A dimensão de serviços usa uma cobertura adaptativa que compara a oferta de serviços com uma meta baseada na necessidade do município e em referências da base inteira.

---

## Dimensão 3: Vulnerabilidade

A dimensão de vulnerabilidade considera o perfil social e econômico do município, a partir de indicadores de grupos de vulnerabilidade social.

**Exemplos de colunas representativas:**

- `baixissima vulnerabilidade_n_pessoas`
- `muito baixa vulnerabilidade_n_pessoas`
- `baixa vulnerabilidade_n_pessoas`
- `media vulnerabilidade_n_pessoas`
- `alta vulnerabilidade_n_pessoas`
- `muito alta vulnerabilidade_n_pessoas`

**Fontes principais:**

- `ipvs_esp.csv`

**Observação:**
- No cálculo do IDS, essa dimensão utiliza média ponderada por população e, em seguida, inverte o resultado para que maior vulnerabilidade social resulte em valor menor de desenvolvimento.

---

## Dimensão 4: Renda

A dimensão de renda representa a capacidade econômica do município e sua relação com a receita anual per capita.

**Coluna representativa:**

- `receita_anual`
- `população`

**Fontes principais:**

- `finbra_2022SP.csv`

**Observação:**
- O índice de renda é calculado como log da renda per capita e depois normalizado para reduzir o impacto de valores extremos.

---

## Campos-chave para integração

As chaves que permitem integrar as bases e construir a tabela final são:

- `cod_ibge`
- `municipio`

**Observação:**
- A base auxiliar `codigos_ibge_sp.csv` é usada para mapear `cod_ibge` em `municipio` e uniformizar as junções entre fontes.

---

## Estrutura dos dados no pipeline

O fluxo de dados segue estas camadas:

- `data/raw/`: arquivos originais brutos
- `data/clean/`: arquivos tratados e padronizados por fonte
- `data/processed/`: base consolidada e final usada para modelagem

---

## Notas finais

- Este dicionário apresenta uma visão de alto nível das dimensões do IDS e exemplos de colunas relevantes.
- A lista completa de features é extensa e pode ser consultada diretamente em `src/config/sources.yaml` e no conjunto final `data/processed/main_dataframe.csv`.