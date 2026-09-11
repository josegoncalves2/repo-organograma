# Importacao e exportacao

## Modelos

Modelos disponiveis na interface:

```text
misc/modelo-organograma.csv
misc/modelo-organograma.json
```

## Importacao

Use `Carregar CSV + fotos`.

Formatos aceitos:

- CSV;
- JSON;
- imagens junto com o arquivo de dados.

O CSV pode usar:

- virgula;
- ponto e virgula;
- tab.

O JSON pode ser:

```json
[
  {"id":"1","parentId":"","position":"PREFEITURA","type":"PREFEITURA"}
]
```

ou:

```json
{
  "nodes": []
}
```

## Fotos

Fotos podem ser enviadas:

- individualmente pelo editor;
- em lote junto com o CSV/JSON.

Correspondencia em lote:

1. pelo `id`;
2. pelo login do e-mail;
3. pelo nome completo.

Fotos enviadas ficam em:

```text
/dados/fotos/<id>.jpg
```

## Exportacao de dados

Exporta todo o organograma:

- `Exportar CSV`
- `Exportar JSON`

Exporta parte do organograma:

- `CSV Parte`
- `JSON Parte`

Regra da exportacao parcial:

1. se houver card selecionado, exporta a subarvore dele;
2. se nao houver card selecionado, usa o escopo atual;
3. se nao houver escopo, exporta tudo.

Na exportacao parcial, o no raiz da parte exportada recebe `parentId` vazio.

## Exportacao visual

Formatos:

- PNG;
- PNG Full;
- SVG;
- PDF.

`PNG Full` exporta o grafo inteiro, nao apenas o que esta visivel na tela.

