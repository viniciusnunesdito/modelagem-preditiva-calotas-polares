# -*- coding: utf-8 -*-
"""
Etapa 43: projecoes de nivel RELATIVO do mar nas estacoes brasileiras e parcela das calotas.

CADEIA DE CALCULO
-----------------
Para cada estacao x, cenario c e horizonte h:

  RSL(x,c,h) = SOMA_p [ FP_p(x) * S_p(c,h) ]  +  FP_esterico(x) * S_esterico(c,h)
               +  S_agua_continental(c,h)     -  VLM(x) * (h - 2020)

onde S_p vem da etapa 42 (vias A, A' e B), FP_p(x) da etapa 20 (impressoes digitais
calculadas a partir dos campos de Frederikse et al., 2020) e VLM(x) da etapa 22 (GNSS).

VALIDACAO
---------
As projecoes oficiais do IPCC AR6 existem para seis estacoes maregraficas brasileiras,
ja com impressao digital, dinamica oceanica e movimento vertical do terreno embutidos.
Comparar a cadeia reconstruida aqui com esses valores e um teste direto de toda a
cadeia, e nao apenas de uma peca dela.

RESULTADO PRINCIPAL
-------------------
A fracao da elevacao projetada em cada ponto do litoral brasileiro atribuivel
especificamente ao degelo dos mantos de gelo da Groenlandia e da Antartica.
"""
import os, sys, json, importlib, warnings
import numpy as np
import xarray as xr

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
E = importlib.import_module('05_estatistica')
OUT, RES, RAW = "02_dados_processados", "05_resultados", "01_dados_brutos"

PR = json.load(open(f"{RES}/projecoes_globais.json", encoding='utf-8'))
FP = json.load(open(f"{OUT}/impressoes_digitais.json", encoding='utf-8'))
VLM = json.load(open(f"{OUT}/vlm_gnss.json", encoding='utf-8'))
ar6g = json.load(open(f"{RAW}/ipcc_ar6/ar6_global.json", encoding='utf-8'))

ANO0, HOR = 2020, [2050, 2100]
SSP = ['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp585']
NOME_SSP = {'ssp119': 'SSP1-1.9', 'ssp126': 'SSP1-2.6', 'ssp245': 'SSP2-4.5',
            'ssp370': 'SSP3-7.0', 'ssp585': 'SSP5-8.5'}
# estacoes com projecao oficial do IPCC AR6 disponivel
AR6_EST = {'IMBITUBA_SC': 542, 'RECIFE_PE': 556, 'SALVADOR_BA': 578,
           'BELEM_PA': 580, 'CANANEIA_SP': 726, 'ILHA_FISCAL_RJ': 1032}

# ------------------------------------------------- padrao esterico/dinamico local/global
# A impressao digital gravitacional nao se aplica ao termo esterico, que nao envolve
# redistribuicao de massa. Para este termo e necessario um fator de padrao local.
#
# OPCAO DESCARTADA: usar a razao entre a tendencia esterica local e a global observada no
# campo de Frederikse et al. (2020), 1957-2018. Essa razao foi calculada e resultou entre
# -0,07 e +0,79 ao longo da costa brasileira, com valores negativos e proximos de zero no
# Norte e no Sul. Isso NAO significa que a expansao termica futura produzira queda do
# nivel do mar nessas regioes: significa que, no periodo historico, a variabilidade
# dinamica decadal mascarou localmente o sinal forcado, e que a cobertura de perfis
# hidrograficos sobre a plataforma e escassa. Aplicar essa razao a uma projecao de
# resposta FORCADA seria um erro de interpretacao: confundiria variabilidade com resposta
# ao forcamento.
#
# OPCAO ADOTADA: usar o padrao da propria resposta forcada, dado pela razao entre a
# projecao de dinamica oceanica do IPCC AR6 na estacao e a correspondente projecao global.
# Esse padrao vem do conjunto CMIP6 e representa a redistribuicao dinamica esperada sob
# aquecimento, que e exatamente a grandeza necessaria aqui. A razao historica e mantida
# no registro apenas para documentar a diferenca entre as duas quantidades.
ds = xr.open_dataset(f"{RAW}/frederikse2020/steric.nc")
st = ds['steric_mean']; t_st = st['time'].values.astype(float)
w = np.cos(np.deg2rad(st['lat']))
gm = st.weighted(w.broadcast_like(st.isel(time=0)).fillna(0)).mean(dim=('lat', 'lon'), skipna=True).values
b_glob = E.ols(t_st, gm)['coef']


