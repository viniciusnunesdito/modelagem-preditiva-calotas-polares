# MODELAGEM PREDITIVA DOS IMPACTOS DO DERRETIMENTO DAS CALOTAS POLARES SOBRE A DINÂMICA COSTEIRA BRASILEIRA

Luiz Tonny Moura Santos¹; Vinícius Nunes Benedito¹; Kauan Henrique Teixeira¹;
Pedro Henrique Pereira Boldrin¹; Mateus da Silva Vieira¹; [Nome completo do 6º integrante]¹;
[Nome completo do 7º integrante]¹; Prof. Dr. Renato Gonçalves Rocha²

¹ Curso de Ciência da Computação, Universidade de Franca (UNIFRAN), Franca, São Paulo, Brasil.
² Professor Orientador, Universidade de Franca (UNIFRAN), Franca, São Paulo, Brasil.

Autor correspondente: ____________________ – e-mail: ____________________

---

## RESUMO

O derretimento dos mantos de gelo da Groenlândia e da Antártica é frequentemente associado à elevação do nível do mar no litoral brasileiro, mas essa associação raramente é quantificada: o que se projeta localmente costuma ser a média global aplicada sem correção, e o que se mede nos marégrafos mistura o sinal oceânico com o movimento do terreno. Este trabalho construiu e validou uma cadeia preditiva que separa essas contribuições, convertendo a perda de massa polar em elevação local por meio das impressões digitais do nível do mar, medindo o movimento vertical do terreno por estações GNSS e acionando um emulador semi-empírico, calibrado em 119 anos de observação, com as trajetórias de temperatura do IPCC AR6. Cinco testes independentes de validação foram aplicados. A costa brasileira recebe 1,12 vez a elevação média global causada pelo degelo polar, com variação de apenas 12,8% ao longo de 4.000 km, porque os gradientes opostos das duas calotas se compensam. O orçamento do nível do mar fecha na Ilha Fiscal, mas é rejeitado em Cananéia, estação cuja regressão apresentava o melhor ajuste estatístico. O desempenho dos quinze algoritmos preditivos testados varia em sentido oposto nas duas séries maregráficas longas do país, conforme a razão sinal-ruído de cada uma e não conforme o algoritmo, e a estação em que eles têm bom desempenho é justamente a que o teste físico rejeita; independentemente da série, seis deles são estruturalmente incapazes de extrapolar. A sensibilidade da Groenlândia ao aquecimento no período de satélite excede provavelmente a média do século XX, com 93% de probabilidade e magnitude mal determinada (razão com mediana de 5,0 e intervalo de 95% de 0 a 13,6), e é compatível com a implícita nas projeções processuais, cuja magnitude fica assim sustentada de forma independente. Projeta-se, no cenário intermediário, elevação de 0,40 a 0,79 m até 2100 nos onze pontos analisados, dos quais 26% a 44% atribuíveis às calotas polares, recuo potencial de linha de costa de 20 a 79 m e multiplicação por 806 da frequência do nível extremo hoje centenário no Rio de Janeiro. Mediu-se subsidência de 3,05 ± 0,87 mm/ano em Recife, não incorporada às projeções oficiais, o que implica subestimação de cerca de 28 cm na elevação relativa projetada para aquela cidade.

**Palavras-chave:** elevação do nível do mar; impressão digital do nível do mar; modelagem preditiva; erosão costeira; validação de modelos.

## ABSTRACT

The melting of the Greenland and Antarctic ice sheets is often linked to sea-level rise along the Brazilian coast, yet this link is rarely quantified: local projections typically apply the global mean without correction, and tide-gauge measurements conflate the oceanic signal with vertical land motion. This study built and validated a predictive chain that separates these contributions, converting polar mass loss into local rise through sea-level fingerprints, measuring vertical land motion from GNSS stations, and driving a semi-empirical emulator calibrated on 119 years of observations with IPCC AR6 temperature pathways. Five independent validation tests were applied. The Brazilian coast receives 1.12 times the global mean rise caused by polar melt, varying by only 12.8% over 4,000 km because the opposing gradients of the two ice sheets cancel. The sea-level budget closes at Ilha Fiscal but is rejected at Cananéia, the station whose regression showed the best statistical fit. The performance of fifteen predictive algorithms diverges in opposite directions between the country's two long tide-gauge series, driven by each record's signal-to-noise ratio rather than by the algorithm, and the station where they perform well is precisely the one the physical test rejects; regardless of the series, six are structurally unable to extrapolate. Greenland's sensitivity to warming during the satellite era most likely exceeds the twentieth-century average, with 93% probability but poorly determined magnitude (ratio median 5.0, 95% interval 0 to 13.6), and is consistent with the sensitivity implicit in process-based projections, whose magnitude is thereby independently supported. Under the intermediate scenario, projected rise by 2100 at the eleven sites ranges from 0.40 to 0.79 m, of which 26% to 44% is attributable to polar ice sheets, implying potential shoreline retreat of 20 to 79 m and an 806-fold increase in the frequency of the present-day one-in-a-century extreme level in Rio de Janeiro. Subsidence of 3.05 ± 0.87 mm/yr was measured at Recife, not incorporated in official projections, implying an underestimation of about 28 cm in projected relative sea-level rise for that city.

**Keywords:** sea-level rise; sea-level fingerprint; predictive modelling; coastal erosion; model validation.

---

## 1 INTRODUÇÃO

A associação entre o derretimento das calotas polares e a elevação do nível do mar no litoral brasileiro é um lugar-comum do debate climático, mas raramente é tratada como questão quantitativa. Afirmar que o degelo da Groenlândia ameaça as cidades costeiras do Brasil exige responder a três perguntas distintas: quanta água o degelo acrescenta ao oceano, quanto dessa água chega à costa brasileira, e quanto da elevação medida pelos marégrafos brasileiros se deve a esse processo e não a outros. As três têm respostas diferentes, e nenhuma delas é a média global.

A primeira tem resposta observacional consolidada: entre 1992 e 2020 os dois mantos perderam cerca de 7.560 bilhões de toneladas de gelo, elevando o nível médio global em aproximadamente 21 mm, com a taxa de perda mais que triplicando ao longo do período (OTOSAKA et al., 2023).

A segunda é menos conhecida e concentra o mal-entendido. A água liberada por um manto de gelo não se distribui uniformemente. A perda de massa reduz a atração gravitacional que o gelo exercia sobre a água vizinha, alivia o peso sobre a crosta, que sobe elasticamente, e desloca ligeiramente o eixo de rotação do planeta. O resultado é que, nas águas próximas à fonte, o nível relativo do mar **cai**, enquanto no campo distante sobe **mais** que a média global (MITROVICA et al., 2001). Essa assinatura espacial chama-se impressão digital do nível do mar. O Brasil está no campo distante de ambas as calotas, mas quanto recebe a mais, e se esse fator varia ao longo do litoral, são questões que a literatura brasileira menciona qualitativamente sem quantificar.

