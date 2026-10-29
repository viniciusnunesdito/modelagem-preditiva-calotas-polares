# -*- coding: utf-8 -*-
"""
Etapa 30: fechamento do orcamento do nivel do mar, do global ao local.

Esta e a etapa que sustenta cientificamente a predicao. A logica e a seguinte: se a
soma independente dos processos fisicos (degelo das calotas, geleiras, agua continental,
expansao termica, movimento do terreno), cada um medido por um instrumento diferente,
reproduz a tendencia efetivamente registrada pelos maregrafos brasileiros, entao a
cadeia causal "degelo polar -> elevacao na costa brasileira" esta demonstrada com dados,
e nao assumida. Um modelo preditivo construido sobre essa cadeia herda essa validacao.

Tres niveis de teste, do mais estabelecido ao mais exigente:
  N1. Global   : soma dos contribuintes vs nivel medio global observado (1900-2018 e 1993-2018)
  N2. Regional : idem para a bacia do Atlantico Sul
  N3. Local    : baristatico x impressao digital + esterico local + VLM vs maregrafo brasileiro

Equacao do nivel relativo do mar em um ponto x:
    RSL(x) = SOMA_p [ FP_p(x) * B_p ]  +  SD(x)  -  VLM(x)
onde B_p e a contribuicao baristatica global do processo p, FP_p(x) a impressao digital
desse processo em x, SD(x) o nivel do mar esterico/dinamico local e VLM(x) a velocidade
vertical do terreno (positiva para soerguimento, que reduz o nivel relativo).
"""
import os, sys, json, importlib
import numpy as np
import xarray as xr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
E = importlib.import_module('05_estatistica')

RAW, OUT, RES = "01_dados_brutos", "02_dados_processados", "05_resultados"
os.makedirs(RES, exist_ok=True)

G = json.load(open(f"{OUT}/dados_globais.json", encoding='utf-8'))
FP = json.load(open(f"{OUT}/impressoes_digitais.json", encoding='utf-8'))
VLM = json.load(open(f"{OUT}/vlm_gnss.json", encoding='utf-8'))
PS = json.load(open(f"{OUT}/psmsl_series_anuais.json", encoding='utf-8'))
saida = {}

# =====================================================================================
print("=" * 98)
print("N1. FECHAMENTO GLOBAL: soma dos contribuintes vs nivel medio global observado")
print("=" * 98)
orc = G['orcamento_global']
anos = np.array(orc['anos'], float)
S = orc['series']


def serie(nome):
    return np.array([np.nan if v is None else v for v in S[nome]], float)


COMP = [('Steric', 'Expansao termica e halosterica'), ('Glaciers', 'Geleiras de montanha'),
        ('Greenland Ice Sheet', 'Manto da Groenlandia'), ('Antarctic Ice Sheet', 'Manto da Antartica'),
        ('Terrestrial Water Storage', 'Agua continental')]

