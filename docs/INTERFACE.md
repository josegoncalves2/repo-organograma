# Interface e fluxos de uso

## Barra lateral

A Tree View mostra a hierarquia completa e permite:

- selecionar card;
- centralizar no organograma;
- editar;
- adicionar subordinado;
- remover ramo;
- abrir a visualizacao a partir de um no.

A largura da sidebar pode ser ajustada arrastando a borda direita.

## Modo claro/escuro

O botao `Dark` / `Light` alterna o tema global da aplicacao.

O modo escolhido fica salvo no navegador.

## Seletor "Ver a partir de"

Permite desenhar somente um ramo do organograma.

Para evitar ruido:

- remove escopos genericos repetidos;
- desambigua nomes repetidos com o ancestral institucional;
- mantem Secretarias, Controladoria, Gabinete, Divisoes e Setores com nome real.

## Edicao

Formas de editar:

- duplo clique no card;
- botao `Editar` na toolbar;
- icone de editar na Tree View.

Campos editaveis:

- foto;
- nome;
- sobrenome;
- cargo/nome da unidade;
- tipo;
- e-mail;
- departamento;
- pai hierarquico.

## Criacao

Selecione uma unidade e clique em `Add Node`.

Colaborador nao pode receber subordinados.

## Remocao

Ao remover um card, todos os subordinados do ramo tambem sao removidos.

A raiz nao pode ser removida.

## Visualizacao

Controles principais:

- `Fit`: ajusta a visao.
- `Full`: tela cheia.
- `Layout`: alterna orientacao.
- `Expand All`: expande tudo.
- `Collapse All`: recolhe tudo.
- `Center`: centraliza no card selecionado.
- `Highlight`: destaca card.
- `To Root`: destaca caminho ate a raiz.
- `Clear`: limpa destaques.
- `Undo`: desfaz a ultima alteracao local.

## Visualizacao publica

Em `/view/`, as acoes da arvore ficam juntas numa barra acima da busca da arvore lateral, e agem no item selecionado (clique no item da arvore ou no card):

- `Expandir`: abre o item e todos os niveis abaixo dele, ate o ultimo.
- `Recolher`: fecha todos os niveis abaixo do item; o item continua visivel.
- `Ver daqui`: desenha o organograma a partir do item.
- `Centralizar`: centraliza o item no organograma.

Sem item selecionado, `Expandir` e `Recolher` agem sobre o organograma exibido inteiro (o completo ou o ramo aberto em `Ver daqui`) e os outros dois ficam desabilitados. Item sem subordinados so pode ser centralizado. A arvore lateral acompanha o grafico.

Nas linhas da arvore da visualizacao publica nao ha botoes; no administrativo as linhas continuam com os botoes de cada item.