A terceira esbarra na natureza do instrumento. Um marégrafo mede o nível **relativo**: a altura da água em relação a um marco fixado em terra. Se o terreno afunda, o aparelho registra elevação mesmo que o volume do oceano não mude. Sem medida independente do movimento vertical do terreno, a tendência observada não pode ser atribuída a causa alguma. O Painel Brasileiro de Mudanças Climáticas já apontava essa limitação, somada à escassez de séries contínuas no país (PBMC, 2016).

Soma-se uma quarta lacuna, metodológica. A expectativa corrente é que técnicas de aprendizado de máquina aplicadas a séries históricas produzam projeções climáticas confiáveis. Revisões recentes recomendam, ao contrário, abordagens híbridas que combinem física e aprendizado para previsões regionais de longo prazo (AYINDE et al., 2024) — recomendação habitualmente aceita por autoridade, sem demonstração numérica de por que a abordagem puramente estatística falha.

O objetivo deste trabalho é construir, validar e aplicar uma cadeia preditiva que responda às três primeiras perguntas de forma quantitativa para a costa brasileira e que submeta a quarta a teste experimental explícito. A contribuição pretendida não é mais uma projeção de elevação do mar, mas a decomposição dessa elevação, atribuindo a cada processo físico a parcela que lhe cabe em cada ponto do litoral, com demonstração, etapa por etapa, de que cada elo reproduz observações independentes.

## 2 FUNDAMENTAÇÃO TEÓRICA

O nível médio global do mar varia por dois mecanismos independentes: a adição de massa de água ao oceano, chamada contribuição baristática, proveniente de mantos de gelo, geleiras e armazenamento de água continental; e a variação do volume ocupado por essa massa, a contribuição estérica, decorrente de expansão térmica e mudanças de salinidade (GREGORY et al., 2019). Verificar se a soma dessas contribuições iguala a elevação observada é o que se chama fechamento do orçamento do nível do mar, teste padrão de consistência física do conjunto de observações (WCRP GLOBAL SEA LEVEL BUDGET GROUP, 2018). Frederikse et al. (2020) reconstruíram esse orçamento desde 1900, disponibilizando séries globais e por bacia e campos espaciais de cada processo.

A equação do nível do mar, resolvida para a perda de massa de um manto de gelo, produz um campo espacial característico: queda do nível relativo nas proximidades da fonte e elevação superior à média no campo distante (MITROVICA et al., 2001; TAMISIEA; MITROVICA, 2011). Define-se o fator de impressão digital de um processo *p* em um ponto *x* como a razão adimensional entre a tendência local do nível relativo e a tendência da média global devidas àquele processo. Esse fator é a ponte quantitativa entre a perda de massa polar e o nível do mar em um ponto específico da costa, e é peça obrigatória de qualquer projeção regional (SLANGEN et al., 2014). O trabalho mais próximo do presente é o de Roffman et al. (2023), que identificou, na costa sul-americana, amplificação de até 2,9 vezes o equivalente médio global em cenário de ganho de massa na Península Antártica.

A tendência de nível relativo relaciona-se à tendência geocêntrica pela subtração da velocidade vertical do terreno, mensurável por posicionamento por satélite. O conjunto MIDAS do Nevada Geodetic Laboratory fornece estimativas robustas a degraus instrumentais para toda a rede GNSS global no referencial IGS14 (BLEWITT et al., 2016).

Modelos semi-empíricos projetam o nível do mar a partir de uma relação ajustada entre temperatura global e taxa de elevação, na forma dS/dt = a(T − T₀) (RAHMSTORF, 2007). A lógica é deslocar o objeto do aprendizado: em vez da forma da curva no tempo, aprende-se a relação entre forçante e resposta, de modo que projetar passe a ser avaliar essa relação em valores de temperatura fornecidos por cenários. A mesma lógica sustenta a emulação estatística usada para substituir modelos de manto de gelo computacionalmente caros (EDWARDS et al., 2021).

Sobre a costa, a elevação média atua por dois caminhos. O morfológico: pela regra de Bruun (1962), o perfil de equilíbrio de uma praia arenosa reajusta-se a uma elevação *S* recuando R = S/tanβ, em que tanβ é a declividade do perfil ativo; como esse inverso é tipicamente de 20 a 200, o recuo é uma a duas ordens de grandeza maior que a elevação. O modelo é objeto de crítica consolidada (COOPER; PILKEY, 2004) e deve ser lido como ordem de grandeza. O probabilístico: como a cauda da distribuição dos níveis extremos decai de forma aproximadamente exponencial, um deslocamento modesto do nível médio multiplica exponencialmente a frequência de excedência de um limiar fixo (VITOUSEK et al., 2017; TAHERKHANI et al., 2020).

Um levantamento das 472 séries maregráficas utilizadas por Frederikse et al. (2020) revelou que **nenhuma delas é brasileira**: no Atlântico Sul o conjunto apoia-se exclusivamente em estações da Argentina, do Uruguai, da África do Sul e da Namíbia. O país com o maior litoral atlântico do Hemisfério Sul não participa da base observacional que sustenta a reconstrução de referência. É a essa lacuna que este trabalho se dirige.

## 3 METODOLOGIA

A Figura 1 resume a cadeia de cálculo e os pontos de validação. O processamento foi implementado em Python; dados brutos, scripts e resultados intermediários estão organizados em repositório com registro de proveniência — URL, data de acesso e soma de verificação criptográfica — para cada arquivo.

**[Figura 1 – Estrutura metodológica da pesquisa e seus cinco pontos de validação.]**
Fonte: Elaborado pelos autores (2026).

### 3.1 Dados e controle de qualidade

Utilizaram-se: séries maregráficas de doze estações brasileiras do PSMSL (HOLGATE et al., 2013) e séries horárias de qualidade de pesquisa do UHSLC (CALDWELL; MERRIFIELD; THOMPSON, 2015); balanço de massa dos dois mantos pelo IMBIE (OTOSAKA et al., 2023); orçamento global e campos espaciais de cada processo em grade de 0,5° (FREDERIKSE et al., 2020); altimetria por satélite (NOAA, 2026); temperatura global HadCRUT5 (MORICE et al., 2021); velocidades verticais de 20.168 estações GNSS (BLEWITT et al., 2016); e as projeções do IPCC AR6 decompostas por processo, cenário e percentil (GARNER et al., 2021).

Às séries maregráficas aplicaram-se regras declaradas e idênticas para todas as estações: descarte do código de ausência e de meses sinalizados; média anual apenas com anos de pelo menos dez meses válidos, para evitar viés sazonal; e exigência mínima de 30 anos válidos e 25 anos de extensão. Para as séries horárias exigiu-se cobertura de 70% das horas de cada mês e dez meses válidos por ano.

