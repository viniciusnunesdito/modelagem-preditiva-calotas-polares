# -*- coding: utf-8 -*-
"""
Etapa 41: emulador semi-empirico da resposta das calotas polares ao aquecimento global.

MOTIVACAO
---------
A etapa 40 mostra, com numeros, que algoritmos que aprendem apenas a forma da serie no
tempo nao extrapolam: seis dos quinze testados produzem resposta constante para sempre e,
na serie maregrafica local, nenhum supera a previsao trivial pela media historica em
horizonte de 20 anos. A alternativa nao e um algoritmo melhor, e mudar o que se aprende:
em vez da forma da curva no tempo, aprende-se a RELACAO FISICA entre o forcante
(temperatura media global da superficie) e a resposta (perda de massa das calotas).
Projetar deixa de ser prolongar uma curva e passa a ser avaliar essa relacao nos valores
de temperatura fornecidos por cenarios. E a logica da emulacao estatistica de Edwards et
al. (2021) e a forma semi-empirica de Rahmstorf (2007).

FORMA FUNCIONAL E RESTRICOES FISICAS
------------------------------------
    M1 (linear)       dS/dt = a (T - T0)
    M2 (com taxa)     dS/dt = a (T - T0) + b dT/dt
    M3 (potencia)     dS/dt = a [max(T - T0, 0)]^q,   q >= 1
    M4 (quadratica)   dS/dt = a (T - T0) + c (T - T0)^2,   c >= 0

As restricoes a >= 0, q >= 1 e c >= 0 impoem que mais aquecimento nunca produza menos
perda de massa. Sem elas, o ajuste de minimos quadrados escolhe uma parabola de curvatura
negativa que reproduz bem o passado e se inverte na extrapolacao, produzindo ganho de
massa sob aquecimento: esse foi o modo de falha observado na primeira versao desta etapa
e e o mesmo mecanismo de sobreajuste que inviabiliza a regressao quadratica no tempo.
T0 permanece livre numa faixa ampla, porque seu valor tem conteudo fisico: T0 negativo
significa que o reservatorio ja estava fora de equilibrio a temperatura pre-industrial,
o que e documentado para as geleiras de montanha, ainda em ajuste ao fim da Pequena Idade
do Gelo.

SUAVIZACAO DO FORCANTE
----------------------
Mantos de gelo e oceano integram o forcante ao longo de anos a decadas; nao respondem a
anomalia de um unico ano. Por isso o preditor e a temperatura suavizada por media movel
centrada, com a janela tratada como hiperparametro e escolhida por validacao aninhada.
Rahmstorf (2007) adota o mesmo procedimento com janela de 15 anos.

AJUSTE E SELECAO
----------------
Ajusta-se a contribuicao ACUMULADA S(t), com deslocamento livre como parametro de
incomodo; a integracao filtra naturalmente o ruido interanual da derivada. A forma
funcional e a janela de suavizacao NAO sao escolhidas por ajuste dentro da amostra (AIC
premiaria a flexibilidade) nem pelo conjunto de teste final (seria vazamento de dado):
sao escolhidas por validacao de origem movel ANINHADA, usando apenas anos anteriores a
1990. Na previsao, a taxa modelada e integrada a partir de uma ancora no ultimo ano de
treino, isolando a capacidade de prever a taxa futura do estado inicial ja conhecido.

VALIDACAO
---------
V1. Calibracao cega ao futuro: ajuste somente com 1900-1989, quando a perda era pequena,
    e previsao de 1990-2018, quando acelerou.
V2. Dado independente: confronto com o IMBIE (Otosaka et al., 2023), medido por satelite,
    com metodologia e consorcio diferentes dos da serie de calibracao.
V3. Estabilidade dos parametros em cortes sucessivos.
V4. Incerteza dos parametros por bootstrap de blocos.
"""
import os, sys, json, importlib, warnings
import numpy as np
from scipy.optimize import least_squares

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
E = importlib.import_module('05_estatistica')
OUT, RES = "02_dados_processados", "05_resultados"
os.makedirs(RES, exist_ok=True)
G = json.load(open(f"{OUT}/dados_globais.json", encoding='utf-8'))
SEM = 20261029

