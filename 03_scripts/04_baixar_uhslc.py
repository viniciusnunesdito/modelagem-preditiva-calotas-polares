# -*- coding: utf-8 -*-
"""Etapa 4: dados horarios de qualidade de pesquisa (UHSLC) para analise de extremos."""
import sys, os, json
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from importlib import import_module
u = import_module('00_util_download')
F = "University of Hawaii Sea Level Center (UHSLC), Research Quality Dataset; Caldwell, Merrifield e Thompson (2015), DOI 10.7289/V5V40S7W"

p = u.try_get("https://uhslc.soest.hawaii.edu/data/meta.geojson", "uhslc/meta.geojson",
              "Metadados de todas as estacoes do UHSLC", F)
g = json.load(open(p, encoding='utf-8'))
br = []
for f in g['features']:
    pr = f['properties']
    lat, lon = f['geometry']['coordinates'][1], f['geometry']['coordinates'][0]
    lo = lon - 360 if lon > 180 else lon
    if -35 < lat < 6 and -56 < lo < -30:
        br.append({'uhslc_id': pr.get('uhslc_id'), 'nome': pr.get('name'), 'pais': pr.get('country'),
                   'lat': lat, 'lon': lo, 'ssc': pr.get('ssc_id'), 'gloss': pr.get('gloss_id'),
                   'inicio': pr.get('rq_span', {}).get('oldest'), 'fim': pr.get('rq_span', {}).get('latest')})
print(f"\nEstacoes UHSLC na costa brasileira: {len(br)}")
for e in sorted(br, key=lambda x: str(x['uhslc_id'])):
    print(f"  id={e['uhslc_id']:<5} {str(e['nome'])[:26]:<26} {str(e['pais'])[:8]:<8} "
          f"lat={e['lat']:>7.2f} lon={e['lon']:>8.2f}  RQ: {e['inicio']} a {e['fim']}")
json.dump(br, open(os.path.join(u.RAW, 'uhslc', 'inventario_brasil.json'), 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)

print("\nBaixando series horarias e diarias de qualidade de pesquisa")
for e in br:
    i = e['uhslc_id']
    if i is None: continue
    for freq, pref in (('hourly', 'h'), ('daily', 'd')):
        u.try_get(f"https://uhslc.soest.hawaii.edu/data/csv/rqds/atlantic/{freq}/{pref}{i}a.csv",
                  f"uhslc/{freq}_{i}a.csv",
                  f"Nivel do mar {'horario' if freq=='hourly' else 'diario'}, qualidade de pesquisa, "
                  f"estacao UHSLC {i} ({e['nome']})", F)
