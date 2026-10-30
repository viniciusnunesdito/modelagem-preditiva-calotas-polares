# Modelagem preditiva dos impactos do derretimento das calotas polares sobre a dinâmica costeira brasileira

Repositório completo da pesquisa: dados, código, resultados, figuras e artigo.

Curso de Ciência da Computação, 8º semestre — Universidade de Franca (UNIFRAN), Franca (SP).
Disciplina: Tendências da Computação — Prof. Dr. Renato Gonçalves Rocha.

Integrantes: Luiz Tonny Moura Santos; Vinícius Nunes Benedito; Kauan Henrique Teixeira; Pedro Henrique Pereira Boldrin; Mateus da Silva Vieira; Miguel Otávio Ferreira Martins; João Pedro Fernandes.

---

## 1. O que foi entregue

| Arquivo | Descrição |
|---|---|
| `06_artigo/ARTIGO_Modelagem_Preditiva_Calotas_Polares.docx` (e `.pdf`) | **Artigo científico**, 26 páginas, 6 figuras, 4 tabelas. Formatação do modelo institucional: A4, margens 3/3/2/2 cm, Arial 12, espaçamento 1,5, texto justificado com recuo de 1,25 cm, seções numeradas, ABNT. |
| `06_artigo/RELATORIO_CIENTIFICO_COMPLETO.docx` (e `.pdf`) | **Versão estendida**, 31 páginas, 8 figuras, 8 tabelas. Contém a fundamentação teórica completa, as tabelas de validação integrais e as duas figuras adicionais. Serve como documentação técnica e como fonte para eventual remanejamento de conteúdo. |
| `06_artigo/*.md` | Versões em Markdown, para edição rápida do texto. |
| `04_figuras/` | 8 figuras em PNG 300 dpi e PDF vetorial. |
| `05_resultados/` | Todos os resultados numéricos em JSON, mais os registros de execução (`_log_*.txt`) e o consolidado `numeros_do_artigo.json`. |
| `07_log_pesquisa/proveniencia_dados.json` | Cobre os 109 arquivos de `01_dados_brutos`. |
| `07_log_pesquisa/proveniencia_dados.json` | Para cada arquivo baixado: URL, descrição, fonte, tamanho, data de acesso e soma SHA-256. |
| `08_portfolio/` | **Portfólio do projeto**, 11 páginas em 16:9, em PDF e em HTML autossuficiente. O HTML lê as figuras de `04_figuras/` e abre em qualquer navegador; o PDF foi gerado a partir dele. |

### Observação sobre a extensão

O modelo institucional sugere 8 a 12 páginas. O artigo tem 26. A diferença decorre do volume de evidência empírica (cinco testes de validação, seis figuras, quatro tabelas) e não de prolixidade. Se o limite for rígido, a redução mais direta, nesta ordem, é: (a) mover a seção 4.6 (impactos costeiros) e a Figura 6 para apêndice, −3 páginas; (b) reduzir a Figura 1 e a seção 3 à metade, −3 páginas; (c) mover a Tabela 3 para apêndice, −1,5 página; (d) enxugar a seção 2, −2 páginas. Isso leva a ~12 páginas preservando os resultados principais.

---

## 2. Como reproduzir

Requisitos: Python 3.11+, `numpy scipy pandas matplotlib statsmodels scikit-learn xarray netCDF4 openpyxl python-docx`.

