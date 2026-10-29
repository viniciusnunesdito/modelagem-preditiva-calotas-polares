# -*- coding: utf-8 -*-
"""Etapa 70: consolidacao dos numeros citados no artigo, para conferencia."""
import json
import numpy as np

OUT, RES = "02_dados_processados", "05_resultados"
L = lambda f: json.load(open(f, encoding='utf-8'))
FP = L(f"{OUT}/impressoes_digitais.json"); TR = L(f"{OUT}/fp_transecto_validacao.json")
VL = L(f"{OUT}/vlm_gnss.json"); QC = L(f"{OUT}/psmsl_qc_resumo.json")
FE = L(f"{RES}/fechamento_orcamento.json"); FL = L(f"{RES}/fechamento_local_refinado.json")
BM = L(f"{RES}/benchmark_algoritmos.json"); EM = L(f"{RES}/emulador_calotas.json")
PG = L(f"{RES}/projecoes_globais.json"); PL = L(f"{RES}/projecoes_locais.json")
VC = L(f"{RES}/vlm_comparacao_ar6.json"); EX = L(f"{RES}/extremos_frequencia.json")
RB = L(f"{RES}/recuo_linha_costa.json")
N = {}
p = print

p("=" * 96); p("NUMEROS CITADOS NO ARTIGO"); p("=" * 96)

p("\n[DADOS]")
ap = [r for r in QC if r['aprovada']]
N['psmsl_total'] = len(QC); N['psmsl_aprovadas'] = len(ap)
p(f"  estacoes PSMSL brasileiras no inventario: {len(QC)}")
p(f"  aprovadas pelos criterios (>=30 anos validos, >=25 de extensao): {len(ap)} "
  f"({', '.join(r['nome'].title() for r in ap)})")
for r in ap:
    p(f"     {r['nome'].title()}: {r['primeiro_ano']}-{r['ultimo_ano']}, {r['n_anos_validos']} anos "
      f"validos, completude {r['completude_pct']}%, {r['n_meses_ausentes']} meses ausentes")
N['frederikse_estacoes_br'] = 0
p("  series maregraficas brasileiras usadas por Frederikse et al. (2020): 0 de 472")

p("\n[V1 - REPRODUCAO DAS TENDENCIAS BARISTATICAS GLOBAIS, 1993-2018]")
for k, d in TR['validacao_global'].items():
    p(f"  {k:<6} reproduzido {d['reproduzido']:+.3f} | publicado {d['publicado']:+.2f} "
      f"+/- {d['inc_publicada']:.2f} mm/ano | diferenca {d['reproduzido']-d['publicado']:+.3f}")
N['validacao_global'] = TR['validacao_global']

p("\n[IMPRESSOES DIGITAIS]")
e = TR['estatisticas_transecto']
p(f"  transecto costeiro de {len(TR['transecto_costeiro'])} pontos, 4,4 N a 34 S")
for k, rot in [('GrIS', 'Groenlandia'), ('AIS', 'Antartica'), ('calotas', 'calotas combinadas'),
               ('total', 'total baristatico')]:
    p(f"  {rot:<20} media {e[k]['media']:.3f} | desvio {e[k]['desvio']:.3f} | "
      f"faixa {e[k]['min']:.3f} a {e[k]['max']:.3f}")
N['fp'] = e
cal = [r['calotas'] for r in TR['transecto_costeiro']]
p(f"  amplitude da impressao digital combinada: {max(cal)-min(cal):.3f} "
  f"({100*(max(cal)-min(cal))/np.mean(cal):.1f}% da media)")
p(f"  Ilha Fiscal: GrIS {FP['locais']['ILHA_FISCAL_RJ']['fp']['GrIS']:.3f}, "
  f"AIS {FP['locais']['ILHA_FISCAL_RJ']['fp']['AIS']:.3f}, "
  f"calotas {FP['locais']['ILHA_FISCAL_RJ']['fp_calotas_combinado']:.3f}")
ct = {c['nome']: c for c in TR['contraste_campo_proximo']}
p(f"  contraste de campo proximo: Nuuk GrIS {ct['Nuuk (Groenlandia)']['GrIS']:.2f}; "
  f"Mar de Amundsen AIS {ct['Mar de Amundsen (Antartica Ocidental)']['AIS']:.2f}")

