# -*- coding: utf-8 -*-
"""
Etapa 11: processamento das series horarias de qualidade de pesquisa do UHSLC.

Produz, para cada estacao: medias mensais, medias anuais e maximos horarios anuais
(estes ultimos usados depois na analise de extremos).
Regras: R1 descartar sentinela de ausencia; R2 mes valido com >= 70% das horas;
R3 ano valido com >= 10 meses validos.
"""
import os, json, numpy as np
from collections import defaultdict

RAW, OUT = "01_dados_brutos", "02_dados_processados"
inv = json.load(open(f"{RAW}/uhslc/inventario_brasil.json", encoding='utf-8'))
SENT = -32767
MIN_FRAC_MES, MIN_MESES_ANO = 0.70, 10
HORAS_MES = {1:744,2:678,3:744,4:720,5:744,6:720,7:744,8:744,9:720,10:744,11:720,12:744}

res, out = [], {}
for e in sorted(inv, key=lambda x: str(x['uhslc_id'])):
    sid = e['uhslc_id']
    p = f"{RAW}/uhslc/hourly_{sid}a.csv"
    if not os.path.exists(p): continue
    mensal = defaultdict(list); maxanual = defaultdict(lambda: -1e18); nhora_ano = defaultdict(int)
    nlin = nval = 0
    for ln in open(p, encoding='latin-1'):
        c = ln.strip().split(',')
        if len(c) < 5: continue
        nlin += 1
        try:
            y, m, d, h, v = int(c[0]), int(c[1]), int(c[2]), int(c[3]), float(c[4])
        except ValueError:
            continue
        if v == SENT: continue
        nval += 1
        mensal[(y, m)].append(v)
        nhora_ano[y] += 1
        if v > maxanual[y]: maxanual[y] = v
    # R2
    mok = {k: float(np.mean(v)) for k, v in mensal.items() if len(v) >= MIN_FRAC_MES * HORAS_MES[k[1]]}
    # R3
    porano = defaultdict(list)
    for (y, m), v in mok.items(): porano[y].append(v)
    anos = sorted(y for y, v in porano.items() if len(v) >= MIN_MESES_ANO)
    niv = [float(np.mean(porano[y])) for y in anos]
    # maximos anuais apenas de anos com cobertura horaria >= 80% do ano
    anos_max = sorted(y for y in anos if nhora_ano[y] >= 0.80 * 8760)
    maxs = [maxanual[y] for y in anos_max]

    if anos:
        ext = anos[-1] - anos[0] + 1
        res.append({'id': sid, 'nome': e['nome'], 'lat': e['lat'], 'lon': e['lon'],
                    'horas_validas': nval, 'primeiro_ano': anos[0], 'ultimo_ano': anos[-1],
                    'n_anos': len(anos), 'extensao': ext, 'completude_pct': round(100*len(anos)/ext, 1),
                    'n_anos_max': len(anos_max)})
        out[str(sid)] = {'nome': e['nome'], 'lat': e['lat'], 'lon': e['lon'],
                         'anos': anos, 'nivel_mm': niv,
                         'anos_max': anos_max, 'max_horario_mm': maxs,
                         'mensal': {f"{k[0]}-{k[1]:02d}": round(v, 1) for k, v in sorted(mok.items())}}

hdr = f"{'ID':>4} {'Estacao':<26} {'lat':>7} {'Periodo':<12} {'Anos':>5} {'Ext':>4} {'Compl%':>7} {'AnosMax':>8}"
print(hdr); print('-'*len(hdr))
for r in sorted(res, key=lambda x: -x['n_anos']):
    print(f"{r['id']:>4} {r['nome'][:26]:<26} {r['lat']:>7.2f} {r['primeiro_ano']}-{r['ultimo_ano']:<7} "
          f"{r['n_anos']:>5} {r['extensao']:>4} {r['completude_pct']:>7.1f} {r['n_anos_max']:>8}")
longas = [r for r in res if r['n_anos'] >= 30]
print(f"\nEstacoes UHSLC com >= 30 anos validos: {len(longas)}")
for r in sorted(longas, key=lambda x: x['lat']): print(f"   {r['id']} {r['nome']:<28} lat {r['lat']:>7.2f}  {r['primeiro_ano']}-{r['ultimo_ano']}  {r['n_anos']} anos")
json.dump(res, open(f"{OUT}/uhslc_qc_resumo.json",'w',encoding='utf-8'), indent=1, ensure_ascii=False)
json.dump(out, open(f"{OUT}/uhslc_series.json",'w',encoding='utf-8'), indent=1, ensure_ascii=False)
print(f"\ngravado {OUT}/uhslc_qc_resumo.json e {OUT}/uhslc_series.json")
