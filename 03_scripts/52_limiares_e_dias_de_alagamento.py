# -*- coding: utf-8 -*-
"""
Etapa 52: metricas operacionais de alagamento costeiro.

MOTIVACAO
---------
A etapa 50 expressa o efeito da elevacao sobre os extremos como fator de multiplicacao
da frequencia. Esse fator e correto, mas pouco tangivel: dizer que um evento ficou 806
vezes mais frequente nao informa quantas vezes por ano ele ocorrera nem quando a
mudanca de regime acontece. Esta etapa converte o mesmo resultado em duas grandezas
diretamente verificaveis e usadas operacionalmente em gestao costeira:

  (a) DIAS POR ANO acima de um limiar de referencia atual, contados hora a hora no
      proprio registro historico deslocado pela elevacao projetada. E a metrica de
      "dias de alagamento" adotada por servicos meteorologicos nacionais;

  (b) ANO DE CRUZAMENTO: o ano em que o nivel que hoje tem periodo de retorno de 100
      anos passa a ter periodo de retorno de 1 ano, isto e, deixa de ser excepcional e
      passa a ser esperado todo ano. E o indicador de mudanca de regime.

Para (b), a trajetoria de elevacao e interpolada anualmente a partir das projecoes do
IPCC AR6 por estacao, e resolve-se numericamente o ano em que a taxa de excedencia
anual do limiar atinge uma ocorrencia por ano.
"""
import os, sys, json, importlib, warnings
import numpy as np

warnings.filterwarnings('ignore')
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
RAW, OUT, RES = "01_dados_brutos", "02_dados_processados", "05_resultados"

EX = json.load(open(f"{RES}/extremos_frequencia.json", encoding='utf-8'))
PL = json.load(open(f"{RES}/projecoes_locais.json", encoding='utf-8'))
SSP = ['ssp126', 'ssp245', 'ssp585']
NOME_SSP = {'ssp126': 'SSP1-2.6', 'ssp245': 'SSP2-4.5', 'ssp585': 'SSP5-8.5'}
AR6_EST = {'IMBITUBA_SC': 542, 'RECIFE_PE': 556, 'SALVADOR_BA': 578,
           'BELEM_PA': 580, 'CANANEIA_SP': 726, 'ILHA_FISCAL_RJ': 1032}
ANO0 = 2020


def trajetoria(cod, cen):
    """Elevacao anual projetada (mm acima de 2020), 2020-2150, para a estacao."""
    pid = AR6_EST.get(cod)
    if pid is None:
        return None, None
    d = json.load(open(f"{RAW}/ipcc_ar6/ar6_psmsl_{pid}.json", encoding='utf-8'))
    r = next((x for x in d if x['process'] == 'total' and x['scenario'] == cen
              and x['confidence'] == 'medium'), None)
    if r is None:
        return None, None
    y = np.array(r['year'], float)
    v = np.array(r['height_50'], float) * 1000.0
    v = v - np.interp(ANO0, y, v)
    anos = np.arange(ANO0, 2151, 1.0)
    return anos, np.interp(anos, y, v)


def taxa_exc(g, z):
    """Excedencias horarias por ano do nivel z, pela GPD ajustada."""
    if z <= g['u']:
        return None
    y = z - g['u']
    if abs(g['xi']) < 1e-6:
        return g['taxa_exc_por_ano'] * np.exp(-y / g['sigma'])
    b = 1 + g['xi'] * y / g['sigma']
    return 0.0 if b <= 0 else g['taxa_exc_por_ano'] * b ** (-1.0 / g['xi'])


print("=" * 104)
print("[1] ANO DE CRUZAMENTO: quando o nivel hoje centenario passa a ocorrer todo ano")
print("=" * 104)
print("Criterio: o ano em que a taxa de excedencia do limiar atual atinge 24 horas por")
print("ano, equivalente a um dia de alagamento anual. Projecoes do IPCC AR6, mediana.")
print()
cab = f"{'Estacao':<22} {'registro':>10} {'limiar 100 anos':>16}" + "".join(f"{NOME_SSP[c]:>12}" for c in SSP)
print(cab); print("-" * len(cab))
res = {}
for cod, d in EX.items():
    g = d['gpd']; n100 = d['niveis_retorno_mm']['100_anos']
    linha = {}
    for cen in SSP:
        anos, S = trajetoria(cod, cen)
        if anos is None:
            linha[cen] = None; continue
        ano_cruz = None
        for a, s_ in zip(anos, S):
            t = taxa_exc(g, n100 - s_)
            if t is not None and t >= 24.0:      # 24 horas/ano = 1 dia/ano
                ano_cruz = int(a); break
        linha[cen] = ano_cruz
    marca = '' if d['registro_longo'] else ' *'
    print(f"{d['nome'][:22]:<22} {str(d['anos']) + ' anos' + marca:>10} {n100:>13.0f} mm"
          + "".join(f"{(str(linha[c]) if linha[c] else '>2150'):>12}" for c in SSP))
    res[cod] = {'nome': d['nome'], 'registro_longo': d['registro_longo'],
                'nivel_100anos_mm': n100, 'ano_cruzamento': linha}
