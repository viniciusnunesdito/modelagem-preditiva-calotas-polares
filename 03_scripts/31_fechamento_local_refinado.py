# -*- coding: utf-8 -*-
"""
Etapa 31: fechamento local refinado do orcamento do nivel do mar nas estacoes brasileiras.

Melhorias em relacao a etapa 30:
 (a) a impressao digital de cada processo e recalculada no MESMO periodo do teste de
     fechamento, e nao fixada em 1993-2018, porque a distribuicao geografica da perda
     de massa muda ao longo do tempo e com ela o padrao espacial;
 (b) a serie temporal local completa de cada contribuinte e reconstruida ponto a ponto
     a partir dos campos espaciais, em vez de escalar a serie global, o que elimina a
     aproximacao de separabilidade;
 (c) a incerteza da soma prevista e propagada a partir dos erros padrao dos campos
     (variaveis *_sterr) e da incerteza do VLM;
 (d) o teste e repetido em dois periodos (serie completa e era altimetrica);
 (e) registra-se explicitamente a defasagem de epoca entre o registro maregrafico e a
     serie GNSS, que e uma limitacao real da atribuicao do VLM.
"""
import os, sys, json, importlib
import numpy as np
import xarray as xr

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
E = importlib.import_module('05_estatistica')
RAW, OUT, RES = "01_dados_brutos", "02_dados_processados", "05_resultados"

VLM = json.load(open(f"{OUT}/vlm_gnss.json", encoding='utf-8'))
PS = json.load(open(f"{OUT}/psmsl_series_anuais.json", encoding='utf-8'))

CAMPOS = {'GrIS': ('GrIS.nc', 'Groenlandia'), 'AIS': ('AIS.nc', 'Antartica'),
          'glac': ('glac.nc', 'Geleiras de montanha'), 'tws': ('tws.nc', 'Agua continental')}
ALVOS = [('ILHA_FISCAL_RJ', '1032', 'Ilha Fiscal (RJ)'),
         ('CANANEIA_SP', '726', 'Cananeia (SP)')]

ds = {k: xr.open_dataset(f"{RAW}/frederikse2020/{a}") for k, (a, _) in CAMPOS.items()}
dst = xr.open_dataset(f"{RAW}/frederikse2020/steric.nc")


def extrai(da, lat, lon):
    """Serie temporal no ponto oceanico valido mais proximo."""
    lo = lon % 360
    nt = da.sizes['time']
    for r in [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]:
        sub = da.sel(lat=slice(lat - r - .26, lat + r + .26), lon=slice(lo - r - .26, lo + r + .26))
        if sub.sizes.get('lat', 0) == 0 or sub.sizes.get('lon', 0) == 0:
            continue
        arr = sub.values
        val = np.isfinite(arr).sum(axis=0) >= 0.9 * nt
        if val.any():
            la, ln = sub['lat'].values, sub['lon'].values
            LA, LN = np.meshgrid(la, ln, indexing='ij')
            d = (LA - lat) ** 2 + np.minimum(abs(LN - lo), 360 - abs(LN - lo)) ** 2
            i, j = np.unravel_index(np.argmin(np.where(val, d, np.inf)), d.shape)
            return arr[:, i, j], (float(la[i]), float(ln[j] - 360 if ln[j] > 180 else ln[j])), r
    return None, None, None


def global_pond(da):
    w = np.cos(np.deg2rad(da['lat']))
    return da.weighted(w.broadcast_like(da.isel(time=0)).fillna(0)).mean(dim=('lat', 'lon'), skipna=True).values


saida = {'nota_lacuna': ("Nenhuma das 472 series maregraficas utilizadas por Frederikse et al. "
                         "(2020) para reconstruir as causas da elevacao do nivel do mar e brasileira; "
                         "no Atlantico Sul o conjunto usa apenas estacoes da Argentina, Uruguai, "
                         "Africa do Sul e Namibia."),
         'estacoes': {}}