Como os resíduos de séries anuais de nível do mar são fortemente autocorrelacionados, o que faz o erro padrão dos mínimos quadrados subestimar a incerteza real, toda tendência foi estimada por três caminhos: mínimos quadrados com erro padrão robusto de Newey e West (1987), estimador de Theil-Sen e reamostragem por blocos móveis.

### 3.2 Impressões digitais e cadeia de projeção local

Os fatores de impressão digital foram calculados a partir dos campos de nível relativo de cada processo baristático, como a razão entre a tendência local e a tendência da média global ponderada pelo cosseno da latitude, no mesmo período em que o fator seria aplicado. Calcularam-se fatores em onze estações, em um transecto contínuo de 28 pontos ao longo do litoral de 4,4° N a 34° S, e em sete pontos de contraste fora do Brasil destinados a verificar a física do campo próximo.

Para cada estação *x*, cenário *c* e horizonte *h*, o nível relativo projetado é

RSL(x, c, h) = Σₚ FPₚ(x) · Sₚ(c, h) + δ(x) · S_estérico(c, h) − VLM(x) · (h − 2020)

em que Sₚ são as contribuições globais de cada processo, FPₚ(x) os fatores de impressão digital, δ(x) o padrão dinâmico local e VLM(x) a velocidade vertical do terreno. Para o termo estérico, ao qual a impressão digital gravitacional não se aplica, δ(x) foi obtido da razão entre a projeção de dinâmica oceânica do IPCC AR6 na estação e a global, por representar a resposta forçada; a razão estérica histórica foi calculada e descartada, por refletir variabilidade dinâmica decadal e não resposta ao forçamento.

### 3.3 Emulador semi-empírico

Para cada componente, ajustou-se dS/dt como função da temperatura média global relativa a 1850–1900, testando quatro formas funcionais: linear, linear com termo de taxa, potência e quadrática. Impuseram-se restrições de monotonicidade — coeficiente principal não negativo, expoente maior ou igual a um, curvatura não negativa — de modo que mais aquecimento jamais produza menos perda de massa. A restrição não é detalhe técnico: sem ela, o ajuste seleciona uma parábola de curvatura negativa que reproduz bem o passado e se inverte na extrapolação, modo de falha efetivamente observado durante o desenvolvimento.

A forma funcional e a janela de suavização do forçante foram escolhidas por validação cruzada de origem móvel aninhada, usando apenas anos anteriores a 1990, com regra de parcimônia: entre as combinações cujo erro está a menos de 5% do melhor, adota-se a de menor número de parâmetros. A aplicação da regra foi decisiva: doze combinações mostraram-se estatisticamente indistinguíveis para os mantos de gelo, e a seleção pela mais flexível produzia projeção de 9 mm/ano a 4,4 K de aquecimento, uma ordem de grandeza acima de qualquer estimativa publicada. A forma selecionada foi a linear de Rahmstorf (2007) para os três componentes de massa; para o termo estérico a validação selecionou a forma de potência, cujo expoente ajustado convergiu para o limite inferior do intervalo admitido (q = 1,00), de modo que ela também se reduz, na prática, à forma linear.

Três vias de projeção foram levadas adiante: a via A, com o emulador calibrado em 1900–2018; a via A′, com a mesma forma linearizada em torno do estado observado recente, usando a sensibilidade medida no período de satélite; e a via B, com as projeções processuais oficiais do IPCC AR6.

### 3.4 Impactos costeiros e protocolo de validação

A frequência de extremos foi modelada por distribuição de Pareto generalizada ajustada aos excessos acima de limiar alto, sobre as séries horárias destendenciadas e dessazonalizadas, com verificação de estabilidade em cinco limiares; a taxa de excedência é definida sobre valores horários. O recuo da linha de costa foi estimado pela regra de Bruun sobre quatro declividades representativas.

Cinco testes independentes foram aplicados: **V1**, reprodução das tendências baristáticas globais publicadas a partir dos campos espaciais; **V2**, fechamento do orçamento em escala global, de bacia e de estação; **V3**, calibração cega ao futuro, com o emulador ajustado somente com 1900–1989 e solicitado a prever 1990–2018; **V4**, confronto com o IMBIE, conjunto independente medido por satélite; **V5**, reprodução das projeções oficiais do IPCC AR6 nas seis estações brasileiras para as quais existem.

## 4 RESULTADOS E DISCUSSÃO

### 4.1 Disponibilidade dos dados e impressões digitais

Das doze estações brasileiras do PSMSL, apenas duas satisfazem os critérios de qualidade: Cananéia (1954–2004, 51 anos válidos) e Ilha Fiscal (1963–2022, 55 anos válidos). As demais têm séries de 1 a 20 anos, em geral encerradas na década de 1960. A verificação das séries horárias confirmou o quadro: embora os metadados indiquem extensão até 2023 em Fortaleza, a cobertura efetiva é de 13 anos. A escassez de séries longas no litoral brasileiro é, portanto, um resultado verificado e não apenas uma observação qualitativa.

A validação V1 confere: as cinco tendências baristáticas globais reproduzidas a partir dos campos espaciais coincidem com os valores publicados dentro da incerteza declarada, com diferença máxima de 0,024 mm/ano (Groenlândia 0,626 contra 0,65 ± 0,04; Antártica 0,302 contra 0,29 ± 0,08; geleiras 0,646 contra 0,65 ± 0,09; água continental 0,312 contra 0,32 ± 0,17 mm/ano).

A Figura 2 mostra os fatores de impressão digital. Ao longo de 4.000 km de litoral, o fator da Groenlândia cresce de forma quase monotônica de 0,97 na foz do Amazonas a 1,32 no Rio Grande do Sul (r = −0,98 com a latitude; a única inversão, de 1,263 para 1,257 entre 22,9° S e 23,5° S, é de 0,5%), enquanto o da Antártica decresce de 1,15 para 0,68 (r = +0,93). Os gradientes têm sinal oposto por descreverem o afastamento de fontes situadas em hemisférios opostos, e **compensam-se**: o fator combinado das duas calotas permanece em 1,119 ± 0,042, variando apenas 12,8% em toda a costa.

O resultado tem duas leituras. Quantitativamente, cada milímetro de elevação média global causado pelo degelo polar produz cerca de 1,12 mm na costa brasileira — amplificação de 12% que as projeções baseadas na média global não contabilizam. Operacionalmente, como o fator é praticamente uniforme, uma única constante de amplificação serve a todo o litoral.

Os pontos de contraste confirmam a física: em Nuuk, o fator do próprio manto groenlandês é −7,49; no Mar de Amundsen, o fator antártico é −10,08. Nas águas que banham a fonte do degelo o nível relativo **cai**, porque a perda de atração gravitacional e o rebote elástico superam o acréscimo de volume. No campo distante, onde está o Brasil, encontra-se o excedente.

**[Figura 2 – Fatores de impressão digital do nível do mar: (a) transecto ao longo do litoral brasileiro; (b) contraste entre campo próximo e campo distante.]**
Fonte: Elaborado pelos autores (2026).

