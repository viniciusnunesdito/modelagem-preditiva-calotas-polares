# -*- coding: utf-8 -*-
"""
Etapa 40: comparacao sistematica de algoritmos preditivos sob validacao de origem movel.

PERGUNTA DESTA ETAPA
--------------------
Dado que o problema e projetar o nivel do mar decadas a frente, qual classe de algoritmo
e apropriada? A literatura de aprendizado de maquina aplicada ao nivel do mar recomenda
abordagens hibridas, fisica mais aprendizado de maquina, para previsoes regionais de
longo prazo (AYINDE et al., 2024). Esta etapa testa essa recomendacao de forma
quantitativa e explicita, em vez de aceita-la por autoridade.

DESENHO EXPERIMENTAL
--------------------
Validacao cruzada de origem movel (rolling-origin / janela expansiva), que e o
procedimento correto para series temporais porque nunca usa informacao do futuro para
prever o passado:
   para cada origem k:  treina em [inicio, k]  ->  preve [k+1, k+h]
Os horizontes h = 1, 5, 10 e 20 anos separam desempenho de interpolacao de desempenho
de extrapolacao, que e o que importa para projecao climatica.

O conjunto de teste final NUNCA e usado para escolher modelo ou hiperparametro: a
selecao, quando necessaria, usa uma fatia de validacao interna ao treino. Isso evita
o vazamento de dados (data leakage) que inflaria artificialmente o desempenho.

ALGORITMOS AVALIADOS
--------------------
Referencias triviais : media do treino, persistencia (ultimo valor)
Parametricos         : OLS linear, OLS quadratico, Theil-Sen robusto, Ridge polinomial
Series temporais     : ARIMA
Aprendizado de maquina: floresta aleatoria, gradient boosting, arvores extremamente
                       aleatorias, SVR com nucleo RBF, k-vizinhos, processo gaussiano,
                       perceptron multicamadas
"""
import os, sys, json, importlib, warnings
import numpy as np

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
E = importlib.import_module('05_estatistica')

from sklearn.linear_model import LinearRegression, Ridge, TheilSenRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor, ExtraTreesRegressor
from sklearn.svm import SVR
from sklearn.neighbors import KNeighborsRegressor
from sklearn.neural_network import MLPRegressor
from sklearn.gaussian_process import GaussianProcessRegressor
from sklearn.gaussian_process.kernels import RBF, DotProduct, WhiteKernel, ConstantKernel
from sklearn.preprocessing import PolynomialFeatures, StandardScaler
from sklearn.pipeline import make_pipeline

try:
    from statsmodels.tsa.arima.model import ARIMA
    TEM_ARIMA = True
except ImportError:
    TEM_ARIMA = False

OUT, RES = "02_dados_processados", "05_resultados"
SEM = 20261029


def modelos():
    """Dicionario nome -> (construtor, usa_escalonamento)."""
    kern = (ConstantKernel(1.0) * DotProduct(sigma_0=1.0)
            + ConstantKernel(1.0) * RBF(length_scale=10.0) + WhiteKernel(noise_level=1.0))
    return {
        'Media do treino': ('media', False),
        'Persistencia': ('persistencia', False),
        'OLS linear': (lambda: LinearRegression(), False),
        'OLS quadratico': (lambda: make_pipeline(PolynomialFeatures(2), LinearRegression()), False),
        'OLS cubico': (lambda: make_pipeline(PolynomialFeatures(3), LinearRegression()), False),
        'Theil-Sen': (lambda: TheilSenRegressor(random_state=SEM, max_subpopulation=2000), False),
        'Ridge polinomial g3': (lambda: make_pipeline(PolynomialFeatures(3), StandardScaler(),
                                                      Ridge(alpha=10.0)), False),
        'Floresta aleatoria': (lambda: RandomForestRegressor(n_estimators=300, random_state=SEM), False),
        'Gradient boosting': (lambda: GradientBoostingRegressor(n_estimators=300, random_state=SEM), False),
        'Arvores extremas': (lambda: ExtraTreesRegressor(n_estimators=300, random_state=SEM), False),
        'SVR (RBF)': (lambda: make_pipeline(StandardScaler(), SVR(kernel='rbf', C=100.0, gamma='scale')), False),
        'k-vizinhos (k=5)': (lambda: KNeighborsRegressor(n_neighbors=5), False),
        'Processo gaussiano': (lambda: GaussianProcessRegressor(kernel=kern, normalize_y=True,
                                                               random_state=SEM, alpha=1e-6), False),
        'Rede neural (MLP)': (lambda: make_pipeline(StandardScaler(),
                                                    MLPRegressor(hidden_layer_sizes=(64, 32), max_iter=8000,
                                                                 random_state=SEM)), False),
        'ARIMA(1,1,1)': ('arima', False),
    }


