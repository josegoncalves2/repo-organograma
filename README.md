<div align="center">

# Organograma Municipal

Aplicacao web para visualizar, editar, importar e exportar o organograma institucional da Prefeitura de Olimpia.

[![Node.js](https://img.shields.io/badge/Node.js-22-5FA04E?style=for-the-badge&logo=nodedotjs&logoColor=white)](https://nodejs.org)
[![JavaScript](https://img.shields.io/badge/JavaScript-vanilla-F7DF1E?style=for-the-badge&logo=javascript&logoColor=black)](https://developer.mozilla.org/docs/Web/JavaScript)
[![D3.js](https://img.shields.io/badge/D3.js-7.9-F9A03C?style=for-the-badge&logo=d3&logoColor=white)](https://d3js.org)
[![d3-org-chart](https://img.shields.io/badge/d3--org--chart-bumbeishvili-2F6DB5?style=for-the-badge&logo=github&logoColor=white)](https://github.com/bumbeishvili/org-chart)
<br>
[![Docker Compose](https://img.shields.io/badge/Docker-Compose-2496ED?style=for-the-badge&logo=docker&logoColor=white)](https://docs.docker.com/compose/)
[![WSL 2](https://img.shields.io/badge/WSL-2-0078D4?style=for-the-badge&logo=linux&logoColor=white)](https://learn.microsoft.com/windows/wsl/)
[![Dependencias npm](https://img.shields.io/badge/depend%C3%AAncias%20npm-0-2EA44F?style=for-the-badge&logo=npm&logoColor=white)](server.js)
[![Idioma](https://img.shields.io/badge/idioma-pt--BR-009C3B?style=for-the-badge)](#)
[![Ultimo commit](https://img.shields.io/github/last-commit/josegoncalves2/repo-organograma?style=for-the-badge&logo=github&label=%C3%BAltimo%20commit)](https://github.com/josegoncalves2/repo-organograma/commits/main)

<br>

<picture>
  <source media="(prefers-color-scheme: dark)" srcset="docs/screenshots/organograma-escuro.png">
  <img alt="Tela administrativa: arvore completa a esquerda e o Gabinete do Prefeito expandido no organograma" src="docs/screenshots/organograma-claro.png">
</picture>

</div>

O projeto roda em Docker via WSL, usando Node.js puro no servidor e uma pagina HTML/JS no navegador. Os dados editados ficam persistidos em volume Docker.

## Telas

### Visualizacao publica

Tela somente leitura em `/view/`, para exibir o organograma sem risco de edicao. As acoes ficam juntas acima da busca da arvore e agem no item selecionado: expandir ate o ultimo nivel, recolher, ver o organograma a partir dele e centralizar.

<img alt="Visualizacao publica com a Secretaria Municipal de Turismo expandida" src="docs/screenshots/visualizacao-publica.png">

### Modo claro e modo escuro

<table>
  <tr>
    <td width="50%"><img alt="Tela administrativa no modo claro" src="docs/screenshots/organograma-claro.png"></td>
    <td width="50%"><img alt="Tela administrativa no modo escuro" src="docs/screenshots/organograma-escuro.png"></td>
  </tr>
</table>

### Edicao de cards e cores por tipo

<table>
  <tr>
    <td width="50%"><img alt="Editor de card com foto, titular, cargo, tipo e responsavel" src="docs/screenshots/editor.png"></td>
    <td width="50%"><img alt="Tabela de cores de fundo, borda, texto e selo de cada tipo de unidade" src="docs/screenshots/cores.png"></td>
  </tr>
  <tr>
    <td align="center">Duplo clique no card abre o editor</td>
    <td align="center">Cores de cada tipo, validas para todos os designs</td>
  </tr>
</table>

### Designs

O mesmo organograma (Controladoria Geral do Municipio) em alguns dos designs do seletor.

<table>
  <tr>
    <td width="50%"><img alt="Design Sky" src="docs/screenshots/design-sky.png"></td>
    <td width="50%"><img alt="Design Oval" src="docs/screenshots/design-oval.png"></td>
  </tr>
  <tr>
    <td align="center">Sky</td>
    <td align="center">Oval</td>
  </tr>
  <tr>
    <td width="50%"><img alt="Design Futuristic" src="docs/screenshots/design-futuristic.png"></td>
    <td width="50%"><img alt="Design Prev version" src="docs/screenshots/design-previous.png"></td>
  </tr>
  <tr>
    <td align="center">Futuristic</td>
    <td align="center">Prev version</td>
  </tr>
</table>

## Acesso

Na maquina atual, o servico esta configurado para WSL com rede espelhada e porta `8085`:

```text
http://192.168.0.218:8085
```

Localmente tambem funciona em:

```text
http://localhost:8085
```

## Subir pelo WSL

```bash
cd /mnt/c/Users/40446686808/projetos/organograma
docker compose up -d --build
docker compose ps
```

Teste de saude:

```bash
curl -fsS http://192.168.0.218:8085/api/saude
```

Resposta esperada:

```json
{"ok":true}
```

## Funcionalidades

- Visualizacao do organograma completo ou a partir de um ramo.
- Sidebar/Tree View hierarquica, redimensionavel e responsiva.
- Modo claro/escuro.
- Seletor de escopo com rotulos repetidos desambiguados pelo orgao ancestral.
- Edicao de card por duplo clique.
- Criacao, edicao e remocao de cards pela toolbar e pela sidebar.
- Upload individual e em lote de fotos.
- Campo de e-mail e foto por card.
- Exportacao completa ou parcial em CSV e JSON.
- Exportacao visual em PNG, PNG completo, SVG e PDF.
- Modelos de importacao em CSV e JSON.
- Persistencia automatica no servidor.

## Regras de modelagem

Unidade institucional e colaborador nao sao a mesma coisa.

- `SECRETARIA`, `CONTROLADORIA`, `GABINETE`, `DIVISAO`, `SETOR`, `COORDENADORIA`, `ASSESSOR`, `FUNDO`, `CHEFE`, `CONSELHO`, `GUARDA`, `CORPO`, `FUNDEB` e `COMISSIONADOS` sao unidades ou grupos institucionais.
- `COLABORADOR` e pessoa.
- O gestor direto de uma unidade aparece dentro do card da unidade quando a regra identifica que ele ocupa aquela unidade.
- Pessoas de `COMISSIONADOS` continuam como cards separados, pois ali sao lista/grupo de colaboradores.

## Dados

Arquivo persistente em runtime:

```text
/dados/organograma.json
```

Arquivo inicial embutido na imagem:

```text
dados/organograma.json
```

Colunas/campos:

```text
id,parentId,name,lastName,position,type,email,department_name,location_state,image
```

Modelos de importacao:

```text
misc/modelo-organograma.csv
misc/modelo-organograma.json
```

## Documentacao

- [Arquitetura](docs/ARQUITETURA.md)
- [Operacao com Docker e WSL](docs/OPERACAO-WSL.md)
- [Dados, tipos e gestores](docs/DADOS-E-HIERARQUIA.md)
- [Interface e fluxos de uso](docs/INTERFACE.md)
- [Importacao e exportacao](docs/IMPORTACAO-EXPORTACAO.md)
- [Troubleshooting](docs/TROUBLESHOOTING.md)

## Estrutura principal

```text
tree.html                 Interface principal
server.js                 Servidor HTTP e API de persistencia
docker-compose.yml        Compose para WSL host network na porta 8085
Dockerfile                Imagem Node.js
dados/organograma.json    Dados iniciais
misc/                     CSVs, modelos, favicon e materiais auxiliares
sidebar/                  Tree View em iframe
build/                    CSS e bibliotecas JS vendorizadas
src/                      Fonte da lib d3-org-chart
scripts/                  Scripts auxiliares
docs/                     Documentacao do projeto
```

## Comandos uteis

```bash
# Rebuild e subida
docker compose up -d --build

# Ver estado
docker compose ps

# Logs
docker compose logs --tail=100 orgchart

# Derrubar
docker compose down
```

