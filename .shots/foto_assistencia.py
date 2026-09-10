"""Fotografa a Secretaria de Assistencia Social, o caso reclamado."""
import asyncio, json
from playwright.async_api import async_playwright
OUT = "/mnt/c/Users/40446686808/projetos/organograma/.shots"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1700, "height": 900})
        await pg.goto("http://localhost:8085", wait_until="networkidle")
        await pg.wait_for_function(
            "() => document.querySelectorAll('.chart-container g.node').length > 0",
            timeout=30000)
        info = await pg.evaluate("""() => {
            const alvo = currentData.find(r =>
                (r.position||"").includes("ASSIST") && !(r.name||"").trim());
            const abrir = (id, prof) => {
              chart.setExpanded(String(id), true);
              if (prof > 1) return;
              currentData.filter(r => String(r.parentId) === String(id))
                         .forEach(f => abrir(f.id, prof + 1));
            };
            abrir(alvo.id, 0);
            chart.render();
            setTimeout(() => chart.setCentered(String(alvo.id)).render(), 300);
            const filhos = currentData.filter(r => String(r.parentId) === String(alvo.id));
            return {secretaria: alvo.position, filhos: filhos.length,
                    pessoasSoltas: filhos.filter(r => (r.name||"").trim()).length};
        }""")
        await pg.wait_for_timeout(3000)
        await pg.evaluate("() => chart.zoomOut()")
        await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f"{OUT}/assistencia_corrigida.png")
        print(json.dumps(info, ensure_ascii=False))
        await b.close()

asyncio.run(main())
