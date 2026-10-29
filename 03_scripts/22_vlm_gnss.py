# -*- coding: utf-8 -*-
"""
Etapa 22: movimento vertical do terreno (VLM) nas estacoes maregraficas brasileiras,
a partir das velocidades GNSS MIDAS (Nevada Geodetic Laboratory, referencial IGS14).

POR QUE ISSO E NECESSARIO
-------------------------
Um maregrafo mede o nivel RELATIVO do mar: a altura da agua em relacao a um marco
fixado no continente. Se o terreno afunda, o maregrafo registra elevacao do mar mesmo
que o volume do oceano nao mude. Portanto:

    tendencia de nivel relativo = tendencia de nivel geocentrico do mar - VLM

Sem uma estimativa independente de VLM e impossivel atribuir a tendencia observada ao
degelo polar. As velocidades verticais GNSS fornecem essa estimativa independente.

Formato MIDAS (27 colunas): 1 estacao, 3 inicio, 4 fim, 5 duracao, 11 velocidade
vertical (m/ano), 14 incerteza da velocidade vertical (m/ano), 25 latitude, 26 longitude.
"""
import json
import numpy as np

RAW, OUT = "01_dados_brutos", "02_dados_processados"
R_TERRA = 6371.0
# estacoes maregraficas de interesse (codigo, nome, lat, lon)
MARES = [('SANTANA_AP', 'Santana (AP)', -0.05, -51.17),
         ('BELEM_PA', 'Belem (PA)', -1.45, -48.50),
         ('MADEIRA_MA', 'Ponta da Madeira (MA)', -2.57, -44.38),
         ('FORTALEZA_CE', 'Fortaleza (CE)', -3.72, -38.48),
         ('RECIFE_PE', 'Recife (PE)', -8.05, -34.87),
         ('SALVADOR_BA', 'Salvador (BA)', -12.97, -38.52),
         ('ILHA_FISCAL_RJ', 'Ilha Fiscal (RJ)', -22.90, -43.17),
         ('SANTOS_SP', 'Santos (SP)', -23.98, -46.30),
         ('CANANEIA_SP', 'Cananeia (SP)', -25.02, -47.93),
         ('IMBITUBA_SC', 'Imbituba (SC)', -28.23, -48.65),
         ('RIO_GRANDE_RS', 'Rio Grande (RS)', -32.10, -52.10)]
RAIO_KM = 100.0        # raio maximo de busca
DUR_MIN = 5.0          # duracao minima da serie GNSS, em anos
# Series GNSS curtas tem velocidade vertical pouco confiavel: carga hidrologica sazonal e
# interanual pode inclinar a reta. Por isso a media ponderada favorece, simultaneamente,
# estacoes precisas (1/sigma^2), longas (duracao/10 anos) e proximas (1/distancia).
DUR_REF = 10.0


def dist(lat1, lon1, lat2, lon2):
    p1, p2 = np.deg2rad(lat1), np.deg2rad(lat2)
    dl = np.deg2rad(lon2 - lon1)
    a = np.sin((p2 - p1) / 2) ** 2 + np.cos(p1) * np.cos(p2) * np.sin(dl / 2) ** 2
    return 2 * R_TERRA * np.arcsin(np.sqrt(np.clip(a, 0, 1)))


est = []
for ln in open(f"{RAW}/gnss/ngl_midas_IGS14.txt", encoding='latin-1'):
    c = ln.split()
    if len(c) < 27:
        continue
    try:
        lat = float(c[24]); lon = float(c[25])
        if lon > 180: lon -= 360
        est.append({'nome': c[0], 'ini': float(c[2]), 'fim': float(c[3]), 'dur': float(c[4]),
                    'vu_mm_ano': float(c[10]) * 1000.0, 'svu_mm_ano': float(c[13]) * 1000.0,
                    'lat': lat, 'lon': lon})
    except ValueError:
        continue
print(f"Velocidades MIDAS lidas: {len(est)} estacoes GNSS globais")

# subconjunto brasileiro, para contexto
brasil = [e for e in est if -34 < e['lat'] < 6 and -75 < e['lon'] < -33 and e['dur'] >= DUR_MIN]
print(f"Estacoes GNSS no territorio brasileiro com >= {DUR_MIN:.0f} anos de serie: {len(brasil)}")
vb = np.array([e['vu_mm_ano'] for e in brasil])
print(f"Velocidade vertical no Brasil: mediana {np.median(vb):+.2f} mm/ano, "
      f"media {vb.mean():+.2f}, desvio {vb.std():.2f} mm/ano "
      f"(percentis 10-90: {np.percentile(vb,10):+.2f} a {np.percentile(vb,90):+.2f})")

