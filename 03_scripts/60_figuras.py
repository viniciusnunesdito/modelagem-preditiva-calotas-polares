# -*- coding: utf-8 -*-
"""
Etapa 60: geracao das figuras do artigo.

Convencoes graficas adotadas (coerentes em todas as figuras):
 - paleta categorica de ordem fixa, validada para deficiencia de visao de cores
   (separacao minima entre pares adjacentes), com rotulos diretos sempre presentes,
   de modo que a identidade nunca dependa apenas da cor;
 - um unico eixo de valores por painel (nunca dois eixos y);
 - malha de fundo continua e discreta (nunca tracejada), eixos finos;
 - tipografia Arial, compativel com o modelo institucional do artigo;
 - saida em PNG 300 dpi e em PDF vetorial, para insercao em editor de texto.
"""
import os, sys, json, importlib, warnings
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
from matplotlib.lines import Line2D

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
E = importlib.import_module('05_estatistica')
OUT, RES, FIG, RAW = "02_dados_processados", "05_resultados", "04_figuras", "01_dados_brutos"
os.makedirs(FIG, exist_ok=True)

# ---------------------------------------------------------------- estilo
C = ['#2a78d6', '#eb6834', '#1baf7a', '#eda100', '#e87ba4', '#008300', '#4a3aa7', '#e34948']
TINTA, TINTA2, MUDO = '#0b0b0b', '#52514e', '#898781'
MALHA, EIXO, SUP = '#e1e0d9', '#c3c2b7', '#ffffff'
plt.rcParams.update({
    'font.family': 'sans-serif',
    'font.sans-serif': ['Arial', 'Helvetica', 'DejaVu Sans'],
    'font.size': 9, 'axes.labelsize': 9, 'axes.titlesize': 9.5,
    'xtick.labelsize': 8.5, 'ytick.labelsize': 8.5, 'legend.fontsize': 8,
    'figure.facecolor': SUP, 'axes.facecolor': SUP, 'savefig.facecolor': SUP,
    'axes.edgecolor': EIXO, 'axes.linewidth': 0.8,
    'xtick.color': MUDO, 'ytick.color': MUDO,
    'axes.labelcolor': TINTA2, 'text.color': TINTA,
    'grid.color': MALHA, 'grid.linewidth': 0.6, 'grid.linestyle': '-',
    'axes.grid': True, 'axes.axisbelow': True, 'legend.frameon': False,
    'lines.linewidth': 1.8, 'lines.markersize': 4.5,
    'axes.spines.top': False, 'axes.spines.right': False,
    'figure.dpi': 110, 'savefig.dpi': 300, 'savefig.bbox': 'tight', 'pdf.fonttype': 42})


def salva(fig, nome):
    for ext in ('png', 'pdf'):
        fig.savefig(f"{FIG}/{nome}.{ext}")
    plt.close(fig)
    print(f"  gravado {FIG}/{nome}.png e .pdf")


# ---------------------------------------------------------------- dados
G = json.load(open(f"{OUT}/dados_globais.json", encoding='utf-8'))
FPd = json.load(open(f"{OUT}/impressoes_digitais.json", encoding='utf-8'))
TR = json.load(open(f"{OUT}/fp_transecto_validacao.json", encoding='utf-8'))
PS = json.load(open(f"{OUT}/psmsl_series_anuais.json", encoding='utf-8'))
VLMd = json.load(open(f"{OUT}/vlm_gnss.json", encoding='utf-8'))
FE = json.load(open(f"{RES}/fechamento_orcamento.json", encoding='utf-8'))
FL = json.load(open(f"{RES}/fechamento_local_refinado.json", encoding='utf-8'))
BM = json.load(open(f"{RES}/benchmark_algoritmos.json", encoding='utf-8'))
EM = json.load(open(f"{RES}/emulador_calotas.json", encoding='utf-8'))
PG = json.load(open(f"{RES}/projecoes_globais.json", encoding='utf-8'))
PLo = json.load(open(f"{RES}/projecoes_locais.json", encoding='utf-8'))
VC = json.load(open(f"{RES}/vlm_comparacao_ar6.json", encoding='utf-8'))
EX = json.load(open(f"{RES}/extremos_frequencia.json", encoding='utf-8'))
RB = json.load(open(f"{RES}/recuo_linha_costa.json", encoding='utf-8'))

# nomes de exibicao das estacoes (os arquivos de dados usam grafia sem acento)
NOME_EST = {'SANTANA_AP': 'Santana (AP)', 'BELEM_PA': 'Belém (PA)',
            'MADEIRA_MA': 'P. da Madeira (MA)', 'FORTALEZA_CE': 'Fortaleza (CE)',
            'RECIFE_PE': 'Recife (PE)', 'SALVADOR_BA': 'Salvador (BA)',
            'CANAVIEIRAS_BA': 'Canavieiras (BA)', 'ILHA_FISCAL_RJ': 'Ilha Fiscal (RJ)',
            'SANTOS_SP': 'Santos (SP)', 'CANANEIA_SP': 'Cananéia (SP)',
            'IMBITUBA_SC': 'Imbituba (SC)', 'RIO_GRANDE_RS': 'Rio Grande (RS)'}