p("\n[V2 - FECHAMENTO DO ORCAMENTO]")
for per in ['1900-2018', '1993-2018']:
    d = FE['global'][per]
    p(f"  Global {per}: soma {d['soma']:.3f} | observado {d['observado']:.3f} | "
      f"residuo {d['residuo']:+.3f} | {'FECHA' if d['fecha'] else 'nao fecha'} | "
      f"calotas {d['calotas_mm_ano']:.3f} mm/ano = {d['parcela_calotas_pct']:.1f}%")
    d2 = FE['atlantico_sul'][per]
    p(f"  Atlantico Sul {per}: soma {d2['soma']:.3f} | observado {d2['observado']:.3f} | "
      f"calotas {d2['parcela_calotas_pct']:.1f}%")
N['orcamento'] = {'global': FE['global'], 'atlantico_sul': FE['atlantico_sul']}
for cod, d in FL['estacoes'].items():
    for per, dd in d['periodos'].items():
        o = dd['observado']['ols']
        p(f"  {d['nome']} {per}: observado {o['coef']:.3f} mm/ano "
          f"(IC95 HAC {o['ic95_hac'][0]:.2f} a {o['ic95_hac'][1]:.2f}; rho1={o['rho1_residuos']:.2f}; "
          f"inflacao do EP {o['fator_inflacao_se']:.2f}x) | soma {dd['soma_prevista']:.3f} "
          f"+/- {dd['inc_soma']:.3f} | z={dd['z']:+.2f} | {'FECHA' if dd['fecha'] else 'NAO FECHA'} | "
          f"calotas {dd['parcela_calotas_observado_pct']:.1f}% do observado, "
          f"{dd['parcela_calotas_soma_pct']:.1f}% da soma")
N['fechamento_local'] = FL['estacoes']

p("\n[BENCHMARK DE ALGORITMOS]")
r1 = BM['teste1_ilha_fiscal']['resultados']; r2 = BM['teste2_calotas_global']['resultados']
p(f"  Teste 1 (Ilha Fiscal, {BM['teste1_ilha_fiscal']['n_anos']} anos, "
  f"{BM['teste1_ilha_fiscal']['n_origens']} origens), RMSE a 20 anos:")
for k in sorted(r1, key=lambda k: r1[k]['rmse']['20'])[:6]:
    p(f"     {k:<24} {r1[k]['rmse']['20']:>7.1f} mm")
p(f"     ...")
p(f"     media do treino = {r1['Media do treino']['rmse']['20']:.1f} mm; "
  f"OLS linear = {r1['OLS linear']['rmse']['20']:.1f} mm; "
  f"MLP = {r1['Rede neural (MLP)']['rmse']['20']:.1f} mm")
melhor1 = min(r1, key=lambda k: r1[k]['rmse']['20'])
p(f"     melhor algoritmo: {melhor1} ({r1[melhor1]['rmse']['20']:.1f} mm), contra "
  f"{r1['Media do treino']['rmse']['20']:.1f} mm da media trivial "
  f"-> ganho de apenas {100*(1-r1[melhor1]['rmse']['20']/r1['Media do treino']['rmse']['20']):.0f}%")
n_pior = sum(1 for k in r1 if r1[k]['rmse']['20'] > r1['Media do treino']['rmse']['20'])
p(f"     {n_pior} dos {len(r1)} algoritmos sao PIORES que prever a media historica")
p(f"  Teste 2 (calotas globais, {BM['teste2_calotas_global']['n_anos']} anos), RMSE a 20 anos:")
for k in sorted(r2, key=lambda k: r2[k]['rmse']['20'])[:4]:
    p(f"     {k:<24} {r2[k]['rmse']['20']:>7.1f} mm")
p(f"     media do treino = {r2['Media do treino']['rmse']['20']:.1f} mm")
p(f"  Extrapolacao a 2100: {len(BM['algoritmos_que_saturam'])} de "
  f"{len(BM['extrapolacao_2100'])} algoritmos saturam")
p(f"     {', '.join(BM['algoritmos_que_saturam'])}")
N['benchmark'] = {'teste1': r1, 'teste2': r2, 'saturam': BM['algoritmos_que_saturam'],
                  'n_piores_que_media': n_pior}