# ---------------------------------------------------------------- temperatura global
ht = np.array(G['hadcrut5']['anos'], float)
hv = np.array(G['hadcrut5']['valores'], float)
base = hv[(ht >= 1850) & (ht <= 1900)].mean()
T_obs = hv - base
print(f"Temperatura global (HadCRUT5) rebaseada para 1850-1900 (deslocamento {-base:+.3f} K)")
print(f"   {int(ht[0])}-{int(ht[-1])}: {T_obs[0]:+.2f} a {T_obs[-1]:+.2f} K | "
      f"media 2015-2024 = {T_obs[(ht>=2015)&(ht<=2024)].mean():+.3f} K")

orc = G['orcamento_global']
A = np.array(orc['anos'], float)
S = orc['series']
sr = lambda k: np.array([np.nan if v is None else v for v in S[k]], float)
ALVOS = {'GrIS': ('Greenland Ice Sheet [mean]', 'Manto de gelo da Groenlandia'),
         'AIS': ('Antarctic Ice Sheet [mean]', 'Manto de gelo da Antartica'),
         'glac': ('Glaciers [mean]', 'Geleiras de montanha'),
         'steric': ('Steric [mean]', 'Expansao termica e halosterica')}


def suaviza(y, w):
    """Media movel centrada de janela w, com janela encurtada nas bordas."""
    if w <= 1:
        return np.asarray(y, float).copy()
    y = np.asarray(y, float); n = len(y); out = np.empty(n)
    h = w // 2
    for i in range(n):
        a0, b0 = max(0, i - h), min(n, i + h + 1)
        out[i] = y[a0:b0].mean()
    return out


# ---------------------------------------------------------------- formas funcionais
DESCR = {'M1': 'dS/dt = a (T - T0)', 'M2': 'dS/dt = a (T - T0) + b dT/dt',
         'M3': 'dS/dt = a [max(T - T0, 0)]^q', 'M4': 'dS/dt = a (T - T0) + c (T - T0)^2'}
NOMES = {'M1': ['a', 'T0'], 'M2': ['a', 'T0', 'b'], 'M3': ['a', 'T0', 'q'], 'M4': ['a', 'T0', 'c']}
T0LIM = (-3.0, 0.9)
JANELAS = [1, 5, 11, 15, 21]
P0 = {'M1': [0.3, 0.0], 'M2': [0.3, 0.0, 0.0], 'M3': [0.3, -0.5, 1.5], 'M4': [0.3, 0.0, 0.1]}
LIM = {'M1': ([0.0, T0LIM[0]], [50.0, T0LIM[1]]),
       'M2': ([0.0, T0LIM[0], -50.0], [50.0, T0LIM[1], 50.0]),
       'M3': ([0.0, T0LIM[0], 1.0], [50.0, T0LIM[1], 3.0]),
       'M4': ([0.0, T0LIM[0], 0.0], [50.0, T0LIM[1], 50.0])}


def taxa(nome, par, T, dT):
    if nome == 'M1':
        a, T0 = par[:2];      return a * (T - T0)
    if nome == 'M2':
        a, T0, b = par[:3];   return a * (T - T0) + b * dT
    if nome == 'M3':
        a, T0, q = par[:3];   return a * np.power(np.maximum(T - T0, 0.0), q)
    if nome == 'M4':
        a, T0, c = par[:3];   return a * (T - T0) + c * (T - T0) ** 2
    raise ValueError(nome)


def cumul(anos, r):
    return np.concatenate([[0.0], np.cumsum(np.diff(anos) * 0.5 * (r[1:] + r[:-1]))])


def ajusta(nome, anos, T, dT, S_obs):
    """Ajusta S(t) acumulado; o ultimo parametro e o deslocamento (incomodo)."""
    def f(p):
        return cumul(anos, taxa(nome, p[:-1], T, dT)) + p[-1] - S_obs
    p0 = P0[nome] + [float(S_obs[0])]
    lo = list(LIM[nome][0]) + [-1e4]; hi = list(LIM[nome][1]) + [1e4]
    r = least_squares(f, p0, bounds=(lo, hi), max_nfev=60000)
    n, k = len(S_obs), len(p0)
    sse = float(np.sum(r.fun ** 2)); sst = float(np.sum((S_obs - S_obs.mean()) ** 2))
    return {'par': r.x[:-1].tolist(), 'offset': float(r.x[-1]),
            'rmse': float(np.sqrt(sse / n)), 'r2': 1 - sse / sst if sst > 0 else np.nan, 'k': k}


def prev_ancorada(nome, par, anos, T, dT, ano_anc, val_anc):
    c = cumul(anos, taxa(nome, par, T, dT))
    return c - np.interp(ano_anc, anos, c) + val_anc


