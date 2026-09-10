"""Fotografa o GABINETE DO PREFEITO na pagina real."""
import asyncio, json
from playwright.async_api import async_playwright
OUT = "/mnt/c/Users/40446686808/projetos/organograma/.shots"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1500, "height": 900})
        await pg.goto("http://localhost:8080", wait_until="networkidle")
        await pg.wait_for_function(
            "() => document.querySelectorAll('.chart-container g.node').length > 0", timeout=30000)
        info = await pg.evaluate("""() => {
            const g = currentData.find(r => (r.position||"").includes("GABINETE DO PREFEITO")
                                            && !(r.name||"").trim());
            const abrir = (id, prof) => { chart.setExpanded(String(id), true);
              if (prof > 1) return;
              currentData.filter(r => String(r.parentId) === String(id))
                         .forEach(f => abrir(f.id, prof + 1)); };
            abrir(g.id, 0); chart.render();
            setTimeout(() => chart.setCentered(String(g.id)).render(), 300);
            const filhos = currentData.filter(r => String(r.parentId) === String(g.id))
              .map(r => ((r.name||"").trim() ? (r.name+" "+(r.lastName||"")).trim() : r.position));
            return {gabinete: filhos};
        }""")
        await pg.wait_for_timeout(3000)
        await pg.screenshot(path=f"{OUT}/gabinete_corrigido.png")
        print(json.dumps(info, ensure_ascii=False, indent=1))
        await b.close()

asyncio.run(main())