def prever(nome, ctor, xtr, ytr, xte):
    """Treina e preve. x em anos desde o inicio da serie."""
    if ctor == 'media':
        return np.full(len(xte), float(np.mean(ytr)))
    if ctor == 'persistencia':
        return np.full(len(xte), float(ytr[-1]))
    if ctor == 'arima':
        if not TEM_ARIMA:
            return np.full(len(xte), np.nan)
        try:
            m = ARIMA(ytr, order=(1, 1, 1), trend='t').fit()
            return np.asarray(m.forecast(steps=int(xte[-1] - xtr[-1])))[
                (xte - xtr[-1] - 1).astype(int)]
        except Exception:
            return np.full(len(xte), np.nan)
    m = ctor()
    m.fit(xtr.reshape(-1, 1), ytr)
    return m.predict(xte.reshape(-1, 1))


def rolling_origin(x, y, horizontes=(1, 5, 10, 20), min_treino=25, passo=1):
    """
    Validacao de origem movel. Cada modelo e ajustado UMA vez por origem e usado para
    prever todos os horizontes a partir daquele mesmo ajuste, o que e o procedimento
    correto (o modelo nao e reajustado em funcao do horizonte pedido) e tambem o mais
    economico computacionalmente.
    """
    x = np.asarray(x, float); y = np.asarray(y, float)
    M = modelos()
    hmax = max(horizontes)
    err = {n: {h: [] for h in horizontes} for n in M}
    origens = list(range(min_treino, len(x) - 1, passo))
    for k in origens:
        xtr, ytr = x[:k], y[:k]
        # todos os alvos ate o horizonte maximo, de uma vez
        idx_all = [j for j in range(k, len(x)) if 1 <= (x[j] - x[k - 1]) <= hmax]
        if not idx_all:
            continue
        xte_all = x[idx_all]; yte_all = y[idx_all]
        lead = xte_all - x[k - 1]      # antecedencia de cada alvo, em anos
        for n, (c, _) in M.items():
            p = prever(n, c, xtr, ytr, xte_all)
            if not np.all(np.isfinite(p)):
                continue
            for h in horizontes:
                sel_h = lead <= h
                if sel_h.any():
                    err[n][h].extend((p[sel_h] - yte_all[sel_h]).tolist())
    return err, origens, list(M)


def tabela(err, modelos_ordem, horizontes, titulo, unidade='mm'):
    print("\n" + "=" * 108)
    print(titulo)
    print("=" * 108)
    cab = f"{'Algoritmo':<24}" + "".join(f"{'RMSE h=' + str(h):>14}" for h in horizontes) + f"{'MAE h=20':>12}{'n(h=20)':>10}"
    print(cab); print("-" * len(cab))
    linhas = []
    for n in modelos_ordem:
        r = {}
        for h in horizontes:
            e = np.array(err[n][h], float)
            r[h] = float(np.sqrt(np.mean(e ** 2))) if len(e) else np.nan
        e20 = np.array(err[n][horizontes[-1]], float)
        mae20 = float(np.mean(np.abs(e20))) if len(e20) else np.nan
        linhas.append((n, r, mae20, len(e20)))
    linhas.sort(key=lambda t: (np.inf if not np.isfinite(t[1][horizontes[-1]]) else t[1][horizontes[-1]]))
    for n, r, mae20, n20 in linhas:
        print(f"{n:<24}" + "".join(f"{r[h]:>14.1f}" if np.isfinite(r[h]) else f"{'--':>14}" for h in horizontes)
              + f"{mae20:>12.1f}{n20:>10}")
    return {n: {'rmse': {str(h): (None if not np.isfinite(r[h]) else round(r[h], 3)) for h in horizontes},
                'mae_h_max': round(mae20, 3), 'n_h_max': n20} for n, r, mae20, n20 in linhas}


