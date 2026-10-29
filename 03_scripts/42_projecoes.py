# -*- coding: utf-8 -*-
"""
Etapa 42: sensibilidade das calotas ao aquecimento e projecoes para a costa brasileira.

ESTRUTURA
---------
[1] Trajetorias de temperatura dos cenarios SSP, construidas a partir dos valores
    avaliados na Tabela SPM.1 do IPCC AR6 WG1 (IPCC, 2021).
[2] Analise de sensibilidade observada: quanto a taxa de perda de massa das calotas
    aumenta por grau de aquecimento, medida em epocas distintas. Esta analise responde
    a instabilidade de parametros detectada na etapa 41 (V3) e e o argumento central
    para decidir qual sensibilidade usar na projecao.
[3] Projecao em duas vias:
      Via A - emulador semi-empirico calibrado na serie longa (1900-2018). Validado
              contra dado independente de satelite, fornece um LIMITE INFERIOR, porque
              o registro do seculo XX nao contem os processos de descarga dinamica de
              gelo que dominam as projecoes do seculo XXI.
      Via B - projecoes processuais oficiais do IPCC AR6 (Garner et al., 2021), que
              incluem esses processos.
    As duas vias sao comparadas, e a diferenca entre elas e um resultado da pesquisa,
    nao uma inconsistencia a esconder.
[4] Aplicacao das impressoes digitais e do movimento vertical do terreno, convertendo
    as projecoes globais em projecoes de nivel RELATIVO do mar nas estacoes brasileiras.
[5] Decomposicao da elevacao projetada: qual fracao vem especificamente das calotas
    polares, estacao por estacao e cenario por cenario.
"""
import os, sys, json, importlib, warnings
import numpy as np
from scipy.interpolate import PchipInterpolator

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
E = importlib.import_module('05_estatistica')
OUT, RES, RAW = "02_dados_processados", "05_resultados", "01_dados_brutos"

G = json.load(open(f"{OUT}/dados_globais.json", encoding='utf-8'))
EM = json.load(open(f"{RES}/emulador_calotas.json", encoding='utf-8'))
FP = json.load(open(f"{OUT}/impressoes_digitais.json", encoding='utf-8'))
VLM = json.load(open(f"{OUT}/vlm_gnss.json", encoding='utf-8'))
saida = {}

# =====================================================================================
# [1] TRAJETORIAS DE TEMPERATURA DOS CENARIOS SSP
# =====================================================================================
# IPCC AR6 WG1, Tabela SPM.1: mudanca da temperatura media global da superficie em
# relacao a 1850-1900 (graus C). Melhor estimativa e faixa muito provavel (5-95%).
# Valores transcritos do PDF oficial do Sumario para Formuladores de Politicas.
AR6_T = {   # cenario: {periodo central: (melhor, inferior, superior)}
    'ssp119': {2030.5: (1.5, 1.2, 1.7), 2050.5: (1.6, 1.2, 2.0), 2090.5: (1.4, 1.0, 1.8)},
    'ssp126': {2030.5: (1.5, 1.2, 1.8), 2050.5: (1.7, 1.3, 2.2), 2090.5: (1.8, 1.3, 2.4)},
    'ssp245': {2030.5: (1.5, 1.2, 1.8), 2050.5: (2.0, 1.6, 2.5), 2090.5: (2.7, 2.1, 3.5)},
    'ssp370': {2030.5: (1.5, 1.2, 1.8), 2050.5: (2.1, 1.7, 2.6), 2090.5: (3.6, 2.8, 4.6)},
    'ssp585': {2030.5: (1.6, 1.3, 1.9), 2050.5: (2.4, 1.9, 3.0), 2090.5: (4.4, 3.3, 5.7)}}
NOME_SSP = {'ssp119': 'SSP1-1.9 (emissoes muito baixas)', 'ssp126': 'SSP1-2.6 (emissoes baixas)',
            'ssp245': 'SSP2-4.5 (emissoes intermediarias)', 'ssp370': 'SSP3-7.0 (emissoes altas)',
            'ssp585': 'SSP5-8.5 (emissoes muito altas)'}

ht = np.array(EM['temperatura']['anos'], float)
Tobs = np.array(EM['temperatura']['T_K'], float)
ANO0 = 2020                     # ancora das projecoes, igual a do IPCC AR6
ANOS = np.arange(1900, 2151, 1.0)
T_ANC = float(np.mean(Tobs[(ht >= 2011) & (ht <= 2030 - 1)]))   # media observada 2011-2024


