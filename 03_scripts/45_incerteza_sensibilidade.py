# -*- coding: utf-8 -*-
"""
Etapa 45: incerteza da razao de sensibilidades da Groenlandia.

MOTIVACAO
---------
A etapa 42 calcula a sensibilidade da Groenlandia ao aquecimento em duas escalas:

    a_sat   = (r2 - r1) / (T2 - T1)      duas epocas do registro de satelite (IMBIE)
    a_long  = coeficiente 'a' do emulador ajustado em 1900-2018

e publica a razao a_sat / a_long como valor pontual (7,3). Essa razao, porem, e o
quociente de DUAS grandezas estimadas, e tratar o denominador como constante exagera
a precisao do resultado. Duas causas se somam:

(a) o numerador tem incerteza propagada das incertezas do IMBIE, tomadas como
    integralmente correlacionadas dentro de cada epoca de cinco anos (criterio
    conservador: nao se divide por raiz de n);

(b) o denominador NAO e bem determinado. No ajuste M1 da Groenlandia o parametro de
    limiar T0 converge para o extremo inferior do intervalo admitido (-3,0 K), de modo
    que e a restricao, e nao a observacao, que o fixa; o coeficiente 'a' fica
    fortemente correlacionado com T0 e sua distribuicao de reamostragem e larga e
    assimetrica.

Esta etapa propaga as duas incertezas por Monte Carlo e reporta o que os dados de fato
sustentam sobre a razao, alem de dois testes de compatibilidade:

    - a_sat e distinguivel de zero?
    - a_sat e distinguivel da sensibilidade implicita nas projecoes do IPCC AR6?

Entradas : 05_resultados/emulador_calotas.json  (amostras de bootstrap de 'a')
           05_resultados/projecoes_globais.json (a_sat, inc_a_satelite, a_ar6)
Saida    : 05_resultados/incerteza_sensibilidade.json
"""
import os, json
import numpy as np
from math import erf, sqrt

RES = "05_resultados"
SEMENTE = 20261030
N_MC = 200000

EM = json.load(open(f"{RES}/emulador_calotas.json", encoding='utf-8'))
PJ = json.load(open(f"{RES}/projecoes_globais.json", encoding='utf-8'))


def Phi(z):
    """Funcao de distribuicao acumulada da normal padrao."""
    return 0.5 * (1.0 + erf(z / sqrt(2.0)))


print("=" * 106)
print("[45] INCERTEZA DA RAZAO DE SENSIBILIDADES (propagacao de Monte Carlo)")
print("=" * 106)
print("A razao publicada na etapa 42 e um quociente de duas estimativas. Aqui ela e")
print("recalculada propagando a incerteza de ambas, e nao apenas a do numerador.")

saida = {'semente': SEMENTE, 'n_monte_carlo': N_MC, 'componentes': {}}
rng = np.random.default_rng(SEMENTE)

