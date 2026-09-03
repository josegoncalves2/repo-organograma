# Organograma — bumbeishvili/org-chart em Docker (WSL)

Demo do projeto [bumbeishvili/org-chart](https://github.com/bumbeishvili/org-chart)
servida por Nginx em um container Docker rodando no WSL (Ubuntu).

## Estrutura

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

## Carregar um CSV

Na aplicação, use **Carregar CSV** para selecionar um arquivo ou arraste o CSV
para a tela. O arquivo precisa ter pelo menos estas colunas:

```csv
id,parentId,name,lastName,position,department_name,image
1,,Diretoria,Executiva,CEO,Empresa,
2,1,João,Silva,Analista,TI,
```

`id` identifica o funcionário, `parentId` liga o funcionário ao gestor e as
demais colunas alimentam o card. O CSV é processado no navegador e não é
enviado para nenhum servidor.
# repo-organograma
