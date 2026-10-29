# -*- coding: utf-8 -*-
"""
Etapa 51: recuo projetado da linha de costa (resposta morfologica a elevacao do mar).

MODELO
------
Regra de Bruun (BRUUN, 1962): quando o nivel do mar sobe S, o perfil de equilibrio de uma
praia arenosa se reajusta transferindo sedimento da face da praia para a parte submersa,
de modo que a linha de costa recua uma distancia

        R = S / tan(beta)

em que tan(beta) e a declividade media do perfil ativo (da berma ate a profundidade de
fechamento). Como 1/tan(beta) e tipicamente entre 20 e 200 nas praias brasileiras, o
recuo e uma a duas ordens de grandeza maior que a elevacao: cada centimetro de mar vira
dezenas de centimetros a metros de praia perdida. E esse fator de amplificacao geometrica
que torna a elevacao do mar um problema de dinamica costeira, e nao apenas de nivel.

LIMITACOES QUE PRECISAM SER DECLARADAS
--------------------------------------
A regra de Bruun e um modelo de equilibrio bidimensional e e objeto de critica
consolidada na literatura (COOPER; PILKEY, 2004): ela supoe perfil de equilibrio
atingido, ausencia de aporte ou perda de sedimento por transporte longitudinal e por
rios, ausencia de afloramento rochoso e de estruturas rigidas, e nao representa dunas,
estuarios, manguezais nem costas de falesia. Em trechos com aporte fluvial abundante o
recuo pode ser menor ou ate negativo (progradacao); em trechos confinados por obras
costeiras o recuo e impedido e o resultado e o estreitamento ou a perda da praia
("coastal squeeze"). Por isso os valores aqui calculados nao sao previsoes de posicao de
linha de costa em um local especifico: sao a ordem de grandeza do recuo potencial de
praias arenosas expostas, apresentada como faixa sobre declividades representativas, e
servem para dimensionar a magnitude do problema, nao para licenciamento.

A declividade e tratada como faixa (1:20 a 1:200) porque nao se dispoe de levantamentos
batimetricos de perfil ativo padronizados para todo o litoral brasileiro; Muehe (2001,
2018) documenta essa heterogeneidade. Reporta-se tambem o recuo por metro de elevacao,
que permite a qualquer leitor recalcular o resultado com a declividade medida de sua
propria praia.
"""
import os, sys, json
import numpy as np

RES = "05_resultados"
PL = json.load(open(f"{RES}/projecoes_locais.json", encoding='utf-8'))
SSP = ['ssp126', 'ssp245', 'ssp585']
NOME_SSP = {'ssp126': 'SSP1-2.6', 'ssp245': 'SSP2-4.5', 'ssp585': 'SSP5-8.5'}
# declividades representativas do perfil ativo; 1:X
DECL = [(20, 'praia reflectiva, perfil ingreme'),
        (50, 'praia intermediaria'),
        (100, 'praia dissipativa, perfil suave'),
        (200, 'planicie costeira muito suave')]
HOR = [2050, 2100]

print("=" * 104)
print("RECUO POTENCIAL DA LINHA DE COSTA PELA REGRA DE BRUUN")
print("=" * 104)
print("Fator de amplificacao geometrica: recuo por metro de elevacao do nivel do mar")
print(f"\n   {'declividade do perfil ativo':<34} {'1/tan(beta)':>12} {'recuo por metro de elevacao':>30}")
print("   " + "-" * 78)
for x, rot in DECL:
    print(f"   1:{x:<4} {rot:<28} {x:>12} {x:>26} m")