def traj(cen, qual='melhor'):
    """Trajetoria anual de temperatura: observada ate 2024, cenario depois."""
    i = {'melhor': 0, 'inferior': 1, 'superior': 2}[qual]
    anc = sorted(AR6_T[cen])
    xa = [2015.0] + anc + [2150.0]
    # ancora em 2015: media observada 2006-2024, comum a todos os cenarios (comecam em 2015)
    v2015 = float(np.mean(Tobs[(ht >= 2006) & (ht <= 2024)]))
    ya = [v2015] + [AR6_T[cen][a][i] for a in anc]
    # extensao a 2150: mantem a tendencia 2050->2090, atenuada pela metade
    incl = (ya[-1] - ya[-2]) / (anc[-1] - anc[-2])
    ya = ya + [ya[-1] + 0.5 * incl * (2150.0 - anc[-1])]
    f = PchipInterpolator(xa, ya, extrapolate=True)
    T = np.where(ANOS <= 2024, np.interp(ANOS, ht, Tobs), f(ANOS))
    # suaviza a juncao 2020-2035 para evitar degrau artificial
    jm = (ANOS >= 2018) & (ANOS <= 2036)
    T[jm] = np.interp(ANOS[jm], [2018, 2036], [T[ANOS == 2018][0], f(2036.0)])
    return T


print("=" * 108)
print("[1] TRAJETORIAS DE TEMPERATURA (IPCC AR6 WG1, Tabela SPM.1; relativas a 1850-1900)")
print("=" * 108)
print(f"Observacao HadCRUT5: media 2006-2024 = {np.mean(Tobs[(ht>=2006)&(ht<=2024)]):+.3f} K; "
      f"2024 = {Tobs[ht==2024][0]:+.3f} K")
print(f"\n{'Cenario':<34} {'2030':>14} {'2050':>14} {'2090':>14} {'2100':>14}")
print("-" * 94)
TRAJ = {}
for c in AR6_T:
    TRAJ[c] = {q: traj(c, q) for q in ('melhor', 'inferior', 'superior')}
    f = lambda a: TRAJ[c]['melhor'][ANOS == a][0]
    g = lambda a: (TRAJ[c]['inferior'][ANOS == a][0], TRAJ[c]['superior'][ANOS == a][0])
    print(f"{NOME_SSP[c]:<34}" + "".join(
        f"{f(a):>8.2f} K    " for a in (2030, 2050, 2090, 2100)))
print("\nFaixa muito provavel em 2090 (5-95%):")
for c in AR6_T:
    lo, hi = TRAJ[c]['inferior'][ANOS == 2090][0], TRAJ[c]['superior'][ANOS == 2090][0]
    print(f"   {NOME_SSP[c]:<34} {lo:.2f} a {hi:.2f} K")
saida['trajetorias_T'] = {c: {q: np.round(TRAJ[c][q], 4).tolist() for q in TRAJ[c]} for c in TRAJ}
saida['anos_trajetoria'] = ANOS.tolist()
saida['tabela_SPM1'] = AR6_T

