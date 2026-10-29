# -*- coding: utf-8 -*-
"""
Etapa 50: amplificacao da frequencia de eventos extremos de nivel do mar.

POR QUE ESTE E O IMPACTO QUE MAIS IMPORTA
-----------------------------------------
A elevacao media do nivel do mar nao inunda nada por si. O que causa dano e a soma do
nivel medio com a mare astronomica e com a mare meteorologica (ressaca). Como a
distribuicao dos extremos tem cauda que decai de forma aproximadamente exponencial, um
deslocamento pequeno do nivel medio desloca toda a distribuicao e multiplica a frequencia
de excedencia de um limiar fixo por um fator que cresce exponencialmente. E por isso que
uma elevacao de poucos decimetros, que parece modesta, transforma um evento raro em
evento corriqueiro. O mecanismo e descrito por Vitousek et al. (2017) e Taherkhani et al.
(2020).

METODO
------
1. Serie horaria de qualidade de pesquisa (UHSLC), o unico tipo de dado que resolve
   extremos. Remove-se a tendencia linear e a sazonalidade climatologica, de modo que a
   distribuicao represente a variabilidade em torno do nivel medio de uma epoca de
   referencia.
2. Ajuste de uma distribuicao de Pareto generalizada (GPD) aos excessos acima de um
   limiar alto, que e o metodo de picos sobre limiar (POT) da teoria de valores extremos.
   Testa-se a estabilidade do ajuste variando o limiar.
3. Para cada elevacao projetada S, calcula-se:
      - o novo periodo de retorno do nivel que hoje tem periodo de retorno de 1, 10 e
        100 anos;
      - o fator de multiplicacao da frequencia de excedencia;
      - o numero de horas e de dias por ano em que o limiar atual seria excedido.
4. O calculo e puramente geometrico: desloca-se a distribuicao observada pelo valor da
   elevacao projetada. Nao se supoe nenhuma mudanca no regime de ondas ou de ventos, o
   que e declarado como limitacao (seria preciso modelagem atmosferica para isso).

CONVENCOES QUE PRECISAM ESTAR EXPLICITAS
----------------------------------------
- A taxa de excedencia e definida sobre VALORES HORARIOS: a taxa lambda e o numero de
  horas por ano acima do limiar. Assim, o nivel de periodo de retorno de 100 anos e o
  nivel excedido, em media, por uma hora a cada 100 anos. Dividindo a taxa por 24
  obtem-se a coluna de dias por ano, que e a metrica usada operacionalmente para dias de
  alagamento costeiro. As duas sao reportadas e sao consistentes entre si.
- Nao se aplicou declusterizacao (agrupamento de horas consecutivas da mesma ressaca em
  um unico evento). Isso nao afeta a comparacao entre o presente e o futuro, que e o
  objeto desta analise, porque o mesmo criterio vale para os dois, mas significa que as
  taxas nao devem ser lidas como numero de tempestades independentes.
"""
import os, sys, json, importlib, warnings
import numpy as np
from collections import defaultdict
from scipy import stats, optimize

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
E = importlib.import_module('05_estatistica')
RAW, OUT, RES = "01_dados_brutos", "02_dados_processados", "05_resultados"

PL = json.load(open(f"{RES}/projecoes_locais.json", encoding='utf-8'))
SENT = -32767
# estacoes com serie horaria longa; codigo UHSLC -> (codigo interno, nome)
EST = [(280, 'ILHA_FISCAL_RJ', 'Ilha Fiscal, Rio de Janeiro (RJ)'),
       (281, 'CANANEIA_SP', 'Cananeia (SP)'),
       (283, 'FORTALEZA_CE', 'Fortaleza (CE)'),
       (708, 'SALVADOR_BA', 'Salvador (BA)'),
       (712, 'RECIFE_PE', 'Recife (PE)'),
       (718, 'IMBITUBA_SC', 'Imbituba (SC)')]
