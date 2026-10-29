# -*- coding: utf-8 -*-
"""
Etapa 10: processamento e controle de qualidade das series maregraficas brasileiras (PSMSL RLR).

Regras de limpeza (declaradas e aplicadas de forma identica a todas as estacoes):
 R1. Descartar valores -99999 (codigo PSMSL para ausencia de dado).
 R2. Descartar meses marcados com flag de atencao (4o campo != 0), registrando quantos foram.
 R3. Formar media anual apenas com anos que tenham >= 10 meses validos (evita vies sazonal).
 R4. Exigir serie com >= 30 anos validos (criterio da OMM para separar tendencia climatica
     de variabilidade natural) e >= 25 anos de extensao temporal.
"""
import os, json, glob, re
import numpy as np

RAW = "01_dados_brutos"; OUT = "02_dados_processados"
os.makedirs(OUT, exist_ok=True)
MIN_MESES, MIN_ANOS = 10, 30

inv = {e['id']: e for e in json.load(open(f"{RAW}/psmsl/inventario_brasil.json", encoding='utf-8'))}

def ler_rlr_mensal(path):
    """Retorna (ano_decimal, nivel_mm, dias_faltantes, flag) para cada registro."""
    reg = []
    for ln in open(path, encoding='latin-1'):
        c = [x.strip() for x in ln.split(';')]
        if len(c) < 4: continue
        try:
            reg.append((float(c[0]), float(c[1]), int(c[2]), c[3]))
        except ValueError:
            continue
    return reg

resumo, series = [], {}
for sid, meta in sorted(inv.items()):
    p = f"{RAW}/psmsl/rlr_monthly_{sid}.rlrdata"
    if not os.path.exists(p): continue
    reg = ler_rlr_mensal(p)
    n_total = len(reg)
    # R1
    v1 = [r for r in reg if r[1] != -99999]
    n_ausente = n_total - len(v1)
    # R2: flag de atencao e o 4o campo; PSMSL usa '000' para sem atencao
    v2 = [r for r in v1 if r[3].strip('0') == '']
    n_flag = len(v1) - len(v2)
    # R3: medias anuais
    porano = {}
    for ano_dec, niv, *_ in v2:
        porano.setdefault(int(np.floor(ano_dec)), []).append(niv)
    anos = sorted(a for a, v in porano.items() if len(v) >= MIN_MESES)
    niveis = [float(np.mean(porano[a])) for a in anos]
    meses_desc = {a: len(porano[a]) for a in sorted(porano) if len(porano[a]) < MIN_MESES}

    if anos:
        ext = anos[-1] - anos[0] + 1
        compl = 100.0 * len(anos) / ext
    else:
        ext = compl = 0
    aprovada = len(anos) >= MIN_ANOS and ext >= 25
    resumo.append({'id': sid, 'nome': meta['nome'].strip(), 'lat': meta['lat'], 'lon': meta['lon'],
                   'n_meses_arquivo': n_total, 'n_meses_ausentes': n_ausente, 'n_meses_flag': n_flag,
                   'n_meses_validos': len(v2), 'primeiro_ano': anos[0] if anos else None,
                   'ultimo_ano': anos[-1] if anos else None, 'n_anos_validos': len(anos),
                   'extensao_anos': ext, 'completude_pct': round(compl, 1),
                   'anos_descartados_poucos_meses': meses_desc, 'aprovada': aprovada})
    series[sid] = {'nome': meta['nome'].strip(), 'lat': meta['lat'], 'lon': meta['lon'],
                   'anos': anos, 'nivel_mm': niveis}

hdr = f"{'ID':>5} {'Estacao':<16} {'Periodo':<12} {'Anos':>5} {'Ext':>4} {'Compl%':>7} {'Ausen':>6} {'Flag':>5} {'Aprov':>6}"
print(hdr); print('-' * len(hdr))
for r in resumo:
    per = f"{r['primeiro_ano']}-{r['ultimo_ano']}" if r['primeiro_ano'] else "--"
    print(f"{r['id']:>5} {r['nome'][:16]:<16} {per:<12} {r['n_anos_validos']:>5} {r['extensao_anos']:>4} "
          f"{r['completude_pct']:>7.1f} {r['n_meses_ausentes']:>6} {r['n_meses_flag']:>5} "
          f"{'SIM' if r['aprovada'] else 'nao':>6}")

ap = [r for r in resumo if r['aprovada']]
print(f"\nEstacoes aprovadas pelos criterios (>= {MIN_ANOS} anos validos e >= 25 anos de extensao): {len(ap)}")
for r in ap: print(f"   {r['id']} {r['nome']}  ({r['primeiro_ano']}-{r['ultimo_ano']}, {r['n_anos_validos']} anos, {r['completude_pct']}%)")

json.dump(resumo, open(f"{OUT}/psmsl_qc_resumo.json", 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
json.dump(series, open(f"{OUT}/psmsl_series_anuais.json", 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f"\ngravado {OUT}/psmsl_qc_resumo.json e {OUT}/psmsl_series_anuais.json")
