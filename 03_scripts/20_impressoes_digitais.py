# -*- coding: utf-8 -*-
"""
Etapa 20: impressoes digitais do nivel do mar (sea-level fingerprints) na costa brasileira.

FUNDAMENTO FISICO
-----------------
Quando um manto de gelo perde massa, a agua liberada NAO se distribui uniformemente
pelos oceanos. Tres efeitos atuam simultaneamente (resposta gravitacional, rotacional
e elastica da Terra solida, ou GRD):
  (i)  a atracao gravitacional exercida pelo proprio gelo sobre o oceano diminui, de
       modo que a agua "escorre" para longe da fonte de degelo;
  (ii) a crosta sob o gelo, aliviada do peso, sobe (rebote elastico);
  (iii) a redistribuicao de massa desloca o eixo de rotacao da Terra, alterando o
       geoide de forma padronizada.
O resultado e que, perto da fonte, o nivel RELATIVO do mar CAI, e no campo distante
ele sobe MAIS que a media global. Essa assinatura espacial e a "impressao digital".

Consequencia para esta pesquisa: a costa brasileira esta no campo distante tanto da
Groenlandia quanto da Antartica. Logo, cada milimetro de elevacao media global causado
pelo degelo polar produz MAIS de um milimetro na costa brasileira. Quantificar esse
fator de amplificacao e o que permite ligar causalmente o degelo polar ao litoral
brasileiro, em vez de apenas supor que a media global se aplica localmente.

METODO
------
Usam-se os campos de nivel relativo do mar (variavel *_rsl_mean) de Frederikse et al.
(2020, Nature), que resolvem a equacao do nivel do mar elastica para cada processo
baristatico, em grade de 0,5 graus, 1900-2018.

Para cada processo p e cada ponto x:
    FP_p(x) = tendencia local de RSL_p(x) / tendencia da media global de RSL_p
A media global e calculada como media ponderada pelo cosseno da latitude sobre os
pontos oceanicos (os campos sao definidos sobre o oceano).

FP > 1  => o ponto recebe mais que a media global (campo distante)
FP < 1  => o ponto recebe menos (campo proximo da fonte)
"""
import os, json
import numpy as np
import xarray as xr

RAW, OUT = "01_dados_brutos", "02_dados_processados"
os.makedirs(OUT, exist_ok=True)

PROC = {'GrIS': ('GrIS.nc', 'GrIS_rsl_mean', 'Manto de gelo da Groenlandia'),
        'AIS': ('AIS.nc', 'AIS_rsl_mean', 'Manto de gelo da Antartica'),
        'glac': ('glac.nc', 'glac_rsl_mean', 'Geleiras de montanha'),
        'tws': ('tws.nc', 'tws_rsl_mean', 'Armazenamento de agua continental'),
        'total': ('total.nc', 'total_rsl_mean', 'Todos os processos baristaticos')}

# Estacoes/pontos de interesse na costa brasileira (de norte a sul)
LOCAIS = [
    ('SANTANA_AP',   -0.05,  -51.17, 'Santana (AP), foz do Amazonas'),
    ('BELEM_PA',     -1.45,  -48.50, 'Belem (PA)'),
    ('MADEIRA_MA',   -2.57,  -44.38, 'Ponta da Madeira (MA)'),
    ('FORTALEZA_CE', -3.72,  -38.48, 'Fortaleza (CE)'),
    ('RECIFE_PE',    -8.05,  -34.87, 'Recife (PE)'),
    ('SALVADOR_BA', -12.97,  -38.52, 'Salvador (BA)'),
    ('CANAVIEIRAS_BA', -15.67, -38.97, 'Canavieiras (BA)'),
    ('ILHA_FISCAL_RJ', -22.90, -43.17, 'Ilha Fiscal, Rio de Janeiro (RJ)'),
    ('SANTOS_SP',   -23.98,  -46.30, 'Santos (SP)'),
    ('CANANEIA_SP', -25.02,  -47.93, 'Cananeia (SP)'),
    ('IMBITUBA_SC', -28.23,  -48.65, 'Imbituba (SC)'),
    ('RIO_GRANDE_RS', -32.10, -52.10, 'Rio Grande (RS)'),
]
# Referencias de contraste para demonstrar o contraste campo proximo / campo distante
CONTRASTE = [
    ('NUUK_GROENLANDIA', 64.17, -51.73, 'Nuuk, Groenlandia (campo proximo do GrIS)'),
    ('REYKJAVIK_ISLANDIA', 64.15, -21.94, 'Reykjavik, Islandia'),
    ('NOVA_YORK', 40.70, -74.01, 'Nova York, EUA'),
    ('LISBOA', 38.70, -9.14, 'Lisboa, Portugal'),
    ('CIDADE_DO_CABO', -33.90, 18.42, 'Cidade do Cabo, Africa do Sul'),
    ('SYOWA_ANTARTICA', -69.00, 39.58, 'Base Syowa, Antartica (campo proximo do AIS)'),
]