print("Gerando figuras do artigo")

# =====================================================================================
# FIGURA 1 - fluxograma metodologico
# =====================================================================================
fig, ax = plt.subplots(figsize=(7.2, 6.4))
ax.set_xlim(0, 10); ax.set_ylim(0, 11.4); ax.axis('off'); ax.grid(False)


def caixa(x, y, w, h, txt, cor, fc=None, fs=8.2, peso='normal'):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.09,rounding_size=0.12",
                                linewidth=1.1, edgecolor=cor,
                                facecolor=fc if fc else cor + '14'))
    ax.text(x + w / 2, y + h / 2, txt, ha='center', va='center', fontsize=fs,
            color=TINTA, weight=peso, linespacing=1.45)


def seta(x1, y1, x2, y2, cor=MUDO, est='-|>', lw=1.1, ls='-'):
    ax.add_patch(FancyArrowPatch((x1, y1), (x2, y2), arrowstyle=est, mutation_scale=11,
                                 linewidth=lw, color=cor, linestyle=ls,
                                 shrinkA=1, shrinkB=1))


caixa(0.2, 10.1, 4.4, 0.95, "ENTRADA OBSERVACIONAL\n"
      "temperatura global, perda de massa das calotas,\n"
      "altimetria, marégrafos, GNSS", C[0], fs=7.9, peso='bold')
caixa(5.4, 10.1, 4.4, 0.95, "CENÁRIOS DE EMISSÃO\n"
      "trajetórias de temperatura SSP\n(IPCC AR6, Tabela SPM.1)", C[3], fs=7.9, peso='bold')

caixa(0.2, 8.5, 4.4, 1.15, "(1) EMULADOR SEMI-EMPÍRICO\n"
      "dS/dt = a (T − T0) por componente\n"
      "seleção por validação aninhada\n"
      "e restrição de monotonicidade", C[0], fs=7.9)
caixa(5.4, 8.5, 4.4, 1.15, "CONTRIBUIÇÕES BARISTÁTICAS\n"
      "Groenlândia, Antártica, geleiras,\n"
      "água continental, estérico\n(mm de nível médio global)", C[2], fs=7.9)

caixa(0.2, 6.9, 9.6, 1.0, "(2) IMPRESSÃO DIGITAL DO NÍVEL DO MAR    FP(x) = RSL local / RSL médio global\n"
      "resposta gravitacional, rotacional e elástica da Terra sólida à redistribuição de massa",
      C[4], fs=8.1)

caixa(0.2, 5.3, 4.4, 1.0, "(3) MOVIMENTO VERTICAL\nDO TERRENO\n"
      "velocidades GNSS (MIDAS/IGS14)", C[1], fs=7.9)
caixa(5.4, 5.3, 4.4, 1.0, "PADRÃO DINÂMICO LOCAL\n"
      "redistribuição estérica e dinâmica\n(conjunto CMIP6 via IPCC AR6)", C[6], fs=7.9)

caixa(0.2, 3.7, 9.6, 1.0,
      "(4) NÍVEL RELATIVO DO MAR PROJETADO NA ESTAÇÃO\n"
      "RSL(x) = Σ FP(x)·S  +  padrão dinâmico · S_estérico  −  VLM(x) · (ano − 2020)",
      C[0], fs=8.3, peso='bold')

caixa(0.2, 2.1, 4.65, 1.0, "(5a) FREQUÊNCIA DE EXTREMOS\n"
      "Pareto generalizada sobre dados\nhorários; deslocamento por S", C[5], fs=7.9)
caixa(5.15, 2.1, 4.65, 1.0, "(5b) RECUO DA LINHA DE COSTA\n"
      "regra de Bruun   R = S / tanβ\nfaixa de declividades 1:20 a 1:200", C[5], fs=7.9)

caixa(0.1, 0.15, 9.8, 1.50,
      "VALIDAÇÃO EM CINCO PONTOS\n"
      "V1 reprodução das tendências baristáticas globais publicadas   |   "
      "V2 fechamento do orçamento\n"
      "do nível do mar (global, Atlântico Sul e estações brasileiras)   |   "
      "V3 calibração cega ao futuro\n"
      "(1900–1989 prevendo 1990–2018)   |   V4 dado independente (IMBIE)   |   "
      "V5 reprodução das\nprojeções oficiais do IPCC AR6 nas seis estações brasileiras",
      C[7], fc='#ffffff', fs=7.6)

for x in (2.4, 7.6):
    seta(x, 10.05, x, 9.68)
seta(4.62, 9.07, 5.36, 9.07)
for x in (2.4, 7.6):
    seta(x, 8.46, x, 7.94)
seta(5.0, 6.85, 2.4, 6.33)
seta(5.0, 6.85, 7.6, 6.33)
for x in (2.4, 7.6):
    seta(x, 5.26, x, 4.74)
seta(2.55, 3.66, 2.55, 3.14)
seta(7.45, 3.66, 7.45, 3.14)
seta(0.05, 1.70, 0.05, 3.2, cor=C[7], est='-|>', lw=1.0, ls=(0, (3, 2)))
ax.text(-0.06, 2.45, 'valida\ncada\netapa', rotation=90, ha='right', va='center',
        fontsize=7, color=C[7])
