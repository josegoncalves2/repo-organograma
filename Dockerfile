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
ENV DOCKER=1
# O serviço escuta apenas dentro do namespace do container; a exposição para o
# host fica restrita ao mapeamento do Docker Compose, sem host networking.
ENV HOST=0.0.0.0
# A aplicação atende em 8085 e o compose mapeia essa porta para o host.
ENV PORT=8085
RUN mkdir -p /dados && chown -R node:node /dados /app
VOLUME ["/dados"]

USER node
EXPOSE 8085

HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
   CMD wget --quiet --tries=1 --spider http://localhost:8085/api/saude || exit 1

CMD ["node", "server.js"]