```
python 03_scripts/01_baixar_psmsl.py          # inventário e séries maregráficas
python 03_scripts/02_baixar_globais.py        # conjuntos globais
python 03_scripts/03_baixar_ipcc_ar6.py       # projeções IPCC AR6 por estação
python 03_scripts/04_baixar_uhslc.py          # séries horárias
python 03_scripts/10_processar_maregrafos.py  # controle de qualidade
python 03_scripts/11_processar_uhslc.py
python 03_scripts/12_processar_globais.py
python 03_scripts/20_impressoes_digitais.py   # impressões digitais
python 03_scripts/21_fp_transecto_e_validacao.py
python 03_scripts/22_vlm_gnss.py              # movimento vertical do terreno
python 03_scripts/30_fechamento_orcamento.py  # validação V2
python 03_scripts/31_fechamento_local_refinado.py
python 03_scripts/40_benchmark_algoritmos.py  # comparação de 15 algoritmos
python 03_scripts/41_emulador_calotas.py      # emulador e validações V3, V4
python 03_scripts/42_projecoes.py             # sensibilidade e projeções globais
python 03_scripts/43_projecoes_locais.py      # projeções locais e validação V5
python 03_scripts/44_vlm_comparacao_ar6.py
python 03_scripts/45_incerteza_sensibilidade.py  # propagacao da incerteza da sensibilidade
python 03_scripts/50_extremos_frequencia.py   # extremos
python 03_scripts/51_recuo_linha_de_costa.py  # regra de Bruun
python 03_scripts/52_limiares_e_dias_de_alagamento.py  # metricas operacionais
python 03_scripts/60_figuras.py               # figuras
python 03_scripts/70_numeros_do_artigo.py     # consolidação dos números
python 03_scripts/80_gerar_docx.py            # artigo .docx
python 03_scripts/80_gerar_docx.py completo   # versão estendida
```

Cada script é autocontido, documentado no cabeçalho com a justificativa metodológica da etapa, e grava seus resultados em JSON.

**Sobre a reprodutibilidade exata.** Os valores publicados reproduzem-se integralmente. Os arquivos JSON, porém, não são byte-idênticos entre máquinas: as etapas que resolvem mínimos quadrados não lineares (`41`) gravam `par_treino_V1` sem arredondamento, e a convergência do otimizador difere a partir da oitava casa significativa conforme a biblioteca de álgebra linear instalada. Nenhum número citado no artigo é afetado — a diferença aparece apenas nos dígitos não significativos desse campo.

---

## 3. Dados utilizados

Todos públicos, obtidos diretamente dos repositórios oficiais. O log `07_log_pesquisa/proveniencia_dados.json` cobre os 109 arquivos de `01_dados_brutos`, com URL, descrição, fonte, tamanho, data de acesso e soma SHA-256 de cada um.

Alimentam resultados numéricos:

- **PSMSL** — nível médio mensal e anual, conjunto RLR, 12 estações brasileiras, 1949–2022.
- **UHSLC** — nível horário de qualidade de pesquisa, 23 estações, 1954–2018.
- **IMBIE 2021** (Otosaka et al., 2023) — balanço de massa dos dois mantos, 1992–2020.
- **Frederikse et al. (2020)** — orçamento global e por bacia, 1900–2018, e campos espaciais de nível relativo de cada processo baristático em grade de 0,5°. Fonte das impressões digitais.
- **NOAA/NESDIS** — altimetria por satélite, 1993–2024.
- **HadCRUT5** (Morice et al., 2021) — temperatura média global, forçante do emulador.
- **MIDAS / Nevada Geodetic Laboratory** — velocidades verticais de 20.168 estações GNSS no referencial IGS14.
- **IPCC AR6 Sea Level Projections** (Garner et al., 2021) — projeções decompostas por processo, cenário e percentil, para 6 estações brasileiras e global.
- **IPCC AR6 WG1, Tabela SPM.1** — trajetórias de temperatura dos cenários SSP, extraídas do PDF oficial.

Obtidos e mantidos no repositório por rastreabilidade, mas **não** utilizados em nenhum resultado (nenhum script de análise os lê):

- **GRACE/GRACE-FO** (Wiese et al., 2022) — massa da Antártica, 2002–2026. A cobertura do balanço de massa vem do IMBIE e de Frederikse et al. (2020).
- **GISTEMP v4** — temperatura média global. O emulador usa HadCRUT5.
- **NOAA NCEI** — conteúdo de calor oceânico, 0–700 m e 0–2000 m.
- **Church e White (2011)** — reconstrução do nível médio global, 1880–2013.
- **IPCC AR6 `location_list.lst`** — lista de 66.190 localidades da ferramenta de projeções.