### 4.2 O orçamento fecha, e onde não fecha isso é informativo

Em escala global o orçamento fecha em todos os períodos: de 1900 a 2018, a soma dos contribuintes é 1,524 mm/ano contra 1,563 observados (resíduo de 0,039); de 1993 a 2018, 3,159 contra 3,353 mm/ano. Os mantos de gelo respondem por 33,3% da elevação global no período longo e 29,1% na era altimétrica; no Atlântico Sul, por 28,9%. A Tabela 1 apresenta o teste em escala local.

**Tabela 1 – Validação V2: fechamento do orçamento nas estações brasileiras (mm/ano).**

| Estação e período | Observado (IC 95% HAC) | Soma prevista | Resíduo | z | Resultado | Calotas |
|---|---|---|---|---|---|---|
| Ilha Fiscal, 1963–2018 | +2,421 (+0,36 a +4,48) | 1,317 ± 0,545 | +1,104 | +0,93 | fecha | 20,5% |
| Ilha Fiscal, 1993–2018 | +2,879 (−2,75 a +8,51) | 1,516 ± 0,547 | +1,362 | +0,47 | fecha | 37,5% |
| Cananéia, 1957–2004 | +4,099 (+3,13 a +5,07) | 0,793 ± 0,942 | +3,306 | +3,11 | **não fecha** | 7,2% |

Fonte: Elaborado pelos autores (2026).

A tendência estimada para a Ilha Fiscal em 1963–2018, de 2,421 mm/ano, coincide com os 2,42 mm/ano publicados por Carvalho et al. (2024) para 1963–2017 na mesma estação. A reprodução independente de um resultado revisado por pares, a partir dos dados brutos e com rotina de limpeza própria, valida o tratamento aplicado.

O resultado de Cananéia merece destaque metodológico. Essa estação apresenta o **melhor** ajuste estatístico de toda a análise — R² de 0,734 contra 0,235 na Ilha Fiscal, intervalo estreito, nenhum sinal de problema nos diagnósticos de regressão — e, ainda assim, o teste de fechamento a rejeita: a tendência observada excede em 3,3 mm/ano tudo o que os processos físicos conhecidos explicam (z = +3,11). Cananéia situa-se em sistema estuarino-lagunar, onde sedimentação, descarga fluvial e movimentos locais do terreno distorcem o sinal oceânico. O ponto é que **nenhum diagnóstico de regressão detectaria isso**; apenas o confronto com a física detecta. Um ajuste excelente sobre dados fisicamente inconsistentes continua sendo um ajuste sobre dados inconsistentes.

Registre-se ainda que, na Ilha Fiscal, a correção de Newey-West infla o erro padrão da tendência em 1,68 vez, com autocorrelação de resíduos de 0,68: intervalos calculados sem essa correção são otimistas por um fator próximo de dois.

**[Figura 3 – Fechamento do orçamento do nível do mar: (a) escala global e de bacia; (b) estações brasileiras.]**
Fonte: Elaborado pelos autores (2026).

### 4.3 Por que não basta aplicar aprendizado de máquina à série local

Quinze algoritmos preditivos foram submetidos a validação cruzada de origem móvel, com horizontes de 1 a 20 anos, sobre as duas séries anuais brasileiras que satisfazem os critérios de qualidade (Tabela 2, Figura 4). O teste foi replicado nas duas estações justamente para distinguir o que é propriedade do problema do que é peculiaridade de um registro — e a replicação **não** confirmou o resultado da primeira estação, o que se revelou mais informativo do que a confirmação teria sido.

**Tabela 2 – Erro quadrático médio fora da amostra no horizonte de 20 anos (mm).** Dez dos quinze algoritmos testados; os quinze constam de `05_resultados/benchmark_algoritmos.json`.

| Algoritmo | Ilha Fiscal (RJ) | Cananéia (SP) |
|---|---|---|
| Theil-Sen | 147,8 | **39,6** |
| OLS linear | 116,7 | 46,5 |
| ARIMA(1,1,1) | 103,5 | 49,7 |
| Gradient boosting | 98,1 | 52,5 |
| Árvores extremas | 98,1 | 52,5 |
| Floresta aleatória | 94,9 | 52,7 |
| Processo gaussiano | **91,1** | 83,9 |
| k-vizinhos (k = 5) | 93,2 | 61,6 |
| **Média do treino (linha de base trivial)** | **93,8** | **113,8** |
| Rede neural (MLP) | 1.918,6 | 2.125,4 |
| *Algoritmos piores que a linha de base* | *12 de 15* | *2 de 15* |
| *Ganho do melhor sobre a linha de base* | *3%* | *65%* |

Fonte: Elaborado pelos autores (2026).

Na Ilha Fiscal, doze dos quinze algoritmos são **piores** que prever simplesmente a média histórica, e o melhor supera essa linha de base trivial em apenas 3%. Em Cananéia, apenas dois são piores e o melhor supera em 65%. A diferença não está no algoritmo, está na razão sinal-ruído de cada série: a Ilha Fiscal tem R² de 0,235 e desvio padrão dos resíduos de 71 mm, enquanto Cananéia tem R² de 0,734 e desvio de 35 mm. Onde a tendência é forte e limpa, qualquer estimador de tendência a aprende; onde está enterrada na variabilidade interanual — ventos, pressão atmosférica, El Niño —, nenhum aprende.

O ponto decisivo é qual das duas séries é fisicamente válida, e a resposta está na Tabela 1: o orçamento do nível do mar **fecha na Ilha Fiscal e é rejeitado em Cananéia**. A tendência forte e facilmente aprendível de Cananéia é exatamente aquela que a física rejeita, por conter 3,3 mm/ano que processo conhecido algum explica. Um procedimento de seleção guiado apenas por desempenho de validação cruzada preferiria Cananéia — maior R², menor erro fora da amostra, ganho expressivo sobre a linha de base — e produziria projeções confiantes, bem validadas e erradas. Desempenho de validação não é evidência de que se está aprendendo a coisa certa.

Observe-se ainda que, mesmo em Cananéia, os vencedores são os dois estimadores mais simples, Theil-Sen e mínimos quadrados; os modelos de aprendizado de máquina permanecem agrupados junto à persistência. O segundo teste, sobre a série global de contribuição das calotas, completa o quadro: ali os algoritmos superam amplamente a linha de base (3,6 mm contra 25,5 mm no horizonte de 20 anos). A previsibilidade reside no sinal global forçado, não no registro local.

O painel (b) da Figura 4 expõe o problema estrutural. Solicitada a contribuição das calotas em 2100, **seis dos quinze algoritmos respondem um valor constante**, idêntico em 2030, 2050 e 2100 — três deles exatamente o valor observado em 2018, e os outros três uma constante diferente dele. Modelos baseados em árvores de decisão e em vizinhança produzem previsões como médias de valores de treino e não podem gerar valor fora do intervalo observado; o núcleo de base radial decai para a média do treino longe dos dados; o modelo quadrático inverte-se; a regressão de suporte vetorial projeta queda do nível do mar. Como a projeção climática é, por definição, extrapolação para fora da faixa histórica, essa classe de algoritmos é inadequada à tarefa **independentemente** do desempenho em horizontes curtos. Esse é o conteúdo empírico da recomendação de Ayinde et al. (2024).

