#!/usr/bin/env python3
"""Analisa a estrutura municipal do organograma."""
import json, urllib.request

URL = "http://localhost:8085/api/organograma"
with urllib.request.urlopen(URL, timeout=10) as r:
    data = json.load(r)
linhas = data.get("linhas", [])

print("=== ANÁLISE DA ESTRUTURA MUNICIPAL ===\n")

# Mapear por id
por_id = {r["id"]: r for r in linhas}

# Encontrar o prefeito
prefeitos = []
for r in linhas:
    nome = str(r.get("name", "")).lower()
    posicao = str(r.get("position", "")).lower()
    if "prefeito" in nome or "prefeito" in posicao:
        prefeitos.append(r)

print(f"1. Prefeitos encontrados: {len(prefeitos)}")
for p in prefeitos:
    print(f"   - id={p['id']} name='{p.get('name','')}' position='{p.get('position','')}' parentId={p.get('parentId','')}")

# Encontrar chefes de gabinete
chefes_gabinete = []
for r in linhas:
    posicao = str(r.get("position", "")).lower()
    if "chefe de gabinete" in posicao:
        chefes_gabinete.append(r)

print(f"\n2. Chefes de gabinete encontrados: {len(chefes_gabinete)}")
for c in chefes_gabinete:
    print(f"   - id={c['id']} name='{c.get('name','')}' position='{c.get('position','')}' parentId={c.get('parentId','')}")

# Encontrar secretarias
secretarias = []
for r in linhas:
    posicao = str(r.get("position", "")).lower()
    if "secretaria" in posicao:
        secretarias.append(r)

print(f"\n3. Secretarias encontradas: {len(secretarias)}")
for s in secretarias:
    print(f"   - id={s['id']} name='{s.get('name','')}' position='{s.get('position','')}' parentId={s.get('parentId','')}")

# Encontrar diretores
diretores = []
for r in linhas:
    posicao = str(r.get("position", "")).lower()
    if "diretor" in posicao:
        diretores.append(r)

print(f"\n4. Diretores encontrados: {len(diretores)}")
for d in diretores:
    print(f"   - id={d['id']} name='{d.get('name','')}' position='{d.get('position','')}' parentId={d.get('parentId','')}")

# Encontrar chefes de setor
chefes_setor = []
for r in linhas:
    posicao = str(r.get("position", "")).lower()
    if "chefe de setor" in posicao:
        chefes_setor.append(r)

print(f"\n5. Chefes de setor encontrados: {len(chefes_setor)}")
for c in chefes_setor:
    print(f"   - id={c['id']} name='{c.get('name','')}' position='{c.get('position','')}' parentId={c.get('parentId','')}")

# Encontrar departamentos
departamentos = []
for r in linhas:
    posicao = str(r.get("position", "")).lower()
    if "departamento" in posicao:
        departamentos.append(r)

print(f"\n6. Departamentos encontrados: {len(departamentos)}")
for d in departamentos:
    print(f"   - id={d['id']} name='{d.get('name','')}' position='{d.get('position','')}' parentId={d.get('parentId','')}")

# Mostrar a hierarquia completa
print("\n=== HIERARQUIA COMPLETA ===")

def mostrar(rid, prefixo="", eh_ultimo=True):
    row = por_id.get(rid)
    if not row: return
    nome = str(row.get("name", "")).strip()
    posicao = str(row.get("position", "")).strip()
    r = rotulo(row)
    ramo = "└── " if eh_ultimo else "├── "
    print(f"{prefixo}{ramo}{posicao} (id={row['id']})")
    if nome and nome != posicao:
        print(f"{prefixo}{'    ' if eh_ultimo else '│   '}{nome}")
    filhos = [f for f in linhas if str(f.get("parentId", "")).strip() == str(rid)]
    for i, f in enumerate(filhos):
        novo_prefixo = prefixo + ("    " if eh_ultimo else "│   ")
        mostrar(f["id"], novo_prefixo, i == len(filhos) - 1)

def rotulo(row):
    nome = str(row.get("name", "")).strip()
    posicao = str(row.get("position", "")).strip()
    if posicao and posicao != nome:
        return f"{posicao} ({nome})" if nome else posicao
    return nome or f"id={row['id']}"

raiz = [r for r in linhas if not str(r.get("parentId", "")).strip()]
for r in raiz:
    mostrar(r["id"])