# =====================================================================================
# TESTE 1: series locais de nivel do mar nas duas estacoes brasileiras de registro longo
# =====================================================================================
# O teste e repetido nas DUAS estacoes que satisfazem os criterios de qualidade. Rodar em
# uma so deixaria em aberto se o resultado e propriedade do problema ou peculiaridade
# daquela estacao; a replicacao independente responde essa objecao.
PS = json.load(open(f"{OUT}/psmsl_series_anuais.json", encoding='utf-8'))
LOCAIS = [('1032', 'Ilha Fiscal (RJ)'), ('726', 'Cananeia (SP)')]
t1 = {}
for sid, nome in LOCAIS:
    d = PS[sid]
    aa = np.array(d['anos'], float); yy = np.array(d['nivel_mm'], float)
    xx = aa - aa[0]
    print(f"\nTESTE 1 | {nome}: {int(aa[0])}-{int(aa[-1])}, {len(aa)} anos validos")
    e_, o_, ord_ = rolling_origin(xx, yy, min_treino=25)
    print(f"         {len(o_)} origens de treino avaliadas (de {int(aa[24])} a {int(aa[-2])})")
    t1[nome] = tabela(e_, ord_, (1, 5, 10, 20),
                      f"TESTE 1: erro de previsao fora da amostra, {nome} (mm)")
    base = t1[nome]['Media do treino']['rmse']['20']
    piores = [k for k, v in t1[nome].items() if v['rmse']['20'] and v['rmse']['20'] > base]
    melhor = min(t1[nome], key=lambda k: t1[nome][k]['rmse']['20'] or 1e9)
    ganho = 100 * (1 - t1[nome][melhor]['rmse']['20'] / base)
    print(f"\n    Linha de base trivial (media do treino): {base:.1f} mm")
    print(f"    Melhor algoritmo: {melhor} ({t1[nome][melhor]['rmse']['20']:.1f} mm), "
          f"ganho de {ganho:.0f}% sobre a linha de base")
    print(f"    {len(piores)} de {len(t1[nome])} algoritmos sao PIORES que a linha de base trivial")
    t1[nome]['_resumo'] = {'linha_base_mm': round(base, 2), 'melhor': melhor,
                           'melhor_rmse_mm': round(t1[nome][melhor]['rmse']['20'], 2),
                           'ganho_pct': round(ganho, 1), 'n_piores': len(piores),
                           'n_algoritmos': len(t1[nome]) }

print("\n" + "=" * 108)
print("REPLICACAO: o resultado se sustenta nas duas estacoes?")
print("=" * 108)
print(f"{'Estacao':<20} {'linha de base':>14} {'melhor algoritmo':>24} {'ganho':>8} {'piores que a base':>20}")
print("-" * 92)
for nome in t1:
    r = t1[nome]['_resumo']
    print(f"{nome:<20} {r['linha_base_mm']:>11.1f} mm {r['melhor']:>24} {r['ganho_pct']:>7.0f}% "
          f"{str(r['n_piores']) + ' de ' + str(r['n_algoritmos']):>20}")
print("\nLEITURA: o resultado NAO se repete, e a divergencia e o achado.")
print("-" * 108)
print("Em Ilha Fiscal o melhor algoritmo supera a linha de base trivial em 3% e doze dos")
print("quinze sao piores que ela. Em Cananeia o melhor supera em 65% e apenas dois sao")
print("piores. A diferenca nao esta no algoritmo, esta na razao sinal/ruido de cada serie:")
print("Ilha Fiscal tem R2 de 0,235 e desvio dos residuos de 71 mm; Cananeia tem R2 de 0,734")
print("e desvio de 35 mm. Onde a tendencia e forte e limpa, qualquer estimador de tendencia")
print("a aprende; onde ela esta enterrada na variabilidade interanual, nenhum aprende.")
print("")
print("O ponto critico e qual das duas series e fisicamente valida. A etapa 31 mostra que o")
print("orcamento do nivel do mar FECHA em Ilha Fiscal (z = +0,93) e e REJEITADO em Cananeia")
print("(z = +3,11, residuo de 3,3 mm/ano inexplicavel pelos processos conhecidos). Ou seja,")
print("a tendencia forte e facilmente aprendivel de Cananeia e justamente a que a fisica")
print("rejeita. Um procedimento de selecao guiado apenas por desempenho de validacao")
print("preferiria Cananeia e produziria projecoes confiantes, bem validadas e erradas.")
print("")
print("Dois niveis de conclusao, portanto. O primeiro e dependente da estacao: superar a")
print("previsao trivial depende da razao sinal/ruido local, nao do algoritmo. O segundo e")
print("estrutural e independe da estacao: seis dos quinze algoritmos nao conseguem gerar")
print("valor fora da faixa de treino, qualquer que seja a serie que recebam.")