# =====================================================================================
print("\n" + "=" * 106)
print("[1] SELECAO DA FORMA FUNCIONAL E DA JANELA DE SUAVIZACAO POR VALIDACAO ANINHADA")
print("=" * 106)
print("Cortes de calibracao usam apenas anos <= 1989; o periodo de teste de V1 (1990-2018)")
print("permanece intocado. Para cada corte, ajusta-se e integra-se ancorado no corte.")
CORTE_V1 = 1989
sel = {}
for p, (col, rot) in ALVOS.items():
    obs = sr(col); m = np.isfinite(obs)
    aa, oo = A[m], obs[m]
    grade = {}
    for w in JANELAS:
        Ts = np.interp(aa, ht, suaviza(T_obs, w)); dTs = np.gradient(Ts, aa)
        for nm in ['M1', 'M2', 'M3', 'M4']:
            er = []
            for corte in range(1950, CORTE_V1 - 9, 5):
                tr = aa <= corte
                va = (aa > corte) & (aa <= min(corte + 20, CORTE_V1))
                if tr.sum() < 35 or va.sum() < 5:
                    continue
                f = ajusta(nm, aa[tr], Ts[tr], dTs[tr], oo[tr])
                pr = prev_ancorada(nm, f['par'], aa, Ts, dTs, corte, float(np.interp(corte, aa, oo)))
                er.extend((pr[va] - oo[va]).tolist())
            grade[(nm, w)] = float(np.sqrt(np.mean(np.square(er)))) if er else np.inf
    # --- REGRA DE PARCIMONIA (regra do erro padrao) ---------------------------------
    # A validacao aninhada frequentemente nao distingue as formas: para as calotas, M1,
    # M3 e M4 produzem RMSE identico ate a segunda casa decimal, porque dentro da faixa
    # estreita de temperatura do registro historico uma reta, uma potencia e uma parabola
    # sao praticamente indistinguiveis. Escolher a mais flexivel nessas condicoes e
    # arbitrario e tem consequencia grave na extrapolacao: a forma M3 com q = 3 ajustada
    # a Antartica projeta taxa de 9 mm/ano a 4,4 K de aquecimento, uma ordem de grandeza
    # acima de qualquer estimativa publicada. Adota-se portanto: entre as combinacoes
    # cujo RMSE esta a menos de TOL do melhor, escolhe-se a de menor numero de parametros
    # e, em empate, a de menor janela e menor expoente/curvatura. A forma resultante, M1,
    # e exatamente a forma semi-empirica linear de Rahmstorf (2007).
    TOL = 1.05
    melhor_rmse = min(v for v in grade.values() if np.isfinite(v))
    cand = [(k, v) for k, v in grade.items() if np.isfinite(v) and v <= melhor_rmse * TOL]
    peso_forma = {'M1': 0, 'M2': 1, 'M3': 1, 'M4': 1}
    (bn, bw) = sorted(cand, key=lambda kv: (peso_forma[kv[0][0]], kv[0][1], kv[1]))[0][0]
    Ts = np.interp(aa, ht, suaviza(T_obs, bw)); dTs = np.gradient(Ts, aa)
    f_v1 = ajusta(bn, aa[aa <= CORTE_V1], Ts[aa <= CORTE_V1], dTs[aa <= CORTE_V1], oo[aa <= CORTE_V1])
    f_fin = ajusta(bn, aa, Ts, dTs, oo)
    sel[p] = {'rotulo': rot, 'forma': bn, 'janela': bw, 'equacao': DESCR[bn],
              'nomes_par': NOMES[bn], 'par_final': [round(x, 5) for x in f_fin['par']],
              'offset_final': round(f_fin['offset'], 4), 'rmse_final': round(f_fin['rmse'], 4),
              'r2_final': round(f_fin['r2'], 4), 'par_treino_V1': f_v1['par'],
              'grade_validacao_aninhada': {f"{k[0]}_j{k[1]}": (None if not np.isfinite(v) else round(v, 3))
                                           for k, v in grade.items()}}
    print(f"\n{rot}  ({int(aa[0])}-{int(aa[-1])}, {len(aa)} anos; "
          f"acumulado observado {oo[-1]-oo[0]:+.1f} mm)")
    print(f"   RMSE da validacao aninhada (mm), por forma e janela de suavizacao:")
    print(f"   {'forma':<6}" + "".join(f"{'j=' + str(w):>9}" for w in JANELAS))
    for nm in ['M1', 'M2', 'M3', 'M4']:
        print(f"   {nm:<6}" + "".join(
            f"{grade[(nm,w)]:>9.2f}" if np.isfinite(grade[(nm, w)]) else f"{'--':>9}" for w in JANELAS))
    txt = ", ".join(f"{NOMES[bn][j]}={f_fin['par'][j]:+.4f}" for j in range(len(NOMES[bn])))
    print(f"   melhor RMSE aninhado: {melhor_rmse:.2f} mm; {len(cand)} combinacoes a menos de "
          f"{100*(TOL-1):.0f}% dele (estatisticamente indistinguiveis)")
    print(f"   -> selecionado por parcimonia: {bn} ({DESCR[bn]}), janela de {bw} ano(s), "
          f"RMSE aninhado {grade[(bn,bw)]:.2f} mm")
    print(f"      ajuste final 1900-2018: {txt}  |  RMSE {f_fin['rmse']:.2f} mm, R2 {f_fin['r2']:.4f}")