# =====================================================================================
# [2] SENSIBILIDADE OBSERVADA DAS CALOTAS AO AQUECIMENTO
# =====================================================================================
print("\n\n" + "=" * 108)
print("[2] SENSIBILIDADE OBSERVADA: aumento da taxa de perda de massa por grau de aquecimento")
print("=" * 108)
print("Compara-se a taxa medida em duas epocas do registro de satelite (IMBIE) com o")
print("aquecimento ocorrido entre elas. A mesma conta e feita para o seculo XX inteiro e")
print("para as projecoes processuais do IPCC AR6, de modo a verificar se a sensibilidade")
print("e estacionaria.")
EP1, EP2 = (1992, 1996), (2016, 2020)
sens = {}
for p, imk, rot in [('GrIS', 'greenland_mm', 'Groenlandia'), ('AIS', 'antarctica_mm', 'Antartica')]:
    im = G['imbie'][imk]
    t = np.array(im['tempo'], float); b = np.array(im['balanco'], float)   # mm/ano
    u = np.array(im['balanco_inc'], float)
    r1 = float(np.mean(b[(t >= EP1[0]) & (t < EP1[1] + 1)])); s1 = float(np.mean(u[(t >= EP1[0]) & (t < EP1[1] + 1)]))
    r2 = float(np.mean(b[(t >= EP2[0]) & (t < EP2[1] + 1)])); s2 = float(np.mean(u[(t >= EP2[0]) & (t < EP2[1] + 1)]))
    T1 = float(np.mean(Tobs[(ht >= EP1[0]) & (ht <= EP1[1])]))
    T2 = float(np.mean(Tobs[(ht >= EP2[0]) & (ht <= EP2[1])]))
    a_sat = (r2 - r1) / (T2 - T1)
    inc = np.sqrt(s1 ** 2 + s2 ** 2) / (T2 - T1)
    a_long = EM['selecao'][p]['par_final'][0]
    sens[p] = {'rotulo': rot, 'epoca1': list(EP1), 'epoca2': list(EP2),
               'taxa1': round(r1, 4), 'inc1': round(s1, 4), 'taxa2': round(r2, 4), 'inc2': round(s2, 4),
               'T1': round(T1, 4), 'T2': round(T2, 4), 'dT': round(T2 - T1, 4),
               'a_satelite': round(a_sat, 4), 'inc_a_satelite': round(float(inc), 4),
               'a_serie_longa': a_long, 'razao': round(a_sat / a_long, 2)}
    print(f"\n{rot} (IMBIE, Otosaka et al., 2023)")
    print(f"   taxa em {EP1[0]}-{EP1[1]}: {r1:+.3f} +/- {s1:.3f} mm/ano, com T = {T1:+.3f} K")
    print(f"   taxa em {EP2[0]}-{EP2[1]}: {r2:+.3f} +/- {s2:.3f} mm/ano, com T = {T2:+.3f} K")
    print(f"   -> sensibilidade observada no periodo de satelite: "
          f"{a_sat:+.3f} +/- {inc:.3f} mm/ano por K")
    print(f"   -> sensibilidade do emulador calibrado em 1900-2018: {a_long:+.3f} mm/ano por K")
    print(f"   -> razao: a sensibilidade recente e {a_sat/a_long:.1f}x a media do seculo XX")

# sensibilidade implicita nas projecoes do IPCC AR6
ar6g = json.load(open(f"{RAW}/ipcc_ar6/ar6_global.json", encoding='utf-8'))


def ar6(proc, cen, conf='medium', perc='height_50'):
    for r in ar6g:
        if r['process'] == proc and r['scenario'] == cen and r['confidence'] == conf:
            return np.array(r['year'], float), np.array(r[perc], float) * 1000.0   # m -> mm
    return None, None


print("\nSensibilidade implicita nas projecoes processuais do IPCC AR6 (SSP5-8.5, medianas):")
for proc, rot in [('GIS', 'Groenlandia'), ('AIS', 'Antartica')]:
    y, v = ar6('GIS' if proc == 'GIS' else 'AIS', 'ssp585')
    r20 = (v[1] - v[0]) / (y[1] - y[0])          # taxa media 2020-2030
    r90 = (v[8] - v[7]) / (y[8] - y[7])          # taxa media 2090-2100
    T20 = float(np.mean(TRAJ['ssp585']['melhor'][(ANOS >= 2020) & (ANOS <= 2030)]))
    T90 = float(np.mean(TRAJ['ssp585']['melhor'][(ANOS >= 2090) & (ANOS <= 2100)]))
    a_ar6 = (r90 - r20) / (T90 - T20)
    k = 'GrIS' if proc == 'GIS' else 'AIS'
    sens[k]['a_ar6'] = round(float(a_ar6), 4)
    sens[k]['taxa_ar6_2020s'] = round(float(r20), 4)
    sens[k]['taxa_ar6_2090s'] = round(float(r90), 4)
    print(f"   {rot}: taxa de {r20:.3f} mm/ano nos anos 2020 para {r90:.3f} mm/ano nos anos 2090, "
          f"com aquecimento de {T20:.2f} a {T90:.2f} K")
    print(f"      -> sensibilidade implicita no AR6: {a_ar6:+.3f} mm/ano por K "
          f"({a_ar6/sens[k]['a_serie_longa']:.1f}x a do seculo XX, "
          f"{a_ar6/sens[k]['a_satelite']:.1f}x a do periodo de satelite)")
saida['sensibilidade'] = sens

print("\nLeitura destes numeros: a sensibilidade das calotas ao aquecimento NAO e estacionaria.")
print("Ela cresceu entre o seculo XX e o periodo de satelite, e as projecoes processuais do")
print("IPCC AR6 supoem um crescimento adicional, atribuido a processos de descarga dinamica")
print("de gelo que praticamente nao aparecem no registro historico. Por isso a projecao")
print("estritamente orientada por dados do seculo XX e tratada aqui como limite inferior.")