print("\n\n" + "=" * 104)
print("RECUO PROJETADO POR ESTACAO (via B, projecoes do IPCC AR6)")
print("=" * 104)
res = {}
for cen in SSP:
    print(f"\n{NOME_SSP[cen]}")
    print(f"   {'Estacao':<24} {'S (m)':>7}" + "".join(f"{'1:' + str(x):>11}" for x, _ in DECL))
    for h in HOR:
        print(f"\n   recuo em {h} (m), por declividade:")
        for cod, dd in PL['projecoes']['B'][cen].items():
            S = dd[str(h)]['total'] / 1000.0
            nome = PL['fatores_locais'][cod]['nome']
            print(f"   {nome[:24]:<24} {S:>7.3f}" + "".join(f"{S*x:>11.1f}" for x, _ in DECL))
            res.setdefault(cen, {}).setdefault(cod, {})[h] = {
                'S_m': round(S, 4),
                'recuo_m': {f"1:{x}": round(S * x, 2) for x, _ in DECL},
                'recuo_por_metro_m': {f"1:{x}": x for x, _ in DECL}}

# parcela do recuo atribuivel especificamente as calotas polares
print("\n\n" + "=" * 104)
print("PARCELA DO RECUO ATRIBUIVEL AO DEGELO DAS CALOTAS POLARES")
print("=" * 104)
print("Aplicando a mesma regra apenas a componente de elevacao causada pelos mantos de gelo")
print("da Groenlandia e da Antartica (impressao digital ja incluida).")
for cen in ['ssp245', 'ssp585']:
    print(f"\n{NOME_SSP[cen]}, horizonte 2100")
    print(f"   {'Estacao':<24} {'S total (m)':>12} {'S calotas (m)':>14} {'%':>6}"
          + "".join(f"{'recuo cal. 1:' + str(x):>17}" for x, _ in DECL[:3]))
    for cod, dd in PL['projecoes']['B'][cen].items():
        d = dd['2100']
        St = d['total'] / 1000.0; Sc = d['calotas'] / 1000.0
        nome = PL['fatores_locais'][cod]['nome']
        print(f"   {nome[:24]:<24} {St:>12.3f} {Sc:>14.3f} {d['pct_calotas']:>6.1f}"
              + "".join(f"{Sc*x:>16.1f} m" for x, _ in DECL[:3]))
        res[cen][cod][2100]['S_calotas_m'] = round(Sc, 4)
        res[cen][cod][2100]['recuo_calotas_m'] = {f"1:{x}": round(Sc * x, 2) for x, _ in DECL}
        res[cen][cod][2100]['pct_calotas'] = d['pct_calotas']

print("\n\nSINTESE")
print("-" * 104)
cen, h = 'ssp245', 2100
Ss = [PL['projecoes']['B'][cen][c][str(h)]['total'] / 1000.0 for c in PL['projecoes']['B'][cen]]
Sc = [PL['projecoes']['B'][cen][c][str(h)]['calotas'] / 1000.0 for c in PL['projecoes']['B'][cen]]
print(f"No cenario intermediario SSP2-4.5 em {h}, a elevacao projetada no litoral brasileiro")
print(f"fica entre {min(Ss):.2f} e {max(Ss):.2f} m, dos quais entre {min(Sc):.2f} e {max(Sc):.2f} m")
print(f"vem do degelo das calotas polares. Em praias de declividade 1:50 a 1:100, isso")
print(f"corresponde a um recuo potencial de {min(Ss)*50:.0f} a {max(Ss)*100:.0f} m no total, dos quais")
print(f"{min(Sc)*50:.0f} a {max(Sc)*100:.0f} m atribuiveis especificamente as calotas.")

json.dump({'declividades': {f"1:{x}": rot for x, rot in DECL},
           'nota_metodologica': ("Regra de Bruun (1962): R = S / tan(beta). Modelo de "
                                 "equilibrio bidimensional, com as limitacoes discutidas por "
                                 "Cooper e Pilkey (2004). Valores de ordem de grandeza para "
                                 "praias arenosas expostas, nao previsoes locais."),
           'recuo': res},
          open(f"{RES}/recuo_linha_costa.json", 'w', encoding='utf-8'), indent=1, ensure_ascii=False)
print(f"\ngravado {RES}/recuo_linha_costa.json")