# =====================================================================================
print("\n\n" + "=" * 106)
print("[2] VALIDACAO V1 (DECISIVA): calibrar em 1900-1989, prever 1990-2018")
print("=" * 106)
v1 = {}
for p, (col, rot) in ALVOS.items():
    obs = sr(col); m = np.isfinite(obs); aa, oo = A[m], obs[m]
    nm, bw = sel[p]['forma'], sel[p]['janela']
    Ts = np.interp(aa, ht, suaviza(T_obs, bw)); dTs = np.gradient(Ts, aa)
    mt, mv = aa <= CORTE_V1, aa > CORTE_V1
    anc = float(np.interp(CORTE_V1, aa, oo))
    prev = prev_ancorada(nm, sel[p]['par_treino_V1'], aa, Ts, dTs, CORTE_V1, anc)[mv]
    real = oo[mv]
    rm, r2 = E.rmse(real, prev), E.r2_fora_amostra(real, prev)
    ref = {}
    for g in (1, 2, 3):
        c = np.polyfit(aa[mt] - 1900, oo[mt], g)
        pr0 = np.polyval(c, aa[mv] - 1900) - np.polyval(c, CORTE_V1 - 1900) + anc
        ref[f'poli_g{g}'] = {'rmse': E.rmse(real, pr0), 'r2': E.r2_fora_amostra(real, pr0),
                             'valor_2018': float(pr0[-1])}
    ref['persistencia'] = {'rmse': E.rmse(real, np.full_like(real, anc)),
                           'r2': E.r2_fora_amostra(real, np.full_like(real, anc)), 'valor_2018': anc}
    tx_o = E.ols(aa[mv], real)['coef']; tx_e = E.ols(aa[mv], prev)['coef']
    txt = ", ".join(f"{NOMES[nm][j]}={sel[p]['par_treino_V1'][j]:+.4f}" for j in range(len(NOMES[nm])))
    print(f"\n{rot}  (forma {nm}, janela {bw})")
    print(f"   calibracao 1900-{CORTE_V1} ({int(mt.sum())} anos): {txt}")
    print(f"   ancora em {CORTE_V1}: S = {anc:+.2f} mm")
    print(f"   {'modelo':<30} {'RMSE 1990-2018':>15} {'R2 fora amostra':>17} {'S em 2018 (mm)':>16}")
    print("   " + "-" * 82)
    print(f"   {'emulador ' + nm + ' (T -> dS/dt)':<30} {rm:>15.2f} {r2:>17.3f} {prev[-1]:>16.2f}")
    for k2 in ['poli_g1', 'poli_g2', 'poli_g3', 'persistencia']:
        print(f"   {'extrapolacao ' + k2:<30} {ref[k2]['rmse']:>15.2f} {ref[k2]['r2']:>17.3f} "
              f"{ref[k2]['valor_2018']:>16.2f}")
    print(f"   {'OBSERVADO':<30} {'':>15} {'':>17} {real[-1]:>16.2f}")
    print(f"   taxa media 1990-2018: observada {tx_o:+.3f} | emulador {tx_e:+.3f} mm/ano "
          f"(erro {100*(tx_e-tx_o)/tx_o:+.1f}%)")
    mb = min(ref, key=lambda k: ref[k]['rmse']); gan = ref[mb]['rmse'] / rm
    print(f"   -> melhor referencia alternativa: {mb} (RMSE {ref[mb]['rmse']:.2f} mm). "
          f"Emulador {gan:.1f}x {'mais' if gan > 1 else 'menos'} preciso.")
    v1[p] = {'rotulo': rot, 'forma': nm, 'janela': bw,
             'par_treino': [round(x, 5) for x in sel[p]['par_treino_V1']],
             'ancora_1989': round(anc, 3), 'rmse': round(rm, 3), 'r2_fora_amostra': round(r2, 4),
             'S2018_emulador': round(float(prev[-1]), 3), 'S2018_observado': round(float(real[-1]), 3),
             'taxa_observada': round(tx_o, 4), 'taxa_emulador': round(tx_e, 4),
             'erro_taxa_pct': round(100 * (tx_e - tx_o) / tx_o, 1),
             'referencias': {k: {kk: round(vv, 4) for kk, vv in v.items()} for k, v in ref.items()},
             'melhor_referencia': mb, 'ganho': round(gan, 2)}