**[Figura 4 – Comparação de quinze algoritmos preditivos: (a) erro fora da amostra por horizonte; (b) comportamento na extrapolação ao ano 2100.]**
Fonte: Elaborado pelos autores (2026).

### 4.4 O emulador prevê a aceleração que nunca viu

A alternativa testada foi deslocar o objeto do aprendizado para a relação entre temperatura e resposta. Na validação V3, o emulador foi calibrado **somente** com 1900–1989, quando a perda de massa era pequena, e solicitado a prever 1990–2018, quando acelerou. Sem jamais ter visto o período de aceleração, reproduziu a taxa de perda da Groenlândia com erro de 5,0% e a taxa de expansão térmica com erro de 10,4%, superando neste último caso a melhor extrapolação polinomial por fator de dois. Subestimou a taxa antártica em 77,7%, o que é coerente com o entendimento de que a perda antártica recente é dominada por descarga dinâmica de gelo, processo praticamente ausente do registro do século XX.

A validação V4 é mais exigente, por usar conjunto inteiramente independente: o emulador, calibrado sobre a reconstrução de Frederikse et al. (2020), reproduz as taxas medidas por satélite pelo consórcio IMBIE — metodologia e equipe diferentes — com erro de +9,5% para a Groenlândia (0,513 contra 0,469 mm/ano) e −16,9% para a Antártica (0,199 contra 0,239 mm/ano).

A análise de estabilidade revelou que o coeficiente de sensibilidade da Groenlândia varia 72,9% conforme o ano de corte da calibração. Em vez de tratar a instabilidade como ruído, mediu-se a sensibilidade diretamente em épocas distintas. Entre 1992–1996 e 2016–2020, a taxa de perda da Groenlândia passou de 0,100 para 0,713 mm/ano, enquanto a temperatura global subiu de 0,59 para 1,23 K acima do nível pré-industrial: a sensibilidade implícita é de **0,965 ± 0,502 mm/ano por kelvin** (1σ), contra 0,132 mm/ano por kelvin no ajuste centenário — razão pontual de 7,3. Essa razão é, contudo, bem menos precisa do que o valor pontual sugere, por duas causas independentes. A incerteza do numerador é propagada das incertezas do IMBIE tratadas como integralmente correlacionadas dentro de cada época de cinco anos, critério conservador que deixa a própria sensibilidade de satélite a 1,92σ de zero. E o denominador não é constante: o bootstrap do ajuste centenário devolve intervalo de 95% de 0,123 a 0,431 mm/ano por kelvin para esse coeficiente, porque o parâmetro de limiar T₀ do ajuste da Groenlândia converge para o extremo do intervalo admitido (seção 4.8). Propagando as duas incertezas, a razão tem mediana de 5,0 e intervalo de 95% de 0 a 13,6, com probabilidade de 93% de exceder a unidade. O que os dados sustentam é, portanto, aumento provável de magnitude mal determinada, e não um fator preciso de 7,3. Para a Antártica, a incerteza (±0,659 sobre 0,198) impede detectar mudança significativa.

A mesma conta aplicada às projeções do IPCC AR6 no cenário SSP5-8.5 fornece sensibilidade implícita de 0,663 mm/ano por kelvin para a Groenlândia, abaixo do valor central observado no período de satélite. A diferença, de +0,302 mm/ano por kelvin, equivale a 0,60σ da incerteza do valor observado (p = 0,55): as duas estimativas são compatíveis, e o dado disponível **não** autoriza afirmar que as projeções oficiais subestimem a sensibilidade da Groenlândia. Autoriza o recíproco, que já é informativo: a sensibilidade medida por satélite não é menor que a embutida no AR6, de modo que a magnitude das projeções oficiais é compatível com a resposta observada.

O achado reposiciona as três vias de projeção. A via A, calibrada em 119 anos, dilui numa média centenária uma sensibilidade que demonstravelmente cresceu, e fornece um limite inferior. A via A′, que usa a sensibilidade medida no próprio período de satélite, produz 359, 460 e 635 mm em 2100 nos cenários SSP1-2.6, SSP2-4.5 e SSP5-8.5 — valores situados **dentro da faixa provável do IPCC AR6 nos cinco cenários**, sem recorrer a modelo processual algum. A magnitude das projeções processuais internacionais é, assim, sustentada de forma independente pela sensibilidade observada nas medições de satélite.

### 4.5 Projeções para o litoral brasileiro e subsidência medida

A Tabela 3 e a Figura 5 apresentam as projeções nos onze pontos analisados.

**Tabela 3 – Elevação projetada do nível relativo do mar e parcela das calotas (SSP2-4.5).**

| Estação | Lat. | 2050 (mm) | 2100 (mm) | Calotas 2100 (mm) | Parcela | VLM GNSS (mm/ano) |
|---|---|---|---|---|---|---|
| Santana (AP) | −0,1° | 165 | 536 | 193 | 36,1% | −0,22 |
| Belém (PA) | −1,4° | 202 | 640 | 194 | 30,3% | −0,98 |
| P. da Madeira (MA) | −2,6° | 175 | 564 | 196 | 34,8% | −0,55 |
| Fortaleza (CE) | −3,7° | 171 | 554 | 202 | 36,5% | −0,30 |
| Recife (PE) | −8,1° | 260 | 794 | 206 | 25,9% | −3,05 |
| Salvador (BA) | −13,0° | 156 | 509 | 201 | 39,5% | +0,09 |
| Ilha Fiscal (RJ) | −22,9° | 156 | 505 | 197 | 39,0% | −0,12 |
| Santos (SP) | −24,0° | 138 | 458 | 192 | 42,0% | +0,69 |
| Cananéia (SP) | −25,0° | 154 | 500 | 190 | 38,0% | −0,04 |
| Imbituba (SC) | −28,2° | 165 | 529 | 189 | 35,7% | −0,41 |
| Rio Grande (RS) | −32,1° | 119 | 404 | 179 | 44,4% | +1,22 |

Fonte: Elaborado pelos autores (2026).

A contribuição absoluta das calotas é notavelmente uniforme — de 179 a 206 mm em 2100 no cenário intermediário —, consequência direta da uniformidade do fator de impressão digital. A variação da elevação total entre estações, de 404 a 794 mm, é portanto produzida quase inteiramente pelo movimento vertical do terreno, e não por diferenças na resposta oceânica. Considerando os cinco cenários e os onze pontos, a parcela das calotas é de 30,5% em média em 2050 (18,7% a 47,9%) e de 37,2% em 2100 (25,6% a 55,6%).

