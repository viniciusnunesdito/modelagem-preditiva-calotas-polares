# -*- coding: utf-8 -*-
"""Etapa 12: processamento dos conjuntos globais (temperatura, altimetria, orcamento, IMBIE, GNSS)."""
import os, json, zipfile, numpy as np, openpyxl
from collections import defaultdict
RAW, OUT = "01_dados_brutos", "02_dados_processados"
G = {}

# ---------- 1. Temperatura global ----------
# GISTEMP v4: coluna J-D = media anual; base 1951-1980
lin = open(f"{RAW}/temperatura/gistemp_v4_global.csv", encoding='utf-8').read().splitlines()
hdr = lin[1].split(',')
iJD = hdr.index('J-D')
gis = {}
for l in lin[2:]:
    c = l.split(',')
    if not c[0].strip().isdigit():
        continue
    try:
        gis[int(c[0])] = float(c[iJD])
    except ValueError:
        pass
G['gistemp'] = {'base': '1951-1980', 'unidade': 'K', 'anos': sorted(gis),
                'valores': [gis[a] for a in sorted(gis)]}

# HadCRUT5: base 1961-1990
had = {}
for l in open(f"{RAW}/temperatura/hadcrut5_global_anual.csv", encoding='utf-8').read().splitlines()[1:]:
    c = l.split(',')
    try:
        had[int(c[0])] = (float(c[1]), float(c[2]), float(c[3]))
    except (ValueError, IndexError):
        pass
G['hadcrut5'] = {'base': '1961-1990', 'unidade': 'K', 'anos': sorted(had),
                 'valores': [had[a][0] for a in sorted(had)],
                 'ic_inf': [had[a][1] for a in sorted(had)],
                 'ic_sup': [had[a][2] for a in sorted(had)]}
print(f"Temperatura: GISTEMP {G['gistemp']['anos'][0]}-{G['gistemp']['anos'][-1]} ({len(gis)} anos); "
      f"HadCRUT5 {G['hadcrut5']['anos'][0]}-{G['hadcrut5']['anos'][-1]} ({len(had)} anos)")

# ---------- 2. Altimetria GMSL (NOAA) -> medias anuais ----------
def ler_noaa(p):
    porano = defaultdict(list)
    for l in open(p, encoding='utf-8'):
        if l.startswith('#') or not l.strip():
            continue
        c = [x.strip() for x in l.split(',')]
        try:
            t = float(c[0])
        except ValueError:
            continue
        vals = [float(x) for x in c[1:] if x not in ('', 'NaN')]
        if vals:
            porano[int(np.floor(t))].append(float(np.mean(vals)))
    anos = sorted(a for a in porano if len(porano[a]) >= 20)
    return anos, [float(np.mean(porano[a])) for a in anos]

a, v = ler_noaa(f"{RAW}/altimetria/noaa_gmsl_66S66N_sazonal_removida.csv")
G['altimetria_gmsl'] = {'fonte': 'NOAA/NESDIS LSA', 'unidade': 'mm',
                        'nota': 'sem correcao de GIA', 'anos': a, 'valores': v}
print(f"Altimetria GMSL: {a[0]}-{a[-1]} ({len(a)} anos anuais completos)")

# ---------- 3. Orcamento do nivel do mar (Frederikse et al., 2020) ----------
wb = openpyxl.load_workbook(f"{RAW}/frederikse2020/global_basin_timeseries.xlsx")

def ler_aba(nome):
    ws = wb[nome]
    cols = [c.value for c in ws[1]]
    anos = []
    dados = defaultdict(list)
    for r in ws.iter_rows(min_row=2, values_only=True):
        if r[0] is None:
            continue
        anos.append(int(r[0]))
        for i, nc in enumerate(cols[1:], start=1):
            dados[nc].append(None if r[i] is None else round(float(r[i]), 3))
    return {'anos': anos, 'colunas': cols[1:], 'series': dict(dados)}

G['orcamento_global'] = ler_aba('Global')
G['orcamento_atlantico_sul'] = ler_aba('South Atlantic')
print(f"Orcamento Frederikse: Global e Atlantico Sul, "
      f"{G['orcamento_global']['anos'][0]}-{G['orcamento_global']['anos'][-1]}")

# ---------- 4. IMBIE (Otosaka et al., 2023) ----------
IM = ("00_materiais_originais/drive-download-20261029T142040Z-1-001/"
      "Tópico 1/Mineração de Dados/1_IMBIE")
