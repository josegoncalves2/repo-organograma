# Dados e hierarquia

## Campos

Cada registro do organograma usa:

```text
id,parentId,name,lastName,position,type,email,department_name,location_state,image
```

## Significado dos campos

- `id`: identificador unico.
- `parentId`: id do pai hierarquico. Vazio apenas na raiz.
- `name`: primeiro nome da pessoa. Vazio para unidade.
- `lastName`: sobrenome da pessoa. Vazio para unidade.
- `position`: cargo da pessoa ou nome da unidade.
- `type`: classe do card.
- `email`: e-mail do colaborador ou da unidade, quando houver.
- `department_name`: secretaria/orgao de referencia.
- `location_state`: UF ou localidade.
- `image`: URL, caminho local ou caminho de foto enviada.

## Tipos aceitos

```text
PREFEITURA
SECRETARIA
GABINETE
CONTROLADORIA
COORDENADORIA
ASSESSOR
FUNDO
CHEFE
CONSELHO
GUARDA
COMISSIONADOS
DIVISAO
FUNDEB
CORPO
SETOR
COLABORADOR
```

`UNIDADE` e `ORGAO` sao aceitos como genericos pelo servidor.

## Unidade nao e colaborador

Unidades institucionais sao caixas estruturais. Colaborador e pessoa.

Exemplo:

```text
SECRETARIA MUNICIPAL DE SAUDE
  gestor: Secretario Nome Sobrenome
  Divisao Administrativa
    gestor: Diretor Nome Sobrenome
```

O gestor pode existir como linha separada nos dados, mas na visualizacao institucional aparece dentro do card da unidade quando identificado como responsavel direto.

## Regra de gestor embutido

Uma pessoa direta abaixo de uma unidade vira gestor embutido quando:

- e o unico colaborador direto da unidade; ou
- o cargo corresponde ao papel esperado daquela unidade.

Mapeamento padrao:

```text
SECRETARIA      -> Secretario
CONTROLADORIA   -> Controlador
GABINETE        -> Gestor
DIVISAO         -> Diretor
SETOR           -> Chefe
ASSESSOR        -> Assessor Executivo
COORDENADORIA   -> Coordenador
FUNDO           -> Gestor
CHEFE           -> Chefe
CONSELHO        -> Presidente
GUARDA          -> Comandante
FUNDEB          -> Gestor
CORPO           -> Comandante
```

`PREFEITURA`, `COLABORADOR` e `COMISSIONADOS` nao usam gestor embutido.

## Seletor de escopo

O seletor "Ver a partir de" nao lista opcoes genericas sem contexto, como:

```text
COORDENADORIA
ASSESSOR EXECUTIVO
CHEFE
COMISSIONADOS
```

Quando existem nomes repetidos, o seletor adiciona o ancestral institucional:

```text
Divisao Administrativa - SECRETARIA MUNICIPAL DE SAUDE
Divisao Administrativa - GABINETE DO PREFEITO
```