A validação V5 confronta a cadeia com as projeções oficiais. Em Ilha Fiscal, Salvador e Imbituba — estações nas quais a estimativa GNSS concorda com a taxa de fundo adotada pelo AR6 — a cadeia reproduz as projeções oficiais com diferença de **1,0% a 3,6%** em 2100 no cenário intermediário, e de 0,7% a 4,4% considerando os três cenários testados. Como a cadeia foi montada de forma independente, a partir de campos de impressão digital, de componentes globais de emulador próprio e de velocidades GNSS, a concordância valida o conjunto, e não apenas uma de suas peças.

Nas três estações restantes a cadeia diverge, e a origem é identificável: a diferença entre a velocidade vertical medida por GNSS e a taxa de fundo do AR6, multiplicada pelos 80 anos de projeção, explica de 85% a 103% da divergência. O caso mais relevante é Recife, onde duas estações GNSS com séries efetivas de 17 anos indicam subsidência de 3,05 ± 0,87 mm/ano, enquanto a taxa de fundo do AR6 indica leve soerguimento (+0,49 mm/ano). A diferença implica que a projeção oficial **subestima** a elevação do nível relativo em Recife em aproximadamente 28 cm até 2100 — mais da metade do próprio valor projetado. Subsidência dessa magnitude em região metropolitana costeira é compatível com extração de água subterrânea e compactação de sedimentos, e a consequência para o planejamento é direta: as estimativas oficiais disponíveis para a quarta maior região metropolitana do país descrevem o oceano corretamente e o terreno não.

**[Figura 5 – (a) Decomposição da elevação projetada por estação; (b) parcela das calotas polares por cenário.]**
Fonte: Elaborado pelos autores (2026).

### 4.6 Impactos sobre a dinâmica costeira

A Figura 6 traduz a elevação projetada em dinâmica costeira. Na Ilha Fiscal, com 51 anos de dados horários, o nível que hoje tem período de retorno de 100 anos — 1.456 mm acima do nível médio atual — passaria a ter período de retorno de 10,4 anos já em 2050 no cenário intermediário, e de 0,12 ano em 2100. O fator de multiplicação da frequência de excedência é de 806 no cenário SSP2-4.5 e de 8.665 no SSP5-8.5; em Cananéia, 184 e 1.381.

Esses fatores são corretos, mas pouco tangíveis, e exigem atenção à unidade: a taxa é definida sobre valores horários, de modo que um período de retorno de 0,12 ano corresponde a cerca de oito **horas** de excedência por ano, e não a oito eventos independentes. Convertida para a métrica operacional de dias de alagamento, contada hora a hora no próprio registro histórico deslocado pela elevação projetada, a Tabela 4 apresenta o resultado em grandeza diretamente verificável.

**Tabela 4 – Métricas operacionais de alagamento costeiro (cenário SSP2-4.5).**

| Estação | Nível de 100 anos hoje | Dias/ano acima do nível anual em 2100 | Dias/ano acima do nível centenário em 2100 | Ano em que o nível centenário passa a ocorrer anualmente |
|---|---|---|---|---|
| Ilha Fiscal (RJ) | 1.456 mm | 11,3 | 0,3 | 2110 |
| Cananéia (SP) | 1.775 mm | 4,9 | 0,1 | 2116 |

Fonte: Elaborado pelos autores (2026).

O mecanismo é geométrico e não requer hipótese alguma sobre mudança no regime de ondas ou de tempestades: basta deslocar a distribuição observada pelo valor da elevação projetada.

A magnitude da amplificação depende de uma propriedade local pouco discutida: a **largura da distribuição de níveis extremos**. Onde a maré astronômica domina e a variabilidade de ressaca é pequena, a distância entre o nível anual e o centenário é curta, e uma elevação modesta do nível médio desloca a distribuição por inteiro. Entre as seis estações analisadas, essa largura varia de 78 mm em Recife a 929 mm em Imbituba, e o fator de amplificação em 2100 varia de 10 a mais de 10⁵ na razão inversa: a correlação entre o logaritmo da largura e o logaritmo do fator é de **r = −0,986**. Em termos práticos, as cidades do Nordeste, de regime de extremos estreito e dominado pela maré, são as mais sensíveis à mesma elevação média — resultado que, apoiado em registros horários de 10 a 14 anos, deve ser lido como indicativo e merece investigação dedicada com séries mais longas.

Pela regra de Bruun, a elevação projetada no cenário intermediário corresponde a recuo potencial de 20 a 79 m em praias arenosas de declividade 1:50 a 1:100, dos quais 9 a 21 m atribuíveis especificamente ao degelo das calotas. A amplificação geométrica — um metro de elevação convertendo-se em dezenas de metros de praia — é o que transforma a elevação do nível do mar de um problema de nível em um problema de dinâmica costeira. Considerando que cerca de 60% do litoral brasileiro — 4.500 de 7.500 km — já apresenta processos erosivos (MUEHE, 2018), o efeito incide sobre um sistema já em desequilíbrio.

### 4.7 Outros processos afetados, em caráter de discussão

As duas subseções anteriores quantificam dois impactos. Outros processos costeiros respondem à mesma elevação sem que o presente trabalho os tenha modelado, e são registrados aqui como discussão, não como resultado, para que a distinção fique explícita.

A **intrusão salina** em estuários e aquíferos costeiros responde à elevação do nível de base: a cunha salina avança rio acima e a interface água doce-água salgada se desloca em direção ao continente. O efeito interage com a captação de água subterrânea, o que é particularmente relevante em Recife, onde a mesma extração que provavelmente explica a subsidência medida na seção 4.5 também rebaixa o nível freático. Os dois processos se reforçam.

Os **manguezais** ocupam posição intermediária entre a terra e o mar e acompanham a elevação enquanto a acreção de sedimento for suficiente; quando a taxa de elevação supera a de acreção, ou quando a migração para o interior é barrada por ocupação urbana, o sistema se afoga. A Baía de Guanabara, onde se situa a Ilha Fiscal, reúne as duas condições desfavoráveis.

A **infraestrutura exposta** inclui o porto de Santos, o maior da América Latina, que está entre os onze pontos analisados e para o qual se projeta elevação de 0,46 m até 2100 no cenário intermediário. Elevação dessa ordem não inviabiliza a operação portuária, mas altera cotas de projeto de cais, sistemas de drenagem e acessos, cujo dimensionamento foi feito para um regime de extremos que a seção 4.6 mostra estar em mudança.

Quantificar esses três processos exigiria, respectivamente, modelagem hidrogeológica, levantamento de taxas de acreção sedimentar e cadastro de cotas de infraestrutura — dados que não foram reunidos aqui. A menção serve para situar o alcance do que foi medido, e não para sugerir que foi medido mais do que de fato o foi.

**[Figura 6 – (a) Curvas de período de retorno deslocadas pela elevação projetada; (b) recuo potencial da linha de costa.]**
Fonte: Elaborado pelos autores (2026).