---

## 4. Resultados principais

**Impressões digitais.** A costa brasileira recebe 1,119 ± 0,042 vez a elevação média global causada pelo degelo polar. O fator da Groenlândia cresce de 0,97 (foz do Amazonas) a 1,32 (RS); o da Antártica decresce de 1,15 a 0,68. Os gradientes se compensam, e o fator combinado varia apenas 12,8% em 4.000 km. Nos pontos de contraste, os fatores são negativos (Nuuk: −7,49; Mar de Amundsen: −10,08), confirmando a física do campo próximo.

**Fechamento do orçamento.** Fecha em escala global (resíduo de 0,039 mm/ano em 1900–2018), no Atlântico Sul e na Ilha Fiscal. É rejeitado em Cananéia (z = +3,11), apesar de essa estação ter o melhor ajuste de regressão de toda a análise — demonstração de que o diagnóstico estatístico não substitui o teste de consistência física.

**Algoritmos preditivos.** O teste foi aplicado às duas estações brasileiras de registro longo, e os resultados divergem. Na Ilha Fiscal, 12 de 15 algoritmos são piores que prever a média histórica no horizonte de 20 anos e o melhor ganha 3%; em Cananéia, apenas 2 são piores e o melhor ganha 65%. A diferença decorre da razão sinal-ruído de cada série (R² de 0,235 contra 0,734), não do algoritmo. O ponto é que a série em que os algoritmos funcionam bem é justamente a que o teste de fechamento rejeita: uma seleção guiada só por desempenho de validação escolheria a estação fisicamente inconsistente. Independentemente da estação, 6 dos 15 algoritmos são estruturalmente incapazes de extrapolar — devolvem um valor constante, idêntico em 2030, 2050 e 2100, quando se pede o de 2100.

**Emulador.** Calibrado apenas com 1900–1989, prevê a taxa de perda da Groenlândia em 1990–2018 com erro de 5,0% e a expansão térmica com erro de 10,4%. Confrontado com o IMBIE, conjunto independente medido por satélite, erra +9,5% (Groenlândia) e −16,9% (Antártica). O resultado de 5,0% é condicionado à convenção de suavização do forçante: com média móvel retroativa em vez de centrada, a seleção recai sobre outra forma funcional e o erro sobe a 64,7%. Ver a seção 4.8 do artigo.

**Sensibilidade.** A sensibilidade da Groenlândia ao aquecimento no período de satélite é 0,965 ± 0,502 mm/ano por kelvin (1σ), contra 0,132 no ajuste centenário — razão pontual de 7,3. Propagando a incerteza das duas estimativas, a razão tem mediana de 5,0 e intervalo de 95% de 0 a 13,6, com 93% de probabilidade de exceder a unidade: o aumento é provável, a magnitude é mal determinada. A diferença em relação à sensibilidade implícita no AR6 (0,663) é de 0,60σ (p = 0,55), ou seja, as duas são compatíveis — o dado não sustenta afirmar que as projeções oficiais sejam conservadoras nesse componente. Ver a seção 4.8 do artigo.

**Projeções.** No cenário SSP2-4.5, elevação de 0,40 a 0,79 m até 2100 nos onze pontos, dos quais 26% a 44% atribuíveis às calotas polares. A cadeia reproduz as projeções oficiais do IPCC AR6 com diferença de 1,0% a 3,6% em 2100 no cenário intermediário (0,7% a 4,4% nos três cenários testados), nas três estações em que as estimativas de movimento do terreno concordam.

**Subsidência.** Medições GNSS indicam −3,05 ± 0,87 mm/ano em Recife, contra +0,49 mm/ano adotado pelo IPCC AR6: implica subestimação de cerca de 28 cm na elevação relativa projetada para 2100.