for per in [(1900, 2018), (1957, 2018), (1993, 2018)]:
    m = (anos >= per[0]) & (anos <= per[1])
    print(f"\n--- Periodo {per[0]}-{per[1]} ({m.sum()} anos) ---")
    print(f"{'Componente':<34} {'tendencia (mm/ano)':>20} {'IC95 HAC':>24}")
    print("-" * 82)
    tot = 0.0
    det = {}
    for col, nome in COMP:
        o = E.ols(anos[m], serie(f"{col} [mean]")[m])
        if o is None: continue
        tot += o['coef']
        ic = o.get('ic95_hac', o['ic95_classico'])
        print(f"{nome:<34} {o['coef']:>+14.3f}       {ic[0]:>+9.3f} a {ic[1]:>+8.3f}")
        det[nome] = {'coef': round(o['coef'], 4), 'ic95': [round(ic[0], 4), round(ic[1], 4)]}
    o_soma = E.ols(anos[m], serie('Sum of contributors [mean]')[m])
    o_obs = E.ols(anos[m], serie('Observed GMSL [mean]')[m])
    print("-" * 82)
    ics = o_soma.get('ic95_hac', o_soma['ic95_classico']); ico = o_obs.get('ic95_hac', o_obs['ic95_classico'])
    print(f"{'SOMA DOS CONTRIBUINTES':<34} {o_soma['coef']:>+14.3f}       {ics[0]:>+9.3f} a {ics[1]:>+8.3f}")
    print(f"{'NIVEL MEDIO GLOBAL OBSERVADO':<34} {o_obs['coef']:>+14.3f}       {ico[0]:>+9.3f} a {ico[1]:>+8.3f}")
    resid = o_obs['coef'] - o_soma['coef']
    inc_comb = np.sqrt(((ics[1]-ics[0])/3.92)**2 + ((ico[1]-ico[0])/3.92)**2)
    fecha = abs(resid) <= 1.96 * inc_comb
    print(f"{'RESIDUO (observado - soma)':<34} {resid:>+14.3f}       "
          f"{'FECHA' if fecha else 'NAO FECHA'} (|res| {'<=' if fecha else '>'} 1,96 x inc. combinada = {1.96*inc_comb:.3f})")
    # verificacao independente com altimetria quando disponivel
    if per[0] >= 1993:
        aa = np.array(G['altimetria_gmsl']['anos'], float); vv = np.array(G['altimetria_gmsl']['valores'], float)
        ma = (aa >= per[0]) & (aa <= per[1])
        oalt = E.ols(aa[ma], vv[ma])
        print(f"{'(altimetria NOAA, verificacao)':<34} {oalt['coef']:>+14.3f}       "
              f"{oalt.get('ic95_hac', oalt['ic95_classico'])[0]:>+9.3f} a {oalt.get('ic95_hac', oalt['ic95_classico'])[1]:>+8.3f}")
    saida.setdefault('global', {})[f"{per[0]}-{per[1]}"] = {
        'componentes': det, 'soma': round(o_soma['coef'], 4), 'observado': round(o_obs['coef'], 4),
        'residuo': round(resid, 4), 'fecha': bool(fecha),
        'calotas_mm_ano': round(det['Manto da Groenlandia']['coef'] + det['Manto da Antartica']['coef'], 4),
        'parcela_calotas_pct': round(100 * (det['Manto da Groenlandia']['coef'] + det['Manto da Antartica']['coef']) / o_obs['coef'], 1)}
    pc = saida['global'][f"{per[0]}-{per[1]}"]
    print(f"\n   >>> Contribuicao das duas calotas polares: {pc['calotas_mm_ano']:.3f} mm/ano "
          f"= {pc['parcela_calotas_pct']:.1f}% da elevacao global observada")

# =====================================================================================
print("\n" + "=" * 98)
print("N2. FECHAMENTO REGIONAL: bacia do Atlantico Sul")
print("=" * 98)
orc2 = G['orcamento_atlantico_sul']
anos2 = np.array(orc2['anos'], float); S2 = orc2['series']
COMP2 = COMP + [('GIA', 'Ajuste isostatico glacial (GIA)')]
for per in [(1900, 2018), (1993, 2018)]:
    m = (anos2 >= per[0]) & (anos2 <= per[1])
    print(f"\n--- Atlantico Sul, {per[0]}-{per[1]} ---")
    tot, det = 0.0, {}
    for col, nome in COMP2:
        k = f"{col} [mean]"
        if k not in S2: continue
        v = np.array([np.nan if x is None else x for x in S2[k]], float)
        o = E.ols(anos2[m], v[m])
        if o is None: continue
        det[nome] = round(o['coef'], 4); tot += o['coef']
        print(f"   {nome:<34} {o['coef']:>+8.3f} mm/ano")
    vs = np.array([np.nan if x is None else x for x in S2['Sum of contributors [mean]']], float)
    vo = np.array([np.nan if x is None else x for x in S2['Observed basin-mean sea level [mean]']], float)
    os_, oo = E.ols(anos2[m], vs[m]), E.ols(anos2[m], vo[m])
    print(f"   {'SOMA DOS CONTRIBUINTES':<34} {os_['coef']:>+8.3f} mm/ano")
    print(f"   {'NIVEL OBSERVADO NA BACIA':<34} {oo['coef']:>+8.3f} mm/ano")
    print(f"   {'RESIDUO':<34} {oo['coef']-os_['coef']:>+8.3f} mm/ano")
    cal = det.get('Manto da Groenlandia', 0) + det.get('Manto da Antartica', 0)
    print(f"   >>> Calotas polares no Atlantico Sul: {cal:.3f} mm/ano = {100*cal/oo['coef']:.1f}% do observado")
    saida.setdefault('atlantico_sul', {})[f"{per[0]}-{per[1]}"] = {
        'componentes': det, 'soma': round(os_['coef'], 4), 'observado': round(oo['coef'], 4),
        'residuo': round(oo['coef'] - os_['coef'], 4), 'calotas_mm_ano': round(cal, 4),
        'parcela_calotas_pct': round(100 * cal / oo['coef'], 1)}

