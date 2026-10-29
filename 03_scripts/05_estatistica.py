# -*- coding: utf-8 -*-
"""
Modulo estatistico compartilhado.

Implementa estimadores de tendencia com tratamento explicito de autocorrelacao, que e a
principal fragilidade de uma regressao OLS simples aplicada a series de nivel do mar:
os residuos de um ano sao correlacionados com os do ano seguinte, de modo que o erro
padrao do OLS classico subestima a incerteza real da tendencia.

Estimadores disponiveis:
  ols          - minimos quadrados ordinarios, erro padrao classico
  ols_hac      - OLS com erro padrao robusto de Newey-West (HAC), que corrige a
                 autocorrelacao e a heterocedasticidade dos residuos
  theilsen     - estimador robusto, resistente a valores extremos
  bootstrap    - reamostragem em blocos moveis, que preserva a estrutura de
                 autocorrelacao da serie e nao depende de hipoteses parametricas
"""
import numpy as np
from scipy import stats

try:
    import statsmodels.api as sm
    TEM_SM = True
except ImportError:
    TEM_SM = False


def _prep(x, y):
    x = np.asarray(x, float); y = np.asarray(y, float)
    m = np.isfinite(x) & np.isfinite(y)
    return x[m], y[m]


def defasagem_hac(n):
    """Defasagem maxima de Newey-West pela regra de Newey-West (1994): 4(n/100)^(2/9)."""
    return max(1, int(np.floor(4 * (n / 100.0) ** (2.0 / 9.0))))


def ols(x, y, hac=True):
    """Tendencia linear. Retorna dicionario com coeficiente, erros padrao classico e HAC."""
    x, y = _prep(x, y)
    n = len(x)
    if n < 5:
        return None
    x0 = x - x.mean()
    X = np.column_stack([np.ones(n), x0])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    s2 = res @ res / (n - 2)
    XtXi = np.linalg.inv(X.T @ X)
    se_cl = float(np.sqrt(s2 * XtXi[1, 1]))
    sst = float(((y - y.mean()) ** 2).sum())
    r2 = 1 - float((res ** 2).sum()) / sst if sst > 0 else np.nan
    # autocorrelacao de defasagem 1 dos residuos
    rho = float(np.corrcoef(res[:-1], res[1:])[0, 1]) if n > 3 else np.nan
    out = {'n': n, 'coef': float(beta[1]), 'intercepto': float(beta[0]),
           'x_ref': float(x.mean()), 'se_classico': se_cl, 'r2': r2, 'rho1_residuos': rho,
           'residuos_dp': float(np.std(res, ddof=2))}
    if hac and TEM_SM:
        L = defasagem_hac(n)
        mod = sm.OLS(y, sm.add_constant(x0)).fit(cov_type='HAC', cov_kwds={'maxlags': L, 'use_correction': True})
        out['se_hac'] = float(mod.bse[1]); out['defasagem_hac'] = L
        out['p_valor_hac'] = float(mod.pvalues[1])
        out['ic95_hac'] = [float(beta[1] - 1.96 * mod.bse[1]), float(beta[1] + 1.96 * mod.bse[1])]
        out['fator_inflacao_se'] = float(mod.bse[1] / se_cl) if se_cl > 0 else np.nan
    tc = stats.t.ppf(0.975, n - 2)
    out['ic95_classico'] = [float(beta[1] - tc * se_cl), float(beta[1] + tc * se_cl)]
    return out


def theilsen(x, y):
    x, y = _prep(x, y)
    if len(x) < 5:
        return None
    r = stats.theilslopes(y, x, alpha=0.95)
    return {'coef': float(r[0]), 'intercepto': float(r[1]),
            'ic95': [float(r[2]), float(r[3])], 'n': len(x)}


def bootstrap_blocos(x, y, n_rep=4000, tam_bloco=None, semente=20261029):
    """
    Bootstrap de blocos moveis sobre os residuos, preservando a autocorrelacao.
    Retorna a distribuicao da tendencia e o IC 95% percentilico.
    """
    x, y = _prep(x, y)
    n = len(x)
    if n < 10:
        return None
    if tam_bloco is None:
        tam_bloco = max(2, int(round(n ** (1 / 3))))
    x0 = x - x.mean()
    X = np.column_stack([np.ones(n), x0])
    beta, *_ = np.linalg.lstsq(X, y, rcond=None)
    res = y - X @ beta
    rng = np.random.default_rng(semente)
    nb = int(np.ceil(n / tam_bloco))
    coefs = np.empty(n_rep)
    for i in range(n_rep):
        ini = rng.integers(0, n - tam_bloco + 1, size=nb)
        r = np.concatenate([res[s:s + tam_bloco] for s in ini])[:n]
        yb = X @ beta + r
        b, *_ = np.linalg.lstsq(X, yb, rcond=None)
        coefs[i] = b[1]
    return {'coef': float(beta[1]), 'se_bootstrap': float(coefs.std(ddof=1)),
            'ic95': [float(np.percentile(coefs, 2.5)), float(np.percentile(coefs, 97.5))],
            'tam_bloco': tam_bloco, 'n_rep': n_rep, 'n': n}


def tendencia_completa(x, y, rotulo=""):
    """Executa os tres estimadores e devolve um resumo comparativo."""
    o = ols(x, y)
    if o is None:
        return None
    return {'rotulo': rotulo, 'ols': o, 'theilsen': theilsen(x, y),
            'bootstrap': bootstrap_blocos(x, y)}


def imprime_tendencia(d, unidade="mm/ano"):
    if d is None:
        print("   (dados insuficientes)"); return
    o = d['ols']; t = d['theilsen']; b = d['bootstrap']
    print(f"   OLS          : {o['coef']:+.3f} {unidade}  (IC95 classico {o['ic95_classico'][0]:+.3f} a {o['ic95_classico'][1]:+.3f})")
    if 'se_hac' in o:
        print(f"   OLS + HAC    : {o['coef']:+.3f} {unidade}  (IC95 HAC      {o['ic95_hac'][0]:+.3f} a {o['ic95_hac'][1]:+.3f})"
              f"  [L={o['defasagem_hac']}, inflacao do EP = {o['fator_inflacao_se']:.2f}x]")
    if t:
        print(f"   Theil-Sen    : {t['coef']:+.3f} {unidade}  (IC95 {t['ic95'][0]:+.3f} a {t['ic95'][1]:+.3f})")
    if b:
        print(f"   Bootstrap    : {b['coef']:+.3f} {unidade}  (IC95 {b['ic95'][0]:+.3f} a {b['ic95'][1]:+.3f})"
              f"  [blocos de {b['tam_bloco']} anos]")
    print(f"   n = {o['n']} anos | R2 = {o['r2']:.3f} | autocorrelacao dos residuos (defasagem 1) = {o['rho1_residuos']:+.3f}")


def rmse(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.sqrt(np.mean((a - b) ** 2)))


def mae(a, b):
    a, b = np.asarray(a, float), np.asarray(b, float)
    return float(np.mean(np.abs(a - b)))


def r2_fora_amostra(obs, prev):
    """R2 fora da amostra (coeficiente de eficiencia de Nash-Sutcliffe)."""
    obs, prev = np.asarray(obs, float), np.asarray(prev, float)
    sse = float(((obs - prev) ** 2).sum())
    sst = float(((obs - obs.mean()) ** 2).sum())
    return 1 - sse / sst if sst > 0 else np.nan
