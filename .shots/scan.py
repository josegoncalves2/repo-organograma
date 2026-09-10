"""Scanner de erros de GUI e de sistema — varre TODOS os 50 temas no
localhost:8085 com o CSV real e reporta defeitos sem ninguem apontar."""
import asyncio, sys, json
from playwright.async_api import async_playwright

URL = "http://localhost:8085"
CSV = "/mnt/c/Users/40446686808/projetos/organograma_antigo/organograma-completo.csv"

# Executado dentro da pagina. Devolve os defeitos observados no DOM real.
SONDA = r"""
() => {
  const out = { transbordo: [], colisao: 0, imgQuebrada: 0, placeholder: [],
                foraDaTela: 0, semTexto: 0, corPorClasse: {}, tamanhoPorClasse: {},
                amostras: [] };
  const nos = [...document.querySelectorAll('.chart-container g.node')];
  out.nos = nos.length;

  const caixas = [];
  const LIXO = /\b(undefined|null|NaN|\[object|Sample Node|Unit)\b/;

  nos.forEach((no) => {
    const div = no.querySelector('.node-foreign-object-div');
    if (!div) return;
    const dado = (window.d3 && d3.select(no).datum()) || null;
    const tipo = dado && dado.data && dado.data._tipoNome ? dado.data._tipoNome : '?';

    // 1. transbordo de texto
    div.querySelectorAll('div').forEach((e) => {
      const st = getComputedStyle(e);
      const clamp = st.webkitLineClamp && st.webkitLineClamp !== 'none';
      const ellip = st.textOverflow === 'ellipsis';
      if (e.scrollWidth > e.clientWidth + 2 && !ellip && !clamp && e.clientWidth > 0)
        out.transbordo.push({ tipo, eixo: 'x', over: e.scrollWidth - e.clientWidth,
                              txt: (e.textContent || '').trim().slice(0, 42) });
      if (e.scrollHeight > e.clientHeight + 2 && !clamp && e.clientHeight > 0)
        out.transbordo.push({ tipo, eixo: 'y', over: e.scrollHeight - e.clientHeight,
                              txt: (e.textContent || '').trim().slice(0, 42) });
    });

    // 2. imagens quebradas
    div.querySelectorAll('img').forEach((im) => {
      if (im.complete && im.naturalWidth === 0 && getComputedStyle(im).display !== 'none')
        out.imgQuebrada++;
    });

    // 3. texto-lixo
    const txt = (div.textContent || '').trim();
    const m = txt.match(LIXO);
    if (m) out.placeholder.push({ tipo, achado: m[0], txt: txt.slice(0, 50) });
    if (!txt) out.semTexto++;

    // 4. cor efetiva do card por classe
    const pintado = [...div.querySelectorAll('div')].find((e) => {
      const bg = getComputedStyle(e).backgroundColor;
      return bg && bg !== 'rgba(0, 0, 0, 0)' && bg !== 'transparent';
    });
    const cor = pintado ? getComputedStyle(pintado).backgroundColor : 'nenhuma';
    (out.corPorClasse[tipo] = out.corPorClasse[tipo] || {});
    out.corPorClasse[tipo][cor] = (out.corPorClasse[tipo][cor] || 0) + 1;

    // 5. tamanho por classe
    const r = no.getBoundingClientRect();
    const fo = no.querySelector('foreignObject');
    const larg = fo ? +fo.getAttribute('width') : Math.round(r.width);
    (out.tamanhoPorClasse[tipo] = out.tamanhoPorClasse[tipo] || {});
    out.tamanhoPorClasse[tipo][larg] = (out.tamanhoPorClasse[tipo][larg] || 0) + 1;

    if (fo) caixas.push({ tipo,
      x: +fo.getAttribute('x'), y: +fo.getAttribute('y'),
      w: +fo.getAttribute('width'), h: +fo.getAttribute('height'),
      m: no.getAttribute('transform') || '' });
  });

  // 6. colisao entre cards (usa a transform do <g>)
  const abs = caixas.map((c) => {
    const t = /translate\(([-\d.]+)\s*,\s*([-\d.]+)\)/.exec(c.m);
    const tx = t ? +t[1] : 0, ty = t ? +t[2] : 0;
    return { tipo: c.tipo, x: c.x + tx, y: c.y + ty, w: c.w, h: c.h };
  });
  for (let i = 0; i < abs.length; i++)
    for (let j = i + 1; j < abs.length; j++) {
      const a = abs[i], b = abs[j];
      const ox = Math.min(a.x + a.w, b.x + b.w) - Math.max(a.x, b.x);
      const oy = Math.min(a.y + a.h, b.y + b.h) - Math.max(a.y, b.y);
      if (ox > 4 && oy > 4) out.colisao++;
    }
  return out;
}
"""