salva(fig, "Figura_01_fluxograma_metodologico")

# =====================================================================================
# FIGURA 2 - impressoes digitais
# =====================================================================================
fig, (a1, a2) = plt.subplots(1, 2, figsize=(7.2, 3.5), gridspec_kw={'width_ratios': [1.35, 1]})
t = TR['transecto_costeiro']
lat = np.array([r['lat'] for r in t])
o = np.argsort(lat)
lat = lat[o]
for k, cor, rot in [('GrIS', C[0], 'Groenlândia'), ('AIS', C[1], 'Antártica'),
                    ('calotas', C[2], 'Calotas combinadas'), ('glac', C[3], 'Geleiras')]:
    v = np.array([r[k] for r in t])[o]
    a1.plot(v, lat, color=cor, label=rot, zorder=3)
    a1.scatter(v[-1], lat[-1], s=18, color=cor, zorder=4, edgecolor=SUP, linewidth=0.8)
a1.axvline(1.0, color=EIXO, linewidth=1.0, zorder=1)
a1.text(1.005, -34.6, 'média global', fontsize=7, color=MUDO, rotation=90, va='bottom')
for nm, la in [('Belém', -1.4), ('Recife', -8.0), ('Rio de Janeiro', -22.9), ('Rio Grande', -32.1)]:
    a1.axhline(la, color=MALHA, linewidth=0.6, zorder=0)
    a1.text(1.355, la, nm, fontsize=6.8, color=MUDO, va='center', ha='right')
a1.set_xlabel('fator de impressão digital (adimensional)')
a1.set_ylabel('latitude (graus)')
a1.set_title('(a) ao longo do litoral brasileiro', loc='left', color=TINTA)
a1.set_xlim(0.62, 1.40); a1.set_ylim(-35.5, 5.5)
a1.legend(loc='lower left', ncol=1)

ct = TR['contraste_campo_proximo']
nomes = ['Mar de\nAmundsen', 'Mar de\nBellingshausen', 'Baia de\nBaffin', 'Nuuk\n(Groenlândia)',
         'Oceano Indico\nequatorial', 'Costa\nbrasileira']
gr = [c['GrIS'] for c in ct[:5]] + [TR['estatisticas_transecto']['GrIS']['media']]
ai = [c['AIS'] for c in ct[:5]] + [TR['estatisticas_transecto']['AIS']['media']]
y = np.arange(len(nomes))
a2.barh(y - 0.19, gr, height=0.34, color=C[0], label='Groenlândia', zorder=3)
a2.barh(y + 0.19, ai, height=0.34, color=C[1], label='Antártica', zorder=3)
a2.axvline(0, color=EIXO, linewidth=1.0, zorder=2)
a2.axvline(1, color=MUDO, linewidth=0.9, zorder=2)
a2.set_yticks(y); a2.set_yticklabels(nomes, fontsize=7.2)
a2.invert_yaxis()
a2.set_xlabel('fator de impressão digital')
a2.set_title('(b) campo próximo contra campo distante', loc='left', color=TINTA)
a2.set_xlim(-11, 3.1)
for i, (g_, a_) in enumerate(zip(gr, ai)):
    for off, v in [(-0.19, g_), (0.19, a_)]:
        a2.text(v + (0.25 if v >= 0 else -0.25), i + off, f'{v:.2f}',
                fontsize=6.6, color=TINTA2, va='center', ha='left' if v >= 0 else 'right')
a2.legend(loc='lower left')
a2.grid(axis='y', visible=False)
fig.tight_layout()
salva(fig, "Figura_02_impressoes_digitais")

# =====================================================================================
# FIGURA 3 - fechamento do orcamento
# =====================================================================================
fig, (b1, b2) = plt.subplots(1, 2, figsize=(7.2, 3.6), gridspec_kw={'width_ratios': [1.25, 1]})
# (chave no arquivo de resultados, rotulo exibido, cor)
COMPS = [('Expansao termica e halosterica', 'Expansão térmica e halostérica', C[0]),
         ('Geleiras de montanha', 'Geleiras de montanha', C[1]),
         ('Manto da Groenlandia', 'Manto da Groenlândia', C[2]),
         ('Manto da Antartica', 'Manto da Antártica', C[3]),
         ('Agua continental', 'Água continental', C[4])]
casos = [('Global\n1900-2018', FE['global']['1900-2018']),
         ('Global\n1993-2018', FE['global']['1993-2018']),
         ('Atlântico Sul\n1900-2018', FE['atlantico_sul']['1900-2018']),
         ('Atlântico Sul\n1993-2018', FE['atlantico_sul']['1993-2018'])]
x = np.arange(len(casos))
basep = np.zeros(len(casos)); basen = np.zeros(len(casos))
for chave, rotulo, cor in COMPS:
    v = np.array([(c['componentes'][chave]['coef'] if isinstance(c['componentes'][chave], dict)
                   else c['componentes'][chave]) for _, c in casos])
    bot = np.where(v >= 0, basep, basen)
    b1.bar(x - 0.19, v, width=0.34, bottom=bot, color=cor, label=rotulo, zorder=3,
           linewidth=0.8, edgecolor=SUP)
    basep = basep + np.where(v >= 0, v, 0); basen = basen + np.where(v < 0, v, 0)