for cod, sid, nome in ALVOS:
    s = PS[sid]
    a_obs = np.array(s['anos'], float); y_obs = np.array(s['nivel_mm'], float)
    lat, lon = s['lat'], s['lon']
    vl = VLM['estacoes_maregraficas'][cod]
    print("=" * 104)
    print(f"{nome}   lat {lat:.3f}  lon {lon:.3f}   registro maregrafico "
          f"{int(a_obs.min())}-{int(a_obs.max())} ({len(a_obs)} anos validos)")
    print("=" * 104)

    # series locais e globais de cada processo (independentes do periodo)
    loc, glb, locerr, grade = {}, {}, {}, {}
    for k, (arq, rot) in CAMPOS.items():
        da = ds[k][[v for v in ds[k].data_vars if v.endswith('rsl_mean')][0]]
        de = ds[k][[v for v in ds[k].data_vars if v.endswith('rsl_sterr')][0]]
        sl, pg, rr = extrai(da, lat, lon)
        se, _, _ = extrai(de, lat, lon)
        loc[k] = (da['time'].values.astype(float), sl)
        locerr[k] = se
        glb[k] = (da['time'].values.astype(float), global_pond(da))
        grade[k] = {'ponto': pg, 'raio_graus': rr}
    stv = dst['steric_mean']; ste = dst['steric_sterr']
    sl_st, pg_st, rr_st = extrai(stv, lat, lon)
    se_st, _, _ = extrai(ste, lat, lon)
    t_st = stv['time'].values.astype(float)

    res_est = {'nome': nome, 'lat': lat, 'lon': lon,
               'registro': [int(a_obs.min()), int(a_obs.max())], 'n_anos': len(a_obs),
               'vlm': {'vu_mm_ano': vl['vlm_mm_ano'], 'inc': vl['vlm_inc_mm_ano'],
                       'n_gnss': vl['n_gnss'], 'periodo_gnss': vl['periodo_gnss'],
                       'defasagem_epoca': ("a serie GNSS cobre " f"{vl['periodo_gnss'][0]:.0f}-{vl['periodo_gnss'][1]:.0f}"
                                           f", enquanto o registro maregrafico cobre "
                                           f"{int(a_obs.min())}-{int(a_obs.max())}; assume-se VLM constante")},
               'pontos_de_grade': grade, 'periodos': {}}

    per_cand = [(max(int(a_obs.min()), 1957), min(int(a_obs.max()), 2018)), (1993, 2018)]
    for ini, fim in per_cand:
        mo = (a_obs >= ini) & (a_obs <= fim)
        if mo.sum() < 15:
            print(f"\n--- {ini}-{fim}: apenas {int(mo.sum())} anos de maregrafo, periodo descartado ---")
            continue
        print(f"\n{'-'*104}\nPERIODO {ini}-{fim}  ({int(mo.sum())} anos de maregrafo)\n{'-'*104}")
        tobs = E.tendencia_completa(a_obs[mo], y_obs[mo], nome)
        o = tobs['ols']; ic = o.get('ic95_hac', o['ic95_classico'])
        print("\n[1] Tendencia observada:")
        E.imprime_tendencia(tobs)

        print(f"\n[2] Decomposicao fisica, com impressao digital recalculada em {ini}-{fim}:")
        print(f"{'Processo':<26} {'global':>9} {'local':>9} {'FP':>7} {'inc.':>7}")
        print("-" * 64)
        soma, var, det = 0.0, 0.0, {}
        for k, (arq, rot) in CAMPOS.items():
            tl, sl = loc[k]; tg, sg = glb[k]
            m = (tl >= ini) & (tl <= fim)
            ol = E.ols(tl[m], sl[m]); og = E.ols(tg[m], sg[m])
            fp = ol['coef'] / og['coef'] if og['coef'] != 0 else np.nan
            # incerteza do processo local: tendencia do campo de erro padrao
            oe = E.ols(tl[m], locerr[k][m])
            inc = abs(oe['coef']) if oe else 0.0
            soma += ol['coef']; var += inc ** 2
            det[k] = {'rotulo': rot, 'global': round(og['coef'], 4), 'local': round(ol['coef'], 4),
                      'fp': round(float(fp), 4), 'inc': round(inc, 4)}
            print(f"{rot:<26} {og['coef']:>+9.3f} {ol['coef']:>+9.3f} {fp:>7.3f} {inc:>7.3f}")
        m = (t_st >= ini) & (t_st <= fim)
        ost = E.ols(t_st[m], sl_st[m]); ose = E.ols(t_st[m], se_st[m])
        inc_st = abs(ose['coef']) if ose else 0.0
        soma += ost['coef']; var += inc_st ** 2
        det['esterico_dinamico'] = {'rotulo': 'Esterico/dinamico local', 'local': round(ost['coef'], 4),
                                    'inc': round(inc_st, 4), 'ponto': pg_st}
        print(f"{'Esterico/dinamico local':<26} {'':>9} {ost['coef']:>+9.3f} {'':>7} {inc_st:>7.3f}")
        cvlm = -vl['vlm_mm_ano']
        soma += cvlm; var += vl['vlm_inc_mm_ano'] ** 2
        det['vlm'] = {'rotulo': 'Movimento do terreno', 'local': round(cvlm, 4),
                      'inc': vl['vlm_inc_mm_ano'], 'vu_gnss': vl['vlm_mm_ano']}
        print(f"{'Movimento do terreno':<26} {'':>9} {cvlm:>+9.3f} {'':>7} {vl['vlm_inc_mm_ano']:>7.3f}")
        inc_soma = float(np.sqrt(var))
        print("-" * 64)
        print(f"{'SOMA PREVISTA':<26} {'':>9} {soma:>+9.3f} {'':>7} {inc_soma:>7.3f}  (+/- 1 sigma)")
        print(f"{'OBSERVADO':<26} {'':>9} {o['coef']:>+9.3f}        IC95 HAC {ic[0]:+.2f} a {ic[1]:+.2f}")
        resid = o['coef'] - soma
        se_obs = o.get('se_hac', o['se_classico'])
        z = resid / np.sqrt(se_obs ** 2 + inc_soma ** 2)
        fecha = abs(z) < 1.96
        print(f"{'RESIDUO':<26} {'':>9} {resid:>+9.3f}        z = {z:+.2f} -> "
              f"{'FECHA (compativel)' if fecha else 'NAO FECHA (discrepancia significativa)'}")
        cal = det['GrIS']['local'] + det['AIS']['local']
        print(f"\n   Calotas polares: {cal:+.3f} mm/ano  =  {100*cal/o['coef']:.1f}% do observado  "
              f"e  {100*cal/soma:.1f}% da soma prevista")
        res_est['periodos'][f"{ini}-{fim}"] = {
            'n_anos': int(mo.sum()), 'observado': tobs, 'decomposicao': det,
            'soma_prevista': round(soma, 4), 'inc_soma': round(inc_soma, 4),
            'residuo': round(resid, 4), 'z': round(float(z), 3), 'fecha': bool(fecha),
            'calotas_mm_ano': round(cal, 4),
            'parcela_calotas_observado_pct': round(100 * cal / o['coef'], 1),
            'parcela_calotas_soma_pct': round(100 * cal / soma, 1)}
    saida['estacoes'][cod] = res_est
    print()

for d in ds.values(): d.close()
dst.close()
json.dump(saida, open(f"{RES}/fechamento_local_refinado.json", 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
print(f"gravado {RES}/fechamento_local_refinado.json")
