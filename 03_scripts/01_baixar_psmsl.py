# -*- coding: utf-8 -*-
"""Etapa 1: inventario PSMSL e download das series maregraficas brasileiras."""
import sys, os, re, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
u = import_module('00_util_download')

print("[1] Inventario completo de estacoes PSMSL (RLR mensal)")
p = u.try_get("https://psmsl.org/data/obtaining/rlr.monthly.data/filelist.txt",
              "psmsl/filelist_rlr_monthly.txt",
              "Inventario de estacoes PSMSL com conjunto RLR mensal",
              "Permanent Service for Mean Sea Level (PSMSL)")
if not p: sys.exit("sem inventario")

txt = open(p, encoding='latin-1').read()
linhas = [l for l in txt.splitlines() if l.strip()]
print(f"    {len(linhas)} estacoes no inventario global")
print("    exemplo:", linhas[0])

# formato: id; lat; lon; nome; codigo pais; ...
est = []
for l in linhas:
    c = [x.strip() for x in l.split(';')]
    if len(c) < 5: continue
    try:
        est.append({'id': int(c[0]), 'lat': float(c[1]), 'lon': float(c[2]),
                    'nome': c[3], 'pais': c[4], 'bruto': l})
    except ValueError:
        continue

br = [e for e in est if e['pais'] == '874']
print(f"\n[2] Estacoes com codigo de pais BRA: {len(br)}")
for e in sorted(br, key=lambda x: x['id']):
    print(f"    {e['id']:>5}  {e['nome']:<30} lat={e['lat']:>8.3f} lon={e['lon']:>9.3f}")

json.dump(est, open(os.path.join(u.RAW, 'psmsl', 'inventario_global.json'), 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
json.dump(br, open(os.path.join(u.RAW, 'psmsl', 'inventario_brasil.json'), 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)

print(f"\n[3] Baixando series RLR (mensal + anual) das {len(br)} estacoes brasileiras")
for e in sorted(br, key=lambda x: x['id']):
    u.try_get(f"https://psmsl.org/data/obtaining/rlr.monthly.data/{e['id']}.rlrdata",
              f"psmsl/rlr_monthly_{e['id']}.rlrdata",
              f"Nivel medio mensal RLR, estacao {e['id']} ({e['nome']})", "PSMSL")
    u.try_get(f"https://psmsl.org/data/obtaining/rlr.annual.data/{e['id']}.rlrdata",
              f"psmsl/rlr_annual_{e['id']}.rlrdata",
              f"Nivel medio anual RLR, estacao {e['id']} ({e['nome']})", "PSMSL")
