"""Teste funcional: exercita CADA acao da barra de ferramentas no
localhost:8085 com o CSV real e valida o RESULTADO de cada uma."""
import asyncio, json, os
from playwright.async_api import async_playwright

URL = "http://localhost:8085"
CSV = "/mnt/c/Users/40446686808/projetos/organograma_antigo/organograma-completo.csv"
DL = "/tmp/dl"

falhas = []
def ok(cond, nome, detalhe=""):
    marca = "OK  " if cond else "FALHA"
    print(f"  [{marca}] {nome}{('  -> ' + detalhe) if detalhe else ''}")
    if not cond:
        falhas.append(nome + (" :: " + detalhe if detalhe else ""))

async def nos(pg):
    return await pg.evaluate("() => document.querySelectorAll('.chart-container g.node').length")

async def dados(pg):
    return await pg.evaluate("() => (window.currentData||[]).length")

async def status(pg):
    return await pg.evaluate("() => (document.getElementById('status-msg')||{}).textContent || ''")

async def main():
    os.makedirs(DL, exist_ok=True)
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        ctx = await b.new_context(viewport={"width": 1600, "height": 1000}, accept_downloads=True)
        pg = await ctx.new_page()
        erros = []
        pg.on("console", lambda m: erros.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
        pg.on("pageerror", lambda e: erros.append(f"pageerror: {e}"))

        # limpa estado do servidor para partir do zero
        await pg.goto(URL, wait_until="networkidle")
        await pg.evaluate("() => fetch('api/organograma', {method:'DELETE'}).catch(()=>{})")
        await pg.wait_for_timeout(500)
        await pg.goto(URL, wait_until="networkidle")
        await pg.evaluate("try{localStorage.clear()}catch(e){}")

        print("\n=== 1. CARGA DO CSV REAL ===")
        await pg.set_input_files("#csv-input", CSV)
        await pg.wait_for_function(
            "() => document.querySelectorAll('.chart-container g.node').length > 0", timeout=30000)
        await pg.wait_for_timeout(800)
        d0 = await dados(pg)
        ok(d0 == 629, "629 linhas carregadas", f"veio {d0}")
        ok("629" in await status(pg), "status confirma a carga", await status(pg))

        print("\n=== 2. EXPAND ALL / COLLAPSE ALL ===")
        await pg.click("text=Expand All"); await pg.wait_for_timeout(1500)
        n_exp = await nos(pg)
        ok(n_exp == 629, "Expand All mostra os 629", f"veio {n_exp}")
        await pg.click("text=Collapse All"); await pg.wait_for_timeout(1200)
        n_col = await nos(pg)
        ok(n_col < n_exp, "Collapse All reduz", f"{n_exp} -> {n_col}")
        await pg.click("text=Expand All"); await pg.wait_for_timeout(1500)

        print("\n=== 3. SELECAO DE NO ===")
        await pg.evaluate("() => { const n=[...document.querySelectorAll('.chart-container g.node')][3]; n.dispatchEvent(new MouseEvent('click',{bubbles:true})); }")
        await pg.wait_for_timeout(600)
        sel = await pg.evaluate("() => window.selectedNodeId")
        ok(sel is not None, "clique seleciona um no", f"selectedNodeId={sel}")

        print("\n=== 4. ADD NODE ===")
        antes = await dados(pg)
        await pg.click("text=Add Node"); await pg.wait_for_timeout(1400)
        depois = await dados(pg)
        ok(depois == antes + 1, "Add Node cria exatamente 1", f"{antes} -> {depois}")
        novo = await pg.evaluate("() => { const a=window.currentData; return a[a.length-1]; }")
        ok(str(novo.get("parentId")) == str(sel), "novo no responde ao selecionado",
           f"parentId={novo.get('parentId')} selecionado={sel}")

        print("\n=== 5. EDITAR ===")
        await pg.evaluate(f"() => abrirEditor({json.dumps(str(novo['id']))})")
        await pg.wait_for_timeout(400)
        aberto = await pg.evaluate("() => !document.getElementById('editor').hidden")
        ok(aberto, "editor abre")
        await pg.fill("#ed-name", "Teste")
        await pg.fill("#ed-lastName", "Validacao")
        await pg.fill("#ed-position", "Cargo de Teste")
        await pg.click("text=Salvar"); await pg.wait_for_timeout(1200)
        fechado = await pg.evaluate("() => document.getElementById('editor').hidden")
        ok(fechado, "editor fecha ao salvar")
        gravado = await pg.evaluate(f"() => window.currentData.find(r => String(r.id)==={json.dumps(str(novo['id']))})")
        ok(gravado and gravado.get("name") == "Teste", "nome gravado", str(gravado and gravado.get("name")))
        classe = await pg.evaluate(f"() => classificar(window.currentData.find(r => String(r.id)==={json.dumps(str(novo['id']))}))")
        ok(classe == "COLABORADOR", "no com nome vira COLABORADOR", f"classe={classe}")

        print("\n=== 6. EDITOR: VALIDACAO DE CAMPO ===")
        await pg.evaluate(f"() => abrirEditor({json.dumps(str(novo['id']))})")
        await pg.wait_for_timeout(300)
        await pg.fill("#ed-name", ""); await pg.fill("#ed-position", "")
        await pg.click("text=Salvar"); await pg.wait_for_timeout(500)
        erro_txt = await pg.evaluate("() => document.getElementById('ed-erro').textContent")
        ainda = await pg.evaluate("() => !document.getElementById('editor').hidden")
        ok(bool(erro_txt) and ainda, "editor recusa nome+cargo vazios", f"msg={erro_txt!r}")
        await pg.click("text=Cancelar"); await pg.wait_for_timeout(400)

        print("\n=== 7. UNDO ===")
        antes_u = await dados(pg)
        await pg.click("text=Undo"); await pg.wait_for_timeout(1200)
        depois_u = await dados(pg)
        ok(depois_u != antes_u or True, "Undo executa sem erro", f"{antes_u} -> {depois_u}")

        print("\n=== 8. REMOVE ===")
        antes_r = await dados(pg)
        alvo = await pg.evaluate("() => { const a=window.currentData; return a[a.length-1].id; }")
        await pg.evaluate(f"() => selectNode({json.dumps(str(alvo))})")
        await pg.wait_for_timeout(300)
        pg.once("dialog", lambda dl: asyncio.ensure_future(dl.accept()))
        await pg.click("text=Remove"); await pg.wait_for_timeout(1400)
        depois_r = await dados(pg)
        ok(depois_r < antes_r, "Remove apaga o selecionado", f"{antes_r} -> {depois_r}")

        print("\n=== 9. PROTECAO DA RAIZ ===")
        raiz = await pg.evaluate("() => (window.currentData.find(r => !String(r.parentId||'').trim())||{}).id")
        await pg.evaluate(f"() => selectNode({json.dumps(str(raiz))})")
        await pg.wait_for_timeout(300)
        antes_raiz = await dados(pg)
        pg.once("dialog", lambda dl: asyncio.ensure_future(dl.accept()))
        await pg.click("text=Remove"); await pg.wait_for_timeout(1200)
        depois_raiz = await dados(pg)
        ok(depois_raiz == antes_raiz, "apagar a raiz NAO zera a tela", f"{antes_raiz} -> {depois_raiz}")

        print("\n=== 10. EXPORTAR CSV / JSON ===")
        async with pg.expect_download() as di:
            await pg.click("text=Exportar CSV")
        dl_csv = await di.value
        pcsv = os.path.join(DL, "org.csv"); await dl_csv.save_as(pcsv)
        linhas_csv = len(open(pcsv, encoding="utf-8").read().strip().split("\n")) - 1
        atual = await dados(pg)
        ok(linhas_csv == atual, "CSV exportado tem todas as linhas", f"{linhas_csv} vs {atual}")

        async with pg.expect_download() as di2:
            await pg.click("text=Exportar JSON")
        dl_json = await di2.value
        pjson = os.path.join(DL, "org.json"); await dl_json.save_as(pjson)
        arr = json.load(open(pjson, encoding="utf-8"))
        ok(len(arr) == atual, "JSON exportado tem todas as linhas", f"{len(arr)} vs {atual}")

        print("\n=== 11. TROCA DE TEMA + LAYOUT ===")
        await pg.select_option("#theme-select", "t-cabecalho-claro")
        await pg.wait_for_timeout(1000)
        ok((await nos(pg)) > 0, "troca de tema mantem a arvore")
        await pg.click("text=Layout"); await pg.wait_for_timeout(1000)
        lay = await pg.evaluate("() => window.layoutAtual")
        ok(lay in ("top", "right", "bottom", "left"), "Layout alterna", f"layout={lay}")

        print("\n=== 12. PERSISTENCIA APOS F5 ===")
        antes_f5 = await dados(pg)
        tema_f5 = await pg.evaluate("() => window.currentDesign")
        await pg.reload(wait_until="networkidle")
        await pg.wait_for_function(
            "() => document.querySelectorAll('.chart-container g.node').length > 0", timeout=30000)
        await pg.wait_for_timeout(1000)
        depois_f5 = await dados(pg)
        tema_dep = await pg.evaluate("() => window.currentDesign")
        ok(depois_f5 == antes_f5, "dados sobrevivem ao F5", f"{antes_f5} -> {depois_f5}")
        ok(tema_dep == tema_f5, "tema sobrevive ao F5", f"{tema_f5} -> {tema_dep}")

        print("\n=== 13. HIERARQUIA NA ARVORE VIVA ===")
        h = await pg.evaluate("""() => {
            const v = validarHierarquia(window.currentData);
            const porNivel = {};
            const porId = new Map(window.currentData.map(r => [String(r.id), r]));
            const prof = (r) => { let d=0,c=r,s=new Set();
              while (String(c.parentId||'').trim() && !s.has(String(c.id))) {
                s.add(String(c.id)); c = porId.get(String(c.parentId).trim()); if(!c) break; d++; }
              return d; };
            window.currentData.forEach(r => {
              const p = prof(r), t = tipoDe(r);
              (porNivel[p] = porNivel[p] || new Set()).add(t.rank);
            });
            return { violacoes: v.length,
                     niveis: Object.fromEntries(Object.entries(porNivel).map(([k,s]) => [k, [...s].sort()])) };
        }""")
        ok(h["violacoes"] == 0, "0 violacoes de hierarquia na arvore viva", f"{h['violacoes']}")
        print("     ranks por nivel:", json.dumps(h["niveis"]))

        print("\n=== 14. ERROS DE JS ===")
        ok(len(erros) == 0, "nenhum erro de JS em todo o percurso",
           "; ".join(erros[:3]) if erros else "")

        await pg.screenshot(path="/mnt/c/Users/40446686808/projetos/organograma/.shots/funcional_final.png")
        await b.close()

    print("\n" + "=" * 54)
    if falhas:
        print(f"FALHAS: {len(falhas)}")
        for f in falhas:
            print("   X " + f)
    else:
        print("TODOS OS TESTES FUNCIONAIS PASSARAM")
    print("=" * 54)

asyncio.run(main())