def no_ponto(da, lat, lon):
    lo = lon % 360; nt = da.sizes['time']
    for r in [0.0, .5, 1., 1.5, 2., 3., 4., 5.]:
        sub = da.sel(lat=slice(lat - r - .26, lat + r + .26), lon=slice(lo - r - .26, lo + r + .26))
        if sub.sizes.get('lat', 0) == 0 or sub.sizes.get('lon', 0) == 0: continue
        arr = sub.values; val = np.isfinite(arr).sum(axis=0) >= .9 * nt
        if val.any():
            la, ln = sub['lat'].values, sub['lon'].values
            LA, LN = np.meshgrid(la, ln, indexing='ij')
            d = (LA - lat) ** 2 + np.minimum(abs(LN - lo), 360 - abs(LN - lo)) ** 2
            i, j = np.unravel_index(np.argmin(np.where(val, d, np.inf)), d.shape)
            return arr[:, i, j]
    return None


def ar6_local(pid, proc, cen, conf='medium', perc='height_50'):
    d = json.load(open(f"{RAW}/ipcc_ar6/ar6_psmsl_{pid}.json", encoding='utf-8'))
    for r in d:
        if r['process'] == proc and r['scenario'] == cen and r['confidence'] == conf:
            return np.array(r['year'], float), np.array(r[perc], float) * 1000.0
    return None, None


def ar6_glob_tmp(proc, cen, conf='medium', perc='height_50'):
    for r in ar6g:
        if r['process'] == proc and r['scenario'] == cen and r['confidence'] == conf:
            return np.array(r['year'], float), np.array(r[perc], float) * 1000.0
    return None, None


def padrao_dinamico(cod, pid):
    """Razao entre a dinamica oceanica projetada na estacao e a global (media dos SSP)."""
    if pid is None:
        return None
    rs = []
    for cen in SSP:
        yl, vl = ar6_local(pid, 'oceandynamics', cen)
        yg, vg = ar6_glob_tmp('oceandynamics', cen)
        if yl is None or yg is None:
            continue
        for h in (2050, 2100):
            a = float(np.interp(h, yl, vl) - np.interp(ANO0, yl, vl))
            b = float(np.interp(h, yg, vg) - np.interp(ANO0, yg, vg))
            if abs(b) > 1e-6:
                rs.append(a / b)
    return float(np.mean(rs)) if rs else None


print("=" * 110)
print("[1] FATORES LOCAIS APLICADOS A CADA ESTACAO")
print("=" * 110)
print(f"{'Estacao':<24} {'lat':>7} {'FP GrIS':>8} {'FP AIS':>7} {'FP glac':>8} {'FP tws':>7} "
      f"{'pad.dinam':>11} {'VLM mm/ano':>10} {'razao hist':>12}")
print("-" * 110)
LOC = {}
pads = {cod: padrao_dinamico(cod, AR6_EST.get(cod)) for cod in FP['locais']}
pad_med = float(np.mean([v for v in pads.values() if v is not None]))
for cod, d in FP['locais'].items():
    vl = VLM['estacoes_maregraficas'].get(cod)
    sv = no_ponto(st, d['lat'], d['lon'])
    rz_hist = (E.ols(t_st, sv)['coef'] / b_glob) if sv is not None else None
    pad = pads[cod] if pads[cod] is not None else pad_med
    LOC[cod] = {'nome': d['nome'], 'lat': d['lat'], 'lon': d['lon'], 'fp': d['fp'],
                'padrao_dinamico': round(float(pad), 4),
                'padrao_dinamico_interpolado': pads[cod] is None,
                'razao_esterica_historica_descartada': (round(float(rz_hist), 4)
                                                        if rz_hist is not None else None),
                'vlm': (vl['vlm_mm_ano'] if vl else None),
                'vlm_inc': (vl['vlm_inc_mm_ano'] if vl else None),
                'vlm_duracao_efetiva': (vl.get('duracao_efetiva_anos') if vl else None),
                'n_gnss': (vl['n_gnss'] if vl else 0)}
    marca = '*' if pads[cod] is None else ' '
    print(f"{d['nome'][:24]:<24} {d['lat']:>7.2f} {d['fp']['GrIS']:>8.3f} {d['fp']['AIS']:>7.3f} "
          f"{d['fp']['glac']:>8.3f} {d['fp']['tws']:>7.3f} {pad:>10.3f}{marca} "
          + (f"{vl['vlm_mm_ano']:>+10.2f}" if vl else f"{'--':>10}")
          + (f"{rz_hist:>12.3f}" if rz_hist is not None else f"{'--':>12}"))