obs = [c['observado'] for _, c in casos]
b1.bar(x + 0.19, obs, width=0.34, color='#d8d7d0', zorder=3, linewidth=0.8, edgecolor=SUP,
       label='Observado')
for i, (s, ob) in enumerate(zip(basep + basen, obs)):
    b1.text(i - 0.19, s + 0.08, f'{s:.2f}', ha='center', fontsize=6.9, color=TINTA2)
    b1.text(i + 0.19, ob + 0.08, f'{ob:.2f}', ha='center', fontsize=6.9, color=TINTA2)
b1.axhline(0, color=EIXO, linewidth=1.0, zorder=2)
b1.set_xticks(x); b1.set_xticklabels([n for n, _ in casos], fontsize=7.4)
b1.set_ylabel('tendência do nível do mar (mm/ano)')
b1.set_title('(a) soma dos processos contra nível observado', loc='left', color=TINTA)
b1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=6.8)
b1.set_ylim(-0.7, 4.6); b1.grid(axis='x', visible=False)

est = [('ILHA_FISCAL_RJ', '1963-2018', 'Ilha Fiscal (RJ)\n1963-2018'),
       ('ILHA_FISCAL_RJ', '1993-2018', 'Ilha Fiscal (RJ)\n1993-2018'),
       ('CANANEIA_SP', '1957-2004', 'Cananéia (SP)\n1957-2004')]
ROTL = {'GrIS': ('Manto da Groenlândia', C[2]), 'AIS': ('Manto da Antártica', C[3]),
        'glac': ('Geleiras de montanha', C[1]), 'tws': ('Água continental', C[4]),
        'esterico_dinamico': ('Estérico/dinâmico local', C[0]),
        'vlm': ('Movimento do terreno', C[6])}
x2 = np.arange(len(est)); bp = np.zeros(len(est)); bn = np.zeros(len(est))
for k, (rot, cor) in ROTL.items():
    v = np.array([FL['estacoes'][c]['periodos'][p]['decomposicao'][k]['local'] for c, p, _ in est])
    bot = np.where(v >= 0, bp, bn)
    b2.bar(x2 - 0.19, v, width=0.34, bottom=bot, color=cor, label=rot, zorder=3,
           linewidth=0.8, edgecolor=SUP)
    bp = bp + np.where(v >= 0, v, 0); bn = bn + np.where(v < 0, v, 0)
ob2 = [FL['estacoes'][c]['periodos'][p]['observado']['ols']['coef'] for c, p, _ in est]
ic2 = [FL['estacoes'][c]['periodos'][p]['observado']['ols'].get('ic95_hac') for c, p, _ in est]
b2.bar(x2 + 0.19, ob2, width=0.34, color='#d8d7d0', zorder=3, linewidth=0.8, edgecolor=SUP,
       label='Observado (marégrafo)')
for i, (o_, ic) in enumerate(zip(ob2, ic2)):
    if ic:
        b2.plot([i + 0.19, i + 0.19], ic, color=TINTA2, linewidth=1.1, zorder=4)
        b2.plot([i + 0.13, i + 0.25], [ic[0]] * 2, color=TINTA2, linewidth=1.1, zorder=4)
        b2.plot([i + 0.13, i + 0.25], [ic[1]] * 2, color=TINTA2, linewidth=1.1, zorder=4)
for i, (c, p, _) in enumerate(est):
    s = FL['estacoes'][c]['periodos'][p]['soma_prevista']
    fecha = FL['estacoes'][c]['periodos'][p]['fecha']
    b2.text(i - 0.19, s + 0.12, f'{s:.2f}', ha='center', fontsize=6.9, color=TINTA2)
    b2.text(i, -1.25, 'fecha' if fecha else 'não fecha', ha='center', fontsize=7.2,
            color=C[5] if fecha else C[7], weight='bold')
b2.axhline(0, color=EIXO, linewidth=1.0, zorder=2)
b2.set_xticks(x2); b2.set_xticklabels([n for _, _, n in est], fontsize=7.4)
b2.set_ylabel('tendência do nível relativo (mm/ano)')
b2.set_title('(b) fechamento nas estações brasileiras', loc='left', color=TINTA)
b2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.18), ncol=2, fontsize=6.8)
b2.set_ylim(-1.9, 9.2); b2.grid(axis='x', visible=False)
fig.tight_layout()
salva(fig, "Figura_03_fechamento_orcamento")

# =====================================================================================
# FIGURA 4 - benchmark de algoritmos
# =====================================================================================
fig, (d1, d2) = plt.subplots(1, 2, figsize=(7.2, 3.9), gridspec_kw={'width_ratios': [1.12, 1]})
HZ = ['1', '5', '10', '20']
ROTA = {'Media do treino': 'Média do treino', 'Persistencia': 'Persistência',
        'OLS quadratico': 'OLS quadrático', 'OLS cubico': 'OLS cúbico',
        'Floresta aleatoria': 'Floresta aleatória', 'Arvores extremas': 'Árvores extremas',
        'Theil-Sen': 'Theil-Sen', 'Ridge polinomial g3': 'Ridge polinomial g3',
        'Gradient boosting': 'Gradient boosting', 'SVR (RBF)': 'SVR (RBF)',
        'k-vizinhos (k=5)': 'k-vizinhos (k=5)', 'Processo gaussiano': 'Processo gaussiano',
        'Rede neural (MLP)': 'Rede neural (MLP)', 'ARIMA(1,1,1)': 'ARIMA(1,1,1)',
        'OLS linear': 'OLS linear'}