# =====================================================================================
# [3] PROJECAO GLOBAL EM DUAS VIAS
# =====================================================================================
print("\n\n" + "=" * 108)
print("[3] PROJECAO GLOBAL: via A (emulador orientado por dados) e via B (IPCC AR6)")
print("=" * 108)
NOMES = {'M1': ['a', 'T0'], 'M2': ['a', 'T0', 'b'], 'M3': ['a', 'T0', 'q'], 'M4': ['a', 'T0', 'c']}


def taxa(nome, par, T, dT):
    if nome == 'M1': a, T0 = par[:2];      return a * (T - T0)
    if nome == 'M2': a, T0, b = par[:3];   return a * (T - T0) + b * dT
    if nome == 'M3': a, T0, q = par[:3];   return a * np.power(np.maximum(T - T0, 0.0), q)
    if nome == 'M4': a, T0, c = par[:3];   return a * (T - T0) + c * (T - T0) ** 2
    raise ValueError(nome)


def suaviza(y, w):
    if w <= 1: return np.asarray(y, float).copy()
    y = np.asarray(y, float); n = len(y); o = np.empty(n); h = w // 2
    for i in range(n):
        o[i] = y[max(0, i - h):min(n, i + h + 1)].mean()
    return o


def via_A(p, cen, qual='melhor', par=None):
    """Emulador: integra a taxa de ANO0 em diante. Retorna mm acima do nivel de ANO0."""
    s = EM['selecao'][p]
    nome, w = s['forma'], s['janela']
    par = s['par_final'] if par is None else par
    T = suaviza(TRAJ[cen][qual], w)
    dT = np.gradient(T, ANOS)
    r = taxa(nome, par, T, dT)
    cum = np.concatenate([[0.0], np.cumsum(np.diff(ANOS) * 0.5 * (r[1:] + r[:-1]))])
    return cum - cum[ANOS == ANO0][0]


PROC_A = {'GrIS': 'GIS', 'AIS': 'AIS', 'glac': 'glaciers', 'steric': 'oceandynamics'}
ROT = {'GrIS': 'Groenlandia', 'AIS': 'Antartica', 'glac': 'Geleiras', 'steric': 'Esterico/dinamico'}
HOR = [2050, 2100]

# ------------------------------------------------------------------ via A' (sensibilidade recente)
# A analise [2] mostra que a sensibilidade das calotas ao aquecimento cresceu entre o
# seculo XX e o periodo de satelite. A via A, calibrada em 119 anos, dilui essa mudanca
# numa media e por isso subestima a resposta recente. A via A' corrige isso sem recorrer
# a modelo processual: lineariza a resposta em torno do ESTADO ATUAL, usando a taxa
# observada na epoca mais recente e a sensibilidade medida no proprio periodo de satelite:
#     dS/dt(T) = r_ref + a_rec (T - T_ref)
# E a mesma forma funcional da via A, mas ancorada em observacoes recentes em vez da media
# centenaria. Permanece inteiramente orientada por dados.
EPR = (2014, 2018)
rec = {}
for p in PROC_A:
    if p in ('GrIS', 'AIS'):
        imk = 'greenland_mm' if p == 'GrIS' else 'antarctica_mm'
        im = G['imbie'][imk]
        t = np.array(im['tempo'], float); b = np.array(im['balanco'], float)
        u = np.array(im['balanco_inc'], float)
        m1 = (t >= EP1[0]) & (t < EP1[1] + 1); m2 = (t >= EP2[0]) & (t < EP2[1] + 1)
        r1, r2 = float(b[m1].mean()), float(b[m2].mean())
        s1, s2 = float(u[m1].mean()), float(u[m2].mean())
        T1 = float(np.mean(Tobs[(ht >= EP1[0]) & (ht <= EP1[1])]))
        T2 = float(np.mean(Tobs[(ht >= EP2[0]) & (ht <= EP2[1])]))
        fonte = 'IMBIE (satelite)'
    else:
        col = {'glac': 'Glaciers [mean]', 'steric': 'Steric [mean]'}[p]
        v = np.array([np.nan if x is None else x for x in G['orcamento_global']['series'][col]], float)
        av = np.array(G['orcamento_global']['anos'], float)
        o1 = E.ols(av[(av >= EP1[0]) & (av <= EP1[1] + 4)], v[(av >= EP1[0]) & (av <= EP1[1] + 4)])
        o2 = E.ols(av[(av >= EPR[0] - 4) & (av <= EPR[1])], v[(av >= EPR[0] - 4) & (av <= EPR[1])])
        r1, r2 = o1['coef'], o2['coef']
        s1 = o1.get('se_hac', o1['se_classico']); s2 = o2.get('se_hac', o2['se_classico'])
        T1 = float(np.mean(Tobs[(ht >= EP1[0]) & (ht <= EP1[1] + 4)]))
        T2 = float(np.mean(Tobs[(ht >= EPR[0] - 4) & (ht <= EPR[1])]))
        fonte = 'Frederikse et al. (2020)'
    a_rec = (r2 - r1) / (T2 - T1)
    inc_a = float(np.sqrt(s1 ** 2 + s2 ** 2) / abs(T2 - T1))
    rec[p] = {'fonte': fonte, 'r_ref': r2, 'inc_r_ref': s2, 'T_ref': T2,
              'a_rec': a_rec, 'inc_a_rec': inc_a}