ds.close()
print("\n* padrao dinamico interpolado pela media das estacoes com projecao do AR6 disponivel")
print(f"Tendencia esterica media global no campo historico (1957-2018): {b_glob:.3f} mm/ano")
print("A ultima coluna traz a razao esterica HISTORICA, calculada e descartada: ela mede")
print("variabilidade dinamica decadal, nao resposta forcada, e por isso nao e usada aqui.")


ar6_global = ar6_glob_tmp


# agua continental: nao e acionada por temperatura (depende de barragens e bombeamento de
# aquiferos); adota-se a projecao do proprio IPCC AR6 em todas as vias, com a impressao
# digital local aplicada.
def comp_global(p, cen, via, h):
    if via == 'B':
        pa = {'GrIS': 'GIS', 'AIS': 'AIS', 'glac': 'glaciers', 'steric': 'oceandynamics'}[p]
        y, v = ar6_global(pa, cen)
        return float(np.interp(h, y, v) - np.interp(ANO0, y, v))
    return PR['projecao_global'][cen][p]['viaA' if via == 'A' else 'viaAl'][str(h)]


y_lw, v_lw = ar6_global('landwaterstorage', 'ssp245')
LW = {h: float(np.interp(h, y_lw, v_lw) - np.interp(ANO0, y_lw, v_lw)) for h in HOR}
print(f"Armazenamento de agua continental (IPCC AR6, comum a todas as vias): "
      + ", ".join(f"{h}: {LW[h]:+.1f} mm" for h in HOR))

# =====================================================================================
print("\n\n" + "=" * 110)
print("[2] PROJECOES DE NIVEL RELATIVO DO MAR NAS ESTACOES BRASILEIRAS")
print("=" * 110)
res = {}
for via in ['A', 'Al', 'B']:
    rot_via = {'A': "VIA A - emulador semi-empirico calibrado em 1900-2018 (limite inferior)",
               'Al': "VIA A' - emulador com a sensibilidade medida no periodo de satelite",
               'B': "VIA B - projecoes processuais oficiais do IPCC AR6"}[via]
    print(f"\n{rot_via}")
    for cen in SSP:
        print(f"\n  {NOME_SSP[cen]}  (mm acima do nivel de {ANO0})")
        print(f"  {'Estacao':<24}" + "".join(
            f"{'RSL ' + str(h):>10}{'calotas':>10}{'%cal':>7}" for h in HOR))
        print("  " + "-" * 76)
        for cod, L in LOC.items():
            if L['vlm'] is None:
                continue
            row = {}
            for h in HOR:
                gr = L['fp']['GrIS'] * comp_global('GrIS', cen, via, h)
                ai = L['fp']['AIS'] * comp_global('AIS', cen, via, h)
                gl = L['fp']['glac'] * comp_global('glac', cen, via, h)
                stc = L['padrao_dinamico'] * comp_global('steric', cen, via, h)
                lw = L['fp']['tws'] * LW[h]
                vl = -L['vlm'] * (h - ANO0)
                tot = gr + ai + gl + stc + lw + vl
                row[h] = {'GrIS': round(gr, 1), 'AIS': round(ai, 1), 'glac': round(gl, 1),
                          'esterico': round(stc, 1), 'agua_continental': round(lw, 1),
                          'vlm': round(vl, 1), 'total': round(tot, 1),
                          'calotas': round(gr + ai, 1),
                          'pct_calotas': round(100 * (gr + ai) / tot, 1) if tot != 0 else None}
            print(f"  {L['nome'][:24]:<24}" + "".join(
                f"{row[h]['total']:>10.0f}{row[h]['calotas']:>10.0f}{row[h]['pct_calotas']:>7.1f}" for h in HOR))
            res.setdefault(via, {}).setdefault(cen, {})[cod] = row