# =====================================================================================
print("\n" + "=" * 98)
print("N3. FECHAMENTO LOCAL nas estacoes maregraficas brasileiras de serie longa")
print("=" * 98)

# nivel do mar esterico/dinamico local, de Frederikse et al. (2020)
ds = xr.open_dataset(f"{RAW}/frederikse2020/steric.nc")
st = ds['steric_mean']
t_st = st['time'].values.astype(float)


def ponto(da, lat, lon, nt):
    lo = lon % 360
    for r in [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]:
        sub = da.sel(lat=slice(lat - r - .26, lat + r + .26), lon=slice(lo - r - .26, lo + r + .26))
        if sub.sizes.get('lat', 0) == 0 or sub.sizes.get('lon', 0) == 0: continue
        arr = sub.values
        val = np.isfinite(arr).sum(axis=0) >= 0.9 * nt
        if val.any():
            la, ln = sub['lat'].values, sub['lon'].values
            LA, LN = np.meshgrid(la, ln, indexing='ij')
            d = (LA - lat) ** 2 + np.minimum(abs(LN - lo), 360 - abs(LN - lo)) ** 2
            i, j = np.unravel_index(np.argmin(np.where(val, d, np.inf)), d.shape)
            return arr[:, i, j], float(la[i]), float(ln[j] if ln[j] <= 180 else ln[j] - 360), r
    return None, None, None, None


# contribuicoes baristaticas globais por processo, em series anuais (Frederikse global)
BARI = {'GrIS': 'Greenland Ice Sheet [mean]', 'AIS': 'Antarctic Ice Sheet [mean]',
        'glac': 'Glaciers [mean]', 'tws': 'Terrestrial Water Storage [mean]'}
ALVOS = [('ILHA_FISCAL_RJ', '1032', 'Ilha Fiscal (RJ)'), ('CANANEIA_SP', '726', 'Cananeia (SP)')]