# painel (a): as duas estacoes lado a lado, no horizonte de 20 anos
T1 = BM['teste1_estacoes_locais']
ests = list(T1)
algos = [k for k in T1[ests[0]]['resultados'] if k != '_resumo']
algos = sorted(algos, key=lambda k: T1[ests[0]]['resultados'][k]['rmse']['20'])
yv = np.arange(len(algos))
cor_est = [C[0], C[1]]
for j, est in enumerate(ests):
    r = T1[est]['resultados']
    v = [min(r[k]['rmse']['20'], 240) for k in algos]
    cort = [r[k]['rmse']['20'] > 240 for k in algos]
    d1.barh(yv + (j - 0.5) * 0.38, v, height=0.34, color=cor_est[j], zorder=3,
            label=est, linewidth=0.7, edgecolor=SUP)
    base = T1[est]['resultados']['_resumo'] if '_resumo' in T1[est]['resultados'] else None
    b = T1[est]['resultados'].get('_resumo', {}).get('linha_base_mm')
    if b:
        d1.axvline(b, color=cor_est[j], linewidth=1.3, zorder=5, alpha=0.9)
    for i, (vv, c_) in enumerate(zip(v, cort)):
        if c_:
            d1.text(241, yv[i] + (j - 0.5) * 0.38, '→', fontsize=8, color=cor_est[j],
                    va='center', ha='left')
d1.set_yticks(yv); d1.set_yticklabels([ROTA.get(k, k) for k in algos], fontsize=7)
d1.invert_yaxis()
d1.set_xlabel('RMSE fora da amostra, horizonte de 20 anos (mm)')
d1.set_title('(a) duas estações, mesmo teste', loc='left', color=TINTA)
d1.set_xlim(0, 250)
d1.grid(axis='y', visible=False)
# legenda deslocada para a faixa livre do painel, incluindo a explicacao das linhas
# verticais, que marcam a previsao trivial pela media em cada estacao
hs1 = [Line2D([0], [0], color=cor_est[j], lw=6, label=ests[j]) for j in range(len(ests))]
hs1 += [Line2D([0], [0], color=MUDO, lw=1.4, label='previsão trivial pela média')]
d1.legend(handles=hs1, loc='center right', fontsize=6.9, bbox_to_anchor=(1.005, 0.40))

# painel (b): extrapolacao ao ano 2100
ex = BM['extrapolacao_2100']
obs18 = BM['valor_observado_2018_mm']
nomes_e = sorted(ex, key=lambda k: ex[k]['2100'])
cores_e = [C[7] if ex[k]['saturou'] else (C[0] if ex[k]['cresce'] else C[1]) for k in nomes_e]
y = np.arange(len(nomes_e))
d2.barh(y, [ex[k]['2100'] for k in nomes_e], height=0.66, color=cores_e, zorder=3)
d2.axvline(obs18, color=MUDO, linewidth=1.0, zorder=2)
# o significado da linha cinza e dado na legenda da figura, nao em anotacao interna,
# porque a faixa livre do painel e estreita demais para o texto sem colisao
d2.axvline(0, color=EIXO, linewidth=1.0, zorder=2)
d2.set_yticks(y); d2.set_yticklabels([ROTA.get(k, k) for k in nomes_e], fontsize=7.2)
d2.set_xlabel('contribuição das calotas projetada para 2100 (mm)')
d2.set_title('(b) extrapolação ao ano 2100', loc='left', color=TINTA)
for i, k in enumerate(nomes_e):
    v = ex[k]['2100']
    d2.text(v + (1.8 if v >= 0 else -1.8), i, f"{v:.0f}", fontsize=6.6, color=TINTA2,
            va='center', ha='left' if v >= 0 else 'right')
d2.legend(handles=[Line2D([0], [0], color=C[7], lw=6, label='satura (não extrapola)'),
                   Line2D([0], [0], color=C[1], lw=6, label='não monotônico'),
                   Line2D([0], [0], color=C[0], lw=6, label='cresce monotonicamente')],
          loc='lower right', fontsize=7)
d2.grid(axis='y', visible=False)
d2.set_xlim(-32, 118)
fig.tight_layout()
salva(fig, "Figura_04_benchmark_algoritmos")
print("  (4 de 8)")

# =====================================================================================
# FIGURA 5 - validacao do emulador
# =====================================================================================
fig, axs = plt.subplots(1, 3, figsize=(7.2, 3.1))
ht = np.array(EM['temperatura']['anos'], float)
Tk = np.array(EM['temperatura']['T_K'], float)
A = np.array(G['orcamento_global']['anos'], float)
Sg = G['orcamento_global']['series']
CH = {'GrIS': ('Greenland Ice Sheet [mean]', 'Groenlândia'),
      'AIS': ('Antarctic Ice Sheet [mean]', 'Antártica'),
      'steric': ('Steric [mean]', 'Expansão térmica')}