# =====================================================================================
print("\n\n" + "=" * 110)
print("[3] VALIDACAO DA CADEIA: comparacao com as projecoes oficiais do IPCC AR6 por estacao")
print("=" * 110)
print("As projecoes do AR6 por estacao ja incluem impressao digital, dinamica oceanica e")
print("movimento vertical do terreno. Reproduzi-las com a cadeia montada aqui testa a cadeia")
print("inteira, nao apenas uma de suas pecas.")
val = {}
for cen in ['ssp126', 'ssp245', 'ssp585']:
    print(f"\n  {NOME_SSP[cen]}")
    print(f"  {'Estacao':<22}" + "".join(
        f"{'AR6 ' + str(h):>11}{'cadeia(B) ' + str(h):>15}{'dif':>8}{'dif %':>8}" for h in HOR))
    print("  " + "-" * 92)
    for cod, pid in AR6_EST.items():
        if cod not in LOC or LOC[cod]['vlm'] is None:
            continue
        d = json.load(open(f"{RAW}/ipcc_ar6/ar6_psmsl_{pid}.json", encoding='utf-8'))
        of = next((r for r in d if r['process'] == 'total' and r['scenario'] == cen
                   and r['confidence'] == 'medium'), None)
        if of is None:
            continue
        y = np.array(of['year'], float); v = np.array(of['height_50'], float) * 1000.0
        v17 = np.array(of['height_17'], float) * 1000.0; v83 = np.array(of['height_83'], float) * 1000.0
        lin = f"  {LOC[cod]['nome'][:22]:<22}"
        reg = {}
        for h in HOR:
            ofi = float(np.interp(h, y, v) - np.interp(ANO0, y, v))
            o17 = float(np.interp(h, y, v17) - np.interp(ANO0, y, v17))
            o83 = float(np.interp(h, y, v83) - np.interp(ANO0, y, v83))
            meu = res['B'][cen][cod][h]['total']
            lin += f"{ofi:>11.0f}{meu:>15.0f}{meu-ofi:>8.0f}{100*(meu-ofi)/ofi:>8.1f}"
            reg[h] = {'ar6_p50': round(ofi, 1), 'ar6_p17': round(o17, 1), 'ar6_p83': round(o83, 1),
                      'cadeia_B': meu, 'dif': round(meu - ofi, 1),
                      'dif_pct': round(100 * (meu - ofi) / ofi, 1),
                      'dentro_faixa': bool(o17 <= meu <= o83)}
        print(lin)
        val.setdefault(cen, {})[cod] = reg
    difs = [abs(val[cen][c][h]['dif_pct']) for c in val[cen] for h in HOR]
    dentro = sum(val[cen][c][h]['dentro_faixa'] for c in val[cen] for h in HOR)
    print(f"  diferenca absoluta media: {np.mean(difs):.1f}% | "
          f"{dentro}/{len(difs)} valores dentro da faixa provavel (17-83%) do AR6")

# =====================================================================================
print("\n\n" + "=" * 110)
print("[4] RESULTADO PRINCIPAL: parcela das calotas polares na elevacao projetada")
print("=" * 110)
print("Valores da via B (IPCC AR6), que e a referencia internacional.")
print(f"\n{'Estacao':<24} {'lat':>7}" + "".join(f"{NOME_SSP[c]:>12}" for c in SSP))
print("-" * 96)
for h in HOR:
    print(f"\n  parcela das calotas (% da elevacao total projetada) em {h}:")
    for cod, L in LOC.items():
        if L['vlm'] is None: continue
        print(f"  {L['nome'][:24]:<24} {L['lat']:>7.2f}" + "".join(
            f"{res['B'][c][cod][h]['pct_calotas']:>12.1f}" for c in SSP))
    med = [res['B'][c][cod][h]['pct_calotas'] for c in SSP for cod in res['B'][c]]
    print(f"  {'media sobre estacoes e cenarios':<24} {'':>7}  {np.mean(med):.1f}% "
          f"(amplitude {min(med):.1f}% a {max(med):.1f}%)")

print(f"\n{'Estacao':<24}" + "".join(f"{'cal. ' + NOME_SSP[c][:8]:>14}" for c in SSP))
print("-" * 96)
print(f"\n  contribuicao absoluta das calotas em 2100 (mm):")
for cod, L in LOC.items():
    if L['vlm'] is None: continue
    print(f"  {L['nome'][:24]:<24}" + "".join(
        f"{res['B'][c][cod][2100]['calotas']:>14.0f}" for c in SSP))

json.dump({'fatores_locais': LOC, 'agua_continental': {str(h): round(LW[h], 2) for h in HOR},
           'tendencia_esterica_global_historica': round(b_glob, 4),
           'padrao_dinamico_medio': round(pad_med, 4),
           'projecoes': {v: {c: {k: {str(h): res[v][c][k][h] for h in HOR} for k in res[v][c]}
                             for c in res[v]} for v in res},
           'validacao_contra_ar6': val, 'horizontes': HOR, 'ano_base': ANO0},
          open(f"{RES}/projecoes_locais.json", 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f"\n\ngravado {RES}/projecoes_locais.json")