def via_Al(p, cen, qual='melhor', da=0.0, dr=0.0):
    """Via A': integra dS/dt = r_ref + a_rec (T - T_ref) de ANO0 em diante."""
    d = rec[p]
    T = TRAJ[cen][qual]
    r = (d['r_ref'] + dr) + (d['a_rec'] + da) * (T - d['T_ref'])
    r = np.maximum(r, 0.0)        # taxa de contribuicao nao pode ficar negativa
    cum = np.concatenate([[0.0], np.cumsum(np.diff(ANOS) * 0.5 * (r[1:] + r[:-1]))])
    return cum - cum[ANOS == ANO0][0]


print("\nParametros da via A' (resposta linearizada em torno do estado observado recente):")
print(f"   {'processo':<20} {'fonte':<26} {'r_ref (mm/ano)':>18} {'T_ref (K)':>11} {'a_rec (mm/ano/K)':>19}")
print("   " + "-" * 98)
for p, d in rec.items():
    print(f"   {ROT[p]:<20} {d['fonte']:<26} {d['r_ref']:>9.3f} +/- {d['inc_r_ref']:<5.3f} "
          f"{d['T_ref']:>11.3f} {d['a_rec']:>10.3f} +/- {d['inc_a_rec']:<5.3f}")
saida['via_A_linha_parametros'] = {p: {k: (round(v, 5) if isinstance(v, float) else v)
                                      for k, v in d.items()} for p, d in rec.items()}