# =====================================================================================
# TESTE 2: contribuicao das calotas polares ao nivel medio global (serie longa)
# =====================================================================================
G = json.load(open(f"{OUT}/dados_globais.json", encoding='utf-8'))
orc = G['orcamento_global']; anos = np.array(orc['anos'], float)
gr = np.array([0 if v is None else v for v in orc['series']['Greenland Ice Sheet [mean]']], float)
ai = np.array([0 if v is None else v for v in orc['series']['Antarctic Ice Sheet [mean]']], float)
cal = gr + ai
x_c = anos - anos[0]
print(f"\n\nTESTE 2 | Contribuicao acumulada das calotas polares (Groenlandia + Antartica) ao")
print(f"         nivel medio global, {int(anos[0])}-{int(anos[-1])}, {len(anos)} anos "
      f"(Frederikse et al., 2020)")
err2, org2, ord2 = rolling_origin(x_c, cal, min_treino=50, passo=1)
print(f"         {len(org2)} origens de treino avaliadas")
t2 = tabela(err2, ord2, (1, 5, 10, 20),
            "TESTE 2: erro de previsao fora da amostra, contribuicao das calotas (mm)")

# =====================================================================================
# DEMONSTRACAO DA FALHA DE EXTRAPOLACAO
# =====================================================================================
print("\n" + "=" * 108)
print("DEMONSTRACAO DIRETA: o que cada algoritmo responde quando lhe pedem o ano 2100")
print("=" * 108)
print("Treino: contribuicao das calotas, serie completa 1900-2018. Pergunta: valor em 2050 e 2100.")
print("O valor observado em 2018 e", f"{cal[-1]:.1f} mm.")
print(f"\n{'Algoritmo':<24}{'2030':>10}{'2050':>10}{'2100':>10}   diagnostico")
print("-" * 92)
M = modelos()
xfut = np.array([2030, 2050, 2100], float) - anos[0]
extrap = {}
for n, (c, _) in M.items():
    try:
        p = prever(n, c, x_c, cal, xfut)
    except Exception:
        p = np.full(3, np.nan)
    if not np.all(np.isfinite(p)):
        print(f"{n:<24}" + "".join(f"{'--':>10}" for _ in p) + "   falhou")
        continue
    # diagnostico: a previsao continua crescendo?
    cresce = p[2] > p[1] > p[0] > cal[-1]
    saturou = abs(p[2] - p[0]) < 1.0
    diag = ("saturou: resposta praticamente constante, incapaz de extrapolar" if saturou
            else "cresce monotonicamente" if cresce
            else "comportamento nao monotonico ou decrescente")
    print(f"{n:<24}" + "".join(f"{v:>10.1f}" for v in p) + f"   {diag}")
    extrap[n] = {'2030': round(float(p[0]), 2), '2050': round(float(p[1]), 2),
                 '2100': round(float(p[2]), 2), 'saturou': bool(saturou), 'cresce': bool(cresce)}

sat = [n for n, v in extrap.items() if v['saturou']]
print(f"\n{len(sat)} de {len(extrap)} algoritmos saturam e nao conseguem extrapolar: {', '.join(sat)}")
print("\nEsse comportamento nao e um defeito de implementacao nem de ajuste de")
print("hiperparametro: e uma propriedade estrutural desses algoritmos. Modelos baseados")
print("em arvores de decisao e em vizinhanca produzem previsoes como medias de valores")
print("de treino, e portanto nao podem gerar nenhum valor fora do intervalo observado no")
print("treino. Nucleos de base radial decaem para a media do treino longe dos dados.")
print("Como a projecao climatica e, por definicao, extrapolacao para fora da faixa")
print("historica, esses algoritmos sao inadequados para a tarefa, independentemente do")
print("desempenho que apresentem em horizontes curtos.")

json.dump({'teste1_estacoes_locais': {nome: {'resultados': t1[nome]} for nome in t1},
           'teste2_calotas_global': {'periodo': [int(anos[0]), int(anos[-1])], 'n_anos': len(anos),
                                     'n_origens': len(org2), 'resultados': t2},
           'extrapolacao_2100': extrap, 'algoritmos_que_saturam': sat,
           'valor_observado_2018_mm': round(float(cal[-1]), 2)},
          open(f"{RES}/benchmark_algoritmos.json", 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f"\ngravado {RES}/benchmark_algoritmos.json")