print("-" * len(cab))
print("* registro horario inferior a 30 anos: nivel de retorno centenario e extrapolacao")
print("  da cauda ajustada; valor indicativo.")

print("\n\n" + "=" * 104)
print("[2] DIAS POR ANO ACIMA DOS LIMIARES ATUAIS")
print("=" * 104)
print("Contagem horaria direta no registro historico deslocado pela elevacao projetada.")
print("Sem hipotese sobre mudanca no regime de ondas ou de tempestades.")
print()
cab2 = (f"{'Estacao':<22} {'cenario':<10}" +
        "".join(f"{'dias/ano >N1a ' + str(h):>18}{'dias/ano >N100a ' + str(h):>20}" for h in [2050, 2100]))
print(cab2); print("-" * len(cab2))
for cod, d in EX.items():
    for cen in SSP:
        a = d['amplificacao'].get(cen)
        if not a:
            continue
        print(f"{d['nome'][:22]:<22} {NOME_SSP[cen]:<10}"
              + "".join(f"{a[str(h)]['dias_por_ano_acima_do_nivel_1ano_hoje']:>18.1f}"
                        f"{a[str(h)]['dias_por_ano_acima_do_nivel_100anos_hoje']:>20.1f}"
                        for h in [2050, 2100]))
        res[cod].setdefault('dias_por_ano', {})[cen] = {
            str(h): {'acima_do_nivel_1ano': a[str(h)]['dias_por_ano_acima_do_nivel_1ano_hoje'],
                     'acima_do_nivel_100anos': a[str(h)]['dias_por_ano_acima_do_nivel_100anos_hoje']}
            for h in [2050, 2100]}
    print()

print("=" * 104)
print("[3] RELACAO ENTRE A LARGURA DA DISTRIBUICAO DE EXTREMOS E A SENSIBILIDADE")
print("=" * 104)
print("A amplificacao da frequencia depende de quao estreita e a distribuicao dos niveis")
print("extremos: onde a mare astronomica domina e a variabilidade de ressaca e pequena, a")
print("distancia entre o nivel anual e o centenario e curta, e uma elevacao modesta do")
print("nivel medio desloca a distribuicao por inteiro.")
print()
cab3 = (f"{'Estacao':<22} {'N 1 ano':>9} {'N 100 anos':>11} {'largura':>9} {'xi':>8} "
        f"{'fator x100a em 2100':>21}")
print(cab3); print("-" * len(cab3))
dados = []
for cod, d in EX.items():
    larg = d['largura_da_cauda_mm']
    f100 = d['amplificacao']['ssp245']['2100']['amplificacao_100anos']
    print(f"{d['nome'][:22]:<22} {d['niveis_retorno_mm']['1_ano']:>9.0f} "
          f"{d['niveis_retorno_mm']['100_anos']:>11.0f} {larg:>9.0f} {d['gpd']['xi']:>8.3f} "
          f"{f100:>20.0f}x")
    dados.append((larg, f100))
    res[cod]['largura_cauda_mm'] = larg
    res[cod]['fator_100anos_ssp245_2100'] = f100
L = np.array([x[0] for x in dados]); F = np.array([x[1] for x in dados])
r = float(np.corrcoef(np.log(L), np.log(F))[0, 1])
print("-" * len(cab3))
print(f"Correlacao entre log(largura da cauda) e log(fator de amplificacao): r = {r:+.3f}")
print("Quanto mais estreita a distribuicao de extremos, maior a amplificacao produzida")
print("pela mesma elevacao do nivel medio.")

json.dump({'criterio_cruzamento': '24 horas de excedencia por ano (1 dia/ano)',
           'ano_base': ANO0, 'estacoes': res,
           'correlacao_log_largura_log_fator': round(r, 4)},
          open(f"{RES}/limiares_alagamento.json", 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
print(f"\ngravado {RES}/limiares_alagamento.json")