imb = {}
for reg in ['all', 'greenland', 'antarctica', 'west_antarctica',
            'east_antarctica', 'antarctic_peninsula']:
    for un in ['Gt', 'mm']:
        p = f"{IM}/imbie_{reg}_2021_{un}.csv"
        if not os.path.exists(p):
            continue
        t, bal, ubal, cum, ucum = [], [], [], [], []
        for l in open(p, encoding='utf-8').read().splitlines()[1:]:
            c = l.split(',')
            if len(c) < 5:
                continue
            try:
                t.append(float(c[0])); bal.append(float(c[1])); ubal.append(abs(float(c[2])))
                cum.append(float(c[3])); ucum.append(abs(float(c[4])))
            except ValueError:
                pass
        pa, pc = defaultdict(list), defaultdict(list)
        for i, tt in enumerate(t):
            pa[int(np.floor(tt))].append(bal[i])
            pc[int(np.floor(tt))].append(cum[i])
        anos = sorted(y for y in pa if len(pa[y]) >= 10)
        imb[f"{reg}_{un}"] = {'tempo': t, 'balanco': bal, 'balanco_inc': ubal,
                              'acumulado': cum, 'acumulado_inc': ucum,
                              'anual': {'anos': anos,
                                        'balanco': [float(np.mean(pa[y])) for y in anos],
                                        'acumulado': [float(np.mean(pc[y])) for y in anos]}}
G['imbie'] = imb
k = 'all_mm'
print(f"IMBIE: {len(imb)} series. Total (mm): {imb[k]['anual']['anos'][0]}-"
      f"{imb[k]['anual']['anos'][-1]}, acumulado final {imb[k]['acumulado'][-1]:.2f} mm")

# ---------- 5. GRACE/GRACE-FO Antartica ----------
pg = ("00_materiais_originais/drive-download-20261029T142040Z-1-001/"
      "Tópico 1/Mineração de Dados/3_NASA_GRACE-FO/antarctica_mass_200204_202607.txt")
t, m, s = [], [], []
for l in open(pg, encoding='latin-1'):
    if l.startswith('HDR') or not l.strip():
        continue
    c = l.split()
    try:
        t.append(float(c[0])); m.append(float(c[1])); s.append(float(c[2]))
    except (ValueError, IndexError):
        pass
G['grace_antartica'] = {'tempo': t, 'massa_Gt': m, 'inc_Gt': s,
                        'fonte': 'JPL GRACE/GRACE-FO RL06.3Mv4 Mascon (Wiese et al., 2022)'}
print(f"GRACE Antartica: {t[0]:.2f}-{t[-1]:.2f}, {len(t)} registros")

# ---------- 6. Conteudo de calor oceanico ----------
def ler_ohc(p):
    a, w, e = [], [], []
    for l in open(p, encoding='latin-1'):
        c = l.split()
        if len(c) < 3 or c[0] == 'YEAR':
            continue
        try:
            a.append(float(c[0])); w.append(float(c[1])); e.append(float(c[2]))
        except ValueError:
            pass
    return {'anos': a, 'ohc_1e22J': w, 'inc': e}

G['ohc_0_700'] = ler_ohc(f"{RAW}/oceano/ncei_ohc_0-700m_anual.dat")
G['ohc_0_2000'] = ler_ohc(f"{RAW}/oceano/ncei_ohc_0-2000m_anual.dat")
print(f"OHC 0-700m: {G['ohc_0_700']['anos'][0]:.0f}-{G['ohc_0_700']['anos'][-1]:.0f}; "
      f"0-2000m: {G['ohc_0_2000']['anos'][0]:.0f}-{G['ohc_0_2000']['anos'][-1]:.0f}")

# ---------- 7. Church e White (1880-2013) ----------
with zipfile.ZipFile(f"{RAW}/altimetria/church_white_gmsl_2011.zip") as z:
    cand = [n for n in z.namelist() if n.endswith(('.txt', '.csv'))]
    print(f"Church e White, arquivos no zip: {cand}")
    # a reconstrucao maregrafica anual (Recons_gmsl_yr) cobre 1880-2013; o arquivo ALT
    # e apenas a altimetria pos-1993 e nao serve para o periodo longo
    for n in cand:
        if 'Recons_gmsl_yr' in n and n.endswith('.csv'):
            a2, v2, u2 = [], [], []
            for l in z.read(n).decode('latin-1').splitlines():
                c = l.replace(',', ' ').split()
                if len(c) < 2:
                    continue
                try:
                    a2.append(float(c[0])); v2.append(float(c[1]))
                    u2.append(float(c[2]) if len(c) > 2 else None)
                except ValueError:
                    pass
            if a2:
                G['church_white'] = {'arquivo': n, 'anos': a2, 'gmsl_mm': v2, 'inc_mm': u2}
                break
if 'church_white' in G:
    cw = G['church_white']
    print(f"Church e White: {cw['anos'][0]:.2f}-{cw['anos'][-1]:.2f}, "
          f"{len(cw['anos'])} registros ({cw['arquivo']})")

json.dump(G, open(f"{OUT}/dados_globais.json", 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f"\ngravado {OUT}/dados_globais.json "
      f"({os.path.getsize(OUT + '/dados_globais.json') / 1e6:.1f} MB)")