print("\n" + "=" * 104)
print(f"VLM NAS ESTACOES MAREGRAFICAS (media ponderada das estacoes GNSS em raio de {RAIO_KM:.0f} km)")
print("=" * 104)
cab = (f"{'Estacao maregrafica':<24} {'n':>3} {'GNSS mais proxima':<22} {'d(km)':>6} "
       f"{'VLM (mm/ano)':>14} {'dur.efet':>8} {'dur.max':>8}")
print(cab); print("-" * len(cab))
res = {}
for cod, nome, lat, lon in MARES:
    viz = []
    for e in est:
        if e['dur'] < DUR_MIN:
            continue
        d = dist(lat, lon, e['lat'], e['lon'])
        if d <= RAIO_KM:
            viz.append((d, e))
    viz.sort(key=lambda x: x[0])
    if not viz:
        print(f"{nome:<24} {0:>3} {'(nenhuma em ' + str(int(RAIO_KM)) + ' km)':<22} {'--':>6} {'--':>14} {'--':>8} {'--':>8}")
        res[cod] = {'nome': nome, 'n_gnss': 0, 'vlm_mm_ano': None}
        continue
    # media ponderada por precisao (1/sigma^2), duracao e proximidade
    w = np.array([(1.0 / max(e['svu_mm_ano'], 0.05) ** 2)
                  * min(e['dur'] / DUR_REF, 3.0)
                  / max(d, 1.0) for d, e in viz])
    v = np.array([e['vu_mm_ano'] for d, e in viz])
    s = np.array([e['svu_mm_ano'] for d, e in viz])
    vlm = float(np.sum(w * v) / np.sum(w))
    dur_ef = float(np.sum(w * np.array([e['dur'] for d, e in viz])) / np.sum(w))
    # incerteza: combina incerteza formal e dispersao entre estacoes
    form = float(np.sqrt(1.0 / np.sum(1.0 / np.maximum(s, 0.05) ** 2)))
    disp = float(np.std(v)) if len(v) > 1 else float(s[0])
    inc = float(np.sqrt(form ** 2 + disp ** 2))
    d0, e0 = viz[0]
    print(f"{nome:<24} {len(viz):>3} {e0['nome']:<22} {d0:>6.1f} "
          f"{vlm:>+8.2f} +/- {inc:<4.2f} {dur_ef:>8.1f} {max(e['dur'] for d, e in viz):>8.1f}")
    res[cod] = {'nome': nome, 'lat': lat, 'lon': lon, 'n_gnss': len(viz),
                'vlm_mm_ano': round(vlm, 3), 'vlm_inc_mm_ano': round(inc, 3),
                'duracao_efetiva_anos': round(dur_ef, 1),
                'duracao_maxima_anos': round(max(e['dur'] for d, e in viz), 1),
                'gnss_mais_proxima': e0['nome'], 'distancia_km': round(d0, 1),
                'periodo_gnss': [e0['ini'], e0['fim']],
                'estacoes': [{'nome': e['nome'], 'd_km': round(d, 1),
                              'vu': round(e['vu_mm_ano'], 3), 'svu': round(e['svu_mm_ano'], 3),
                              'dur': round(e['dur'], 1)} for d, e in viz[:8]]}

com = [r for r in res.values() if r.get('vlm_mm_ano') is not None]
vv = np.array([r['vlm_mm_ano'] for r in com])
print("-" * len(cab))
print(f"Cobertura: {len(com)}/{len(MARES)} estacoes maregraficas com GNSS em raio de {RAIO_KM:.0f} km")
print(f"VLM medio nas estacoes cobertas: {vv.mean():+.2f} mm/ano (desvio {vv.std():.2f}); "
      f"mediana {np.median(vv):+.2f} mm/ano")
print(f"Sinal: {(vv<0).sum()} estacoes com subsidencia (terreno afundando), "
      f"{(vv>0).sum()} com soerguimento")
print("\nInterpretacao: VLM negativo (subsidencia) soma-se a elevacao do oceano no registro")
print("maregrafico; VLM positivo (soerguimento) subtrai-se dela.")

json.dump({'raio_busca_km': RAIO_KM, 'duracao_minima_anos': DUR_MIN,
           'fonte': 'Blewitt et al. (2016), MIDAS, Nevada Geodetic Laboratory, referencial IGS14',
           'contexto_brasil': {'n_estacoes': len(brasil), 'mediana_mm_ano': float(np.median(vb)),
                               'media_mm_ano': float(vb.mean()), 'desvio_mm_ano': float(vb.std())},
           'estacoes_maregraficas': res},
          open(f"{OUT}/vlm_gnss.json", 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f"\ngravado {OUT}/vlm_gnss.json")