for cod, sid, nome in ALVOS:
    s = PS[sid]
    a_obs = np.array(s['anos'], float); y_obs = np.array(s['nivel_mm'], float)
    lat, lon = s['lat'], s['lon']
    fp = FP['locais'][cod]['fp']
    vlm = VLM['estacoes_maregraficas'][cod]

    # periodo comum: maregrafo ^ esterico (1957-2018) ^ baristatico (1900-2018)
    ini = max(int(a_obs.min()), 1957); fim = min(int(a_obs.max()), 2018)
    print(f"\n{'='*98}\n{nome}  |  lat {lat:.3f}  lon {lon:.3f}  |  periodo de fechamento {ini}-{fim}\n{'='*98}")

    mo = (a_obs >= ini) & (a_obs <= fim)
    tend_obs = E.tendencia_completa(a_obs[mo], y_obs[mo], nome)
    print(f"\n[1] Tendencia observada pelo maregrafo ({int(mo.sum())} anos validos):")
    E.imprime_tendencia(tend_obs)

    print(f"\n[2] Decomposicao fisica da tendencia esperada no mesmo periodo:")
    print(f"{'Processo':<30} {'global':>9} {'x FP':>7} {'= local':>9}   observacao")
    print("-" * 86)
    soma, detalhe = 0.0, {}
    for p, col in BARI.items():
        v = np.array([np.nan if x is None else x for x in S[col]], float)
        mm = (anos >= ini) & (anos <= fim)
        o = E.ols(anos[mm], v[mm])
        loc = o['coef'] * fp[p]
        soma += loc
        detalhe[p] = {'global': round(o['coef'], 4), 'fp': fp[p], 'local': round(loc, 4)}
        rot = {'GrIS': 'Groenlandia', 'AIS': 'Antartica', 'glac': 'Geleiras', 'tws': 'Agua continental'}[p]
        print(f"{rot:<30} {o['coef']:>+9.3f} {fp[p]:>7.3f} {loc:>+9.3f}   baristatico x impressao digital")
    ser, pla, plo, praio = ponto(st, lat, lon, len(t_st))
    msk = (t_st >= ini) & (t_st <= fim)
    o_st = E.ols(t_st[msk], ser[msk])
    soma += o_st['coef']
    detalhe['esterico_dinamico'] = {'local': round(o_st['coef'], 4),
                                    'ponto_grade': [pla, plo], 'raio_busca': praio}
    print(f"{'Esterico/dinamico local':<30} {'':>9} {'':>7} {o_st['coef']:>+9.3f}   campo de Frederikse et al. (2020)")
    contrib_vlm = -vlm['vlm_mm_ano']   # subsidencia (VLM<0) eleva o nivel relativo
    soma += contrib_vlm
    detalhe['vlm'] = {'vu_gnss': vlm['vlm_mm_ano'], 'inc': vlm['vlm_inc_mm_ano'],
                      'contribuicao_rsl': round(contrib_vlm, 4), 'n_gnss': vlm['n_gnss']}
    print(f"{'Movimento vertical do terreno':<30} {'':>9} {'':>7} {contrib_vlm:>+9.3f}   "
          f"GNSS vu = {vlm['vlm_mm_ano']:+.2f} mm/ano ({vlm['n_gnss']} estacoes)")
    print("-" * 86)
    print(f"{'SOMA PREVISTA PELA FISICA':<30} {'':>9} {'':>7} {soma:>+9.3f} mm/ano")
    obs = tend_obs['ols']['coef']
    ic_obs = tend_obs['ols'].get('ic95_hac', tend_obs['ols']['ic95_classico'])
    print(f"{'OBSERVADO PELO MAREGRAFO':<30} {'':>9} {'':>7} {obs:>+9.3f} mm/ano  (IC95 {ic_obs[0]:+.2f} a {ic_obs[1]:+.2f})")
    res = obs - soma
    dentro = ic_obs[0] <= soma <= ic_obs[1]
    print(f"{'RESIDUO (obs - previsto)':<30} {'':>9} {'':>7} {res:>+9.3f} mm/ano")
    print(f"\n   >>> A soma dos processos fisicos {'ESTA' if dentro else 'NAO esta'} dentro do intervalo de")
    print(f"       confianca de 95% da tendencia observada. "
          f"{'O orcamento local fecha.' if dentro else 'O orcamento local nao fecha.'}")
    cal_loc = detalhe['GrIS']['local'] + detalhe['AIS']['local']
    print(f"   >>> Parcela das calotas polares na tendencia observada: {cal_loc:.3f} mm/ano "
          f"= {100*cal_loc/obs:.1f}% de {obs:.3f} mm/ano")
    print(f"   >>> Parcela das calotas na soma prevista: {100*cal_loc/soma:.1f}%")

    saida.setdefault('local', {})[cod] = {
        'nome': nome, 'lat': lat, 'lon': lon, 'periodo': [ini, fim],
        'n_anos': int(mo.sum()), 'observado': tend_obs, 'decomposicao': detalhe,
        'soma_prevista': round(soma, 4), 'residuo': round(res, 4), 'fecha': bool(dentro),
        'calotas_local_mm_ano': round(cal_loc, 4),
        'parcela_calotas_do_observado_pct': round(100 * cal_loc / obs, 1),
        'parcela_calotas_da_soma_pct': round(100 * cal_loc / soma, 1)}

ds.close()
json.dump(saida, open(f"{RES}/fechamento_orcamento.json", 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f"\n\ngravado {RES}/fechamento_orcamento.json")