SSP = ['ssp126', 'ssp245', 'ssp585']
NOME_SSP = {'ssp126': 'SSP1-2.6', 'ssp245': 'SSP2-4.5', 'ssp585': 'SSP5-8.5'}


def ler_horario(sid):
    """Le todos os registros horarios de uma estacao, em qualquer sufixo de arquivo."""
    t, v = [], []
    for suf in ['a', 'b', 'c', 'd']:
        p = f"{RAW}/uhslc/hourly_{sid}{suf}.csv"
        if not os.path.exists(p):
            continue
        for ln in open(p, encoding='latin-1'):
            c = ln.strip().split(',')
            if len(c) < 5:
                continue
            try:
                y, m, d, h, x = int(c[0]), int(c[1]), int(c[2]), int(c[3]), float(c[4])
            except ValueError:
                continue
            if x == SENT:
                continue
            # tempo decimal aproximado, suficiente para destendenciar e sazonalizar
            t.append(y + (m - 0.5) / 12.0 + (d - 1) / 365.25 + h / 8766.0)
            v.append(x)
        break        # usa apenas o registro principal, para nao misturar referenciais
    return np.array(t), np.array(v)


def prepara(t, v):
    """Remove tendencia linear e ciclo sazonal climatologico medio."""
    o = E.ols(t, v)
    r = v - (o['intercepto'] + o['coef'] * (t - o['x_ref']))
    mes = np.minimum(((t % 1.0) * 12).astype(int), 11)
    clim = np.array([r[mes == k].mean() if (mes == k).sum() > 50 else 0.0 for k in range(12)])
    return r - clim[mes], o['coef'], clim


def ajusta_gpd(x, q_limiar):
    """Ajusta GPD aos excessos acima do quantil q_limiar. Retorna (u, xi, sigma, taxa)."""
    u = float(np.quantile(x, q_limiar))
    exc = x[x > u] - u
    if len(exc) < 60:
        return None
    xi, loc, sig = stats.genpareto.fit(exc, floc=0)
    return {'u': u, 'xi': float(xi), 'sigma': float(sig), 'n_exc': int(len(exc)),
            'taxa_exc_por_ano': float(len(exc) / ((x.size) / 8766.0))}


def nivel_retorno(g, Tr):
    """Nivel com periodo de retorno Tr anos, a partir de um ajuste GPD."""
    lam = g['taxa_exc_por_ano']
    p = 1.0 / (lam * Tr)
    if p >= 1:
        return np.nan
    if abs(g['xi']) < 1e-6:
        return g['u'] - g['sigma'] * np.log(p)
    return g['u'] + g['sigma'] / g['xi'] * (p ** (-g['xi']) - 1)


def taxa_exc(g, z):
    """Numero esperado de excedencias por ano do nivel z."""
    if z <= g['u']:
        # abaixo do limiar o modelo GPD nao se aplica; usa a frequencia empirica
        return None
    y = (z - g['u'])
    if abs(g['xi']) < 1e-6:
        return g['taxa_exc_por_ano'] * np.exp(-y / g['sigma'])
    b = 1 + g['xi'] * y / g['sigma']
    if b <= 0:
        return 0.0
    return g['taxa_exc_por_ano'] * b ** (-1.0 / g['xi'])