### 4.8 Limitações

A regra de Bruun é um modelo de equilíbrio bidimensional, criticado por supor perfil de equilíbrio atingido e ausência de aporte sedimentar (COOPER; PILKEY, 2004); os valores de recuo são ordens de grandeza para praias arenosas expostas, não previsões locais, e não se aplicam a costas de falésia, manguezais ou trechos confinados por obras. A análise de extremos não incorpora mudanças futuras no regime de ondas e ventos, que exigiriam modelagem atmosférica, nem aplica declusterização, de modo que as taxas não devem ser lidas como número de tempestades independentes. As velocidades GNSS cobrem de 8 a 21 anos e são extrapoladas como constantes até 2100, hipótese razoável para processos geológicos mas questionável onde a subsidência decorre de extração de água subterrânea. O emulador reproduz mal a resposta antártica, pelo motivo discutido na seção 4.4, e por isso a via B é mantida como projeção de referência. Três parâmetros do emulador não são identificados pelos dados: o limiar T₀ converge para o extremo inferior do intervalo admitido nos ajustes da Groenlândia e das geleiras (−3,0 K), e o expoente q do termo estérico converge para o extremo inferior (q = 1), com intervalo de bootstrap cobrindo todo o intervalo permitido. Nesses três casos é a restrição imposta, e não a observação, que fixa o valor; a consequência é que o coeficiente de sensibilidade centenário tem incerteza larga (seção 4.4) e que a via A amortece a aceleração projetada, o que reforça sua leitura como limite inferior. O forçante é suavizado por média móvel centrada, escolha que mantém o alinhamento temporal entre forçante e resposta mas faz o valor suavizado de um ano depender de anos posteriores. Para os três componentes de massa a janela selecionada é de um ano, de modo que nenhuma suavização é aplicada e a calibração cega da validação V3 é estritamente cega; para o termo estérico, de janela cinco, a janela de calibração incorpora dois anos além do corte de 1989. Substituída a média centrada por média retroativa, a validação aninhada passa a selecionar para a Groenlândia a forma com termo de taxa e janela de vinte e um anos, e o erro de V3 nesse componente sobe de 5,0% para 64,7% — o resultado de V3 é, portanto, condicionado à convenção de suavização, e não deve ser lido como propriedade invariante do emulador. Por fim, apenas duas estações brasileiras possuem registro longo o bastante para o teste de fechamento local — limitação que é ela própria um dos resultados deste trabalho.

## 5 CONCLUSÃO

O objetivo era construir e validar uma cadeia preditiva capaz de atribuir, em cada ponto do litoral brasileiro, a parcela da elevação do nível do mar imputável ao derretimento das calotas polares, e traduzir essa elevação em dinâmica costeira. O objetivo foi alcançado, e cada elo da cadeia foi submetido a teste independente.

Os resultados principais são quatro. Primeiro, a costa brasileira recebe 1,12 vez a elevação média global causada pelo degelo polar, com variação de apenas 12,8% ao longo de 4.000 km, porque os gradientes opostos da Groenlândia e da Antártica se compensam — fator de amplificação uniforme que as projeções baseadas na média global não contabilizam. Segundo, os mantos de gelo respondem por 20,5% da elevação observada na Ilha Fiscal entre 1963 e 2018, por 37,5% entre 1993 e 2018, e deverão responder por 26% a 44% da elevação projetada até 2100. Terceiro, a sensibilidade da Groenlândia ao aquecimento medida no período de satélite excede provavelmente a média do século XX — razão com mediana de 5,0, intervalo de 95% de 0 a 13,6 e probabilidade de 93% de exceder a unidade — e é compatível com a sensibilidade implícita nas projeções do IPCC AR6, o que sustenta de forma independente a magnitude dessas projeções sem autorizar a conclusão de que sejam conservadoras. Quarto, medições GNSS indicam subsidência de 3,05 ± 0,87 mm/ano em Recife, não incorporada às projeções oficiais, com implicação de subestimação de cerca de 28 cm na elevação relativa projetada para 2100.

A contribuição metodológica é de natureza distinta e igualmente deliberada, e o resultado mais útil veio de uma replicação que falhou. Submetidos a validação cruzada de origem móvel, quinze algoritmos comportam-se de modo oposto nas duas estações brasileiras de registro longo: na Ilha Fiscal, doze são piores que prever a média histórica e o melhor ganha 3%; em Cananéia, apenas dois são piores e o melhor ganha 65%. A diferença decorre da razão sinal-ruído de cada série, não do algoritmo. E a série em que os algoritmos têm bom desempenho é precisamente aquela que o teste de fechamento rejeita. Uma seleção guiada apenas por desempenho de validação escolheria a estação fisicamente inconsistente e produziria projeções bem validadas e erradas: desempenho de validação não é evidência de que se está aprendendo a grandeza certa. Independentemente da estação, porém, seis dos quinze algoritmos são estruturalmente incapazes de gerar valor fora da faixa de treino, o que os exclui de qualquer tarefa de projeção. A previsibilidade reside no sinal global forçado, acessível por meio da relação física entre forçante e resposta. Demonstrou-se igualmente que restrições de monotonicidade e regras de parcimônia na seleção de modelo não são refinamentos opcionais: sem elas, a seleção por melhor ajuste escolhe formas funcionais que reproduzem o passado e se invertem ou explodem na extrapolação. E demonstrou-se, no caso de Cananéia, que o diagnóstico estatístico de uma regressão — ainda que excelente — não substitui o teste de consistência física dos dados sobre os quais ela foi ajustada.

Como trabalhos futuros, recomenda-se estender a análise de extremos com séries horárias mais longas nas estações do Nordeste, onde a distribuição estreita de níveis extremos produz os maiores fatores de amplificação; instalar e manter estações GNSS colocalizadas com os marégrafos brasileiros, requisito para qualquer atribuição confiável; e incorporar modelos morfodinâmicos que superem as limitações da regra de Bruun. Recomenda-se, por fim, que séries maregráficas brasileiras sejam submetidas às reconstruções globais do orçamento do nível do mar, das quais hoje estão inteiramente ausentes.

## AGRADECIMENTOS

Os autores agradecem às instituições que mantêm e disponibilizam publicamente os conjuntos de dados utilizados: Permanent Service for Mean Sea Level, University of Hawaii Sea Level Center, Nevada Geodetic Laboratory, Met Office Hadley Centre, NASA/JPL e os consórcios IMBIE e IPCC. Conforme a política de uso da fonte, registra-se que os dados de altimetria são fornecidos pelo NOAA Laboratory for Satellite Altimetry (*Altimetry data are provided by NOAA Laboratory for Satellite Altimetry*). Agradecem igualmente ao Prof. Dr. Renato Gonçalves Rocha pela orientação.

## REFERÊNCIAS

