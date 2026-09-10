"""Fotografa a Casa Civil expandida, que e o caso reclamado pelo usuario."""
import asyncio, json
from playwright.async_api import async_playwright
OUT = "/mnt/c/Users/40446686808/projetos/organograma/.shots"

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1700, "height": 900})
        await pg.goto("http://localhost:8080", wait_until="networkidle")
        await pg.wait_for_function(
            "() => document.querySelectorAll('.chart-container g.node').length > 0",
            timeout=30000)
        info = await pg.evaluate("""() => {
            const cc = currentData.find(r => (r.position||"").includes("CASA CIVIL")
                                             && !(r.name||"").trim());
            chart.setExpanded(String(cc.id), true);
            const marca = (id, prof) => {
              if (prof > 2) return;
              currentData.filter(r => String(r.parentId) === String(id))
                         .forEach(f => { chart.setExpanded(String(f.id), true);
                                         marca(String(f.id), prof + 1); });
            };
            marca(String(cc.id), 0);
            chart.render();
            setTimeout(() => chart.setCentered(String(cc.id)).render(), 300);
            return {id: cc.id};
        }""")
        await pg.wait_for_timeout(3000)
        await pg.evaluate("() => chart.zoomOut()")
        await pg.wait_for_timeout(1500)
        await pg.screenshot(path=f"{OUT}/casacivil_corrigida.png")
        print(json.dumps(info))
        await b.close()

asyncio.run(main())