def tendencia(t, y):
    """Tendencia linear por minimos quadrados. Retorna (coef, erro_padrao)."""
    t = np.asarray(t, float); y = np.asarray(y, float)
    m = np.isfinite(y)
    if m.sum() < 5:
        return np.nan, np.nan
    t, y = t[m], y[m]
    X = np.column_stack([np.ones_like(t), t - t.mean()])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    s2 = res @ res / (len(y) - 2)
    cov = s2 * np.linalg.inv(X.T @ X)
    return float(beta[1]), float(np.sqrt(cov[1, 1]))


def media_global_ponderada(da):
    """Media global ponderada por cos(lat), ignorando NaN (continentes)."""
    w = np.cos(np.deg2rad(da['lat']))
    return da.weighted(w.broadcast_like(da.isel(time=0)).fillna(0)).mean(dim=('lat', 'lon'), skipna=True)


def valor_no_ponto(da, lat, lon):
    """Valor no ponto oceanico valido mais proximo (busca em raio crescente)."""
    lo = lon % 360
    for raio in [0.0, 0.5, 1.0, 1.5, 2.0, 3.0, 4.0, 5.0]:
        sub = da.sel(lat=slice(lat - raio - 0.26, lat + raio + 0.26),
                     lon=slice(lo - raio - 0.26, lo + raio + 0.26))
        if sub.sizes.get('lat', 0) == 0 or sub.sizes.get('lon', 0) == 0:
            continue
        arr = sub.values                      # (time, lat, lon)
        validos = np.isfinite(arr).all(axis=0)
        if validos.any():
            # escolhe o ponto valido geograficamente mais proximo
            la = sub['lat'].values; ln = sub['lon'].values
            LA, LN = np.meshgrid(la, ln, indexing='ij')
            d = (LA - lat) ** 2 + (np.minimum(np.abs(LN - lo), 360 - np.abs(LN - lo))) ** 2
            d = np.where(validos, d, np.inf)
            i, jj = np.unravel_index(np.argmin(d), d.shape)
            return arr[:, i, jj], float(la[i]), float(ln[jj]), raio
    return None, np.nan, np.nan, np.nan


PER = (1993, 2018)   # periodo da era altimetrica, usado para as tendencias
print(f"Impressoes digitais do nivel do mar, tendencias no periodo {PER[0]}-{PER[1]}")
print("=" * 100)

resultado = {'periodo': list(PER), 'locais': {}, 'contraste': {},
             'media_global': {}, 'descricao_processos': {k: v[2] for k, v in PROC.items()}}
campos = {}

for proc, (arq, var, desc) in PROC.items():
    p = f"{RAW}/frederikse2020/{arq}"
    if not os.path.exists(p):
        print(f"  ausente: {arq}")
        continue
    ds = xr.open_dataset(p)
    if var not in ds.data_vars:
        var = [v for v in ds.data_vars if v.endswith('rsl_mean')][0]
    da = ds[var].sel(time=slice(PER[0], PER[1]))
    t = da['time'].values.astype(float)

    gm = media_global_ponderada(da).values
    bg, sg = tendencia(t, gm)
    resultado['media_global'][proc] = {'tendencia_mm_ano': round(bg, 4), 'erro_padrao': round(sg, 4)}
    campos[proc] = (da, t, bg)
    print(f"\n{proc:>6} ({desc})")
    print(f"       tendencia da media global: {bg:+.3f} mm/ano")
    ds.close()

