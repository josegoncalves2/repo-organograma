#!/usr/bin/env python3
"""Mostra a hierarquia completa do organograma."""
import json, urllib.request
from collections import defaultdict

URL = "http://localhost:8080/api/organograma"
with urllib.request.urlopen(URL, timeout=10) as r:
    data = json.load(r)
linhas = data.get("linhas", [])
por_id = {str(r["id"]): r for r in linhas}
filhos = defaultdict(list)
for r in linhas:
    pid = str(r.get("parentId", "")).strip()
    if pid:
        filhos[pid].append(r)

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

def rotulo(row):
    nome = str(row.get("name", "")).strip()
    if nome: return f"{nome} {str(row.get('lastName',''))}".strip()
    return str(row.get("position", "")) or f"#{row['id']}"

def mostrar(rid, prefixo="", eh_ultimo=True):
    row = por_id.get(str(rid))
    if not row: return
    t = tipo(row)
    r = rotulo(row)
    ramo = "└── " if eh_ultimo else "├── "
    print(f"{prefixo}{ramo}[{t}] {r} (id={row['id']})")
    novos = filhos.get(str(rid), [])
    for i, f in enumerate(novos):
        novo_prefixo = prefixo + ("    " if eh_ultimo else "│   ")
        mostrar(f["id"], novo_prefixo, i == len(novos) - 1)

raiz = [r for r in linhas if not str(r.get("parentId", "")).strip()]
for r in raiz:
    print(f"[{tipo(r)}] {rotulo(r)} (id={r['id']})")
    for i, f in enumerate(filhos.get(str(r["id"]), [])):
        mostrar(f["id"], "", i == len(filhos.get(str(r["id"]), [])) - 1)