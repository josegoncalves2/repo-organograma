# Dockerfile - bumbeishvili/org-chart demo
# Imagem leve baseada em Nginx para servir a página estática (tree.html)
FROM nginx:1.27-alpine

# Metadados
LABEL maintainer="organograma" \
   description="Demo do bumbeishvili/org-chart servido via Nginx" \
   source="https://github.com/bumbeishvili/org-chart"

# Remove a página default do Nginx
RUN rm -rf /usr/share/nginx/html/*

# Copia a árvore do projeto (HTML + JS + assets)
COPY tree.html /usr/share/nginx/html/index.html
COPY index.js /usr/share/nginx/html/
COPY src/ /usr/share/nginx/html/src/
COPY build/ /usr/share/nginx/html/build/
COPY misc/ /usr/share/nginx/html/misc/

# Configuração customizada do Nginx (SPA friendly, cache de assets)
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
   CMD wget --quiet --tries=1 --spider http://localhost/ || exit 1

CMD ["nginx", "-g", "daemon off;"]