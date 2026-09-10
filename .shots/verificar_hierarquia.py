"""Abre a pagina real com os dados que estao no ar e confere a hierarquia.

Nao carrega CSV: usa exatamente o que o servidor devolve, que e o que o
usuario ve. Confere na arvore desenhada (nao no JSON) que nenhum orgao de
linha pendura em assessoria e que nenhum SETOR pendura em SETOR.
"""
import asyncio, sys, json
from playwright.async_api import async_playwright

URL = "http://localhost:8085"
OUT = "/mnt/c/Users/40446686808/projetos/organograma/.shots"

CHECAGEM = """
() => {
  const linhas = currentData;
  const por = new Map(linhas.map(r => [String(r.id), r]));
  const cls = r => classificar(r);
  const RANK = {PREFEITURA:0,SECRETARIA:1,GABINETE:1,CONTROLADORIA:1,
    COORDENADORIA:2,ASSESSOR:2,FUNDO:2,CHEFE:2,CONSELHO:2,GUARDA:2,
    DIVISAO:3,FUNDEB:3,CORPO:3,SETOR:4,COLABORADOR:5};
  const v = {setorSobSetor:0, linhaSobAssessoria:0, pessoaComFilho:0,
             rankInvertido:0, semClasse:0};
  for (const r of linhas) {
    const c = cls(r);
    if (!c) v.semClasse++;
    const pai = por.get(String(r.parentId || "").trim());
    if (!pai) continue;
    const pc = cls(pai);
    if (pc === "COLABORADOR") v.pessoaComFilho++;
    if (RANK[c] < RANK[pc]) v.rankInvertido++;
    if (c === "SETOR" && pc === "SETOR") v.setorSobSetor++;
    if ((c === "DIVISAO" || c === "SETOR") &&
        ["ASSESSOR","COORDENADORIA","CHEFE"].includes(pc)) v.linhaSobAssessoria++;
  }
  const cc = linhas.find(r => (r.position||"").includes("CASA CIVIL") && !(r.name||"").trim());
  const filhos = linhas.filter(r => String(r.parentId) === String(cc.id))
                       .map(r => cls(r) + " | " + ((r.name||"").trim()
                            ? (r.name + " " + (r.lastName||"")).trim() : r.position));
  const assessores = linhas.filter(r => cls(r) === "ASSESSOR");
  const comFilhoDeLinha = assessores.filter(a =>
      linhas.some(r => String(r.parentId) === String(a.id) &&
                  ["DIVISAO","SETOR"].includes(cls(r)))).length;
  return {total: linhas.length, violacoes: v, casaCivil: filhos,
          assessores: assessores.length, assessoresChefiandoLinha: comFilhoDeLinha,
          nosDesenhados: document.querySelectorAll('.chart-container g.node').length,
          validadorDoApp: (typeof validarHierarquia === 'function')
                          ? validarHierarquia(linhas).length : 'ausente'};
}
"""


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1700, "height": 1000})
        erros = []
        pg.on("console", lambda m: erros.append(m.type + ": " + m.text) if m.type == "error" else None)
        pg.on("pageerror", lambda e: erros.append("pageerror: " + str(e)))
        await pg.goto(URL, wait_until="networkidle")
        await pg.wait_for_function(
            "() => document.querySelectorAll('.chart-container g.node').length > 0",
            timeout=30000)
        await pg.evaluate("() => { try { chart.expandAll().render() } catch(e){} }")
        await pg.wait_for_timeout(2500)
        r = await pg.evaluate(CHECAGEM)
        r["errosDeConsole"] = erros[:5]
        print(json.dumps(r, ensure_ascii=False, indent=1))
        await pg.screenshot(path=f"{OUT}/hierarquia_corrigida.png")
        await b.close()
        mau = sum(r["violacoes"].values()) + r["assessoresChefiandoLinha"]
        sys.exit(1 if mau else 0)


asyncio.run(main())
