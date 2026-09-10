"""Teste do seletor de Tipo e do bloqueio de hierarquia no editor."""
import asyncio, json
from playwright.async_api import async_playwright

URL = "http://localhost:8085"
CSV = "/mnt/c/Users/40446686808/projetos/organograma_antigo/organograma-completo.csv"

falhas = []
def ok(cond, nome, detalhe=""):
    print(f"  [{'OK  ' if cond else 'FALHA'}] {nome}{('  -> ' + detalhe) if detalhe else ''}")
    if not cond:
        falhas.append(nome + (" :: " + detalhe if detalhe else ""))

async def dados(pg):
    return await pg.evaluate("() => (window.currentData||[]).length")

async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1600, "height": 1000})
        erros = []
        pg.on("pageerror", lambda e: erros.append(str(e)))
        pg.on("console", lambda m: erros.append(m.text) if m.type == "error" else None)

        await pg.goto(URL, wait_until="networkidle")
        await pg.evaluate("() => fetch('api/organograma',{method:'DELETE'}).catch(()=>{})")
        await pg.wait_for_timeout(400)
        await pg.goto(URL, wait_until="networkidle")
        await pg.evaluate("try{localStorage.clear()}catch(e){}")
        await pg.set_input_files("#csv-input", CSV)
        await pg.wait_for_function(
            "() => document.querySelectorAll('.chart-container g.node').length > 0", timeout=30000)
        await pg.wait_for_timeout(800)

        print("\n=== A. Add Node sob COLABORADOR e recusado ===")
        colab = await pg.evaluate("() => (window.currentData.find(r => ehColaborador(r))||{}).id")
        await pg.evaluate(f"() => selectNode({json.dumps(str(colab))})")
        await pg.wait_for_timeout(250)
        n0 = await dados(pg)
        await pg.click("text=Add Node"); await pg.wait_for_timeout(700)
        aberto = await pg.evaluate("() => !document.getElementById('editor').hidden")
        st = await pg.evaluate("() => document.getElementById('status-msg').textContent")
        ok(not aberto and await dados(pg) == n0,
           "COLABORADOR nao pode receber subordinado", st)

        print("\n=== B. Add Node sob unidade abre o modal ===")
        # pai precisa ser de rank ALTO (SETOR=4) para que SECRETARIA (rank 1)
        # caia em rank invertido. Rank igual e permitido de proposito: o
        # arquivo real tem SETOR sob SETOR 100 vezes.
        unid = await pg.evaluate(
            "() => (window.currentData.find(r => classificar(r) === 'SETOR')||{}).id")
        await pg.evaluate(f"() => selectNode({json.dumps(str(unid))})")
        await pg.wait_for_timeout(250)
        n1 = await dados(pg)
        await pg.click("text=Add Node"); await pg.wait_for_timeout(800)
        ok(await pg.evaluate("() => !document.getElementById('editor').hidden"),
           "editor abre (sem prompt cru)")
        titulo = await pg.evaluate("() => document.getElementById('editor-titulo').textContent")
        ok("Novo" in titulo, "editor identifica no novo", titulo)

        print("\n=== C. seletor de Tipo ===")
        opts = await pg.evaluate("() => [...document.querySelectorAll('#ed-type option')].map(o=>o.value)")
        ok(len(opts) == 15, "traz as 15 classes", f"veio {len(opts)}")
        for e in ["SECRETARIA", "DIVISAO", "SETOR", "COLABORADOR", "PREFEITURA"]:
            ok(e in opts, f"oferece {e}")
        ok(opts[0] == "PREFEITURA", "ordenado por rank (rank 0 primeiro)", opts[0])
        ok(opts[-1] == "COLABORADOR", "COLABORADOR por ultimo (rank 5)", opts[-1])

        print("\n=== D. dropdown 'Responde a' ===")
        chefes = await pg.evaluate(
            "() => [...document.querySelectorAll('#ed-parentId option')].map(o=>o.textContent)")
        sem_nome = [c for c in chefes if c.strip().startswith("#")]
        ok(len(sem_nome) == 0, "nenhum chefe listado como '#id'", f"{len(sem_nome)} sem nome")
        ok(all(" · " in c for c in chefes), "todo chefe mostra a classe", chefes[0] if chefes else "")
        colab_como_chefe = await pg.evaluate("""() => {
            const ids = [...document.querySelectorAll('#ed-parentId option')].map(o=>o.value);
            return ids.filter(i => { const r = window.currentData.find(x=>String(x.id)===String(i));
                                     return r && ehColaborador(r); }).length; }""")
        ok(colab_como_chefe == 0, "COLABORADOR nao aparece como chefe possivel",
           f"{colab_como_chefe} encontrados")

        print("\n=== E. hierarquia bloqueia rank invertido ===")
        tipo_pai = await pg.evaluate(f"() => tipoDe(window.currentData.find(r=>String(r.id)==={json.dumps(str(unid))})).rotulo")
        await pg.fill("#ed-position", "SECRETARIA DE TESTE")
        await pg.select_option("#ed-type", "SECRETARIA")
        await pg.click("text=Salvar"); await pg.wait_for_timeout(600)
        msg = await pg.evaluate("() => document.getElementById('ed-erro').textContent")
        barrado = await pg.evaluate("() => !document.getElementById('editor').hidden")
        ok(bool(msg) and barrado, f"SECRETARIA sob {tipo_pai} recusada", f"msg={msg!r}")

        print("\n=== F. tipo valido salva e classifica ===")
        await pg.fill("#ed-position", "Setor de Teste Automatizado")
        await pg.select_option("#ed-type", "SETOR")
        await pg.click("text=Salvar"); await pg.wait_for_timeout(1200)
        fechou = await pg.evaluate("() => document.getElementById('editor').hidden")
        ok(fechou, "editor fecha ao salvar tipo valido")
        n2 = await dados(pg)
        ok(n2 == n1 + 1, "criou exatamente 1", f"{n1} -> {n2}")
        novo = await pg.evaluate("() => { const a=window.currentData; return a[a.length-1]; }")
        cls = await pg.evaluate(f"() => classificar(window.currentData.find(r=>String(r.id)==={json.dumps(str(novo['id']))}))")
        ok(cls == "SETOR", "no gravado classifica como SETOR", f"classe={cls}")
        ok(novo.get("type") == "SETOR", "coluna type gravada", str(novo.get("type")))

        print("\n=== G. cancelar novo no nao deixa linha em branco ===")
        n3 = await dados(pg)
        await pg.evaluate(f"() => selectNode({json.dumps(str(unid))})")
        await pg.click("text=Add Node"); await pg.wait_for_timeout(700)
        ok(await dados(pg) == n3 + 1, "linha provisoria criada")
        await pg.click("text=Cancelar"); await pg.wait_for_timeout(900)
        ok(await dados(pg) == n3, "cancelar remove a linha provisoria", f"{n3} -> {await dados(pg)}")

        print("\n=== H. hierarquia integra apos as edicoes ===")
        v = await pg.evaluate("() => validarHierarquia(window.currentData).length")
        ok(v == 0, "0 violacoes", str(v))
        ok(len(erros) == 0, "nenhum erro de JS", "; ".join(erros[:2]))

        await pg.screenshot(path="/mnt/c/Users/40446686808/projetos/organograma/.shots/editor_tipos.png")
        await b.close()

    print("\n" + "=" * 54)
    if falhas:
        print(f"FALHAS: {len(falhas)}")
        for f in falhas: print("   X " + f)
    else:
        print("TODOS OS TESTES DE TIPO PASSARAM")
    print("=" * 54)

asyncio.run(main())