# =====================================================================================
print("\n\n" + "=" * 106)
print("[3] VALIDACAO V2: confronto com dado independente (IMBIE, Otosaka et al., 2023)")
print("=" * 106)
v2r = {}
for p, imk, rot in [('GrIS', 'greenland_mm', 'Groenlandia'), ('AIS', 'antarctica_mm', 'Antartica')]:
    im = G['imbie'][imk]['anual']
    ia = np.array(im['anos'], float); iv = np.array(im['acumulado'], float)
    obs = sr(ALVOS[p][0]); m = np.isfinite(obs); aa, oo = A[m], obs[m]
    nm, bw = sel[p]['forma'], sel[p]['janela']
    Ts = np.interp(aa, ht, suaviza(T_obs, bw)); dTs = np.gradient(Ts, aa)
    com = np.intersect1d(ia, aa)
    if len(com) < 10:
        continue
    emu = prev_ancorada(nm, sel[p]['par_final'], aa, Ts, dTs, com[0], float(np.interp(com[0], aa, oo)))
    e_em = np.interp(com, aa, emu); e_em -= e_em[0]
    e_im = np.interp(com, ia, iv); e_im -= e_im[0]
    e_fr = np.interp(com, aa, oo); e_fr -= e_fr[0]
    rm, r2 = E.rmse(e_im, e_em), E.r2_fora_amostra(e_im, e_em)
    t_im = E.ols(com, e_im)['coef']; t_em = E.ols(com, e_em)['coef']; t_fr = E.ols(com, e_fr)['coef']
    print(f"\n{rot}, periodo comum {int(com[0])}-{int(com[-1])} ({len(com)} anos)")
    print(f"   {'fonte':<36} {'acumulado (mm)':>15} {'taxa media (mm/ano)':>21}")
    print("   " + "-" * 74)
    print(f"   {'IMBIE (satelite, independente)':<36} {e_im[-1]:>+15.2f} {t_im:>+21.3f}")
    print(f"   {'Frederikse (serie de calibracao)':<36} {e_fr[-1]:>+15.2f} {t_fr:>+21.3f}")
    print(f"   {'emulador acionado por temperatura':<36} {e_em[-1]:>+15.2f} {t_em:>+21.3f}")
    print(f"   emulador vs IMBIE: diferenca de {e_em[-1]-e_im[-1]:+.2f} mm no acumulado "
          f"({100*(e_em[-1]-e_im[-1])/e_im[-1]:+.1f}%), RMSE {rm:.2f} mm, R2 {r2:.3f}")
    v2r[p] = {'rotulo': rot, 'periodo': [int(com[0]), int(com[-1])], 'n': len(com),
              'acum_imbie': round(float(e_im[-1]), 3), 'acum_frederikse': round(float(e_fr[-1]), 3),
              'acum_emulador': round(float(e_em[-1]), 3), 'taxa_imbie': round(t_im, 4),
              'taxa_frederikse': round(t_fr, 4), 'taxa_emulador': round(t_em, 4),
              'rmse': round(rm, 3), 'r2': round(r2, 4)}

