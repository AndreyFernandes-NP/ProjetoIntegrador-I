# Fontes de Dados

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](data/README.md), [`docs/`](docs/README.md)
- **Projeto**: [`CRONOGRAMA.md`](docs/project/CRONOGRAMA.md), [`ESCOPO.md`](docs/project/ESCOPO.md), [`OBJETIVOS.md`](docs/project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](docs/data/DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](docs/data/FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](docs/data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura**: [`ARQUITETURA.md`](docs/architecture/ARQUITETURA.md), [`PIPELINE.md`](docs/architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](docs/analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](docs/analysis/HIPOTESES.md), [`METODOLOGIA.md`](docs/analysis/METODOLOGIA.md)

## Visão geral

Este documento registra as fontes oficiais das bases utilizadas no projeto, bem como seu contexto de uso, recorte e função dentro da análise.

As bases atuais foram selecionadas por sua aderência ao objetivo do projeto, que busca investigar a relação entre vulnerabilidade social, infraestrutura urbana e pressão sobre os serviços públicos de saúde no estado de São Paulo.

---

## 1. Códigos de municípios do IBGE

**Fonte oficial:**  
IBGE — Tabela de Códigos dos Municípios / Divisão Territorial Brasileira

**Instituição responsável:**  
Instituto Brasileiro de Geografia e Estatística (IBGE)

**Recorte temporal:**  
Tabela oficial de códigos vigente no momento da coleta

**Recorte geográfico:**  
Municípios do estado de São Paulo

**Forma de obtenção:**  
Consulta e exportação da tabela oficial de códigos de municípios disponibilizada pelo IBGE

**Uso no projeto:**  
Esta base é utilizada como apoio para padronização e identificação dos municípios, permitindo compatibilizar diferentes bases por meio do código IBGE e do nome do município.

**Arquivos internos relacionados:**  
- `codigos_ibge_sp.csv`

**Observações:**  
A tabela de códigos de municípios do IBGE associa cada município brasileiro a um código oficial de 7 dígitos, sendo uma referência importante para integração entre bases.  
Também serve como apoio para evitar inconsistências em nomes de municípios e facilitar merges futuros.

---

## 2. Instalações hospitalares em São Paulo

**Fonte oficial:**  
DATASUS / CNES — Cadastro Nacional de Estabelecimentos de Saúde

**Instituição responsável:**  
Ministério da Saúde / DATASUS

**Recorte temporal:**  
2022

**Recorte geográfico:**  
Estado de São Paulo

**Forma de obtenção:**  
Extração de dados públicos do DATASUS com base nas informações do CNES

**Uso no projeto:**  
Esta base é utilizada para representar, de forma inicial, a distribuição de instalações hospitalares entre municípios paulistas, servindo como uma das referências para análise da capacidade estrutural de atendimento em saúde.

**Arquivos internos relacionados:**  
- `inst_hospitalares_sp-raw.csv`
- `inst_hospitalares_sp-clean.csv`

**Observações:**  
O CNES é a base oficial de cadastramento dos estabelecimentos de saúde do país, reunindo informações sobre capacidade instalada, serviços e recursos assistenciais.  
No projeto, a base passou por tratamento inicial para padronização do campo de município e conversão de valores quantitativos.

---

## 3. IPVS — Índice Paulista de Vulnerabilidade Social

**Fonte oficial:**  
IPVS / Fundação Seade

**Instituição responsável:**  
Fundação Seade

**Recorte temporal:**  
2022

**Recorte geográfico:**  
Estado de São Paulo

**Forma de obtenção:**  
Consulta e exportação de dados públicos disponibilizados pela plataforma oficial do IPVS

**Uso no projeto:**  
Esta base é utilizada para representar diferentes níveis de vulnerabilidade social nos municípios paulistas, permitindo relacionar características populacionais e territoriais com indicadores de infraestrutura e saúde.

**Arquivos internos relacionados:**  
- `ipvs_esp-raw.csv`
- `ipvs_esp-merge.csv`

**Observações:**  
O IPVS é um indicador voltado à identificação de áreas e grupos mais vulneráveis à pobreza no estado de São Paulo.  
No projeto, essa base foi integrada a uma tabela auxiliar de códigos IBGE para facilitar a padronização dos municípios e futuras junções com outras bases.

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

## Observações finais

Este documento deverá ser atualizado sempre que novas bases forem incorporadas ao projeto ou quando houver refinamento na forma de obtenção e uso dos dados.