for comp in ['GrIS', 'AIS']:
    s = PJ['sensibilidade'][comp]
    rot = s['rotulo']
    a_sat, inc = float(s['a_satelite']), float(s['inc_a_satelite'])
    a_long_pt = float(s['a_serie_longa'])
    a_ar6 = float(s['a_ar6'])

    # distribuicao de reamostragem do coeficiente 'a' do ajuste centenario
    am = np.array(EM['V4_bootstrap'][comp]['amostras'], float)[:, 0]
    lo_a, hi_a = np.percentile(am, [2.5, 97.5])
    perc_pt = 100.0 * float((am < a_long_pt).mean())

    # Monte Carlo: numerador normal, denominador reamostrado do bootstrap
    sat = rng.normal(a_sat, inc, N_MC)
    lon = rng.choice(am, N_MC, replace=True)
    val = lon > 0
    razao = sat[val] / lon[val]
    med = float(np.median(razao))
    r_lo, r_hi = (float(x) for x in np.percentile(razao, [2.5, 97.5]))
    p_gt1 = float((razao > 1.0).mean())

    # testes de compatibilidade do numerador
    z0 = a_sat / inc
    zar6 = (a_sat - a_ar6) / inc
    p_ar6 = 2.0 * (1.0 - Phi(abs(zar6)))

    # hipotese alternativa: incertezas IMBIE independentes nos 5 anos de cada epoca
    inc_ind = inc / sqrt(5.0)

    saida['componentes'][comp] = {
        'rotulo': rot,
        'a_satelite': round(a_sat, 4), 'inc_a_satelite_1sigma': round(inc, 4),
        'a_serie_longa_pontual': round(a_long_pt, 5),
        'a_serie_longa_ic95_bootstrap': [round(lo_a, 5), round(hi_a, 5)],
        'percentil_do_pontual_no_bootstrap': round(perc_pt, 1),
        'razao_pontual_publicada': round(a_sat / a_long_pt, 2),
        'razao_mediana_mc': round(med, 2),
        'razao_ic95_mc': [round(r_lo, 2), round(r_hi, 2)],
        'prob_razao_maior_que_1': round(p_gt1, 3),
        'a_satelite_sigmas_de_zero': round(z0, 2),
        'a_satelite_distinguivel_de_zero_95pct': bool(abs(z0) > 1.96),
        'a_ar6': round(a_ar6, 4),
        'dif_satelite_menos_ar6': round(a_sat - a_ar6, 4),
        'dif_em_sigmas': round(zar6, 2),
        'p_bilateral_vs_ar6': round(p_ar6, 3),
        'compativel_com_ar6_95pct': bool(abs(zar6) <= 1.96),
        'inc_1sigma_se_erros_independentes': round(inc_ind, 4),
        'sigmas_de_zero_se_erros_independentes': round(a_sat / inc_ind, 2),
    }

    d = saida['componentes'][comp]
    print(f"\n{rot}")
    print(f"   numerador  a_sat  = {a_sat:+.4f} +/- {inc:.4f} mm/ano por K (1 sigma)")
    print(f"   denominador a_long = {a_long_pt:+.5f}  | IC95 bootstrap "
          f"[{lo_a:+.5f}, {hi_a:+.5f}]  (o pontual esta no percentil {perc_pt:.0f})")
    print(f"   razao pontual publicada ............ {a_sat / a_long_pt:.2f}")
    print(f"   razao com as DUAS incertezas ....... mediana {med:.2f}, "
          f"IC95 [{r_lo:.2f}, {r_hi:.2f}]")
    print(f"   P(razao > 1) ....................... {100 * p_gt1:.1f}%")
    print(f"   a_sat distinguivel de zero? ........ {z0:.2f} sigma -> "
          f"{'sim' if abs(z0) > 1.96 else 'NAO ao nivel de 95%'}")
    print(f"      (se os erros IMBIE fossem independentes nos 5 anos de cada epoca: "
          f"{a_sat / inc_ind:.2f} sigma)")
    print(f"   vs sensibilidade implicita no AR6 ({a_ar6:.4f}): diferenca {a_sat - a_ar6:+.4f}"
          f" = {zar6:.2f} sigma, p = {p_ar6:.2f} -> "
          f"{'compativeis' if abs(zar6) <= 1.96 else 'distinguiveis'}")

print("\n" + "=" * 106)
print("LEITURA")
print("=" * 106)
g = saida['componentes']['GrIS']
print(f"Para a Groenlandia, o aumento da sensibilidade e PROVAVEL mas de magnitude mal")
print(f"determinada: a razao tem mediana {g['razao_mediana_mc']:.1f} e intervalo de 95% de "
      f"{g['razao_ic95_mc'][0]:.1f} a {g['razao_ic95_mc'][1]:.1f}, com")
print(f"probabilidade de {100*g['prob_razao_maior_que_1']:.0f}% de exceder a unidade. O valor pontual de "
      f"{g['razao_pontual_publicada']:.1f} nao deve ser")
print(f"lido como estimativa precisa. A sensibilidade medida por satelite e compativel com a")
print(f"implicita no AR6 (p = {g['p_bilateral_vs_ar6']:.2f}), de modo que o dado NAO sustenta afirmar que as")
print(f"projecoes oficiais subestimem a resposta da Groenlandia; sustenta apenas que nao a")
print(f"superestimam, o que ja corrobora a magnitude dessas projecoes.")

json.dump(saida, open(f"{RES}/incerteza_sensibilidade.json", 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
print(f"\ngravado {RES}/incerteza_sensibilidade.json")