# =====================================================================================
print("\n\n" + "=" * 106)
print("[4] VALIDACAO V3: estabilidade dos parametros em cortes sucessivos")
print("=" * 106)
v3 = {}
for p, (col, rot) in ALVOS.items():
    obs = sr(col); m = np.isfinite(obs); aa, oo = A[m], obs[m]
    nm, bw = sel[p]['forma'], sel[p]['janela']
    Ts = np.interp(aa, ht, suaviza(T_obs, bw)); dTs = np.gradient(Ts, aa)
    regs = []
    for corte in range(1960, 2011, 10):
        tr = aa <= corte; va = aa > corte
        if tr.sum() < 40 or va.sum() < 5:
            continue
        f = ajusta(nm, aa[tr], Ts[tr], dTs[tr], oo[tr])
        pr = prev_ancorada(nm, f['par'], aa, Ts, dTs, corte, float(np.interp(corte, aa, oo)))
        regs.append({'corte': corte, 'par': [round(x, 4) for x in f['par']],
                     'rmse_fora': round(E.rmse(oo[va], pr[va]), 3),
                     'r2_fora': round(E.r2_fora_amostra(oo[va], pr[va]), 4)})
    if not regs:
        continue
    av = np.array([r['par'][0] for r in regs]); tv = np.array([r['par'][1] for r in regs])
    print(f"\n{rot} (forma {nm}, {DESCR[nm]}, janela {bw})")
    hdr = f"   {'corte':>7}" + "".join(f"{n:>10}" for n in NOMES[nm]) + f"{'RMSE fora':>11}{'R2 fora':>9}"
    print(hdr)
    for r in regs:
        print(f"   {r['corte']:>7}" + "".join(f"{v:>10.4f}" for v in r['par'])
              + f"{r['rmse_fora']:>11.2f}{r['r2_fora']:>9.3f}")
    print(f"   coeficiente de variacao de a: {100*av.std()/abs(av.mean()):.1f}% | "
          f"T0 entre {tv.min():+.3f} e {tv.max():+.3f} K")
    v3[p] = {'rotulo': rot, 'forma': nm, 'regimes': regs,
             'cv_a_pct': round(float(100 * av.std() / abs(av.mean())), 2),
             'T0_min': round(float(tv.min()), 3), 'T0_max': round(float(tv.max()), 3)}

# =====================================================================================
print("\n\n" + "=" * 106)
print("[5] VALIDACAO V4: incerteza dos parametros por bootstrap de blocos moveis")
print("=" * 106)
rng = np.random.default_rng(SEM)
boot = {}
for p, (col, rot) in ALVOS.items():
    obs = sr(col); m = np.isfinite(obs); aa, oo = A[m], obs[m]
    nm, bw = sel[p]['forma'], sel[p]['janela']
    Ts = np.interp(aa, ht, suaviza(T_obs, bw)); dTs = np.gradient(Ts, aa)
    par0 = sel[p]['par_final']; off0 = sel[p]['offset_final']
    ajust0 = cumul(aa, taxa(nm, par0, Ts, dTs)) + off0
    res0 = oo - ajust0
    n = len(aa); L = max(3, int(round(n ** (1 / 3)))); nb = int(np.ceil(n / L))
    amostras = []
    for _ in range(500):
        ini = rng.integers(0, n - L + 1, size=nb)
        rb = np.concatenate([res0[s:s + L] for s in ini])[:n]
        try:
            amostras.append(ajusta(nm, aa, Ts, dTs, ajust0 + rb)['par'])
        except Exception:
            pass
    Ab = np.array(amostras)
    print(f"\n{rot} ({nm}): {len(amostras)} reamostragens, blocos de {L} anos")
    for j, nmp in enumerate(NOMES[nm]):
        print(f"   {nmp:<4} = {par0[j]:+.5f}   IC95 [{np.percentile(Ab[:,j],2.5):+.5f}, "
              f"{np.percentile(Ab[:,j],97.5):+.5f}]   (dp {Ab[:,j].std():.5f})")
    boot[p] = {'forma': nm, 'janela': bw, 'nomes': NOMES[nm], 'par': par0,
               'ic95': [[round(float(np.percentile(Ab[:, j], 2.5)), 5),
                         round(float(np.percentile(Ab[:, j], 97.5)), 5)] for j in range(Ab.shape[1])],
               'dp': [round(float(Ab[:, j].std()), 5) for j in range(Ab.shape[1])],
               'amostras': Ab.round(5).tolist(), 'tam_bloco': L, 'n_rep': len(amostras)}

json.dump({'temperatura': {'fonte': 'HadCRUT5 (Morice et al., 2021)', 'base': '1850-1900',
                           'deslocamento_K': round(float(-base), 4),
                           'anos': ht.tolist(), 'T_K': np.round(T_obs, 4).tolist()},
           'selecao': sel, 'V1_calibracao_cega': v1, 'V2_dado_independente': v2r,
           'V3_estabilidade': v3, 'V4_bootstrap': boot, 'descricao_formas': DESCR,
           'limites_T0': list(T0LIM), 'janelas_testadas': JANELAS},
          open(f"{RES}/emulador_calotas.json", 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f"\n\ngravado {RES}/emulador_calotas.json")
