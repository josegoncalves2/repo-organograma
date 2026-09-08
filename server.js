"use strict";

// Servidor mínimo do organograma: serve a página e guarda os dados num único
// arquivo JSON em disco. Sem dependências e sem banco — o volume do container
// é a persistência.

const http = require("http");
const fs = require("fs");
const fsp = require("fs/promises");
const path = require("path");
const crypto = require("crypto");

const RAIZ = __dirname;
const DIR_DADOS = process.env.DADOS_DIR || "/dados";
const ARQUIVO = path.join(DIR_DADOS, "organograma.json");
const ANTERIOR = path.join(DIR_DADOS, "organograma.anterior.json");
const PORTA = Number(process.env.PORT || 80);
const LIMITE_BYTES = 25 * 1024 * 1024;

const TIPOS = {
  ".html": "text/html; charset=utf-8",
  ".js": "application/javascript; charset=utf-8",
  ".css": "text/css; charset=utf-8",
  ".csv": "text/csv; charset=utf-8",
  ".json": "application/json; charset=utf-8",
  ".svg": "image/svg+xml",
  ".png": "image/png",
  ".jpg": "image/jpeg",
  ".ico": "image/x-icon",
  ".woff": "font/woff",
  ".woff2": "font/woff2",
  ".ttf": "font/ttf"
};

function json(res, status, corpo) {
  const texto = JSON.stringify(corpo);
  res.writeHead(status, {
    "Content-Type": "application/json; charset=utf-8",
    "Content-Length": Buffer.byteLength(texto),
    "Cache-Control": "no-store"
  });
  res.end(texto);
}

// Mesmas regras do front: um organograma sem raiz, com id repetido ou com pai
// inexistente não desenha. Validar aqui evita gravar um arquivo que deixaria a
// página em branco no próximo acesso de todo mundo.
function validar(linhas) {
  if (!Array.isArray(linhas) || !linhas.length) return "envie uma lista de pessoas";
  const ids = new Set();
  for (const linha of linhas) {
    if (!linha || typeof linha !== "object") return "há um registro que não é um objeto";
    const id = String(linha.id ?? "").trim();
    if (!id) return "há um registro sem id";
    if (ids.has(id)) return `id repetido: ${id}`;
    ids.add(id);
  }
  const raizes = linhas.filter((l) => !String(l.parentId ?? "").trim());
  if (raizes.length !== 1) return `o organograma precisa de exatamente uma raiz (encontrei ${raizes.length})`;
  for (const linha of linhas) {
    const pai = String(linha.parentId ?? "").trim();
    if (pai && !ids.has(pai)) return `${linha.id} aponta para um chefe inexistente (${pai})`;
  }
  // ciclo: subir de cada nó até a raiz tem de terminar
  const paiDe = new Map(linhas.map((l) => [String(l.id), String(l.parentId ?? "").trim()]));
  for (const id of ids) {
    const visto = new Set();
    let atual = id;
    while (atual) {
      if (visto.has(atual)) return `há um ciclo de chefia envolvendo ${id}`;
      visto.add(atual);
      atual = paiDe.get(atual);
    }
  }
  return null;
}

const versaoDe = (texto) => crypto.createHash("sha1").update(texto).digest("hex").slice(0, 12);

async function lerArquivo() {
  try {
    const texto = await fsp.readFile(ARQUIVO, "utf8");
    return { linhas: JSON.parse(texto), versao: versaoDe(texto) };
  } catch (erro) {
    if (erro.code === "ENOENT") return null;
    throw erro;
  }
}

// Grava no temporário e renomeia: se o processo morrer no meio, o arquivo bom
// continua intacto em vez de virar metade de um JSON.
async function gravarArquivo(linhas) {
  const texto = JSON.stringify(linhas, null, 1);
  await fsp.mkdir(DIR_DADOS, { recursive: true });
  const temp = ARQUIVO + ".tmp";
  await fsp.writeFile(temp, texto, "utf8");
  try {
    await fsp.copyFile(ARQUIVO, ANTERIOR);
  } catch (erro) {
    if (erro.code !== "ENOENT") throw erro;
  }
  await fsp.rename(temp, ARQUIVO);
  return versaoDe(texto);
}

function lerCorpo(req) {
  return new Promise((resolve, reject) => {
    let total = 0;
    const partes = [];
    req.on("data", (pedaco) => {
      total += pedaco.length;
      if (total > LIMITE_BYTES) {
        reject(Object.assign(new Error("corpo grande demais"), { grande: true }));
        req.destroy();
        return;
      }
      partes.push(pedaco);
    });
    req.on("end", () => resolve(Buffer.concat(partes).toString("utf8")));
    req.on("error", reject);
  });
}

const DIR_FOTOS = path.join(DIR_DADOS, "fotos");
const LIMITE_FOTO = 3 * 1024 * 1024;

