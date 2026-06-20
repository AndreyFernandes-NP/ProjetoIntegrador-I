# Fontes de Dados

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](../../data/README.md), [`docs/`](../README.md)
- **Visão geral**: [`README.md`](../README.md)
- **Planejamento**: [`CRONOGRAMA.md`](../project/CRONOGRAMA.md), [`ESCOPO.md`](../project/ESCOPO.md), [`OBJETIVOS.md`](../project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](TRATAMENTO_DE_DADOS.md)
- **Arquitetura & Pipeline**: [`ARQUITETURA.md`](../architecture/ARQUITETURA.md), [`PIPELINE.md`](../architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](../analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](../analysis/HIPOTESES.md), [`METODOLOGIA.md`](../analysis/METODOLOGIA.md)

## Visão geral

Este documento registra as principais fontes de dados usadas no projeto, descrevendo seu contexto, sua função no pipeline e o papel de cada base dentro das dimensões do IDS.

A partir do arquivo de configuração `src/config/sources.yaml`, o pipeline define quais bases serão transformadas, validadas e integradas ao dataset final. A seleção das fontes passa por critérios de disponibilidade pública, compatibilidade por município e utilidade para análise de saúde pública.

## Referências externas

- DATASUS: https://datasus.saude.gov.br/
- IBGE Saúde: https://www.ibge.gov.br/estatisticas/sociais/saude/9067-pesquisa-de-assistencia-medico-sanitaria.html
- Observa Sampa: https://observasampa.prefeitura.sp.gov.br/
- Seade Saúde Painel: https://repositorio.seade.gov.br/dataset/saude-painel
- Seade Municípios: https://repositorio.seade.gov.br/group/seade-municipios

---

## 1. Base de código municipal e geolocalização

**Fonte interna:** `codigos_ibge_sp.csv`

**Origem e contexto:**
- base de referência oficial usada para mapear `cod_ibge` em `municipio`
- apoia a padronização de nomes e chaves entre diferentes datasets
- utilizada para coordenadas geográficas e atributos administrativos de municípios paulistas

**Uso no pipeline:**
- transformações do tipo `mapa_ibge` em `sources.yaml`
- fonte principal para merge e validação geográfica entre bases
- mantém os campos `latitude` e `longitude` úteis para análises espaciais

**Papel no IDS:**
- fornece a chave de integração principal do dataset final
- oferece a base de municípios de São Paulo para o cálculo agregado

**Arquivos internos relacionados:**
- `codigos_ibge_sp.csv`

---

## 2. Estabelecimentos de saúde (CNES / DATASUS)

**Fonte oficial:**
- DATASUS/CNES — Cadastro Nacional de Estabelecimentos de Saúde
- portal de dados públicos do Ministério da Saúde

**Contexto:**
- o CNES é a principal base de equipamentos e unidades de saúde públicas e privadas no Brasil
- usada para entender infraestrutura de atendimento por município
- documentação e dados relacionados estão disponíveis no portal DATASUS

**Uso no projeto:**
- origem: `estabelecimentos_saude.csv`
- no `sources.yaml`, `tipo: purge` é aplicado ao campo `municipio`
- a coluna `tipo` é convertida em múltiplas colunas via pivot (`convert_to_column`)
- mantém contagens por classe de estabelecimento: estadual, federal, municipal, particular e total

**Colunas representativas:**
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

**Papel no IDS:**
- alimenta a dimensão de `infraestrutura`
- possui pesos definidos no YAML para refletir a importância relativa de cada tipo de estabelecimento

**Arquivos internos relacionados:**
- `estabelecimentos_saude.csv`

---

## 3. Instalações hospitalares em São Paulo

**Fonte oficial:**
- DATASUS / CNES

**Contexto:**
- apresenta a quantidade de instituições hospitalares por município
- extraída de dados do CNES em 2022, segmentada para São Paulo
- serve como indicador de capacidade instalada em saúde

**Uso no projeto:**
- origem: `inst_hospitalares_sp.csv`
- o campo `municipio` recebe limpeza de texto (`purge`)
- `quantidade` é convertido para `Int64` e renomeado para `Instituições Hospitalares`
- esta base não é incluída no merge final (`merge: false`) na configuração atual

**Papel no pipeline:**
- apoio analítico para entender a distribuição hospitalar local
- referência complementar de infraestrutura

**Arquivos internos relacionados:**
- `inst_hospitalares_sp.csv`

---

## 4. IPVS — vulnerabilidade social (Seade / IBGE)

**Fonte oficial:**
- IPVS / Fundação Seade
- contém indicadores sociais de vulnerabilidade no estado de São Paulo

**Contexto:**
- baseada em dados do Instituto Brasileiro de Geografia e Estatística (IBGE) e da Fundação Seade
- oferece recortes por grupo de vulnerabilidade social
- conectada ao repositório Seade e ao painel de saúde da organização

**Uso no projeto:**
- origem: `ipvs_esp.csv`
- `cod_ibge` é mapeado para `municipio` via `mapa_ibge`
- a dimensão `grupo_ipvs` é pivotada para criar colunas de `n_pessoas`, `n_domicilios` e `n_setores`
- `cols_obrigatorias`, `cols_unicas` e `cols_nao_nulas` são validadas no YAML

