import asyncio, sys, json
from playwright.async_api import async_playwright

URL  = "http://localhost:8085"
CSV  = "/mnt/c/Users/40446686808/projetos/organograma_antigo/organograma-completo.csv"
OUT  = "/mnt/c/Users/40446686808/projetos/organograma/.shots"

async def main():
    tema = sys.argv[1] if len(sys.argv) > 1 else "default"
    nome = sys.argv[2] if len(sys.argv) > 2 else tema
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width":1600,"height":1000})
        erros = []
        pg.on("console", lambda m: erros.append(m.type+": "+m.text) if m.type=="error" else None)
        pg.on("pageerror", lambda e: erros.append("pageerror: "+str(e)))
        await pg.goto(URL, wait_until="networkidle")
        await pg.evaluate("try{localStorage.clear()}catch(e){}")
        await pg.set_input_files("#csv-input", CSV)
        await pg.wait_for_function("() => document.querySelectorAll('.chart-container g.node').length > 0", timeout=30000)
        # troca de tema
        await pg.select_option("#theme-select", tema)
        await pg.wait_for_timeout(1200)
        await pg.evaluate("() => { try { chart.expandAll().render() } catch(e){} }")
        await pg.wait_for_timeout(1500)
        info = await pg.evaluate("""() => ({
            nos: document.querySelectorAll('.chart-container g.node').length,
            temas: document.querySelectorAll('#theme-select option').length,
            temaAtivo: document.getElementById('theme-select').value,
            status: (document.getElementById('status-msg')||{}).textContent
        })""")
        print(json.dumps({"tema":tema, **info, "erros":erros[:5]}, ensure_ascii=False))
        await pg.screenshot(path=f"{OUT}/{nome}.png")
        await b.close()

asyncio.run(main())