p("\n[EMULADOR]")
for k, d in EM['selecao'].items():
    par = ', '.join(f"{n_}={v:+.4f}" for n_, v in zip(d['nomes_par'], d['par_final']))
    p(f"  {d['rotulo']:<32} forma {d['forma']} | {par} | R2 {d['r2_final']:.4f}")
p("\n  V3 (calibracao cega 1900-1989 -> 1990-2018):")
for k, d in EM['V1_calibracao_cega'].items():
    p(f"     {d['rotulo']:<32} RMSE {d['rmse']:>6.2f} mm | R2 fora {d['r2_fora_amostra']:+.3f} | "
      f"erro na taxa {d['erro_taxa_pct']:+.1f}% | melhor referencia: {d['melhor_referencia']} "
      f"(ganho {d['ganho']:.1f}x)")
p("\n  V4 (dado independente IMBIE 1992-2018):")
for k, d in EM['V2_dado_independente'].items():
    p(f"     {d['rotulo']:<16} IMBIE {d['taxa_imbie']:+.3f} | emulador {d['taxa_emulador']:+.3f} mm/ano "
      f"({100*(d['taxa_emulador']-d['taxa_imbie'])/d['taxa_imbie']:+.1f}%) | R2 {d['r2']:.3f}")
N['emulador'] = {'selecao': EM['selecao'], 'V1': EM['V1_calibracao_cega'],
                 'V2': EM['V2_dado_independente']}

p("\n[SENSIBILIDADE DAS CALOTAS]")
for k, d in PG['sensibilidade'].items():
    p(f"  {d['rotulo']:<14} seculo XX {d['a_serie_longa']:.3f} | satelite {d['a_satelite']:.3f} "
      f"+/- {d['inc_a_satelite']:.3f} | AR6 {d['a_ar6']:.3f} mm/ano/K | "
      f"razao satelite/seculo XX = {d['razao']:.1f}x")
    p(f"     taxa {d['epoca1'][0]}-{d['epoca1'][1]}: {d['taxa1']:+.3f} mm/ano (T={d['T1']:+.2f} K) -> "
      f"{d['epoca2'][0]}-{d['epoca2'][1]}: {d['taxa2']:+.3f} mm/ano (T={d['T2']:+.2f} K)")
N['sensibilidade'] = PG['sensibilidade']

p("\n[PROJECOES GLOBAIS EM 2100 (mm acima de 2020)]")
for c in ['ssp126', 'ssp245', 'ssp585']:
    d = PG['projecao_global'][c]['total']
    p(f"  {c}: via A {d['viaA']['2100']:.0f} | via A' {d['viaAl']['2100']:.0f} | "
      f"via B {d['viaB']['2100']['p50']:.0f} (faixa provavel {d['viaB']['2100']['p17']:.0f}-"
      f"{d['viaB']['2100']['p83']:.0f}) | A' dentro da faixa: "
      f"{d.get('viaAl_dentro_faixa_AR6', {}).get('2100')}")
N['projecao_global'] = PG['projecao_global']

p("\n[V5 - REPRODUCAO DAS PROJECOES DO IPCC AR6 POR ESTACAO]")
for cen in PL['validacao_contra_ar6']:
    difs = [abs(PL['validacao_contra_ar6'][cen][c][str(h)]['dif_pct'])
            for c in PL['validacao_contra_ar6'][cen] for h in [2050, 2100]]
    p(f"  {cen}: diferenca absoluta media {np.mean(difs):.1f}%")
    for c, d in PL['validacao_contra_ar6'][cen].items():
        p(f"     {PL['fatores_locais'][c]['nome'][:22]:<22} 2100: AR6 {d['2100']['ar6_p50']:>6.0f} | "
          f"cadeia {d['2100']['cadeia_B']:>6.0f} mm | {d['2100']['dif_pct']:>+6.1f}%")
N['validacao_ar6'] = PL['validacao_contra_ar6']

