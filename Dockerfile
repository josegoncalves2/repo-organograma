# Organograma — página estática + API que grava os dados num arquivo JSON.
# Node puro, sem dependências: não há package.json nem npm install.
FROM node:22-alpine

LABEL maintainer="organograma" \
   description="Organograma editável, com persistência em arquivo JSON" \
   source="https://github.com/bumbeishvili/org-chart"

WORKDIR /app

COPY server.js ./
COPY tree.html ./
COPY index.js ./
COPY src/ ./src/
COPY build/ ./build/
COPY misc/ ./misc/
COPY sidebar/ ./sidebar/
COPY view/ ./view/
COPY dados/ ./dados/

# Volume: é aqui que organograma.json sobrevive a rebuilds do container.
ENV DADOS_DIR=/dados
# Explícito de propósito: EXPOSE, healthcheck, o mapeamento do compose e o
# label do traefik falam todos em 80. Deixar a porta no default do server.js
# fazia o container escutar noutra porta e nunca ficar healthy.
ENV PORT=80
RUN mkdir -p /dados && chown -R node:node /dados /app
VOLUME ["/dados"]

USER node
EXPOSE 80

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
   CMD wget --quiet --tries=1 --spider http://localhost/api/saude || exit 1

CMD ["node", "server.js"]
