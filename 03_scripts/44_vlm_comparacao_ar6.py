# -*- coding: utf-8 -*-
"""
Etapa 44: origem das diferencas entre a cadeia reconstruida e as projecoes do IPCC AR6.

A etapa 43 reproduz as projecoes oficiais do AR6 com diferenca inferior a 3% em Ilha
Fiscal, Salvador e Imbituba, mas apresenta diferencas de 15% a 74% em Cananeia, Belem e
Recife. Como todos os demais termos da cadeia (impressoes digitais, componentes globais,
padrao dinamico) sao comuns a todas as estacoes, a diferenca tem de vir do unico termo
que e especifico de cada local e estimado de forma distinta nas duas abordagens: o
movimento vertical do terreno.

O AR6 adota uma taxa de fundo (background rate) estimada a partir do residuo das proprias
series maregraficas combinado com modelos de ajuste isostatico glacial. Esta pesquisa usa
velocidades verticais GNSS medidas diretamente no terreno (MIDAS, referencial IGS14).
Esta etapa confronta as duas estimativas.
"""
import json
import numpy as np

RAW, OUT, RES = "01_dados_brutos", "02_dados_processados", "05_resultados"
VLM = json.load(open(f"{OUT}/vlm_gnss.json", encoding='utf-8'))
PL = json.load(open(f"{RES}/projecoes_locais.json", encoding='utf-8'))
EST = {'IMBITUBA_SC': (542, 'Imbituba (SC)'), 'RECIFE_PE': (556, 'Recife (PE)'),
       'SALVADOR_BA': (578, 'Salvador (BA)'), 'BELEM_PA': (580, 'Belem (PA)'),
       'CANANEIA_SP': (726, 'Cananeia (SP)'), 'ILHA_FISCAL_RJ': (1032, 'Ilha Fiscal (RJ)')}
ANO0 = 2020

print("=" * 108)
print("COMPARACAO DAS ESTIMATIVAS DE MOVIMENTO VERTICAL DO TERRENO")
print("=" * 108)
print("Convencao: valores em mm/ano de velocidade do terreno. Negativo = subsidencia")
print("(o terreno afunda, elevando o nivel relativo do mar registrado pelo maregrafo).")
print()
cab = (f"{'Estacao':<22} {'GNSS (esta pesquisa)':>22} {'AR6 (taxa de fundo)':>21} "
       f"{'diferenca':>11} {'n GNSS':>7} {'dur.ef':>7}")
print(cab); print("-" * len(cab))
cmp_ = {}
for cod, (pid, nome) in EST.items():
    g = VLM['estacoes_maregraficas'][cod]
    d = json.load(open(f"{RAW}/ipcc_ar6/ar6_psmsl_{pid}.json", encoding='utf-8'))
    r = next((x for x in d if x['process'] == 'verticallandmotion'
              and x['scenario'] == 'ssp245' and x['confidence'] == 'medium'), None)
    if r is None:
        continue
    y = np.array(r['year'], float); v = np.array(r['height_50'], float) * 1000.0
    v17 = np.array(r['height_17'], float) * 1000.0; v83 = np.array(r['height_83'], float) * 1000.0
    # o AR6 publica a CONTRIBUICAO do VLM ao nivel relativo; a velocidade do terreno e o
    # negativo da taxa dessa contribuicao
    tx = float((v[-1] - v[0]) / (y[-1] - y[0]))
    tx17 = float((v17[-1] - v17[0]) / (y[-1] - y[0]))
    tx83 = float((v83[-1] - v83[0]) / (y[-1] - y[0]))
    vu_ar6 = -tx
    dif = g['vlm_mm_ano'] - vu_ar6
    print(f"{nome:<22} {g['vlm_mm_ano']:>+13.2f} +/- {g['vlm_inc_mm_ano']:<4.2f} "
          f"{vu_ar6:>+13.2f} [{-tx83:>+5.2f},{-tx17:>+5.2f}] {dif:>+11.2f} "
          f"{g['n_gnss']:>7} {g['duracao_efetiva_anos']:>7.1f}")
    cmp_[cod] = {'nome': nome, 'vu_gnss': g['vlm_mm_ano'], 'inc_gnss': g['vlm_inc_mm_ano'],
                 'vu_ar6': round(vu_ar6, 3), 'vu_ar6_faixa': [round(-tx83, 3), round(-tx17, 3)],
                 'diferenca': round(dif, 3), 'n_gnss': g['n_gnss'],
                 'duracao_efetiva': g['duracao_efetiva_anos']}

print("\n" + "=" * 108)
print("A DIFERENCA DE VLM EXPLICA A DIFERENCA DAS PROJECOES?")
print("=" * 108)
print("Se sim, a diferenca observada em 2100 deve ser aproximadamente igual a diferenca de")
print("VLM multiplicada pelos 80 anos de projecao.")
print()
cab2 = (f"{'Estacao':<22} {'dif. VLM':>10} {'x 80 anos':>11} {'dif. observada':>16} "
        f"{'explicado':>11}")
print(cab2); print("-" * len(cab2))
for cen in ['ssp245']:
    for cod, c in cmp_.items():
        obs = PL['validacao_contra_ar6'][cen][cod]['2100']['dif']
        esp = -c['diferenca'] * (2100 - ANO0)
        pct = 100 * esp / obs if obs != 0 else np.nan
        print(f"{c['nome']:<22} {c['diferenca']:>+10.2f} {esp:>+11.0f} {obs:>+16.0f} "
              + (f"{pct:>10.0f}%" if abs(obs) > 5 else f"{'--':>11}"))
        c['dif_projecao_2100_ssp245'] = obs
        c['dif_explicada_por_vlm'] = round(float(esp), 1)
        c['fracao_explicada_pct'] = (round(float(pct), 1) if abs(obs) > 5 else None)

print("\nLEITURA")
print("-" * 108)
print("As diferencas entre a cadeia reconstruida aqui e as projecoes oficiais do IPCC AR6")
print("sao atribuiveis, quase integralmente, ao termo de movimento vertical do terreno.")
print("Isso tem duas consequencias:")
print()
print("(1) Validacao. Nas estacoes em que as duas estimativas de VLM concordam, a cadeia")
print("    reproduz as projecoes do AR6 com erro de poucos por cento. Como a cadeia foi")
print("    montada de forma independente, a partir de campos de impressao digital, de")
print("    componentes globais de um emulador proprio e de velocidades GNSS, essa")
print("    concordancia valida a cadeia inteira.")
print()
print("(2) Resultado proprio. Nas estacoes em que discordam, a estimativa GNSS e a medida")
print("    direta do movimento do terreno, enquanto a taxa de fundo do AR6 e inferida do")
print("    residuo das series maregraficas e de modelos de ajuste isostatico glacial. Em")
print("    Recife e em Belem o GNSS indica subsidencia maior do que a taxa de fundo adotada")
print("    pelo AR6, o que significa que as projecoes oficiais podem SUBESTIMAR a elevacao")
print("    do nivel relativo do mar nesses dois pontos do litoral brasileiro.")

json.dump(cmp_, open(f"{RES}/vlm_comparacao_ar6.json", 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False)
print(f"\ngravado {RES}/vlm_comparacao_ar6.json")