def suav(y, w):
    if w <= 1: return np.asarray(y, float).copy()
    y = np.asarray(y, float); n = len(y); o_ = np.empty(n); h = w // 2
    for i in range(n): o_[i] = y[max(0, i - h):min(n, i + h + 1)].mean()
    return o_


def taxa(nome, par, T, dT):
    if nome == 'M1': a, T0 = par[:2];    return a * (T - T0)
    if nome == 'M2': a, T0, b = par[:3]; return a * (T - T0) + b * dT
    if nome == 'M3': a, T0, q = par[:3]; return a * np.power(np.maximum(T - T0, 0.), q)
    if nome == 'M4': a, T0, c = par[:3]; return a * (T - T0) + c * (T - T0) ** 2


for ax_, (k, (col, rot)) in zip(axs, CH.items()):
    obs = np.array([np.nan if v is None else v for v in Sg[col]], float)
    m = np.isfinite(obs); aa, oo = A[m], obs[m]
    s = EM['selecao'][k]; v1 = EM['V1_calibracao_cega'][k]
    Ts = np.interp(aa, ht, suav(Tk, s['janela'])); dTs = np.gradient(Ts, aa)
    r = taxa(s['forma'], v1['par_treino'], Ts, dTs)
    cum = np.concatenate([[0.], np.cumsum(np.diff(aa) * .5 * (r[1:] + r[:-1]))])
    prev = cum - np.interp(1989, aa, cum) + v1['ancora_1989']
    ax_.plot(aa, oo, color=TINTA, linewidth=1.9, label='Observado', zorder=4)
    mt = aa <= 1989
    ax_.plot(aa[mt], prev[mt], color=C[0], linewidth=1.3, zorder=3, alpha=0.55)
    ax_.plot(aa[~mt], prev[~mt], color=C[0], linewidth=2.0, zorder=5,
             label='Emulador (cego pós-1989)')
    cpol = np.polyfit(aa[mt] - 1900, oo[mt], 1)
    pr = (np.polyval(cpol, aa[~mt] - 1900) - np.polyval(cpol, 89) + v1['ancora_1989'])
    ax_.plot(aa[~mt], pr, color=C[1], linewidth=1.6, zorder=4,
             label='Extrapolação linear')
    ax_.axvspan(1989, aa[-1], color='#f4f3ef', zorder=0)
    ax_.axvline(1989, color=EIXO, linewidth=0.9, zorder=1)
    ax_.set_title(rot, loc='left', color=TINTA)
    ax_.set_xlabel('ano')
    ax_.set_xlim(1900, 2020)
    if k == 'GrIS':
        ax_.set_ylabel('contribuição acumulada (mm)')
        ax_.legend(loc='upper left', fontsize=6.9)
        ax_.text(1991, ax_.get_ylim()[0] + 2, 'periodo previsto\n(nunca visto no treino)',
                 fontsize=6.6, color=MUDO)
    ax_.text(0.97, 0.06, f"RMSE {v1['rmse']:.1f} mm\nerro na taxa {v1['erro_taxa_pct']:+.0f}%",
             transform=ax_.transAxes, fontsize=6.9, color=TINTA2, ha='right', va='bottom')
fig.tight_layout()
salva(fig, "Figura_05_validacao_emulador")

# =====================================================================================
# FIGURA 6 - sensibilidade e projecoes globais
# =====================================================================================
fig, (f1, f2) = plt.subplots(1, 2, figsize=(7.2, 3.5), gridspec_kw={'width_ratios': [1, 1.3]})
S = PG['sensibilidade']
grupos = ['Média do\nséculo XX\n(1900–2018)', 'Período de\nsatélite\n(1992–2020)',
          'Implícita no\nIPCC AR6\n(2020–2100)']
gr_v = [S['GrIS']['a_serie_longa'], S['GrIS']['a_satelite'], S['GrIS']['a_ar6']]
ai_v = [S['AIS']['a_serie_longa'], S['AIS']['a_satelite'], S['AIS']['a_ar6']]
gr_e = [0, S['GrIS']['inc_a_satelite'], 0]
ai_e = [0, S['AIS']['inc_a_satelite'], 0]
xg = np.arange(3)
f1.bar(xg - 0.19, gr_v, width=0.34, color=C[0], label='Groenlândia', zorder=3,
       yerr=gr_e, error_kw=dict(ecolor=TINTA2, elinewidth=1.0, capsize=2.5))
f1.bar(xg + 0.19, ai_v, width=0.34, color=C[1], label='Antártica', zorder=3,
       yerr=ai_e, error_kw=dict(ecolor=TINTA2, elinewidth=1.0, capsize=2.5))
for i, (g_, a_) in enumerate(zip(gr_v, ai_v)):
    f1.text(i - 0.19, g_ + 0.05, f'{g_:.2f}', ha='center', fontsize=6.9, color=TINTA2)
    f1.text(i + 0.19, a_ + 0.05, f'{a_:.2f}', ha='center', fontsize=6.9, color=TINTA2)