async def main():
    alvos = sys.argv[1:] if len(sys.argv) > 1 else None
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1600, "height": 1000})
        erros = []
        pg.on("console", lambda m: erros.append(f"console.{m.type}: {m.text}") if m.type == "error" else None)
        pg.on("pageerror", lambda e: erros.append(f"pageerror: {e}"))

        await pg.goto(URL, wait_until="networkidle")
        await pg.evaluate("try{localStorage.clear()}catch(e){}")
        await pg.set_input_files("#csv-input", CSV)
        await pg.wait_for_function(
            "() => document.querySelectorAll('.chart-container g.node').length > 0", timeout=30000)

        temas = await pg.evaluate(
            "() => [...document.querySelectorAll('#theme-select option')].map(o => o.value)")
        if alvos:
            temas = [t for t in temas if t in alvos]
        print(f"temas a varrer: {len(temas)}\n")

        total = {"transbordo": 0, "colisao": 0, "imgQuebrada": 0,
                 "placeholder": 0, "semTexto": 0, "achatamento": 0}
        problemas = []

        for idx, tema in enumerate(temas, 1):
            erros.clear()
            await pg.select_option("#theme-select", tema)
            await pg.wait_for_timeout(450)
            await pg.evaluate("() => { try { chart.expandAll().render() } catch(e){} }")
            await pg.wait_for_timeout(700)
            r = await pg.evaluate(SONDA)

            # achatamento: classes diferentes com a MESMA cor de card
            cor_de = {}
            for classe, cores in r["corPorClasse"].items():
                cor_de[classe] = max(cores.items(), key=lambda kv: kv[1])[0]
            inverso = {}
            for classe, cor in cor_de.items():
                inverso.setdefault(cor, []).append(classe)
            achatados = {c: cs for c, cs in inverso.items() if len(cs) > 1 and c != "nenhuma"}

            n_tb = len(r["transbordo"])
            n_ph = len(r["placeholder"])
            n_ach = sum(len(cs) for cs in achatados.values())
            total["transbordo"] += n_tb
            total["colisao"] += r["colisao"]
            total["imgQuebrada"] += r["imgQuebrada"]
            total["placeholder"] += n_ph
            total["semTexto"] += r["semTexto"]
            total["achatamento"] += n_ach

            flags = []
            if n_tb: flags.append(f"transbordo={n_tb}")
            if r["colisao"]: flags.append(f"colisao={r['colisao']}")
            if r["imgQuebrada"]: flags.append(f"imgQuebrada={r['imgQuebrada']}")
            if n_ph: flags.append(f"placeholder={n_ph}")
            if r["semTexto"]: flags.append(f"semTexto={r['semTexto']}")
            if achatados: flags.append(f"CLASSES_MESMA_COR={n_ach}")
            if erros: flags.append(f"js={len(erros)}")

            marca = "  OK" if not flags else "  <<< " + "  ".join(flags)
            print(f"{idx:3d}/{len(temas)} {tema:38s} nos={r['nos']:4d}{marca}")

            if flags:
                d = {"tema": tema, "nos": r["nos"]}
                if achatados:
                    d["mesma_cor"] = {c: cs for c, cs in achatados.items()}
                if n_tb:
                    d["transbordo_ex"] = r["transbordo"][:3]
                if n_ph:
                    d["placeholder_ex"] = r["placeholder"][:3]
                if erros:
                    d["js"] = erros[:3]
                problemas.append(d)

        print("\n==================== TOTAIS ====================")
        for k, v in total.items():
            print(f"  {k:14s} {v}")
        print("================================================")
        if problemas:
            print("\nDETALHE DOS TEMAS COM PROBLEMA:")
            for d in problemas[:12]:
                print(json.dumps(d, ensure_ascii=False, indent=1))
        await b.close()

asyncio.run(main())