**Colunas representativas para o IDS:**
- `baixissima vulnerabilidade_n_pessoas`
- `muito baixa vulnerabilidade_n_pessoas`
- `baixa vulnerabilidade_n_pessoas`
- `media vulnerabilidade_n_pessoas`
- `alta vulnerabilidade_n_pessoas`
- `muito alta vulnerabilidade_n_pessoas`

**Papel no IDS:**
- alimenta a dimensão de `vulnerabilidade`
- os pesos refletem diferentes níveis de risco social e pobreza

**Arquivos internos relacionados:**
- `ipvs_esp.csv`

---

## 5. Rede de Atenção à Saúde / SIA (DATASUS)

**Fonte oficial:**
- DATASUS — Sistema de Informações Ambulatoriais (SIA)

**Contexto:**
- reúne procedimentos realizados em ambulatórios e unidades básicas de saúde
- indicada para medir volume e variedade de serviços de saúde ofertados
- dados agregados por município em 2022

**Uso no projeto:**
- origem: `sia_cnv_qgsp.csv`
- `Município gestor` é limpo e renomeado para `municipio`
- diversas colunas de procedimento são mantidas como úteis em `colunas_uteis`
- não há regras de qualidade explícitas listadas no YAML, mas os valores são usados diretamente no merge

**Colunas representativas:**
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
- `acoes coletivas / individuais em saude`

**Papel no IDS:**
- alimenta a dimensão de `serviços`
- o cálculo ajusta a cobertura de serviços com base na necessidade social do município

**Arquivos internos relacionados:**
- `sia_cnv_qgsp.csv`

---

## 6. Sistema de Informações Hospitalares — SIH (DATASUS)

**Fonte oficial:**
- DATASUS — Sistema de Informações Hospitalares (SIH)

**Contexto:**
- apresenta dados sobre internações hospitalares e procedimentos cirúrgicos
- útil para avaliar a capacidade de oferta hospitalar e procedimentos de maior complexidade

**Uso no projeto:**
- origem: `sih_cnv_spgsp.csv`
- `Município` é limpo e renomeado para `municipio`
- `Total` é convertido para `Int64`
- esta base possui muitas variáveis de procedimentos cirúrgicos e hospitalares que podem ser usadas em análise

**Papel no IDS:**
- contribui à dimensão de `serviços`
- os pesos de cada procedimento refletem sua importância relativa na oferta hospitalar

**Arquivos internos relacionados:**
- `sih_cnv_spgsp.csv`

---

## 7. Internações por tipo de serviço ou equipamento (Tabnet)

**Fonte oficial:**
- DATASUS / Tabnet — tabela de internações por município e tipo de serviço

**Contexto:**
- tabela30_SP_internacao apresenta volumetria de internações por serviço, setor público/privado e tipo de equipamento
- extraída do portal de planejamento e informações de saúde do DATASUS

**Uso no projeto:**
- origem: `tabela30_SP_internacao.csv`
- colunas como `Internação x tipo de Serviços ou Equipamentos` são limpas e convertidas para `Int64`
- atualmente, esta base não é incluída no merge final (`merge: false`)

**Papel no pipeline:**
- fonte de suporte para estudos exploratórios da estrutura de internações
- potencial insumo para expansão futura da dimensão de serviços

**Arquivos internos relacionados:**
- `tabela30_SP_internacao.csv`

---

## 8. Receita municipal e Finanças (Finbra)

**Fonte oficial:**
- Finbra 2022 — dados financeiros municipais do Estado de São Paulo

**Contexto:**
- base da Secretaria da Fazenda do Estado de São Paulo
- contém receita anual dos municípios e outros dados financeiros
- usada para ponderar a capacidade econômica na análise de desenvolvimento em saúde

**Uso no projeto:**
- origem: `finbra_2022SP.csv`
- `cod_ibge` é mapeado para `municipio`
- `valor` é convertido para `receita_anual`
- `receita_anual` é validada como numérica

**Papel no IDS:**
- alimenta a dimensão de `renda`
- é usada no cálculo de renda per capita como parte do índice final

**Arquivos internos relacionados:**
- `finbra_2022SP.csv`

---

## 9. Estabelecimentos geolocalizados

**Fonte interna/adicional:**
- `healthcare_final_latlon.csv`
- construído a partir de dados do CNES cruzados com geolocalização via QGIS e plugin MMQGIS

**Contexto:**
- tem coordenadas `latitude` e `longitude` para estabelecimentos de saúde
- fornece uma camada espacial para análise de localização de serviços

**Uso no projeto:**
- `latitude` e `longitude` são convertidos para `float64`
- esta base não é incluída no merge final (`merge: false`)

**Papel no pipeline:**
- suporte para análises espaciais e geográficas
- referência extra para visualizar distribuição de estabelecimentos

**Arquivos internos relacionados:**
- `healthcare_final_latlon.csv`

---

## Critérios de seleção das bases

As bases atualmente utilizadas foram escolhidas com base nos seguintes critérios:

- disponibilidade pública
- relevância para o problema do projeto
- possibilidade de comparação por município
- compatibilidade com outras fontes de dados
- potencial de uso em análise exploratória e modelagem supervisionada

## Limitações atuais

- as bases ainda não esgotam todas as dimensões do problema estudado
- parte dos indicadores ainda depende de novas fontes complementares
- algumas bases exigem padronização adicional de nomes, chaves e granularidade
- a variável final de modelagem ainda está em definição
