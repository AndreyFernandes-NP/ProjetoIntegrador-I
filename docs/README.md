# Documentação do Projeto

Esta pasta reúne a documentação técnica e organizacional do **Projeto Integrador I**, centralizando definições, decisões e descrições importantes sobre o desenvolvimento do trabalho.

O objetivo desta estrutura é facilitar a navegação, manter o projeto organizado e registrar, de forma clara, as principais informações relacionadas ao escopo, dados, análise e arquitetura.

## Estrutura da pasta `docs`

```text
docs/
├── analysis/
├── architecture/
├── data/
├── project/
└── README.md
```

## Organização da documentação

`analysis/`
Contém os documentos relacionados à abordagem analítica e metodológica do projeto.

Arquivos esperandos nessa pasta:

- `ABORDAGEM_ANALITICA.md` — descreve como os dados serão analisados e como a modelagem será conduzida
- `HIPOTESES.md` — registra a hipótese principal e hipóteses secundárias da análise
- `METODOLOGIA.md` — apresenta a metodologia geral adotada no desenvolvimento do trabalho

`architecture/`
Documenta a organização técnica do projeto e o fluxo de trabalho dos dados.

Arquivos esperados nessa pasta:

- `ARQUITETURA.md` — descreve as ferramentas, ambientes e a estrutura geral do projeto
- `PIPELINE.md` — apresenta o fluxo do projeto, desde a obtenção dos dados até a análise e documentação dos resultados

`data/`
Reúne a documentação relacionada às bases de dados utilizadas no projeto.

Arquivos esperados nessa pasta:

- `DICIONARIO_DE_DADOS.md` — explica os principais campos e variáveis das bases utilizadas
- `FONTES_DE_DADOS.md` — descreve a origem oficial das bases, instituições responsáveis, recortes e forma de uso no projeto
- `TRATAMENTO_DE_DADOS.md` — registra os tratamentos, padronizações e transformações aplicadas aos dados

`project/`
Contém os documentos voltados à definição e ao planejamento geral do projeto.

Arquivos esperados nessa pasta:

- `CRONOGRAMA.md` — organiza as principais etapas do projeto ao longo do semestre
- `ESCOPO.md` — delimita o problema, o recorte adotado, o que está dentro e fora do escopo e a hipótese inicial
- `OBJETIVOS.md` — registra o objetivo geral, os objetivos específicos e o resultado esperado

## Finalidade da documentação

A documentação tem como principais objetivos:

- registrar decisões importantes do projeto
- tornar a estrutura do trabalho mais clara
- facilitar manutenção e evolução do repositório
- apoiar a comunicação entre os membros do grupo
- fornecer uma visão organizada do projeto para fins acadêmicos

## Mapa de Documentação do Repositório

- **Pastas**: [`data/`](../data/README.md), [`docs/`](README.md)
- **Planejamento**: [`CRONOGRAMA.md`](project/CRONOGRAMA.md), [`ESCOPO.md`](project/ESCOPO.md), [`OBJETIVOS.md`](project/OBJETIVOS.md)
- **Dados**: [`DICIONARIO_DE_DADOS.md`](data/DICIONARIO_DE_DADOS.md), [`FONTES_DE_DADOS.md`](data/FONTES_DE_DADOS.md), [`TRATAMENTO_DE_DADOS.md`](data/TRATAMENTO_DE_DADOS.md)
- **Arquitetura & Pipeline**: [`ARQUITETURA.md`](architecture/ARQUITETURA.md), [`PIPELINE.md`](architecture/PIPELINE.md)
- **Análise**: [`ABORDAGEM_ANALITICA.md`](analysis/ABORDAGEM_ANALITICA.md), [`HIPOTESES.md`](analysis/HIPOTESES.md), [`METODOLOGIA.md`](analysis/METODOLOGIA.md)
