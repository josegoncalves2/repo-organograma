"""Mede se os 50 temas sao REALMENTE distintos.

Captura o MESMO no em cada tema, recorta o card, normaliza para um tamanho
comum e compara par a par. Tema que so muda de tamanho ou de arredondamento
some na normalizacao e aparece aqui como duplicata.
"""
import asyncio, sys, io, json
import numpy as np
from PIL import Image
from playwright.async_api import async_playwright

URL = "http://localhost:8080"
CSV = "/mnt/c/Users/40446686808/projetos/organograma_antigo/organograma-completo.csv"
NORM = (160, 80)          # tudo reduzido ao mesmo tamanho: forma e cor, nao escala
LIMIAR = 0.045            # abaixo disso = visualmente iguais


def assinatura(png_bytes):
    im = Image.open(io.BytesIO(png_bytes)).convert("RGB").resize(NORM, Image.BILINEAR)
    return np.asarray(im, dtype=np.float32) / 255.0


def diferenca(a, b):
    return float(np.abs(a - b).mean())


async def main():
    async with async_playwright() as p:
        b = await p.chromium.launch(args=["--no-sandbox"])
        pg = await b.new_page(viewport={"width": 1600, "height": 1000})
        await pg.goto(URL, wait_until="networkidle")
        await pg.evaluate("try{localStorage.clear()}catch(e){}")
        await pg.set_input_files("#csv-input", CSV)
        await pg.wait_for_function(
            "() => document.querySelectorAll('.chart-container g.node').length > 0", timeout=30000)
        await pg.wait_for_timeout(700)

        temas = await pg.evaluate(
            "() => [...document.querySelectorAll('#theme-select option')].map(o => ({v:o.value, t:o.textContent}))")
        print(f"temas: {len(temas)}\n")

        assinaturas = {}
        for i, t in enumerate(temas, 1):
            await pg.select_option("#theme-select", t["v"])
            await pg.wait_for_timeout(700)
            # o mesmo no em todos os temas: a raiz, sempre presente e sempre visivel
            # amostra VARIAS classes, nao so a raiz: uma classe de paleta
            # infeliz num modo escondia a silhueta e falseava a medida.
            caixas = await pg.evaluate("""() => {
                const vistos = new Set(); const out = [];
                for (const n of document.querySelectorAll('.chart-container g.node')) {
                  const dd = d3.select(n).datum();
                  const cls = dd && dd.data && dd.data._tipoNome;
                  if (!cls || vistos.has(cls)) continue;
                  const r = n.getBoundingClientRect();
                  // card so vale se estiver INTEIRO dentro da janela, senao
                  // o recorte sai vazio ou cortado e falseia a comparacao.
                  if (r.width < 5 || r.height < 5) continue;
                  if (r.x < 0 || r.y < 0) continue;
                  if (r.x + r.width > innerWidth || r.y + r.height > innerHeight) continue;
                  vistos.add(cls);
                  out.push({ cls: cls, x: r.x, y: r.y, width: r.width, height: r.height });
                  if (out.length >= 5) break;
                }
                return out;
            }""")
            if not caixas:
                print(f"{i:3d} {t['v']:38s} SEM CARD")
                continue
            partes = []
            for cx in caixas:
                png = await pg.screenshot(clip={k: cx[k] for k in ("x","y","width","height")})
                partes.append(assinatura(png))
            # todos os temas precisam do MESMO numero de blocos para a
            # comparacao ser valida; completa repetindo o ultimo.
            while len(partes) < 5:
                partes.append(partes[-1])
            assinaturas[t["v"]] = (np.concatenate(partes[:5], axis=0), t["t"])
            print(f"{i:3d} {t['v']:38s} {len(caixas)} classes: {','.join(c['cls'][:6] for c in caixas)}")

        await b.close()

    chaves = list(assinaturas)
    print("\n=== PARES VISUALMENTE IGUAIS (dif < %.3f) ===" % LIMIAR)
    iguais = []
    difs = []
    for i in range(len(chaves)):
        for j in range(i + 1, len(chaves)):
            d = diferenca(assinaturas[chaves[i]][0], assinaturas[chaves[j]][0])
            difs.append(d)
            if d < LIMIAR:
                iguais.append((d, chaves[i], chaves[j]))
    iguais.sort()
    for d, a, c in iguais[:40]:
        print(f"   dif={d:.4f}   {a}   ==   {c}")
    if not iguais:
        print("   (nenhum)")

    difs = np.array(difs)
    print("\n=== ESTATISTICA ===")
    print(f"  pares comparados : {len(difs)}")
    print(f"  pares iguais     : {len(iguais)}")
    print(f"  diferenca minima : {difs.min():.4f}")
    print(f"  diferenca mediana: {np.median(difs):.4f}")
    print(f"  diferenca maxima : {difs.max():.4f}")

    # quantos temas tem pelo menos um "gemeo"
    com_gemeo = set()
    for _, a, c in iguais:
        com_gemeo.add(a); com_gemeo.add(c)
    print(f"  temas com gemeo  : {len(com_gemeo)} de {len(chaves)}")

    json.dump({"iguais": [[d, a, c] for d, a, c in iguais],
               "min": float(difs.min()), "mediana": float(np.median(difs))},
              open("/mnt/c/Users/40446686808/projetos/organograma/.shots/distintos.json", "w"),
              indent=1)
    sys.exit(1 if iguais else 0)

asyncio.run(main())