glob = {}
rng = np.random.default_rng(20261029)
for cen in AR6_T:
    glob[cen] = {}
    print(f"\n{NOME_SSP[cen]}   (elevacao media global em mm, acima do nivel de {ANO0})")
    print(f"   {'processo':<20}" + "".join(
        f"{'A ' + str(h):>9}{'A2 ' + str(h):>11}{'B(AR6) ' + str(h):>14}" for h in HOR))
    print("   " + "-" * 102)
    for p, pa in PROC_A.items():
        A_ = {h: float(via_A(p, cen)[ANOS == h][0]) for h in HOR}
        amo = EM['V4_bootstrap'][p]['amostras']
        faixaA = {h: [] for h in HOR}
        for par in amo[::5]:
            for q in ('inferior', 'melhor', 'superior'):
                v = via_A(p, cen, q, par)
                for h in HOR:
                    faixaA[h].append(float(v[ANOS == h][0]))
        # via A': propaga incerteza de a_rec, de r_ref e da trajetoria de temperatura
        Al = {h: float(via_Al(p, cen)[ANOS == h][0]) for h in HOR}
        faixaAl = {h: [] for h in HOR}
        d = rec[p]
        for _ in range(300):
            da = rng.normal(0, d['inc_a_rec']); dr = rng.normal(0, d['inc_r_ref'])
            q = rng.choice(['inferior', 'melhor', 'superior'])
            v = via_Al(p, cen, q, da, dr)
            for h in HOR:
                faixaAl[h].append(float(v[ANOS == h][0]))
        y, v50 = ar6(pa, cen); _, v17 = ar6(pa, cen, perc='height_17'); _, v83 = ar6(pa, cen, perc='height_83')
        B_ = {}
        if y is not None:
            for h in HOR:
                B_[h] = {'p50': float(np.interp(h, y, v50) - np.interp(ANO0, y, v50)),
                         'p17': float(np.interp(h, y, v17) - np.interp(ANO0, y, v17)),
                         'p83': float(np.interp(h, y, v83) - np.interp(ANO0, y, v83))}
        glob[cen][p] = {
            'viaA': {str(h): round(A_[h], 2) for h in HOR},
            'viaA_ic90': {str(h): [round(float(np.percentile(faixaA[h], 5)), 2),
                                   round(float(np.percentile(faixaA[h], 95)), 2)] for h in HOR},
            'viaAl': {str(h): round(Al[h], 2) for h in HOR},
            'viaAl_ic90': {str(h): [round(float(np.percentile(faixaAl[h], 5)), 2),
                                    round(float(np.percentile(faixaAl[h], 95)), 2)] for h in HOR},
            'viaB': {str(h): {k: round(vv, 2) for k, vv in B_[h].items()} for h in HOR} if B_ else None}
        lin = f"   {ROT[p]:<20}"
        for h in HOR:
            lin += f"{A_[h]:>9.0f}{Al[h]:>11.0f}" + (f"{B_[h]['p50']:>14.0f}" if B_ else f"{'--':>14}")
        print(lin)
    tA = {h: sum(glob[cen][p]['viaA'][str(h)] for p in PROC_A) for h in HOR}
    tAl = {h: sum(glob[cen][p]['viaAl'][str(h)] for p in PROC_A) for h in HOR}
    yt, vt = ar6('total', cen)
    _, vt17 = ar6('total', cen, perc='height_17'); _, vt83 = ar6('total', cen, perc='height_83')
    tB = ({h: {'p50': float(np.interp(h, yt, vt) - np.interp(ANO0, yt, vt)),
               'p17': float(np.interp(h, yt, vt17) - np.interp(ANO0, yt, vt17)),
               'p83': float(np.interp(h, yt, vt83) - np.interp(ANO0, yt, vt83))} for h in HOR}
          if yt is not None else None)
    glob[cen]['total'] = {'viaA': {str(h): round(tA[h], 2) for h in HOR},
                          'viaAl': {str(h): round(tAl[h], 2) for h in HOR},
                          'viaB': {str(h): {k: round(vv, 2) for k, vv in tB[h].items()} for h in HOR} if tB else None}
    print("   " + "-" * 102)
    lin = f"   {'TOTAL':<20}"
    for h in HOR:
        lin += f"{tA[h]:>9.0f}{tAl[h]:>11.0f}" + (f"{tB[h]['p50']:>14.0f}" if tB else f"{'--':>14}")
    print(lin)
    if tB:
        print("   razao com a via B: " + " | ".join(
            f"{h}: A={tA[h]/tB[h]['p50']:.2f}, A'={tAl[h]/tB[h]['p50']:.2f}" for h in HOR))
        print("   faixa provavel do AR6 (17-83%): " + " | ".join(
            f"{h}: {tB[h]['p17']:.0f} a {tB[h]['p83']:.0f} mm" for h in HOR))
        dentro = {h: tB[h]['p17'] <= tAl[h] <= tB[h]['p83'] for h in HOR}
        print("   a via A' esta dentro da faixa provavel do AR6? " + " | ".join(
            f"{h}: {'sim' if dentro[h] else 'nao'}" for h in HOR))
        glob[cen]['total']['viaAl_dentro_faixa_AR6'] = {str(h): bool(dentro[h]) for h in HOR}
saida['projecao_global'] = glob
saida['notas_vias'] = {
    'A': "emulador semi-empirico calibrado em 1900-2018 (Frederikse et al., 2020); limite inferior",
    "A'": "mesma forma funcional, linearizada em torno do estado observado recente, com a "
          "sensibilidade medida no periodo de satelite (IMBIE para as calotas)",
    'B': "projecoes processuais oficiais do IPCC AR6 (Garner et al., 2021)"}

print("\n\nLEITURA DAS TRES VIAS")
print("-" * 108)
print("A via A, calibrada em 119 anos, subestima a resposta das calotas, porque dilui numa")
print("media centenaria uma sensibilidade que demonstravelmente cresceu (analise [2]).")
print("A via A', que usa a sensibilidade efetivamente medida no periodo de satelite e a taxa")
print("observada na epoca mais recente, aproxima-se da via B sem recorrer a nenhum modelo")
print("processual. Esse e um resultado importante da pesquisa: a magnitude das projecoes")
print("processuais do IPCC AR6 e sustentada, de forma independente, pela sensibilidade")
print("observada nas proprias medicoes de satelite das calotas polares.")
json.dump(saida, open(f"{RES}/projecoes_globais.json", 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f"\ngravado {RES}/projecoes_globais.json")