p("\n[MOVIMENTO VERTICAL DO TERRENO: GNSS CONTRA IPCC AR6]")
for c, d in VC.items():
    p(f"  {d['nome']:<20} GNSS {d['vu_gnss']:+.2f} +/- {d['inc_gnss']:.2f} | "
      f"AR6 {d['vu_ar6']:+.2f} | diferenca {d['diferenca']:+.2f} mm/ano | "
      f"explica {d['fracao_explicada_pct']}% da diferenca da projecao")
N['vlm_vs_ar6'] = VC

p("\n[PARCELA DAS CALOTAS NA ELEVACAO PROJETADA, via B]")
for h in [2050, 2100]:
    todos = [PL['projecoes']['B'][c][k][str(h)]['pct_calotas']
             for c in PL['projecoes']['B'] for k in PL['projecoes']['B'][c]]
    p(f"  {h}: media {np.mean(todos):.1f}% | faixa {min(todos):.1f}% a {max(todos):.1f}%")
for c in ['ssp126', 'ssp245', 'ssp585']:
    v = [PL['projecoes']['B'][c][k]['2100']['pct_calotas'] for k in PL['projecoes']['B'][c]]
    a = [PL['projecoes']['B'][c][k]['2100']['calotas'] for k in PL['projecoes']['B'][c]]
    p(f"  {c} em 2100: {np.mean(v):.1f}% em media ({min(v):.1f}-{max(v):.1f}%); "
      f"contribuicao absoluta {min(a):.0f} a {max(a):.0f} mm")
N['parcela_calotas'] = {h: {c: {k: PL['projecoes']['B'][c][k][str(h)]
                                for k in PL['projecoes']['B'][c]} for c in PL['projecoes']['B']}
                        for h in [2050, 2100]}

p("\n[ELEVACAO PROJETADA POR ESTACAO, SSP2-4.5 (mm)]")
for k in PL['projecoes']['B']['ssp245']:
    d = PL['projecoes']['B']['ssp245'][k]
    p(f"  {PL['fatores_locais'][k]['nome'][:24]:<24} 2050: {d['2050']['total']:>5.0f} | "
      f"2100: {d['2100']['total']:>5.0f} mm")

p("\n[EXTREMOS]")
for c, d in EX.items():
    if not d['registro_longo']:
        continue
    n100 = d['niveis_retorno_mm']['100_anos']
    p(f"  {d['nome']} ({d['periodo'][0]}-{d['periodo'][1]}, {d['anos']:.0f} anos, "
      f"{d['n_horas']:,} horas)")
    p(f"     GPD: limiar {d['gpd']['u']:.0f} mm, xi={d['gpd']['xi']:+.3f}, sigma={d['gpd']['sigma']:.1f}")
    p(f"     niveis de retorno: 1 ano {d['niveis_retorno_mm']['1_ano']:.0f} | "
      f"10 anos {d['niveis_retorno_mm']['10_anos']:.0f} | 100 anos {n100:.0f} mm")
    for cen in ['ssp126', 'ssp245', 'ssp585']:
        for h in ['2050', '2100']:
            a = d['amplificacao'][cen][h]
            p(f"     {cen} {h}: S={a['S_mm']:.0f} mm -> T.R. do nivel de 100 anos passa a "
              f"{a['novo_TR_do_nivel_100anos_anos']:.2f} anos (x{a['amplificacao_100anos']:.0f}), "
              f"{a['dias_por_ano_acima_do_nivel_100anos_hoje']:.1f} dias/ano acima")
N['extremos'] = EX

p("\n[RECUO DA LINHA DE COSTA, SSP2-4.5 em 2100]")
r = RB['recuo']['ssp245']
for k in r:
    d = r[k]['2100']
    p(f"  {PL['fatores_locais'][k]['nome'][:24]:<24} S={d['S_m']:.3f} m -> recuo "
      f"1:50 {d['recuo_m']['1:50']:.0f} m | 1:100 {d['recuo_m']['1:100']:.0f} m "
      f"(parcela das calotas: {d['recuo_calotas_m']['1:100']:.0f} m)")
N['recuo'] = RB['recuo']

json.dump(N, open(f"{RES}/numeros_do_artigo.json", 'w', encoding='utf-8'),
          indent=1, ensure_ascii=False, default=str)
p(f"\ngravado {RES}/numeros_do_artigo.json")
