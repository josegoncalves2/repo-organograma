"""Navegador limpo, sem cache, sem storage: o que a pagina desenha de fato."""
import asyncio, json
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": 1500, "height": 900})
        pg = await ctx.new_page()
        erros = []
        pg.on("pageerror", lambda e: erros.append(str(e)))
        await pg.goto("http://localhost:8085", wait_until="networkidle")
        await pg.evaluate("try{localStorage.clear();sessionStorage.clear()}catch(e){}")
        await pg.reload(wait_until="networkidle")
        await pg.wait_for_function(
            "() => document.querySelectorAll('.chart-container g.node').length > 0", timeout=30000)
        r = await pg.evaluate("""() => {
          const por = new Map(currentData.map(x => [String(x.id), x]));
          const pessoa = x => (x.name||"").trim() || (x.lastName||"").trim();
          const nome = x => pessoa(x) ? (x.name+" "+(x.lastName||"")).trim() : x.position;
          const raizes = currentData.filter(x => !pessoa(x) &&
              ["SECRETARIA","GABINETE","CONTROLADORIA"].includes(classificar(x)));
          const linhas = raizes.map(s => {
            const ti = currentData.filter(x => String(x.parentId)===String(s.id) && pessoa(x))
                                  .map(nome);
            return (s.position||"").slice(0,42) + "  ->  " + (ti.join(", ") || "*** SEM TITULAR ***");
          });
          const gz = currentData.find(x => (x.name||"")==="Geninho");
          return {titulares: linhas, prefeito: gz ? nome(gz)+" sob "+(por.get(String(gz.parentId))||{}).position : "nao achei",
                  total: currentData.length, desenhados: document.querySelectorAll('.chart-container g.node').length};
        }""")
        r["errosDeConsole"] = erros
        print(json.dumps(r, ensure_ascii=False, indent=1))
        await b.close()

asyncio.run(main())