AYINDE, A. S. et al. Review of machine learning methods for sea level change modeling and prediction. **Science of the Total Environment**, v. 954, art. 176410, 2024. DOI: https://doi.org/10.1016/j.scitotenv.2024.176410.

BLEWITT, G. et al. MIDAS robust trend estimator for accurate GPS station velocities without step detection. **Journal of Geophysical Research: Solid Earth**, v. 121, n. 3, p. 2054-2068, 2016. DOI: https://doi.org/10.1002/2015JB012552.

BRUUN, P. Sea-level rise as a cause of shore erosion. **Journal of the Waterways and Harbors Division**, v. 88, n. 1, p. 117-130, 1962.

CALDWELL, P. C.; MERRIFIELD, M. A.; THOMPSON, P. R. **Sea level measured by tide gauges from global oceans**: the Joint Archive for Sea Level holdings (NCEI Accession 0019568), Version 5.5. NOAA National Centers for Environmental Information, 2015. DOI: https://doi.org/10.7289/V5V40S7W.

CARVALHO, B. C.; ARAUJO, T. A. A.; GUERRA, J. V.; REIS, A. T. dos. Mean sea level trends based on tide gauge records and their possible morphological effects on the coastline of southern Rio de Janeiro (SE Brazil). **Thalassas**, v. 40, p. 261-272, 2024. DOI: https://doi.org/10.1007/s41208-023-00618-6.

COOPER, J. A. G.; PILKEY, O. H. Sea-level rise and shoreline retreat: time to abandon the Bruun Rule. **Global and Planetary Change**, v. 43, n. 3-4, p. 157-171, 2004. DOI: https://doi.org/10.1016/j.gloplacha.2004.07.001.

EDWARDS, T. L. et al. Projected land ice contributions to twenty-first-century sea level rise. **Nature**, v. 593, p. 74-82, 2021. DOI: https://doi.org/10.1038/s41586-021-03302-y.

FREDERIKSE, T. et al. The causes of sea-level rise since 1900. **Nature**, v. 584, p. 393-397, 2020. DOI: https://doi.org/10.1038/s41586-020-2591-3.

GARNER, G. G. et al. **IPCC AR6 Sea Level Projections**. Zenodo, 2021. DOI: https://doi.org/10.5281/zenodo.6382554.

GREGORY, J. M. et al. Concepts and terminology for sea level: mean, variability and change, both local and global. **Surveys in Geophysics**, v. 40, p. 1251-1289, 2019. DOI: https://doi.org/10.1007/s10712-019-09525-z.

HOLGATE, S. J. et al. New data systems and products at the Permanent Service for Mean Sea Level. **Journal of Coastal Research**, v. 29, n. 3, p. 493-504, 2013. DOI: https://doi.org/10.2112/JCOASTRES-D-12-00175.1.

IPCC. Summary for Policymakers. In: **Climate Change 2021**: The Physical Science Basis. Cambridge: Cambridge University Press, 2021. p. 3-32.

MITROVICA, J. X.; TAMISIEA, M. E.; DAVIS, J. L.; MILNE, G. A. Recent mass balance of polar ice sheets inferred from patterns of global sea-level change. **Nature**, v. 409, p. 1026-1029, 2001. DOI: https://doi.org/10.1038/35059054.

MORICE, C. P. et al. An updated assessment of near-surface temperature change from 1850: the HadCRUT5 data set. **Journal of Geophysical Research: Atmospheres**, v. 126, e2019JD032361, 2021. DOI: https://doi.org/10.1029/2019JD032361.

MUEHE, D. (org.). **Panorama da erosão costeira no Brasil**. Brasília: Ministério do Meio Ambiente, 2018.

NEWEY, W. K.; WEST, K. D. A simple, positive semi-definite, heteroskedasticity and autocorrelation consistent covariance matrix. **Econometrica**, v. 55, n. 3, p. 703-708, 1987. DOI: https://doi.org/10.2307/1913610.

NOAA. **Laboratory for Satellite Altimetry: global mean sea level time series**. Disponível em: https://www.star.nesdis.noaa.gov/socd/lsa/SeaLevelRise/. Acesso em: 29 out. 2026.

OTOSAKA, I. N. et al. Mass balance of the Greenland and Antarctic ice sheets from 1992 to 2020. **Earth System Science Data**, v. 15, p. 1597-1616, 2023. DOI: https://doi.org/10.5194/essd-15-1597-2023.

PBMC. **Impacto, vulnerabilidade e adaptação das cidades costeiras brasileiras às mudanças climáticas**: Relatório Especial do Painel Brasileiro de Mudanças Climáticas. Rio de Janeiro: PBMC/COPPE-UFRJ, 2016.

RAHMSTORF, S. A semi-empirical approach to projecting future sea-level rise. **Science**, v. 315, n. 5810, p. 368-370, 2007. DOI: https://doi.org/10.1126/science.1135456.

ROFFMAN, J.; GOMEZ, N.; YOUSEFI, M.; HAN, H. K.; NOWICKI, S. Spatial and temporal variability of 21st century sea level changes. **Geophysical Journal International**, v. 235, n. 1, p. 342-352, 2023. DOI: https://doi.org/10.1093/gji/ggad170.

SLANGEN, A. B. A. et al. Projecting twenty-first century regional sea-level changes. **Climatic Change**, v. 124, p. 317-332, 2014. DOI: https://doi.org/10.1007/s10584-014-1080-9.

TAHERKHANI, M. et al. Sea-level rise exponentially increases coastal flood frequency. **Scientific Reports**, v. 10, art. 6466, 2020. DOI: https://doi.org/10.1038/s41598-020-62188-4.

TAMISIEA, M. E.; MITROVICA, J. X. The moving boundaries of sea level change: understanding the origins of geographic variability. **Oceanography**, v. 24, n. 2, p. 24-39, 2011. DOI: https://doi.org/10.5670/oceanog.2011.25.

VITOUSEK, S. et al. Doubling of coastal flooding frequency within decades due to sea-level rise. **Scientific Reports**, v. 7, art. 1399, 2017. DOI: https://doi.org/10.1038/s41598-017-01362-7.

WCRP GLOBAL SEA LEVEL BUDGET GROUP. Global sea-level budget 1993-present. **Earth System Science Data**, v. 10, p. 1551-1590, 2018. DOI: https://doi.org/10.5194/essd-10-1551-2018.

---

## APÊNDICE A – DIVISÃO DE RESPONSABILIDADES

| Atividade | Responsável(is) | Contribuição realizada |
|---|---|---|
| Planejamento da pesquisa | ________________ | ________________ |
| Revisão da literatura | ________________ | ________________ |
| Coleta e organização dos dados | ________________ | ________________ |
| Desenvolvimento e implementação | ________________ | ________________ |
| Análise dos resultados | ________________ | ________________ |
| Redação inicial | ________________ | ________________ |
| Revisão final do manuscrito | Todos os autores | ________________ |

Fonte: Elaborado pelos autores (2026).