f1.set_xticks(xg); f1.set_xticklabels(grupos, fontsize=7.2)
f1.set_ylabel('sensibilidade (mm/ano por K de aquecimento)')
f1.set_title('(a) a sensibilidade não é estacionária', loc='left', color=TINTA)
f1.legend(loc='upper left'); f1.grid(axis='x', visible=False); f1.set_ylim(0, 1.72)

SSP = ['ssp119', 'ssp126', 'ssp245', 'ssp370', 'ssp585']
NS = {'ssp119': 'SSP1-1.9', 'ssp126': 'SSP1-2.6', 'ssp245': 'SSP2-4.5',
      'ssp370': 'SSP3-7.0', 'ssp585': 'SSP5-8.5'}
xs = np.arange(len(SSP))
vA = [PG['projecao_global'][c]['total']['viaA']['2100'] for c in SSP]
vAl = [PG['projecao_global'][c]['total']['viaAl']['2100'] for c in SSP]
vB = [PG['projecao_global'][c]['total']['viaB']['2100']['p50'] for c in SSP]
b17 = [PG['projecao_global'][c]['total']['viaB']['2100']['p17'] for c in SSP]
b83 = [PG['projecao_global'][c]['total']['viaB']['2100']['p83'] for c in SSP]
f2.fill_between(xs, b17, b83, color='#dfe8f3', zorder=1,
                label='faixa provável do IPCC AR6 (17–83%)')
f2.plot(xs, vB, color=TINTA, linewidth=2.0, marker='s', markersize=5,
        markeredgecolor=SUP, markeredgewidth=0.8, label='Via B: IPCC AR6 (mediana)', zorder=5)
f2.plot(xs, vAl, color=C[0], linewidth=2.0, marker='o', markersize=5,
        markeredgecolor=SUP, markeredgewidth=0.8, zorder=5,
        label="Via A′: emulador, sensibilidade recente")
f2.plot(xs, vA, color=C[1], linewidth=2.0, marker='^', markersize=5,
        markeredgecolor=SUP, markeredgewidth=0.8, zorder=5,
        label='Via A: emulador, série longa')
for i in range(len(SSP)):
    f2.text(i, vB[i] + 26, f'{vB[i]:.0f}', ha='center', fontsize=6.9, color=TINTA2)
f2.set_xticks(xs); f2.set_xticklabels([NS[c] for c in SSP], fontsize=7.2, rotation=12)
f2.set_ylabel('elevacao média global em 2100 (mm acima de 2020)')
f2.set_title('(b) projeção global nas três vias', loc='left', color=TINTA)
f2.legend(loc='upper left', fontsize=7)
f2.grid(axis='x', visible=False); f2.set_ylim(150, 1060)
fig.tight_layout()
salva(fig, "Figura_06_sensibilidade_projecoes")

# =====================================================================================
# FIGURA 7 - projecoes locais e parcela das calotas
# =====================================================================================
fig, (g1, g2) = plt.subplots(1, 2, figsize=(7.2, 4.1), gridspec_kw={'width_ratios': [1.18, 1]})
cen = 'ssp245'
pj = PLo['projecoes']['B'][cen]
cods = sorted(pj, key=lambda c: -PLo['fatores_locais'][c]['lat'])
nomes_l = [NOME_EST[c] for c in cods]
lats = [PLo['fatores_locais'][c]['lat'] for c in cods]
COMP7 = [('GrIS', 'Manto da Groenlândia', C[0]), ('AIS', 'Manto da Antártica', C[1]),
         ('glac', 'Geleiras de montanha', C[2]), ('esterico', 'Estérico/dinâmico', C[3]),
         ('agua_continental', 'Água continental', C[4]), ('vlm', 'Movimento do terreno', C[6])]
y = np.arange(len(cods)); bp = np.zeros(len(cods)); bn = np.zeros(len(cods))
for k, rot, cor in COMP7:
    v = np.array([pj[c]['2100'][k] for c in cods], float)
    left = np.where(v >= 0, bp, bn)
    g1.barh(y, v, height=0.66, left=left, color=cor, label=rot, zorder=3,
            linewidth=0.8, edgecolor=SUP)
    bp = bp + np.where(v >= 0, v, 0); bn = bn + np.where(v < 0, v, 0)
tot = [pj[c]['2100']['total'] for c in cods]
for i, tt in enumerate(tot):
    g1.text(bp[i] + 18, i, f'{tt:.0f}', fontsize=7.2, color=TINTA, va='center', weight='bold')
g1.axvline(0, color=EIXO, linewidth=1.0, zorder=2)
g1.set_yticks(y)
g1.set_yticklabels([f'{n}\n{la:.1f}' + chr(176) for n, la in zip(nomes_l, lats)], fontsize=7)
g1.invert_yaxis()
g1.set_xlabel('elevação do nível relativo do mar em 2100 (mm acima de 2020)')
g1.set_title(f'(a) decomposição, cenário {NS[cen]}', loc='left', color=TINTA)
g1.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=3, fontsize=6.9)
g1.grid(axis='y', visible=False); g1.set_xlim(-70, 980)