// A foto vira um arquivo em /dados/fotos/<id>.jpg e o CSV guarda só o caminho.
// Guardar a imagem embutida como data URI incharia o CSV em alguns MB e o
// tornaria impossível de abrir no Excel.
async function fotos(req, res, rota) {
  const id = decodeURIComponent(rota.slice("/api/fotos/".length));
  if (!id || !/^[A-Za-z0-9_.-]+$/.test(id)) return json(res, 400, { erro: "id inválido" });
  const arquivo = path.join(DIR_FOTOS, id + ".jpg");

  if (req.method === "PUT") {
    const partes = [];
    let total = 0;
    for await (const pedaco of req) {
      total += pedaco.length;
      if (total > LIMITE_FOTO) {
        req.destroy();
        return json(res, 413, { erro: "a imagem passou de 3 MB" });
      }
      partes.push(pedaco);
    }
    if (!total) return json(res, 400, { erro: "imagem vazia" });
    await fsp.mkdir(DIR_FOTOS, { recursive: true });
    const temp = arquivo + ".tmp";
    await fsp.writeFile(temp, Buffer.concat(partes));
    await fsp.rename(temp, arquivo);
    return json(res, 200, { caminho: `fotos/${id}.jpg`, bytes: total });
  }

  if (req.method === "DELETE") {
    try {
      await fsp.unlink(arquivo);
    } catch (erro) {
      if (erro.code !== "ENOENT") throw erro;
    }
    return json(res, 200, { removida: true });
  }

  res.writeHead(405, { Allow: "PUT, DELETE" });
  return res.end();
}

async function api(req, res, rota) {
  if (rota === "/api/saude") return json(res, 200, { ok: true });
  if (rota.startsWith("/api/fotos/")) return fotos(req, res, rota);
  if (rota !== "/api/organograma") return json(res, 404, { erro: "rota desconhecida" });

  if (req.method === "GET") {
    const atual = await lerArquivo();
    if (!atual) return json(res, 200, { existe: false });
    return json(res, 200, { existe: true, versao: atual.versao, linhas: atual.linhas });
  }

  if (req.method === "PUT") {
    let corpo;
    try {
      corpo = JSON.parse(await lerCorpo(req));
    } catch (erro) {
      return json(res, erro.grande ? 413 : 400, {
        erro: erro.grande ? "os dados passaram de 25 MB" : "JSON inválido"
      });
    }
    const problema = validar(corpo && corpo.linhas);
    if (problema) return json(res, 422, { erro: problema });

    // Se o arquivo mudou desde que este navegador carregou, alguém salvou no
    // meio: recusa em vez de apagar o trabalho da outra pessoa em silêncio.
    const atual = await lerArquivo();
    if (atual && corpo.versao && corpo.versao !== atual.versao) {
      return json(res, 409, {
        erro: "outra pessoa salvou alterações depois que você abriu a página",
        versao: atual.versao,
        linhas: atual.linhas
      });
    }
    const versao = await gravarArquivo(corpo.linhas);
    return json(res, 200, { versao, total: corpo.linhas.length });
  }

  if (req.method === "DELETE") {
    try {
      await fsp.copyFile(ARQUIVO, ANTERIOR);
      await fsp.unlink(ARQUIVO);
    } catch (erro) {
      if (erro.code !== "ENOENT") throw erro;
    }
    return json(res, 200, { existe: false });
  }

  res.writeHead(405, { Allow: "GET, PUT, DELETE" });
  res.end();
}

function estatico(req, res, rota) {
  const relativo = rota === "/" ? "tree.html" : decodeURIComponent(rota).replace(/^\/+/, "");
  // As fotos enviadas vivem no volume, não na imagem do container. O resolve
  // normaliza as barras: comparar com a string crua de DADOS_DIR recusava tudo
  // com 403 quando o caminho vinha com "/" e o sistema usa "\\".
  const base = path.resolve(relativo.startsWith("fotos/") ? DIR_DADOS : RAIZ);
  const alvo = path.resolve(base, relativo);
  if (alvo !== base && !alvo.startsWith(base + path.sep)) {
    res.writeHead(403).end("proibido");
    return;
  }
  fs.stat(alvo, (erro, info) => {
    if (erro || !info.isFile()) {
      res.writeHead(404, { "Content-Type": "text/plain; charset=utf-8" }).end("não encontrado");
      return;
    }
    res.writeHead(200, {
      "Content-Type": TIPOS[path.extname(alvo).toLowerCase()] || "application/octet-stream",
      "Content-Length": info.size,
      "Cache-Control": "no-cache"
    });
    fs.createReadStream(alvo).pipe(res);
  });
}

http
  .createServer((req, res) => {
    const rota = (req.url || "/").split("?")[0];
    if (rota.startsWith("/api/")) {
      api(req, res, rota).catch((erro) => {
        console.error("erro na api:", erro);
        json(res, 500, { erro: "falha ao gravar no servidor" });
      });
      return;
    }
    if (req.method !== "GET" && req.method !== "HEAD") {
      res.writeHead(405).end();
      return;
    }
    estatico(req, res, rota);
  })
  .listen(PORTA, () => console.log(`organograma em :${PORTA} — dados em ${ARQUIVO}`));
