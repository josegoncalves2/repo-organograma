#!/usr/bin/env python3
"""Analisa o CSV original para entender a estrutura municipal."""
import csv
from collections import defaultdict

# Ler o CSV original
linhas = []
with open('misc/data.csv', newline='', encoding='utf-8-sig') as f:
    reader = csv.DictReader(f)
    for row in reader:
        linhas.append(row)

print(f"Total de linhas no CSV: {len(linhas)}")

# Mapear por id
por_id = {r['id']: r for r in linhas}

# Contar por tipo baseado na inferência do servidor

def tipo_inferido(row):
    t = str(row.get('type', '')).strip().lower()
    if t: return t
    if str(row.get('name', '')).strip(): return 'colaborador'
    pos = str(row.get('position', '')).lower()
    if 'secretaria' in pos: return 'secretaria'
    if 'divisao' in pos or 'divisão' in pos: return 'divisao'
    if 'setor' in pos: return 'setor'
    if 'coordenadoria' in pos: return 'coordenadoria'
    if 'gabinete' in pos: return 'gabinete'
    if 'fundo' in pos: return 'fundo'
    if 'assessor' in pos: return 'assessor'
    return 'unidade'

# Contar por tipo
from collections import Counter
conta = Counter()
for r in linhas:
    conta[tipo_inferido(r)] += 1

print("\nContagem por tipo (inferido):")
for t, c in conta.most_common():
    print(f"  {t}: {c}")

# Mostrar as primeiras 50 linhas
print("\nPrimeiras 50 linhas do CSV:")
for i, r in enumerate(linhas[:50]):
    print(f"{i+1:3d}. id={r['id']:>4} parentId={r.get('parentId',''):>4} name='{r.get('name','')[:30]}' position='{r.get('position','')[:40]}' type='{r.get('type','')}'")

# Mostrar as linhas que contêm 'prefeito' ou 'prefeita'
print("\nLinhas que contêm 'prefeito' ou 'prefeita':")
for r in linhas:
    if 'prefeito' in str(r.get('name','')).lower() or 'prefeito' in str(r.get('position','')).lower():
        print(f"  id={r['id']} parentId={r.get('parentId','')} name='{r.get('name','')}' position='{r.get('position','')}' type='{r.get('type','')}'")

# Mostrar as linhas que contêm 'secretaria'
print("\nLinhas que contêm 'secretaria':")
for r in linhas:
    if 'secretaria' in str(r.get('position','')).lower():
        print(f"  id={r['id']} parentId={r.get('parentId','')} name='{r.get('name','')}' position='{r.get('position','')}' type='{r.get('type','')}'")

# Mostrar as linhas que contêm 'diretor'
print("\nLinhas que contêm 'diretor':")
for r in linhas:
    if 'diretor' in str(r.get('position','')).lower():
        print(f"  id={r['id']} parentId={r.get('parentId','')} name='{r.get('name','')}' position='{r.get('position','')}' type='{r.get('type','')}'")

# Mostrar as linhas que contêm 'chefe'
print("\nLinhas que contêm 'chefe':")
for r in linhas:
    if 'chefe' in str(r.get('position','')).lower():
        print(f"  id={r['id']} parentId={r.get('parentId','')} name='{r.get('name','')}' position='{r.get('position','')}' type='{r.get('type','')}'")

# Mostrar as linhas que contêm 'departamento'
print("\nLinhas que contêm 'departamento':")
for r in linhas:
    if 'departamento' in str(r.get('position','')).lower():
        print(f"  id={r['id']} parentId={r.get('parentId','')} name='{r.get('name','')}' position='{r.get('position','')}' type='{r.get('type','')}'")