for j, c in enumerate(SSP):
    v = [PLo['projecoes']['B'][c][k]['2100']['pct_calotas'] for k in cods]
    g2.plot(v, y, color=C[j if j < 3 else j + 1], marker='o', markersize=3.8,
            markeredgecolor=SUP, markeredgewidth=0.6, label=NS[c], zorder=3)
g2.set_yticks(y); g2.set_yticklabels([])
g2.invert_yaxis()
g2.set_xlabel('parcela das calotas polares na elevação (%)')
g2.set_title('(b) atribuição às calotas em 2100', loc='left', color=TINTA)
g2.legend(loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=3, fontsize=6.9)
g2.grid(axis='y', visible=False)
mn = min(PLo['projecoes']['B'][c][k]['2100']['pct_calotas'] for c in SSP for k in cods)
mx = max(PLo['projecoes']['B'][c][k]['2100']['pct_calotas'] for c in SSP for k in cods)
g2.set_xlim(mn - 3, mx + 3)
g2.set_yticklabels([f'{n}\n{la:.1f}' + chr(176) for n, la in zip(nomes_l, lats)],
                   fontsize=7)
fig.tight_layout()
salva(fig, "Figura_07_projecoes_locais")

# =====================================================================================
# FIGURA 8 - extremos e recuo da linha de costa
# =====================================================================================
fig, (h1, h2) = plt.subplots(1, 2, figsize=(7.2, 3.6), gridspec_kw={'width_ratios': [1.1, 1]})
e = EX['ILHA_FISCAL_RJ']
g_ = e['gpd']
Tr = np.logspace(-2.2, 2.3, 260)
lam = g_['taxa_exc_por_ano']
p = 1.0 / (lam * Tr)
ok = p < 1
niv = g_['u'] + g_['sigma'] / g_['xi'] * (p[ok] ** (-g_['xi']) - 1)
Tro = Tr[ok]
h1.plot(Tro, niv, color=TINTA, linewidth=2.0, label='Hoje', zorder=5)
for j, (c, rot) in enumerate([('ssp126', 'SSP1-2.6'), ('ssp245', 'SSP2-4.5'), ('ssp585', 'SSP5-8.5')]):
    S = e['amplificacao'][c]['2100']['S_mm']
    h1.plot(Tro, niv + S, color=C[j], linewidth=1.9, label=f'{rot} em 2100 (+{S:.0f} mm)', zorder=4)
n100 = e['niveis_retorno_mm']['100_anos']
h1.axhline(n100, color=MUDO, linewidth=1.0, zorder=2)
h1.text(0.0065, n100 + 24, f'nível com período de retorno de 100 anos hoje ({n100:.0f} mm)',
        fontsize=6.8, color=TINTA2)
for j, c in enumerate(['ssp126', 'ssp245', 'ssp585']):
    tr = e['amplificacao'][c]['2100']['novo_TR_do_nivel_100anos_anos']
    h1.scatter([tr], [n100], s=34, color=C[j], zorder=6, edgecolor=SUP, linewidth=1.0)
h1.set_xscale('log')
h1.set_xlabel('período de retorno (anos)')
h1.set_ylabel('nível do mar acima da média atual (mm)')
h1.set_title('(a) extremos na Ilha Fiscal (RJ), 1963-2014', loc='left', color=TINTA)
h1.legend(loc='upper left', fontsize=6.9)
h1.set_xlim(0.006, 200); h1.set_ylim(500, 2350)

rb = RB['recuo']['ssp245']
cods8 = [c for c in cods if c in rb]
y8 = np.arange(len(cods8))
for j, (dk, rot) in enumerate([('1:20', 'declividade 1:20'), ('1:50', '1:50'),
                               ('1:100', '1:100'), ('1:200', '1:200')]):
    v = [rb[c]['2100']['recuo_m'][dk] for c in cods8]
    vc = [rb[c]['2100']['recuo_calotas_m'][dk] for c in cods8]
    h2.barh(y8 + (j - 1.5) * 0.2, v, height=0.18, color=C[j], zorder=3,
            label=rot, linewidth=0.7, edgecolor=SUP)
    h2.barh(y8 + (j - 1.5) * 0.2, vc, height=0.18, color=C[j], zorder=4,
            hatch='////', edgecolor=SUP, linewidth=0.7, alpha=0.999)
h2.set_yticks(y8)
h2.set_yticklabels([NOME_EST[c] for c in cods8], fontsize=7)
h2.invert_yaxis()
h2.set_xlabel('recuo potencial da linha de costa em 2100 (m)')
h2.set_title('(b) recuo pela regra de Bruun, SSP2-4.5', loc='left', color=TINTA)
hs = [Line2D([0], [0], color=C[j], lw=6) for j in range(4)]
hs.append(Rectangle((0, 0), 1, 1, facecolor='#d8d7d0', hatch='////', edgecolor=SUP))
h2.legend(hs, ['1:20', '1:50', '1:100', '1:200', 'parcela das calotas'],
          loc='upper center', bbox_to_anchor=(0.5, -0.13), ncol=3, fontsize=6.9,
          title='declividade do perfil ativo', title_fontsize=7)
h2.grid(axis='y', visible=False)
fig.tight_layout()
salva(fig, "Figura_08_extremos_recuo")
print("\nFiguras concluidas.")
