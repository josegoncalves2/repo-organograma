# Arquitetura

## Visao geral

O projeto e uma aplicacao web autocontida:

- `server.js` serve arquivos estaticos e expoe uma API HTTP simples.
- `tree.html` contem a interface principal e a logica de manipulacao do organograma.
- `sidebar/sidebar.html` roda dentro de um iframe e exibe a Tree View hierarquica.
- `build/` contem CSS e dependencias JS locais.
- `dados/organograma.json` e a carga inicial embutida na imagem Docker.
- `/dados/organograma.json` e o arquivo persistente dentro do volume Docker.

Nao ha banco de dados. A persistencia e feita por arquivo JSON.

## API

### `GET /api/saude`

Retorna:

```json
{"ok":true}
```

### `GET /api/organograma`

Retorna os dados atuais do volume. Se o volume ainda estiver vazio, o servidor usa a carga inicial embutida em `dados/organograma.json`.

### `PUT /api/organograma`

Grava o organograma no volume. Antes de gravar, valida:

- lista nao vazia;
- ids unicos;
- exatamente uma raiz;
- `parentId` existente;
- ausencia de ciclos;
- colaborador sem filhos;
- tipo valido quando informado.

### `DELETE /api/organograma`

Remove o arquivo persistido do volume. Na proxima leitura, volta a carga inicial embutida.

### `PUT /api/fotos/:id`

Grava foto em `/dados/fotos/<id>.jpg`.

### `DELETE /api/fotos/:id`

Remove foto do volume.

## Renderizacao

A renderizacao usa `d3-org-chart`. O app prepara cada linha antes de entregar ao grafico:

- classifica o tipo;
- calcula rotulos e cores;
- embute gestor no card da unidade quando aplicavel;
- filtra colaboradores absorvidos como gestores para nao aparecerem como cards paralelos;
- recorta a subarvore quando o usuario escolhe um escopo.

## Sidebar

A sidebar recebe dados da pagina principal via chamada direta ao iframe:

```js
iframe.contentWindow.setSidebarData(...)
```

A sidebar chama a pagina principal com:

```js
window.parent.selectNode(...)
window.parent.abrirEditor(...)
window.parent.addSampleNode(...)
window.parent.removeSampleNode(...)
window.parent.aplicarEscopo(...)
```

## Persistencia visual

Preferencias do usuario ficam em `localStorage`, incluindo:

- tema visual do card;
- layout;
- nos expandidos;
- card selecionado;
- escopo atual;
- modo claro/escuro;
- largura da sidebar.

