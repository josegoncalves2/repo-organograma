# 🏛️ Organograma Municipal — Prefeitura de Olímpia

> **Visualização institucional completa** da Prefeitura Municipal de Olímpia, com 15 Secretarias, Gabinete do Prefeito, Controladoria Geral, Divisões, Setores e Colaboradores — tudo renderizado diretamente no navegador via Docker.

![Organograma Preview](https://raw.githubusercontent.com/bumbeishvili/org-chart/master/assets/preview.png)

---

## 📊 Estrutura do Organograma

- `Dockerfile` — imagem `nginx:1.27-alpine`, estática, sem build step
- `nginx.conf` — gzip, cache de assets (7d), fallback SPA, endpoint `/healthz`
- `docker-compose.yml` — serviço `orgchart`, porta `8080:80`, `restart: unless-stopped`
- `tree.html` — página do demo (copiada como `index.html` na imagem)
- `src/`, `build/`, `misc/` — código da lib, vendors e dados (`misc/data.csv`)

## Assets locais (imagem self-contained)

As fontes são servidas pelo próprio container, sem CDN externo:

- `build/fonts/inter-400.ttf` — Inter 400 (antes vinha de `fonts.gstatic.com`)
- `build/webfonts/fa-*.woff2|woff|ttf` — Font Awesome Free 5.15.4 (os `url()`
  do `build/fontawesome.min.css` foram reescritos de `../webfonts/` para `webfonts/`)

Ainda dependem de internet, apenas cosmeticamente: os avatares dos nós
(`https://bumbeishvili.github.io/avatars/...`, vindos do `data.csv` — há
`onerror` que os oculta) e a faixa "Fork me on GitHub".

## Designs

O seletor da toolbar traz os 7 designs publicados no repositório upstream
(seção *Jump To Examples* do README do `bumbeishvili/org-chart`), portados
literalmente dos exemplos no StackBlitz:

| # | Design | Fonte |
|---|--------|-------|
| 01 | Default | `tree.html` do próprio repositório |
| 02 | Sky | `web-platform-jyncb9` |
| 03 | Circles | `web-platform-lwyild` |
| 04 | Oval | `web-platform-uhd3q7` |
| 05 | Clean | `web-platform-3gwnsg` |
| 06 | Futuristic | `web-platform-o5t1ha` |
| 07 | Prev version design | `web-platform-thplyq` |

> O exemplo `web-platform-sgsxzp` ("Default" no *Jump To Examples*) só chama
> `.container().data().render()`, então cai no `nodeContent` padrão da lib —
> que em toda versão publicada (2.1 → 3.1.1) é apenas o placeholder
> "Sample Node(id=…), override using…". O card real do `Default` é o que está
> no `tree.html` do repositório, comentado logo abaixo da configuração ativa
> (`nodeHeight 85+25`, `nodeWidth 220+2`, override de `layoutBindings`);
> é esse bloco que o slot 01 usa, descomentado.

Adaptações necessárias, documentadas em comentário no `tree.html`:

- os exemplos leem `sample-data/main/org.csv`; aqui as colunas do
  `misc/data.csv` são mapeadas para os nomes esperados
  (`imageUrl`, `positionName`, `area`, `office`);
- `neightbourMargin` (typo do setter na v2 da lib) virou `neighbourMargin`,
  o nome correto na v3 que está em `src/`;
- `svgHeight` vem da altura do container da página, não de `window.innerHeight`;
- em `Sky`, `Circles` e `Oval` o nome/cargo ganharam `nowrap` + reticências:
  os exemplos usam cargos curtos ("CTO") e os cargos deste CSV quebram em
  duas linhas — no `Circles` e no `Oval` vazavam para fora da faixa (28px) e
  do pill (70px); no `Sky` empurravam o rodapé *Manages/Oversees* contra a
  borda inferior, deixando cards do mesmo design com espaçamentos diferentes
  (14px de folga em 103 cards contra 1px em 4).

O `Futuristic` depende do `PieChart` do próprio exemplo, versionado em
`build/vendor/pieChart.js`.

## Uso

```bash
# dentro do WSL, na raiz do projeto
cd /mnt/c/Users/40446686808/projetos/organograma

docker compose up -d --build   # subir / rebuildar
docker compose ps              # status + health
docker compose logs -f orgchart
docker compose down            # parar e remover
```

## Acesso

- App: http://localhost:8080
- Health: http://localhost:8080/healthz → `ok`

## Carregar CSV ou JSON

Na aplicação, use **Carregar CSV** (aceita `.csv` ou `.json`) ou arraste o
arquivo para a tela. O arquivo precisa ter pelo menos `id` e `name`. Um modelo
deve ser baixado pelo botão **Modelo**.

Formato CSV (inclui coluna `email`):

```csv
id,parentId,name,lastName,position,email,department_name,location_state,image
1,,Maria,Silva,Diretora,maria.silva@empresa.com,Diretoria,SP,
2,1,João,Santos,Gerente,joao.santos@empresa.com,Engenharia,SP,
```

Formato JSON: lista de objetos ou `{ "nodes": [...] }` com a mesma estrutura.

## Exportar

- **Exportar CSV** baixa o organograma atual com as colunas `id`, `parentId`,
  `name`, `lastName`, `position`, `email`, `department_name`, `location_state`,
  `image`.
- **Exportar JSON** baixa o organograma atual como array JSON.

## Editar

- **Add Node** cria um novo nó sob a raiz.
- **Remove** remove o último nó adicionado (ou uma folha da árvore).

Cada nó renderizado mostra o e-mail em um selo no canto inferior direito.
# repo-organograma
# repo-organograma