res = {}
for sid, cod, nome in EST:
    t, v = ler_horario(sid)
    if len(t) < 8766 * 8:
        print(f"\n{nome}: serie horaria insuficiente ({len(t)} horas), estacao descartada")
        continue
    x, tend, clim = prepara(t, v)
    anos = (t.max() - t.min())
    print("\n" + "=" * 104)
    print(f"{nome}   |   UHSLC {sid}   |   {int(t.min())}-{int(t.max())}   |   "
          f"{len(t):,} horas validas em {anos:.0f} anos")
    print("=" * 104)
    print(f"tendencia removida: {tend:+.2f} mm/ano | amplitude do ciclo sazonal: "
          f"{clim.max()-clim.min():.0f} mm")

    # --- estabilidade do ajuste GPD em relacao ao limiar
    print(f"\n[a] Estabilidade do ajuste GPD (metodo de picos sobre limiar)")
    print(f"    {'quantil':>8} {'limiar (mm)':>12} {'xi':>8} {'sigma':>8} {'n exc':>7} "
          f"{'N1a (mm)':>9} {'N10a (mm)':>10} {'N100a (mm)':>11}")
    ajustes = {}
    for q in [0.95, 0.98, 0.99, 0.995, 0.998]:
        g = ajusta_gpd(x, q)
        if g is None:
            continue
        ajustes[q] = g
        print(f"    {q:>8.3f} {g['u']:>12.0f} {g['xi']:>8.3f} {g['sigma']:>8.1f} "
              f"{g['n_exc']:>7} {nivel_retorno(g,1):>9.0f} {nivel_retorno(g,10):>10.0f} "
              f"{nivel_retorno(g,100):>11.0f}")
    if not ajustes:
        print("    ajuste impossivel, estacao descartada"); continue
    Q = 0.99 if 0.99 in ajustes else sorted(ajustes)[len(ajustes) // 2]
    g = ajustes[Q]
    n1, n10, n100 = (nivel_retorno(g, 1), nivel_retorno(g, 10), nivel_retorno(g, 100))
    print(f"    -> adotado o quantil {Q}; a variacao de xi entre limiares "
          f"({min(a['xi'] for a in ajustes.values()):+.3f} a "
          f"{max(a['xi'] for a in ajustes.values()):+.3f}) indica "
          f"{'boa' if (max(a['xi'] for a in ajustes.values())-min(a['xi'] for a in ajustes.values()))<0.25 else 'moderada'} estabilidade")

    # --- amplificacao
    print(f"\n[b] Efeito da elevacao projetada sobre a frequencia de excedencia")
    print(f"    Niveis de referencia (acima do nivel medio atual): 1 ano = {n1:.0f} mm, "
          f"10 anos = {n10:.0f} mm, 100 anos = {n100:.0f} mm")
    tab = {}
    disponivel = cod in PL['projecoes']['B']['ssp245']
    if not disponivel:
        print("    (sem projecao local para esta estacao)")
    else:
        print(f"\n    O nivel que HOJE tem periodo de retorno de 100 anos ({n100:.0f} mm) passaria a:")
        print(f"    {'cenario':<10} {'ano':>5} {'S (mm)':>7} {'novo T.R. (anos)':>18} "
              f"{'dias/ano acima':>16} {'% do tempo':>11}")
        print("    " + "-" * 72)
        for cen in SSP:
            for h in [2050, 2100]:
                S = PL['projecoes']['B'][cen][cod][str(h)]['total']
                f1, f10, f100 = taxa_exc(g, n1 - S), taxa_exc(g, n10 - S), taxa_exc(g, n100 - S)
                # se o nivel deslocado cai abaixo do limiar, usa a contagem empirica direta
                emp = lambda z: float((x > z).sum() / (x.size / 8766.0))
                f1 = f1 if f1 is not None else emp(n1 - S)
                f10 = f10 if f10 is not None else emp(n10 - S)
                f100 = f100 if f100 is not None else emp(n100 - S)
                # contagem empirica direta: quantas horas distintas do registro historico
                # ficariam acima do limiar atual se o nivel medio subisse S
                fr100 = float((x > (n100 - S)).sum() / x.size)
                dias100 = fr100 * 365.25
                fr1 = float((x > (n1 - S)).sum() / x.size)
                dias1 = fr1 * 365.25
                TR = (1.0 / f100) if f100 > 0 else np.inf
                txtTR = (f"{TR:>18.2f}" if TR < 1000 else f"{'>1000':>18}")
                print(f"    {NOME_SSP[cen]:<10} {h:>5} {S:>7.0f} {txtTR} "
                      f"{dias100:>16.1f} {100*fr100:>10.1f}%")
                tab.setdefault(cen, {})[h] = {
                    'S_mm': S,
                    'freq_nivel_1ano_por_ano': round(float(f1), 3),
                    'freq_nivel_10anos_por_ano': round(float(f10), 4),
                    'freq_nivel_100anos_por_ano': round(float(f100), 5),
                    'amplificacao_1ano': round(float(f1), 1),
                    'amplificacao_10anos': round(float(f10 * 10), 1),
                    'amplificacao_100anos': round(float(f100 * 100), 1),
                    'novo_TR_do_nivel_100anos_anos': (round(float(TR), 3) if np.isfinite(TR) else None),
                    'dias_por_ano_acima_do_nivel_100anos_hoje': round(dias100, 2),
                    'fracao_do_tempo_acima_do_nivel_100anos_pct': round(100 * fr100, 2),
                    'dias_por_ano_acima_do_nivel_1ano_hoje': round(dias1, 2),
                    'fracao_do_tempo_acima_do_nivel_1ano_pct': round(100 * fr1, 2)}
        print(f"\n    Fatores de multiplicacao da frequencia de excedencia:")
        print(f"    {'cenario':<10} {'ano':>5} {'nivel de 1 ano':>17} {'de 10 anos':>14} {'de 100 anos':>15}")
        print("    " + "-" * 64)
        for cen in SSP:
            for h in [2050, 2100]:
                d_ = tab[cen][h]
                print(f"    {NOME_SSP[cen]:<10} {h:>5} {d_['amplificacao_1ano']:>16.0f}x "
                      f"{d_['amplificacao_10anos']:>13.0f}x {d_['amplificacao_100anos']:>14.0f}x")
        print("\n    Interpretacao. O periodo de retorno (T.R.) e o intervalo medio entre")
        print("    ocorrencias; um nivel com T.R. de 100 anos e, por definicao, excepcional.")
        print("    Quando seu T.R. cai abaixo de um ano, ele passa a ocorrer varias vezes por")
        print("    ano e deixa de ser excepcional: torna-se a condicao normal de mare alta.")
        print("    A coluna de dias por ano traduz isso para grandeza diretamente verificavel,")
        print("    contando no proprio registro horario historico quantas horas ficariam acima")
        print("    do limiar atual se o nivel medio subisse S.")
        if anos < 30:
            print(f"\n    ATENCAO: o registro horario desta estacao tem apenas {anos:.0f} anos. O nivel")
            print("    de periodo de retorno de 100 anos e, aqui, extrapolacao da cauda ajustada e")
            print("    nao frequencia observada; os valores devem ser lidos como indicativos.")
            print("    Somente Ilha Fiscal e Cananeia tem registro longo o bastante (mais de 50")
            print("    anos) para sustentar diretamente esse nivel de retorno.")

    res[cod] = {'nome': nome, 'uhslc_id': sid, 'periodo': [int(t.min()), int(t.max())],
                'registro_longo': bool(anos >= 30),
                'largura_da_cauda_mm': round(float(n100 - n1), 1),
                'n_horas': int(len(t)), 'anos': round(float(anos), 1),
                'tendencia_removida_mm_ano': round(float(tend), 3),
                'amplitude_sazonal_mm': round(float(clim.max() - clim.min()), 1),
                'quantil_adotado': Q, 'gpd': {k: round(v, 4) if isinstance(v, float) else v
                                              for k, v in g.items()},
                'ajustes_por_limiar': {str(q): {k: round(vv, 4) if isinstance(vv, float) else vv
                                                for k, vv in a.items()} for q, a in ajustes.items()},
                'niveis_retorno_mm': {'1_ano': round(float(n1), 1), '10_anos': round(float(n10), 1),
                                      '100_anos': round(float(n100), 1)},
                'amplificacao': tab}

json.dump(res, open(f"{RES}/extremos_frequencia.json", 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
print(f"\n\ngravado {RES}/extremos_frequencia.json")
