#!/usr/bin/env python3
"""Diagnostico do organograma: mostra a estrutura hierarquica atual."""
import json, urllib.request, sys

URL = "http://localhost:8085/api/organograma"
try:
    with urllib.request.urlopen(URL, timeout=10) as r:
        data = json.load(r)
except Exception as e:
    print("ERRO ao buscar:", e)
    sys.exit(1)

linhas = data.get("linhas", [])
print(f"Total de linhas: {len(linhas)}")

# Mapa por id
por_id = {str(r["id"]): r for r in linhas}

# Raiz
raizes = [r for r in linhas if not str(r.get("parentId", "")).strip()]
print(f"Raizes: {len(raizes)}")
for r in raizes:
    print(f"  RAIZ id={r['id']} name='{r.get('name','')}' position='{r.get('position','')}' type='{r.get('type','')}'")

# Contar filhos por tipo de nó
def tipo(row):
    t = str(row.get("type", "")).strip().lower()
    if t: return t
    if str(row.get("name", "")).strip(): return "colaborador"
    pos = str(row.get("position", "")).lower()
    if "secretaria" in pos: return "secretaria"
    if "divisao" in pos or "divisão" in pos: return "divisao"
    if "setor" in pos: return "setor"
    if "coordenadoria" in pos: return "coordenadoria"
    if "gabinete" in pos: return "gabinete"
    if "fundo" in pos: return "fundo"
    if "assessor" in pos: return "assessor"
    return "unidade"

# Contar por tipo
from collections import Counter
conta = Counter()
for r in linhas:
    conta[tipo(r)] += 1
print("\nContagem por tipo:")
for t, c in conta.most_common():
    print(f"  {t}: {c}")

# Mostrar os primeiros 20 nós com seus pais
print("\nPrimeiros 30 nós:")
for r in linhas[:30]:
    pai_id = str(r.get("parentId", "")).strip()
    pai = por_id.get(pai_id)
    pai_rot = f"{pai.get('position','')}" if pai else "RAIZ"
    print(f"  id={r['id']:>4} pai={pai_id:>4}({pai_rot[:40]}) nome='{r.get('name','')[:30]}' pos='{r.get('position','')[:40]}' tipo={tipo(r)}")

# Verificar se há COLABORADOR com filhos
print("\nColaboradores com filhos (VIOLAÇÃO):")
for r in linhas:
    if tipo(r) == "colaborador":
        filhos = [f for f in linhas if str(f.get("parentId", "")).strip() == str(r["id"])]
        if filhos:
            print(f"  id={r['id']} {r.get('name')} tem {len(filhos)} filhos")

# Verificar ciclo
print("\nVerificando ciclos...")
pai_de = {str(r["id"]): str(r.get("parentId", "")).strip() for r in linhas}
for id in list(pai_de.keys())[:10]:
    visto = set()
    atual = id
    while atual:
        if atual in visto:
            print(f"  CICLO detectado em {id}")
            break
        visto.add(atual)
        atual = pai_de.get(atual, "")