# Arquitetura do Projeto

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](data/README.md), [`docs/`](docs/README.md)
- **Projeto**: [`CRONOGRAMA.md`](docs/project/CRONOGRAMA.md), [`ESCOPO.md`](docs/project/ESCOPO.md), [`OBJETIVOS.md`](docs/project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](docs/data/DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](docs/data/FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](docs/data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura**: [`ARQUITETURA.md`](docs/architecture/ARQUITETURA.md), [`PIPELINE.md`](docs/architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](docs/analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](docs/analysis/HIPOTESES.md), [`METODOLOGIA.md`](docs/analysis/METODOLOGIA.md)

## Visão geral

A arquitetura do projeto foi definida de forma simples e compatível com o escopo acadêmico da proposta, priorizando organização, reprodutibilidade e facilidade de evolução ao longo do semestre.

O projeto combina desenvolvimento local, versionamento no GitHub, acompanhamento das tarefas no GitHub Projects e uso de ambientes de análise interativos, como Jupyter Notebook e Google Colab, para exploração, testes e preparação de modelos.

## Estrutura geral

A arquitetura atual do projeto está organizada em quatro frentes principais:

- versionamento e gerenciamento do projeto
- armazenamento e preparação de dados
- análise e experimentação
- documentação técnica e acadêmica

## Ferramentas e ambientes utilizados

### GitHub

O GitHub é utilizado como plataforma principal de versionamento do código, armazenamento da documentação e centralização do repositório do projeto.

Seu uso permite:

- manter histórico de alterações
- organizar a evolução do código e dos documentos
- registrar tarefas por meio de issues e pull requests
- centralizar a base do projeto em um único ambiente

### GitHub Projects

O GitHub Projects é utilizado como ferramenta de organização das atividades do grupo, permitindo acompanhar o andamento das tarefas ao longo do semestre.

Seu uso atual está voltado para:

- controle de backlog
- priorização de tarefas
- acompanhamento do desenvolvimento
- apoio à organização do cronograma do grupo

### Desenvolvimento local

O desenvolvimento local é utilizado para:

- tratamento inicial das bases
- construção e execução de scripts Python
- organização do projeto em pastas
- validação das transformações de dados
- testes de integração entre arquivos e estruturas

Esse ambiente representa a base principal de construção do projeto.

### Jupyter Notebook

O Jupyter Notebook será utilizado principalmente para:

- análise exploratória dos dados
- visualização de distribuições e correlações
- testes analíticos iniciais
- experimentação com variáveis e abordagens de modelagem

Seu uso favorece iteração rápida e documentação mais clara do processo analítico.

### Google Colab

O Google Colab será utilizado como ambiente complementar para:

- testes rápidos de análise e modelagem
- execução de notebooks sem dependência do ambiente local
- experimentos com treinamento, ajuste e validação de modelos
- exploração inicial de abordagens mais pesadas, quando necessário

O uso do Colab será principalmente de apoio, sem substituir a organização central do projeto no repositório local.

## Organização do repositório

A estrutura atual do repositório está organizada da seguinte forma:

```text
ProjetoIntegrador-I/
├── data/
|   ├── clean/
|   |   ├── inst_hospitalares_sp-clean.csv
|   |   └── ipvs_esp-merge.csv
|   ├── processed/
|   ├── raw/
|   |   ├── codigos_ibge_sp.csv
|   |   ├── inst_hospitalares_sp-raw.csv
|   |   └── ipvs_esp-raw.csv
|   └── data_cleaner+merger.py
├── docs/
|   ├── analysis/
|   |   ├── ABORDAGEM_ANALITICA.md
|   |   ├── HIPOTESES.md
|   |   └── METODOLOGIA.md
|   ├── architecture/
|   |   ├── ARQUITETURA.md
|   |   └── PIPELINE.md
|   ├── data/
|   |   ├── DICIONARIO_DE_DADOS.md
|   |   ├── FONTES_DE_DADOS.md
|   |   └── TRATAMENTO_DE_DADOS.md
|   └── project/
|       ├── CRONOGRAMA.md
|       ├── ESCOPO.md
|       └── OBJETIVOS.md
├── notebooks/
├── src/
├── requirements.txt
└── README.md
```

## Papéis da estrutura

`data/`
Armazena as bases utilizadas no projeto, incluindo arquivos brutos, dados limpos e dados processados.

`docs/`
Armazena as bases utilizadas no projeto, incluindo arquivos brutos, dados limpos e dados processados.

`notebooks/`
Reúne a documentação do projeto, cobrindo escopo, dados, metodologia, arquitetura e demais definições relevantes.

`src/`
Espaço destinado a notebooks de análise exploratória, testes estatísticos e experimentos de modelagem.

## Diretrizes da arquitetura
A arquitetura do projeto segue algumas diretrizes principais:

- manter o repositório como fonte central de organização
- separar dados brutos de dados tratados
- documentar as principais decisões técnicas
- permitir experimentação sem comprometer a base principal do projeto
- favorecer evolução gradual da estrutura, sem complexidade excessiva

## Limitações atuais
A arquitetura ainda está em estágio inicial e poderá ser refinada ao longo do desenvolvimento, principalmente em relação a:

- organização definitiva dos scripts
- padronização do uso entre notebooks e código em `src/`
- definição mais clara do fluxo de modelagem
- consolidação dos artefatos finais de análise

# Observações
Esta arquitetura foi planejada para ser suficiente ao projeto acadêmico atual, sem adoção de ferramentas ou camadas desnecessariamente complexas para o estágio do trabalho.