print("\n" + "=" * 100)
print("FATORES DE IMPRESSAO DIGITAL (adimensionais: tendencia local / tendencia global)")
print("=" * 100)
cab = f"{'Local':<22} {'lat':>7} {'lon':>8} | " + " ".join(f"{p:>8}" for p in campos) + f" | {'GrIS+AIS':>9}"
print(cab); print("-" * len(cab))

for grupo, lista, chave in [('BR', LOCAIS, 'locais'), ('CT', CONTRASTE, 'contraste')]:
    if grupo == 'CT':
        print("-" * len(cab))
        print("  [pontos de contraste fora do Brasil]")
    for cod, lat, lon, nome in lista:
        row = {'nome': nome, 'lat': lat, 'lon': lon, 'fp': {}, 'tendencia_local_mm_ano': {}}
        vals = []
        for proc, (da, t, bg) in campos.items():
            serie, la, ln, raio = valor_no_ponto(da, lat, lon)
            if serie is None:
                row['fp'][proc] = None; vals.append(np.nan); continue
            bl, sl = tendencia(t, serie)
            fp = bl / bg if bg != 0 else np.nan
            row['fp'][proc] = round(float(fp), 4)
            row['tendencia_local_mm_ano'][proc] = round(float(bl), 4)
            row['ponto_grade'] = {'lat': la, 'lon': ln if ln <= 180 else ln - 360, 'raio_busca_graus': raio}
            vals.append(fp)
        # impressao digital combinada das duas calotas, ponderada pelas tendencias globais
        bgr, bai = campos['GrIS'][2], campos['AIS'][2]
        fgr, fai = row['fp'].get('GrIS'), row['fp'].get('AIS')
        if None not in (fgr, fai) and (bgr + bai) != 0:
            comb = (fgr * bgr + fai * bai) / (bgr + bai)
            row['fp_calotas_combinado'] = round(float(comb), 4)
        else:
            comb = np.nan
        print(f"{nome[:22]:<22} {lat:>7.2f} {lon:>8.2f} | " +
              " ".join(f"{v:>8.3f}" if np.isfinite(v) else f"{'--':>8}" for v in vals) +
              f" | {comb:>9.3f}" if np.isfinite(comb) else "")
        resultado[chave][cod] = row

# media da costa brasileira
br = [v for v in resultado['locais'].values()]
print("-" * len(cab))
med = {}
for proc in campos:
    vs = [v['fp'][proc] for v in br if v['fp'].get(proc) is not None]
    med[proc] = (float(np.mean(vs)), float(np.std(vs)), float(np.min(vs)), float(np.max(vs)))
cs = [v['fp_calotas_combinado'] for v in br if v.get('fp_calotas_combinado') is not None]
resultado['media_costa_brasileira'] = {
    **{p: {'media': round(m, 4), 'desvio': round(s, 4), 'min': round(mn, 4), 'max': round(mx, 4)}
       for p, (m, s, mn, mx) in med.items()},
    'calotas_combinado': {'media': round(float(np.mean(cs)), 4), 'desvio': round(float(np.std(cs)), 4),
                          'min': round(float(np.min(cs)), 4), 'max': round(float(np.max(cs)), 4)}}
print(f"{'MEDIA COSTA BRASILEIRA':<22} {'':>7} {'':>8} | " +
      " ".join(f"{med[p][0]:>8.3f}" for p in campos) + f" | {np.mean(cs):>9.3f}")
print(f"{'(desvio padrao)':<22} {'':>7} {'':>8} | " +
      " ".join(f"{med[p][1]:>8.3f}" for p in campos) + f" | {np.std(cs):>9.3f}")

json.dump(resultado, open(f"{OUT}/impressoes_digitais.json", 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
print(f"\ngravado {OUT}/impressoes_digitais.json")