**Impactos costeiros.** O nível hoje centenário no Rio de Janeiro passa a período de retorno de 0,12 ano em 2100 (fator 806 no SSP2-4.5). Em métrica operacional, isso equivale a 11,3 dias por ano acima do nível hoje anual e 0,3 dia por ano acima do centenário; o nível centenário passa a ocorrer anualmente em 2110. A amplificação é inversamente proporcional à largura da distribuição de extremos de cada estação (correlação entre logaritmos r = −0,986), o que torna as cidades do Nordeste, de regime estreito dominado pela maré, as mais sensíveis. Recuo potencial de linha de costa de 20 a 79 m em praias arenosas, dos quais 9 a 21 m atribuíveis às calotas.

---

## 5. Relação com o material anterior do grupo

O material em `00_materiais_originais/` foi integralmente lido e aproveitado. O que foi mantido, corrigido e acrescentado:

**Mantido e confirmado.** A escolha da Ilha Fiscal como estação principal, o diagnóstico de que Cananéia e Imbituba têm confiabilidade limitada, e a estrutura treino/teste/projeção. A tendência de 2,42 mm/ano para 1963–2018 foi reproduzida de forma independente e coincide com Carvalho et al. (2024).

**Corrigido.** (a) O R² negativo fora da amostra, antes tratado como anomalia da estação, revelou-se propriedade geral do problema: nenhum algoritmo supera a média histórica naquele horizonte. (b) A autocorrelação dos resíduos, antes apenas declarada, foi tratada com erro padrão robusto e bootstrap de blocos; os intervalos aumentam em até 1,7 vez. (c) O descarte do modelo quadrático foi generalizado: sem restrição de monotonicidade, toda forma flexível se inverte ou explode na extrapolação. (d) A projeção local, antes extrapolação da tendência histórica, foi substituída por cadeia física com atribuição por processo.

**Acrescentado.** As impressões digitais do nível do mar, que são o elo causal faltante entre degelo polar e costa brasileira; a medida independente do movimento vertical do terreno por GNSS; o teste de fechamento do orçamento; o emulador acionado por temperatura; a expansão de uma para onze localidades; a análise de extremos sobre dados horários; e a modelagem do recuo da linha de costa.

**Escopo não desenvolvido.** O Tópico 2 (AMOC e salinidade) permanece como fundamentação teórica e não foi incorporado à cadeia quantitativa. A razão é declarada no artigo: o sinal de nível do mar dinâmico associado ao enfraquecimento da AMOC no Atlântico Sul é pequeno e pouco restringido observacionalmente, e incorporá-lo exigiria modelagem oceânica fora do alcance deste trabalho. O material do Tópico 2 sustenta a discussão, mas não entra nos números.

---

## 6. Pontos que exigem decisão ou verificação

1. **Autoria e afiliação.** Os sete integrantes, o curso e a instituição estão preenchidos no artigo, no relatório e no portfólio. Faltam apenas o autor correspondente com e-mail e a tabela de divisão de responsabilidades no Apêndice A.
2. **Extensão.** Ver a observação da seção 1.
3. **Referências.** Autor, título, periódico, volume, páginas e DOI de todas as entradas foram conferidos contra Crossref/DataCite. Dois DOIs estavam incorretos e foram corrigidos: Frederikse et al. (2020), de `10.1038/s41586-020-2591-4` para `...-2591-3`, e Roffman et al. (2023), de `10.1093/gji/ggad265` para `10.1093/gji/ggad170`. Recomenda-se, ainda assim, conferência final contra os originais antes da submissão.
4. **Dados não obtidos.** A série GRACE/GRACE-FO da Groenlândia exige credenciais Earthdata e não foi baixada; a lacuna é coberta pelo IMBIE (1992–2020) e pela reconstrução de Frederikse (1900–2018), suficientes para todas as análises realizadas. A série antártica do GRACE foi obtida, mas não entra em nenhum resultado (ver seção 3).
