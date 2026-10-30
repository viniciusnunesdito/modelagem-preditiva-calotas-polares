# MODELAGEM PREDITIVA DOS IMPACTOS DO DERRETIMENTO DAS CALOTAS POLARES SOBRE A DINÂMICA COSTEIRA BRASILEIRA: ATRIBUIÇÃO POR IMPRESSÃO DIGITAL DO NÍVEL DO MAR E VALIDAÇÃO EM CINCO ETAPAS

João Pedro Fernandes¹; Kauan Henrique Teixeira¹; Luiz Tonny Moura Santos¹;
Mateus da Silva Vieira¹; Miguel Otávio Ferreira Martins¹; Pedro Henrique Pereira Boldrin¹;
Vinícius Nunes Benedito¹; Prof. Dr. Renato Gonçalves Rocha²

¹ Curso de Ciência da Computação, Universidade de Franca (UNIFRAN), Franca, São Paulo, Brasil.
² Professor Orientador, Universidade de Franca (UNIFRAN), Franca, São Paulo, Brasil.

Autor correspondente: Miguel Otávio Ferreira Martins – e-mail: miguelotavio018@gmail.com

---

## RESUMO

O derretimento dos mantos de gelo da Groenlândia e da Antártica é frequentemente associado à elevação do nível do mar no litoral brasileiro, mas essa associação raramente é quantificada: o que se projeta localmente costuma ser a média global aplicada sem correção, e o que se mede nos marégrafos mistura o sinal oceânico com o movimento do terreno. Este trabalho construiu e validou uma cadeia preditiva que separa essas contribuições. A perda de massa polar foi convertida em elevação local por meio das impressões digitais do nível do mar, que descrevem a resposta gravitacional, rotacional e elástica da Terra sólida à redistribuição de massa, calculadas a partir de campos espaciais publicados em grade de 0,5°. O movimento vertical do terreno foi medido de forma independente por 27 estações GNSS próximas a onze pontos do litoral. Um emulador semi-empírico, que aprende a relação entre temperatura média global e taxa de perda de massa em vez da forma da curva no tempo, foi calibrado com 119 anos de observação e acionado pelas trajetórias de temperatura do IPCC AR6. A cadeia foi submetida a cinco testes independentes de validação. Os resultados mostram que a costa brasileira recebe, em média, 1,12 vez a elevação média global causada pelo degelo polar, com variação de apenas 12,8% ao longo de 4.000 km porque os gradientes opostos da Groenlândia e da Antártica se compensam; que o orçamento do nível do mar fecha na Ilha Fiscal mas é rejeitado em Cananéia, estação cuja regressão apresentava o melhor ajuste estatístico; que o desempenho dos quinze algoritmos preditivos testados varia em sentido oposto nas duas séries maregráficas longas do país, conforme a razão sinal-ruído de cada uma e não conforme o algoritmo, e que a estação em que eles têm bom desempenho é justamente a que o teste físico rejeita, sendo seis deles estruturalmente incapazes de extrapolar; e que a sensibilidade da Groenlândia ao aquecimento no período de satélite excede provavelmente a média do século XX, com 93% de probabilidade e magnitude mal determinada (razão com mediana de 5,0 e intervalo de 95% de 0 a 13,6), sendo compatível com a implícita nas projeções processuais, cuja magnitude fica assim sustentada de forma independente. Projeta-se, no cenário intermediário, elevação de 0,40 a 0,79 m até 2100 nos onze pontos analisados, dos quais 26% a 44% atribuíveis às calotas polares, recuo potencial de linha de costa de 20 a 79 m em praias arenosas e multiplicação por 184 a 806 da frequência do nível extremo hoje centenário no Rio de Janeiro. Mediu-se ainda subsidência de 3,05 ± 0,87 mm/ano em Recife, valor que as projeções oficiais não incorporam e que implica subestimação de aproximadamente 28 cm na elevação relativa projetada para aquela cidade até 2100.

**Palavras-chave:** elevação do nível do mar; impressão digital do nível do mar; modelagem preditiva; erosão costeira; validação de modelos.

## ABSTRACT

The melting of the Greenland and Antarctic ice sheets is often linked to sea-level rise along the Brazilian coast, yet this link is rarely quantified: local projections typically apply the global mean without correction, and tide-gauge measurements conflate the oceanic signal with vertical land motion. This study built and validated a predictive chain that separates these contributions. Polar mass loss was converted into local rise using sea-level fingerprints, which describe the gravitational, rotational and elastic response of the solid Earth to mass redistribution, computed from published spatial fields on a 0.5° grid. Vertical land motion was independently measured from 27 GNSS stations near eleven coastal sites. A semi-empirical emulator, which learns the relationship between global mean temperature and mass-loss rate rather than the shape of the curve in time, was calibrated on 119 years of observations and driven by IPCC AR6 temperature pathways. The chain underwent five independent validation tests. Results show that the Brazilian coast receives on average 1.12 times the global mean rise caused by polar melt, varying by only 12.8% over 4,000 km because the opposing Greenland and Antarctic gradients cancel; that the sea-level budget closes at Ilha Fiscal but is rejected at Cananéia, the station whose regression showed the best statistical fit; that the performance of fifteen predictive algorithms diverges in opposite directions between the country's two long tide-gauge series, driven by each record's signal-to-noise ratio rather than by the algorithm, with the station where they perform well being precisely the one the physical test rejects, and six being structurally unable to extrapolate; and that Greenland's sensitivity to warming during the satellite era most likely exceeds the twentieth-century average, with 93% probability but poorly determined magnitude (ratio median 5.0, 95% interval 0 to 13.6), being consistent with the sensitivity implicit in process-based projections, whose magnitude is thereby independently supported. Under the intermediate scenario, projected rise by 2100 at the eleven sites ranges from 0.40 to 0.79 m, of which 26% to 44% is attributable to polar ice sheets, implying potential shoreline retreat of 20 to 79 m on sandy beaches and a 184- to 806-fold increase in the frequency of the present-day one-in-a-century extreme level in Rio de Janeiro. Subsidence of 3.05 ± 0.87 mm/yr was measured at Recife, a value not incorporated in official projections, implying an underestimation of about 28 cm in projected relative sea-level rise for that city by 2100.

**Keywords:** sea-level rise; sea-level fingerprint; predictive modelling; coastal erosion; model validation.

---

## 1 INTRODUÇÃO

A associação entre o derretimento das calotas polares e a elevação do nível do mar no litoral brasileiro é um lugar-comum do debate climático, mas raramente é tratada como uma questão quantitativa. Afirmar que o degelo da Groenlândia ameaça as cidades costeiras do Brasil exige responder a três perguntas distintas: quanta água o degelo efetivamente acrescenta ao oceano, quanto dessa água chega à costa brasileira, e quanto da elevação medida pelos marégrafos brasileiros se deve a esse processo e não a outros. As três perguntas têm respostas diferentes, e nenhuma delas é a média global.

A primeira pergunta tem resposta observacional consolidada. Entre 1992 e 2020, os mantos de gelo da Groenlândia e da Antártica perderam cerca de 7.560 bilhões de toneladas de gelo, elevando o nível médio global do mar em aproximadamente 21 mm, com a taxa de perda mais que triplicando ao longo do período (OTOSAKA et al., 2023).

A segunda pergunta é menos conhecida e é onde reside a maior parte do mal-entendido. A água liberada por um manto de gelo não se distribui uniformemente pelos oceanos. A perda de massa reduz a atração gravitacional que o gelo exercia sobre a água vizinha, alivia o peso sobre a crosta, que sobe elasticamente, e desloca ligeiramente o eixo de rotação do planeta. O resultado conjunto é que, nas águas próximas à fonte de degelo, o nível relativo do mar **cai**, enquanto no campo distante ele sobe **mais** que a média global (MITROVICA et al., 2001). Essa assinatura espacial é chamada de impressão digital do nível do mar. O Brasil está no campo distante tanto da Groenlândia quanto da Antártica, o que significa que recebe mais do que a média global — mas quanto mais, e se esse fator varia ao longo dos mais de 7.000 km de litoral, são questões que a literatura brasileira sobre impactos costeiros menciona qualitativamente (ROFFMAN; GOMEZ; YOUSEFI, 2023) sem quantificar.

A terceira pergunta esbarra na natureza do instrumento. Um marégrafo mede o nível **relativo** do mar: a altura da água em relação a um marco fixado em terra. Se o terreno afunda, o aparelho registra elevação mesmo que o volume do oceano não mude. Sem uma medida independente do movimento vertical do terreno, a tendência observada não pode ser atribuída a causa alguma. O Painel Brasileiro de Mudanças Climáticas já apontava essa limitação, somada à escassez de séries históricas contínuas no país (PBMC, 2016).

A essas três lacunas soma-se uma quarta, de natureza metodológica e diretamente ligada ao escopo deste trabalho. A expectativa corrente é que técnicas de aprendizado de máquina, aplicadas a séries históricas, produzam projeções climáticas confiáveis. Revisões recentes da aplicação dessas técnicas ao nível do mar recomendam, ao contrário, abordagens híbridas que combinem física e aprendizado para previsões regionais de longo prazo (AYINDE et al., 2024). Essa recomendação, porém, é habitualmente aceita por autoridade, sem que se demonstre com números por que a abordagem puramente estatística falha.

O presente trabalho tem por objetivo construir, validar e aplicar uma cadeia preditiva que responda às três primeiras perguntas de forma quantitativa para a costa brasileira, e que, ao fazê-lo, submeta a quarta a teste experimental explícito. A contribuição pretendida não é apresentar mais uma projeção de elevação do mar — projeções oficiais já existem —, e sim decompor essa elevação, atribuindo a cada processo físico a parcela que lhe cabe em cada ponto do litoral, e demonstrar, etapa por etapa, que cada elo da cadeia reproduz observações independentes.

## 2 FUNDAMENTAÇÃO TEÓRICA E TRABALHOS RELACIONADOS

### 2.1 Orçamento do nível do mar

O nível médio global do mar varia por dois mecanismos independentes: a adição de massa de água ao oceano, chamada contribuição baristática, proveniente de mantos de gelo, geleiras de montanha e armazenamento de água continental; e a variação do volume ocupado por essa massa, chamada contribuição estérica, decorrente da expansão térmica e de mudanças de salinidade (GREGORY et al., 2019). A soma dessas contribuições deve igualar a elevação observada; verificar essa igualdade é o que se chama fechamento do orçamento do nível do mar, e constitui o teste padrão de consistência física do conjunto de observações (WCRP GLOBAL SEA LEVEL BUDGET GROUP, 2018). Frederikse et al. (2020) reconstruíram esse orçamento desde 1900, disponibilizando tanto as séries globais e por bacia oceânica quanto os campos espaciais de cada processo.

### 2.2 Impressões digitais do nível do mar

A equação do nível do mar descreve a resposta elástica e gravitacional da Terra à redistribuição de massa superficial. Resolvida para a perda de massa de um manto de gelo, produz um campo espacial característico: queda do nível relativo nas proximidades da fonte, que pode superar em muitas vezes a média global em magnitude e ter sinal oposto, e elevação superior à média no campo distante (MITROVICA et al., 2001; TAMISIEA; MITROVICA, 2011). Define-se o fator de impressão digital de um processo *p* em um ponto *x* como a razão adimensional entre a tendência local do nível relativo e a tendência da média global devidas àquele processo. Esse fator é a ponte quantitativa entre a perda de massa polar e o nível do mar em um ponto específico da costa, e é peça obrigatória de qualquer projeção regional (SLANGEN et al., 2014).

### 2.3 Nível relativo e movimento vertical do terreno

A tendência de nível relativo registrada por um marégrafo relaciona-se à tendência geocêntrica do nível do mar pela subtração da velocidade vertical do terreno. Essa velocidade pode ser medida diretamente por posicionamento por satélite. O conjunto de velocidades MIDAS do Nevada Geodetic Laboratory fornece estimativas robustas a degraus instrumentais para a totalidade da rede GNSS global no referencial IGS14 (BLEWITT et al., 2016), e constitui a fonte independente necessária para separar oceano e terreno.

### 2.4 Modelagem preditiva e o limite da extrapolação

Modelos semi-empíricos projetam o nível do mar a partir de uma relação ajustada entre temperatura global e taxa de elevação, na forma dS/dt = a(T − T₀) (RAHMSTORF, 2007). A lógica é deslocar o objeto do aprendizado: em vez de aprender a forma da curva no tempo, aprende-se a relação entre forçante e resposta, de modo que projetar passe a ser avaliar essa relação em valores de temperatura fornecidos por cenários. A mesma lógica sustenta a emulação estatística usada para substituir modelos de manto de gelo computacionalmente caros (EDWARDS et al., 2021), que é a conexão direta entre este tema e as técnicas de inteligência artificial aplicadas ao clima.

### 2.5 Dinâmica costeira

A elevação média do nível do mar atua sobre a costa por dois caminhos. O primeiro é morfológico: segundo a regra de Bruun (1962), o perfil de equilíbrio de uma praia arenosa reajusta-se a uma elevação *S* recuando uma distância R = S/tanβ, em que tanβ é a declividade do perfil ativo; como esse inverso é tipicamente de 20 a 200, o recuo é uma a duas ordens de grandeza maior que a elevação. O modelo é objeto de crítica consolidada (COOPER; PILKEY, 2004) e deve ser lido como ordem de grandeza, não como previsão local. O segundo caminho é probabilístico: como a cauda da distribuição dos níveis extremos decai de forma aproximadamente exponencial, um deslocamento modesto do nível médio multiplica de forma exponencial a frequência de excedência de um limiar fixo (VITOUSEK et al., 2017; TAHERKHANI et al., 2020). É por esse segundo caminho que decímetros de elevação se convertem em mudanças de regime de inundação.

### 2.6 A lacuna

Um levantamento das 472 séries maregráficas utilizadas por Frederikse et al. (2020) para reconstruir as causas da elevação do nível do mar desde 1900 revelou que **nenhuma delas é brasileira**. Na bacia do Atlântico Sul, o conjunto apoia-se exclusivamente em estações da Argentina, do Uruguai, da África do Sul e da Namíbia. O país com o maior litoral atlântico do Hemisfério Sul não participa da base observacional que sustenta a reconstrução de referência. É a essa lacuna que o presente trabalho se dirige.

## 3 METODOLOGIA

A Figura 1 resume a cadeia de cálculo e os pontos de validação. Todo o processamento foi implementado em Python; os dados brutos, os scripts e os resultados intermediários estão organizados em repositório com registro de proveniência (URL, data de acesso e soma de verificação criptográfica) para cada arquivo baixado.

**[Figura 1 – Estrutura metodológica da pesquisa e seus cinco pontos de validação.]**
Fonte: Elaborado pelos autores (2026).

### 3.1 Dados

A Tabela 1 relaciona as fontes utilizadas. Todas são públicas, revisadas por pares ou institucionais, e foram obtidas diretamente dos respectivos repositórios.

**Tabela 1 – Conjuntos de dados obtidos.** A última coluna distingue os conjuntos que alimentam resultados numéricos dos que foram obtidos e mantidos no repositório por rastreabilidade, sem entrar na cadeia de cálculo.

| Conjunto | Conteúdo | Período | Fonte | Entra na cadeia quantitativa |
|---|---|---|---|---|
| PSMSL (RLR mensal e anual) | 12 estações maregráficas brasileiras | 1949–2022 | Holgate et al. (2013) | sim |
| UHSLC (qualidade de pesquisa) | níveis horários, 23 estações | 1954–2018 | Caldwell, Merrifield e Thompson (2015) | sim |
| IMBIE 2021 | balanço de massa dos dois mantos | 1992–2020 | Otosaka et al. (2023) | sim |
| GRACE/GRACE-FO | massa da Antártica | 2002–2026 | Wiese et al. (2022) | não |
| Frederikse et al. (2020) | orçamento global e por bacia; campos espaciais de cada processo em grade de 0,5° | 1900–2018 | Frederikse et al. (2020) | sim |
| Altimetria NOAA/NESDIS | nível médio global por satélite | 1993–2024 | NOAA (2026) | sim |
| HadCRUT5 e GISTEMP v4 | temperatura média global | 1850–2025 | Morice et al. (2021) | somente HadCRUT5 |
| NCEI | conteúdo de calor oceânico | 1955–2026 | Levitus et al. (2012) | não |
| MIDAS (IGS14) | velocidades verticais de 20.168 estações GNSS | variável | Blewitt et al. (2016) | sim |
| IPCC AR6 | projeções por processo, cenário e percentil, em 6 estações brasileiras e global | 2020–2150 | Garner et al. (2021) | sim |
| CSIRO (reconstrução) | nível médio global | 1880–2013 | Church e White (2011) | não |

Fonte: Elaborado pelos autores (2026).

### 3.2 Controle de qualidade

Às séries maregráficas aplicaram-se regras declaradas e idênticas para todas as estações: descarte do código de ausência de dado; descarte de meses sinalizados; formação de média anual apenas com anos de pelo menos dez meses válidos, para evitar viés sazonal; e exigência de no mínimo 30 anos válidos e 25 anos de extensão, critério que corresponde ao período mínimo recomendado para separar tendência climática de variabilidade natural. Para as séries horárias do UHSLC, exigiu-se cobertura de 70% das horas de cada mês e de dez meses válidos por ano.

### 3.3 Estimadores de tendência

Os resíduos de séries anuais de nível do mar são fortemente autocorrelacionados, o que faz o erro padrão do método dos mínimos quadrados subestimar a incerteza real da tendência. Por isso toda tendência foi estimada por três caminhos independentes: mínimos quadrados com erro padrão robusto de Newey e West (1987), que corrige autocorrelação e heterocedasticidade; estimador robusto de Theil-Sen; e reamostragem por blocos móveis, que preserva a estrutura de autocorrelação sem hipótese paramétrica.

### 3.4 Impressões digitais

Os fatores de impressão digital foram calculados a partir dos campos de nível relativo do mar de cada processo baristático (FREDERIKSE et al., 2020), em grade de 0,5°, como a razão entre a tendência local e a tendência da média global ponderada pelo cosseno da latitude, no mesmo período em que o fator seria aplicado. Calcularam-se fatores em onze pontos correspondentes a estações maregráficas e em um transecto contínuo de 28 pontos ao longo do litoral, de 4,4° N a 34° S, além de sete pontos de contraste fora do Brasil destinados a verificar a física do campo próximo.

### 3.5 Emulador semi-empírico

Para cada componente, ajustou-se dS/dt como função da temperatura média global relativa a 1850–1900. Quatro formas funcionais foram consideradas: linear, linear com termo de taxa, potência e quadrática. Impuseram-se restrições de monotonicidade — coeficiente principal não negativo, expoente maior ou igual a um, curvatura não negativa — de modo que mais aquecimento jamais produza menos perda de massa. Essa restrição não é detalhe técnico: sem ela, o ajuste por mínimos quadrados seleciona uma parábola de curvatura negativa que reproduz bem o passado e se inverte na extrapolação, modo de falha efetivamente observado durante o desenvolvimento e idêntico ao que inviabiliza a regressão quadrática no tempo.

A forma funcional e a janela de suavização do forçante não foram escolhidas por ajuste dentro da amostra, critério que premiaria a flexibilidade, nem pelo desempenho no conjunto de teste final, o que configuraria vazamento de dado. Foram escolhidas por validação cruzada de origem móvel aninhada, usando apenas anos anteriores a 1990, com regra de parcimônia: entre as combinações cujo erro está a menos de 5% do melhor, adota-se a de menor número de parâmetros. A aplicação dessa regra foi decisiva: para os mantos de gelo, doze combinações mostraram-se estatisticamente indistinguíveis, e a seleção pela mais flexível produzia projeção de 9 mm/ano a 4,4 K de aquecimento, uma ordem de grandeza acima de qualquer estimativa publicada. A forma selecionada por parcimônia foi a linear de Rahmstorf (2007) para os três componentes de massa; para o termo estérico a validação selecionou a forma de potência, cujo expoente convergiu para o limite inferior admitido (q = 1,00), reduzindo-a na prática à forma linear.

### 3.6 Cadeia de projeção local

Para cada estação *x*, cenário *c* e horizonte *h*, o nível relativo projetado é

RSL(x, c, h) = Σₚ FPₚ(x) · Sₚ(c, h) + δ(x) · S_estérico(c, h) − VLM(x) · (h − 2020)

em que Sₚ são as contribuições globais de cada processo, FPₚ(x) os fatores de impressão digital, δ(x) o padrão dinâmico local e VLM(x) a velocidade vertical do terreno. Para o termo estérico, que não envolve redistribuição de massa e ao qual a impressão digital gravitacional não se aplica, δ(x) foi obtido da razão entre a projeção de dinâmica oceânica do IPCC AR6 na estação e a correspondente projeção global, por representar a resposta forçada. A razão estérica histórica também foi calculada, mas descartada: resultou entre −0,07 e +0,79 ao longo da costa, refletindo variabilidade dinâmica decadal e escassez de perfis hidrográficos sobre a plataforma, e não a resposta ao forçamento.

Três vias de projeção foram levadas adiante: a via A, com o emulador calibrado em 1900–2018; a via A′, com a mesma forma funcional linearizada em torno do estado observado recente, usando a sensibilidade medida no período de satélite; e a via B, com as projeções processuais oficiais do IPCC AR6.

### 3.7 Modelos de impacto costeiro

A frequência de extremos foi modelada por distribuição de Pareto generalizada ajustada aos excessos acima de limiar alto, sobre as séries horárias destendenciadas e dessazonalizadas, com verificação de estabilidade do ajuste em cinco limiares. A taxa de excedência é definida sobre valores horários; não se aplicou agrupamento de horas consecutivas, o que não afeta a comparação entre presente e futuro, objeto desta análise, mas significa que as taxas não devem ser lidas como número de tempestades independentes. O recuo da linha de costa foi estimado pela regra de Bruun sobre quatro declividades representativas.

### 3.8 Protocolo de validação

Cinco testes independentes foram aplicados: **V1**, reprodução das tendências baristáticas globais publicadas a partir dos campos espaciais; **V2**, fechamento do orçamento do nível do mar em escala global, de bacia e de estação; **V3**, calibração cega ao futuro, com o emulador ajustado somente com 1900–1989 e solicitado a prever 1990–2018; **V4**, confronto com o IMBIE, conjunto independente medido por satélite; **V5**, reprodução das projeções oficiais do IPCC AR6 nas seis estações brasileiras para as quais existem.

## 4 RESULTADOS E DISCUSSÃO

### 4.1 Disponibilidade dos dados maregráficos brasileiros

Das doze estações brasileiras no acervo do PSMSL, apenas duas satisfazem os critérios de qualidade: Cananéia (1954–2004, 51 anos válidos, completude de 100%) e Ilha Fiscal (1963–2022, 55 anos válidos, completude de 91,7%). As demais possuem séries de 1 a 20 anos, em geral encerradas na década de 1960. A verificação das séries horárias do UHSLC confirmou o quadro: embora os metadados indiquem extensão até 2023 em Fortaleza e 2018 em Salvador, a cobertura efetiva é de 13 e 10 anos, respectivamente. A escassez de séries longas no litoral brasileiro, apontada pelo PBMC (2016), é portanto um resultado verificado e não apenas uma observação qualitativa, e condiciona tudo o que se segue.

### 4.2 O Brasil recebe mais que a média global

A Tabela 2 apresenta a validação V1. As cinco tendências baristáticas globais reproduzidas a partir dos campos espaciais conferem com os valores publicados dentro da incerteza declarada, com diferença máxima de 0,024 mm/ano.

**Tabela 2 – Validação V1: tendências baristáticas globais, 1993–2018 (mm/ano).**

| Processo | Reproduzido | Publicado | Diferença | Dentro da incerteza |
|---|---|---|---|---|
| Groenlândia | +0,626 | 0,65 ± 0,04 | −0,024 | sim |
| Antártica | +0,302 | 0,29 ± 0,08 | +0,012 | sim |
| Geleiras | +0,646 | 0,65 ± 0,09 | −0,004 | sim |
| Água continental | +0,312 | 0,32 ± 0,17 | −0,008 | sim |
| Soma baristática | +1,896 | 1,91 ± 0,22 | −0,014 | sim |

Fonte: Elaborado pelos autores (2026), a partir de Frederikse et al. (2020).

A Figura 2 mostra os fatores de impressão digital. Ao longo de 4.000 km de litoral, o fator da Groenlândia cresce de forma quase monotônica de 0,97 na foz do Amazonas a 1,32 no Rio Grande do Sul (correlação com a latitude r = −0,98; a única inversão, de 1,263 para 1,257 entre 22,9° S e 23,5° S, é de 0,5%), enquanto o da Antártica decresce de 1,15 para 0,68 (r = +0,93). Os dois gradientes têm sinal oposto porque descrevem o afastamento de fontes situadas em hemisférios opostos, e **compensam-se**: o fator combinado das duas calotas permanece em 1,119 ± 0,042, variando apenas 12,8% em toda a costa.

O resultado tem duas leituras. A primeira é quantitativa: cada milímetro de elevação média global causado pelo degelo polar produz cerca de 1,12 mm na costa brasileira, uma amplificação de 12% que as projeções que aplicam a média global sem correção deixam de contabilizar. A segunda é operacional: como o fator é praticamente uniforme, uma única constante de amplificação é suficiente para todo o litoral brasileiro, o que simplifica consideravelmente qualquer aplicação prática.

Os pontos de contraste confirmam a física subjacente. Em Nuuk, na Groenlândia, o fator do próprio manto groenlandês é −7,49; no Mar de Amundsen, o fator antártico é −10,08. Nas águas que banham a fonte do degelo o nível relativo do mar **cai**, porque a perda de atração gravitacional do gelo e o rebote elástico da crosta superam o acréscimo de volume de água. No campo distante, onde está o Brasil, encontra-se o excedente.

O trabalho mais próximo do presente, em termos de objeto, é o de Roffman et al. (2023), que calculou padrões de nível do mar com efeitos gravitacionais, rotacionais e deformacionais para projeções dos dois mantos e identificou, na costa sul-americana, amplificação de até 2,9 vezes o equivalente médio global em cenário de **ganho** de massa na Península Antártica, por interferência construtiva dos efeitos. Os dois resultados não são comparáveis diretamente, por descreverem cenários de sinal oposto, mas convergem no ponto essencial: a costa sul-americana situa-se em região de amplificação, e tratá-la pela média global subestima sistematicamente a resposta local.

**[Figura 2 – Fatores de impressão digital do nível do mar: (a) transecto ao longo do litoral brasileiro; (b) contraste entre campo próximo e campo distante.]**
Fonte: Elaborado pelos autores (2026), a partir dos campos de Frederikse et al. (2020).

### 4.3 O orçamento fecha, e onde não fecha isso é informativo

A Figura 3 e a Tabela 3 apresentam a validação V2. Em escala global o orçamento fecha em todos os períodos: de 1900 a 2018, a soma dos contribuintes é 1,524 mm/ano contra 1,563 mm/ano observados, resíduo de 0,039 mm/ano; de 1993 a 2018, 3,159 contra 3,353 mm/ano. Os mantos de gelo respondem por 33,3% da elevação global no período longo e 29,1% na era altimétrica. No Atlântico Sul, bacia que banha o Brasil, a parcela das calotas é de 28,9%.

**Tabela 3 – Validação V2: fechamento do orçamento nas estações brasileiras (mm/ano).**

| Estação e período | Observado (IC 95% HAC) | Soma prevista | Resíduo | z | Resultado | Calotas (% do observado) |
|---|---|---|---|---|---|---|
| Ilha Fiscal, 1963–2018 | +2,421 (+0,36 a +4,48) | 1,317 ± 0,545 | +1,104 | +0,93 | fecha | 20,5% |
| Ilha Fiscal, 1993–2018 | +2,879 (−2,75 a +8,51) | 1,516 ± 0,547 | +1,362 | +0,47 | fecha | 37,5% |
| Cananéia, 1957–2004 | +4,099 (+3,13 a +5,07) | 0,793 ± 0,942 | +3,306 | +3,11 | **não fecha** | 7,2% |

Fonte: Elaborado pelos autores (2026).

A tendência estimada para a Ilha Fiscal no período 1963–2018, de 2,421 mm/ano, coincide com os 2,42 mm/ano publicados por Carvalho et al. (2024) para 1963–2017 na mesma estação. A reprodução independente de um resultado revisado por pares, a partir dos dados brutos e com rotina de limpeza própria, valida o tratamento aplicado.

O resultado de Cananéia merece destaque metodológico. Essa estação apresenta o **melhor** ajuste estatístico de toda a análise: R² de 0,734 contra 0,235 na Ilha Fiscal, intervalo de confiança estreito, nenhum sinal de problema nos diagnósticos de regressão. E, no entanto, o teste de fechamento a rejeita: a tendência observada de 4,099 mm/ano excede em 3,3 mm/ano tudo o que os processos físicos conhecidos conseguem explicar, com z = +3,11. Cananéia situa-se em sistema estuarino-lagunar, onde sedimentação, descarga fluvial e movimentos locais do terreno distorcem o sinal oceânico. O ponto é que **nenhum diagnóstico de regressão detectaria isso**; apenas o confronto com a física detecta. Um ajuste estatístico excelente sobre dados fisicamente inconsistentes continua sendo um ajuste sobre dados inconsistentes, e essa é a principal lição metodológica que o presente estudo extrai de sua própria análise.

Observe-se ainda que, na Ilha Fiscal, a correção de Newey-West infla o erro padrão da tendência em 1,68 vez em relação ao mínimos quadrados clássico, com autocorrelação de resíduos de 0,68. Intervalos de confiança calculados sem essa correção são otimistas por um fator próximo de dois.

**[Figura 3 – Fechamento do orçamento do nível do mar: (a) escala global e de bacia; (b) estações brasileiras.]**
Fonte: Elaborado pelos autores (2026).

### 4.4 Por que não basta aplicar aprendizado de máquina à série local

Quinze algoritmos preditivos foram submetidos a validação cruzada de origem móvel sobre a série anual da Ilha Fiscal, com 29 origens de treino e horizontes de 1 a 20 anos. O resultado, apresentado na Tabela 4 e na Figura 4, é inequívoco e negativo.

**Tabela 4 – Erro quadrático médio fora da amostra, série da Ilha Fiscal (mm).**

| Algoritmo | h = 1 | h = 5 | h = 10 | h = 20 |
|---|---|---|---|---|
| Processo gaussiano | 52,3 | 71,3 | 80,0 | **91,1** |
| k-vizinhos (k = 5) | 56,8 | 66,4 | 78,6 | 93,2 |
| **Média do treino (linha de base trivial)** | 76,3 | 80,5 | 84,4 | **93,8** |
| Floresta aleatória | 46,5 | 66,0 | 76,2 | 94,9 |
| Gradient boosting | 44,1 | 68,6 | 78,4 | 98,1 |
| ARIMA(1,1,1) | 47,0 | 72,2 | 83,7 | 103,5 |
| OLS linear | 78,8 | 91,8 | 106,6 | 116,7 |
| Theil-Sen | 97,7 | 112,5 | 131,3 | 147,8 |
| OLS quadrático | 90,8 | 125,6 | 178,4 | 306,4 |
| Rede neural (MLP) | 218,6 | 581,9 | 1.043,9 | 1.918,6 |

Fonte: Elaborado pelos autores (2026).

O teste foi replicado nas duas estações brasileiras de registro longo, e a replicação **não** confirmou o resultado da primeira. Na Ilha Fiscal, doze dos quinze algoritmos são **piores** que prever simplesmente a média histórica, e o melhor — um processo gaussiano — supera essa linha de base trivial em apenas 3%. Em Cananéia, apenas dois são piores e o melhor, o estimador de Theil-Sen, supera em 65% (39,6 mm contra 113,8 mm). A diferença não está no algoritmo, está na razão sinal-ruído de cada série: a Ilha Fiscal tem R² de 0,235 e desvio padrão dos resíduos de 71 mm, enquanto Cananéia tem R² de 0,734 e desvio de 35 mm. Onde a tendência é forte e limpa, qualquer estimador de tendência a aprende; onde está enterrada na variabilidade interanual, nenhum aprende.

O ponto decisivo é qual das duas séries é fisicamente válida, e a resposta está na Tabela 3: o orçamento fecha na Ilha Fiscal e é rejeitado em Cananéia. A tendência forte e facilmente aprendível de Cananéia é exatamente a que a física rejeita, por conter 3,3 mm/ano que processo conhecido algum explica. Um procedimento de seleção guiado apenas por desempenho de validação cruzada preferiria Cananéia e produziria projeções confiantes, bem validadas e erradas. Desempenho de validação não é evidência de que se está aprendendo a grandeza certa. Note-se ainda que, mesmo em Cananéia, os vencedores são os dois estimadores mais simples, Theil-Sen e mínimos quadrados, enquanto os modelos de aprendizado de máquina permanecem agrupados junto à persistência.

O segundo teste, sobre a série global de contribuição das calotas, mostra o contraste: ali os algoritmos superam amplamente a linha de base trivial (3,6 mm contra 25,5 mm no horizonte de 20 anos). A previsibilidade existe no sinal global forçado, não no registro local.

O painel (b) da Figura 4 expõe o problema estrutural. Quando se pede a cada algoritmo, treinado com a série completa, a contribuição das calotas em 2100, **seis dos quinze respondem um valor constante**, idêntico em 2030, 2050 e 2100: a persistência, o gradient boosting e as árvores extremas devolvem exatamente o valor observado em 2018 (9,78 mm); a floresta aleatória devolve 9,19, o k-vizinhos 7,74 e a média do treino −26,3, cada um preso à sua própria constante. Modelos baseados em árvores de decisão e em vizinhança produzem previsões como médias de valores de treino e, portanto, não podem gerar valor algum fora do intervalo observado. O núcleo de base radial decai para a média do treino longe dos dados; o modelo quadrático inverte-se; a regressão de suporte vetorial projeta queda do nível do mar. Como a projeção climática é, por definição, extrapolação para fora da faixa histórica, essa classe de algoritmos é inadequada à tarefa **independentemente** do desempenho que apresente em horizontes curtos. Esse é o conteúdo empírico da recomendação de Ayinde et al. (2024).

**[Figura 4 – Comparação de algoritmos preditivos: (a) erro fora da amostra por horizonte; (b) comportamento na extrapolação ao ano 2100.]**
Fonte: Elaborado pelos autores (2026).

### 4.5 O emulador prevê a aceleração que nunca viu

A alternativa testada foi deslocar o objeto do aprendizado da forma da curva no tempo para a relação entre temperatura e resposta. A validação V3 é o teste decisivo: o emulador foi calibrado **somente** com 1900–1989, período em que a perda de massa era pequena, e solicitado a prever 1990–2018, quando acelerou. A Figura 5 e a Tabela 5 apresentam o resultado.

**Tabela 5 – Validações V3 e V4 do emulador.**

| Componente | V3: RMSE (mm) | V3: erro na taxa | V4: taxa IMBIE | V4: taxa emulador | V4: diferença |
|---|---|---|---|---|---|
| Groenlândia | 3,67 | +5,0% | +0,469 mm/ano | +0,513 mm/ano | +9,5% |
| Antártica | 2,85 | −77,7% | +0,239 mm/ano | +0,199 mm/ano | −16,9% |
| Geleiras | 4,57 | +41,5% | — | — | — |
| Expansão térmica | 2,56 | +10,4% | — | — | — |

Fonte: Elaborado pelos autores (2026).

O emulador, sem jamais ter visto o período de aceleração, reproduz a taxa de perda da Groenlândia de 1990–2018 com erro de 5,0% e a taxa de expansão térmica com erro de 10,4%, superando neste último caso a melhor extrapolação polinomial por fator de dois. Subestima a taxa antártica em 77,7%, o que é coerente com o entendimento de que a perda antártica recente é dominada por descarga dinâmica de gelo, processo praticamente ausente do registro do século XX.

A validação V4 é mais exigente ainda, por usar conjunto inteiramente independente: o emulador, calibrado sobre a reconstrução de Frederikse et al. (2020), reproduz as taxas medidas por satélite pelo consórcio IMBIE, com metodologia e equipe diferentes, com erro de +9,5% para a Groenlândia e −16,9% para a Antártica.

**[Figura 5 – Validação V3: emulador calibrado apenas com 1900–1989 prevendo 1990–2018.]**
Fonte: Elaborado pelos autores (2026).

### 4.6 A sensibilidade das calotas não é estacionária

A análise de estabilidade dos parâmetros revelou que o coeficiente de sensibilidade da Groenlândia varia 72,9% conforme o ano de corte da calibração. Em vez de tratar essa instabilidade como ruído, mediu-se diretamente a sensibilidade em épocas distintas. Entre 1992–1996 e 2016–2020, a taxa de perda da Groenlândia passou de 0,100 para 0,713 mm/ano, enquanto a temperatura global subiu de 0,59 para 1,23 K acima do nível pré-industrial. A sensibilidade implícita é de **0,965 ± 0,502 mm/ano por kelvin** (1σ), contra 0,132 mm/ano por kelvin no ajuste centenário — razão pontual de 7,3. Essa razão é bem menos precisa do que o valor pontual sugere, por duas causas independentes. A incerteza do numerador é propagada das incertezas do IMBIE tratadas como integralmente correlacionadas dentro de cada época de cinco anos, critério conservador que deixa a própria sensibilidade de satélite a 1,92σ de zero; sob a hipótese alternativa de erros independentes nos cinco anos de cada época, ela estaria a 4,3σ. E o denominador não é constante: o bootstrap do ajuste centenário devolve intervalo de 95% de 0,123 a 0,431 mm/ano por kelvin para esse coeficiente, porque o parâmetro de limiar T₀ do ajuste da Groenlândia converge para o extremo do intervalo admitido (seção 4.10), e a estimativa pontual de 0,132 situa-se no percentil 23 da própria distribuição de reamostragem. Propagando as duas incertezas por Monte Carlo, a razão tem mediana de 5,0 e intervalo de 95% de 0 a 13,6, com probabilidade de 93% de exceder a unidade. O que os dados sustentam é aumento provável de magnitude mal determinada, e não um fator preciso de 7,3. Para a Antártica, a incerteza (±0,659 sobre 0,198) impede detectar mudança significativa.

A mesma conta aplicada às projeções do IPCC AR6 no cenário SSP5-8.5 (FOX-KEMPER et al., 2021) fornece sensibilidade implícita de 0,663 mm/ano por kelvin para a Groenlândia, abaixo do valor central observado no período de satélite. A diferença, de +0,302 mm/ano por kelvin, equivale a 0,60σ da incerteza do valor observado (p = 0,55): as duas estimativas são estatisticamente compatíveis, e o dado disponível **não** autoriza afirmar que as projeções oficiais subestimem a sensibilidade da Groenlândia. Autoriza a afirmação recíproca, que já é informativa: a sensibilidade medida por satélite não é menor que a embutida no AR6, de modo que a magnitude das projeções oficiais é compatível com a resposta observada.

Esse achado reposiciona as três vias de projeção. A via A, calibrada em 119 anos, dilui numa média centenária uma sensibilidade que provavelmente cresceu, e fornece portanto um limite inferior — leitura reforçada pelo fato de o limiar T₀ convergir para o extremo do intervalo admitido nesse ajuste, o que amortece a aceleração projetada (seção 4.10). A via A′, que usa a sensibilidade medida no próprio período de satélite, produz 359, 460 e 635 mm em 2100 nos cenários SSP1-2.6, SSP2-4.5 e SSP5-8.5 — valores que se situam **dentro da faixa provável do IPCC AR6 nos cinco cenários**, sem recorrer a modelo processual algum. Esse é um resultado próprio da pesquisa: a magnitude das projeções processuais internacionais é sustentada, de forma independente, pela sensibilidade observada nas medições de satélite das calotas.

**[Figura 6 – (a) Sensibilidade das calotas ao aquecimento em três épocas; (b) projeção global nas três vias.]**
Fonte: Elaborado pelos autores (2026).

### 4.7 Projeções para o litoral brasileiro

A Tabela 6 e a Figura 7 apresentam as projeções de nível relativo do mar nos onze pontos analisados.

**Tabela 6 – Elevação projetada do nível relativo do mar e parcela das calotas polares (cenário SSP2-4.5).**

| Estação | Latitude | 2050 (mm) | 2100 (mm) | Calotas em 2100 (mm) | Parcela |
|---|---|---|---|---|---|
| Santana (AP) | −0,1° | 165 | 536 | 193 | 36,1% |
| Belém (PA) | −1,4° | 202 | 640 | 194 | 30,3% |
| Ponta da Madeira (MA) | −2,6° | 175 | 564 | 196 | 34,8% |
| Fortaleza (CE) | −3,7° | 171 | 554 | 202 | 36,5% |
| Recife (PE) | −8,1° | 260 | 794 | 206 | 25,9% |
| Salvador (BA) | −13,0° | 156 | 509 | 201 | 39,5% |
| Ilha Fiscal (RJ) | −22,9° | 156 | 505 | 197 | 39,0% |
| Santos (SP) | −24,0° | 138 | 458 | 192 | 42,0% |
| Cananéia (SP) | −25,0° | 154 | 500 | 190 | 38,0% |
| Imbituba (SC) | −28,2° | 165 | 529 | 189 | 35,7% |
| Rio Grande (RS) | −32,1° | 119 | 404 | 179 | 44,4% |

Fonte: Elaborado pelos autores (2026).

A contribuição absoluta das calotas polares é notavelmente uniforme ao longo da costa — de 179 a 206 mm em 2100 no cenário intermediário —, consequência direta da uniformidade do fator de impressão digital demonstrada na seção 4.2. A variação da elevação total entre estações, de 404 a 794 mm, é portanto produzida quase inteiramente pelo movimento vertical do terreno, e não por diferenças na resposta oceânica.

Considerando os cinco cenários e os onze pontos, a parcela das calotas polares na elevação projetada é de 30,5% em média em 2050 (faixa de 18,7% a 47,9%) e de 37,2% em 2100 (faixa de 25,6% a 55,6%). A parcela cresce com o tempo porque a contribuição das calotas acelera mais que as demais, e é maior nos cenários de menor emissão porque neles a expansão térmica é proporcionalmente menor.

A validação V5 confronta a cadeia com as projeções oficiais. Em Ilha Fiscal, Salvador e Imbituba, estações nas quais a estimativa GNSS de movimento do terreno concorda com a taxa de fundo adotada pelo AR6, a cadeia reproduz as projeções oficiais com diferença de **1,0% a 3,6%** em 2100 no cenário intermediário, e de 0,7% a 4,4% considerando os três cenários testados. Como a cadeia foi montada de forma independente, a partir de campos de impressão digital, de componentes globais de emulador próprio e de velocidades GNSS, essa concordância valida o conjunto, e não apenas uma de suas peças.

**[Figura 7 – (a) Decomposição da elevação projetada por estação; (b) parcela das calotas polares por cenário.]**
Fonte: Elaborado pelos autores (2026).

### 4.8 Subsidência medida e implicação para as projeções oficiais

Nas três estações restantes a cadeia diverge das projeções oficiais, e a origem da divergência é identificável. A Tabela 7 mostra que a diferença entre a velocidade vertical medida por GNSS e a taxa de fundo adotada pelo IPCC AR6, multiplicada pelos 80 anos de projeção, explica de 85% a 103% da diferença observada.

**Tabela 7 – Movimento vertical do terreno: GNSS contra IPCC AR6 (mm/ano).**

| Estação | GNSS (esta pesquisa) | IPCC AR6 | Diferença | Diferença explicada na projeção de 2100 |
|---|---|---|---|---|
| Recife (PE) | −3,05 ± 0,87 | +0,49 | −3,55 | 103% |
| Belém (PA) | −0,98 ± 0,95 | +0,52 | −1,50 | 97% |
| Cananéia (SP) | −0,04 ± 0,94 | −1,29 | +1,25 | 85% |
| Ilha Fiscal (RJ) | −0,12 ± 0,53 | +0,07 | −0,19 | — |
| Salvador (BA) | +0,09 ± 0,47 | +0,12 | −0,02 | — |
| Imbituba (SC) | −0,41 ± 0,71 | −0,23 | −0,17 | — |

Fonte: Elaborado pelos autores (2026).

O caso de Recife é o mais relevante em termos práticos. Duas estações GNSS, com séries efetivas de 17 anos, indicam subsidência de 3,05 ± 0,87 mm/ano, enquanto a taxa de fundo adotada pelo AR6 indica leve soerguimento. A diferença implica que a projeção oficial **subestima** a elevação do nível relativo do mar em Recife em aproximadamente 28 cm até 2100 — mais da metade do próprio valor projetado. Subsidência dessa magnitude em região metropolitana costeira é compatível com extração de água subterrânea e compactação de sedimentos, e a consequência para o planejamento é direta: as estimativas oficiais disponíveis para a quarta maior região metropolitana do país descrevem o oceano corretamente e o terreno não.

### 4.9 Impactos sobre a dinâmica costeira

A Figura 8 e a Tabela 8 traduzem a elevação projetada em dinâmica costeira. Na Ilha Fiscal, com 51 anos de dados horários, o nível que hoje tem período de retorno de 100 anos (1.456 mm acima do nível médio atual) passaria a ter período de retorno de 10,4 anos já em 2050 no cenário intermediário, e de 0,12 ano em 2100. O fator de multiplicação da frequência de excedência é de 806 no cenário SSP2-4.5 e de 8.665 no SSP5-8.5; em Cananéia, 184 e 1.381.

Esses fatores exigem atenção à unidade: a taxa é definida sobre valores horários, de modo que um período de retorno de 0,12 ano corresponde a cerca de oito **horas** de excedência por ano, e não a oito eventos independentes. Convertido para a métrica operacional de dias de alagamento, contada hora a hora no registro histórico deslocado pela elevação projetada, o resultado em 2100 no cenário intermediário é de 11,3 dias por ano acima do nível hoje anual e 0,3 dia por ano acima do nível hoje centenário na Ilha Fiscal, e de 4,9 e 0,1 dia por ano em Cananéia. O nível hoje centenário passa a ocorrer anualmente em 2110 na Ilha Fiscal e em 2116 em Cananéia.

A magnitude da amplificação depende da **largura da distribuição de níveis extremos**: onde a maré astronômica domina e a variabilidade de ressaca é pequena, a distância entre o nível anual e o centenário é curta, e uma elevação modesta desloca a distribuição por inteiro. Entre as seis estações, essa largura varia de 78 mm em Recife a 929 mm em Imbituba, e o fator de amplificação varia na razão inversa, com correlação entre os logaritmos de r = −0,986.

**Tabela 8 – Amplificação da frequência de extremos e recuo da linha de costa (SSP2-4.5).**

| Estação | Nível de retorno de 100 anos hoje | Novo período de retorno em 2050 | Novo período de retorno em 2100 | Fator em 2100 | Recuo em 2100 (declividade 1:50 a 1:100) |
|---|---|---|---|---|---|
| Ilha Fiscal (RJ) | 1.456 mm | 10,4 anos | 0,12 ano | ×806 | 25 a 51 m |
| Cananéia (SP) | 1.775 mm | 19,1 anos | 0,54 ano | ×184 | 25 a 50 m |

Fonte: Elaborado pelos autores (2026).

O mecanismo é geométrico e não requer hipótese alguma sobre mudança no regime de ondas ou de tempestades: basta deslocar a distribuição observada pelo valor da elevação projetada. Um evento hoje excepcional torna-se a condição normal de maré alta. A mesma análise aplicada a Recife, Salvador e Fortaleza produz fatores ainda maiores, entre 1,9 × 10⁴ e 1,2 × 10⁵, porque nessas estações os níveis extremos são dominados pela maré astronômica, com pouca variabilidade de ressaca, de modo que a distribuição de extremos é estreita e a elevação média a desloca por inteiro. Esses valores, contudo, apoiam-se em registros horários de 10 a 14 anos e devem ser lidos como indicativos; a relação entre a largura da distribuição de extremos e a sensibilidade à elevação é, em si, um resultado que merece investigação dedicada com séries mais longas.

Pela regra de Bruun, a elevação projetada no cenário intermediário corresponde a recuo potencial de 20 a 79 m em praias arenosas de declividade 1:50 a 1:100, dos quais 9 a 21 m atribuíveis especificamente ao degelo das calotas polares. A amplificação geométrica — um metro de elevação convertendo-se em dezenas de metros de praia — é o que transforma a elevação do nível do mar de um problema de nível em um problema de dinâmica costeira. Considerando que cerca de 60% do litoral brasileiro — 4.500 de 7.500 km — já apresenta processos erosivos (MUEHE, 2018), o efeito incide sobre um sistema já em desequilíbrio.

**[Figura 8 – (a) Curvas de período de retorno deslocadas pela elevação projetada; (b) recuo potencial da linha de costa.]**
Fonte: Elaborado pelos autores (2026).

### 4.10 Limitações

A regra de Bruun é um modelo de equilíbrio bidimensional, criticado por supor perfil de equilíbrio atingido e ausência de aporte sedimentar (COOPER; PILKEY, 2004); os valores de recuo são ordens de grandeza para praias arenosas expostas, não previsões locais, e não se aplicam a costas de falésia, manguezais ou trechos confinados por obras. A análise de extremos não incorpora mudanças futuras no regime de ondas e ventos, que exigiriam modelagem atmosférica. As velocidades GNSS cobrem de 8 a 21 anos e são extrapoladas como constantes até 2100, hipótese razoável para processos geológicos mas questionável onde a subsidência decorre de extração de água subterrânea, cuja taxa pode variar. O emulador reproduz mal a resposta antártica, pelo motivo discutido na seção 4.5, e por isso a via B é mantida como projeção de referência. Três parâmetros do emulador não são identificados pelos dados: o limiar T₀ converge para o extremo inferior do intervalo admitido nos ajustes da Groenlândia e das geleiras (−3,0 K), e o expoente q do termo estérico converge para o extremo inferior (q = 1), com intervalo de bootstrap cobrindo todo o intervalo permitido (1 a 3). Nesses três casos é a restrição imposta, e não a observação, que fixa o valor. O forçante é suavizado por média móvel centrada, escolha que preserva o alinhamento temporal entre forçante e resposta mas faz o valor suavizado de um ano depender de anos posteriores. Para os três componentes de massa a janela selecionada é de um ano, de modo que nenhuma suavização é aplicada e a calibração cega da validação V3 é estritamente cega ao futuro; para o termo estérico, de janela cinco, a janela de calibração incorpora dois anos além do corte de 1989. Substituída a média centrada por média retroativa, a validação aninhada passa a selecionar para a Groenlândia a forma com termo de taxa e janela de vinte e um anos, e o erro de V3 nesse componente sobe de 5,0% para 64,7%: o resultado de V3 é condicionado à convenção de suavização e não deve ser lido como propriedade invariante do emulador. Por fim, apenas duas estações brasileiras possuem registro longo o bastante para o teste de fechamento local, limitação que é ela própria um dos resultados deste trabalho.

## 5 CONCLUSÃO

O objetivo deste trabalho era construir e validar uma cadeia preditiva capaz de atribuir, em cada ponto do litoral brasileiro, a parcela da elevação do nível do mar imputável ao derretimento das calotas polares, e traduzir essa elevação em dinâmica costeira. O objetivo foi alcançado, e cada elo da cadeia foi submetido a teste independente.

Os resultados principais são quatro. Primeiro, a costa brasileira recebe 1,12 vez a elevação média global causada pelo degelo polar, com variação de apenas 12,8% ao longo de 4.000 km, porque os gradientes opostos da Groenlândia e da Antártica se compensam — um fator de amplificação uniforme que as projeções baseadas na média global não contabilizam. Segundo, os mantos de gelo respondem por 20,5% da elevação observada na Ilha Fiscal entre 1963 e 2018, por 37,5% entre 1993 e 2018, e deverão responder por 26% a 44% da elevação projetada até 2100. Terceiro, a sensibilidade da Groenlândia ao aquecimento medida no período de satélite excede provavelmente a média do século XX — razão com mediana de 5,0, intervalo de 95% de 0 a 13,6 e probabilidade de 93% de exceder a unidade — e é compatível com a sensibilidade implícita nas projeções do IPCC AR6, o que sustenta de forma independente a magnitude dessas projeções sem autorizar a conclusão de que sejam conservadoras. Quarto, medições GNSS indicam subsidência de 3,05 ± 0,87 mm/ano em Recife, não incorporada às projeções oficiais, com implicação de subestimação de cerca de 28 cm na elevação relativa projetada para 2100.

A contribuição metodológica é de natureza distinta e igualmente deliberada, e o resultado mais útil veio de uma replicação que falhou. Submetidos a validação cruzada de origem móvel, quinze algoritmos comportam-se de modo oposto nas duas estações brasileiras de registro longo: na Ilha Fiscal, doze são piores que prever a média histórica e o melhor ganha 3%; em Cananéia, apenas dois são piores e o melhor ganha 65%. A diferença decorre da razão sinal-ruído de cada série, não do algoritmo. E a série em que os algoritmos têm bom desempenho é precisamente aquela que o teste de fechamento rejeita: uma seleção guiada apenas por desempenho de validação escolheria a estação fisicamente inconsistente e produziria projeções bem validadas e erradas. Independentemente da estação, porém, seis dos quinze são estruturalmente incapazes de gerar valor fora da faixa de treino. A previsibilidade reside no sinal global forçado, acessível por meio da relação física entre forçante e resposta. Demonstrou-se igualmente que restrições de monotonicidade e regras de parcimônia na seleção de modelo não são refinamentos opcionais: sem elas, a seleção por melhor ajuste escolhe formas funcionais que reproduzem o passado e se invertem ou explodem na extrapolação. E demonstrou-se, no caso de Cananéia, que o diagnóstico estatístico de uma regressão — ainda que excelente — não substitui o teste de consistência física dos dados sobre os quais ela foi ajustada.

Como trabalhos futuros, recomenda-se estender a análise de extremos com séries horárias mais longas nas estações do Nordeste, onde a distribuição estreita de níveis extremos produz os maiores fatores de amplificação e onde os registros atuais não sustentam níveis de retorno centenários; instalar e manter estações GNSS colocalizadas com os marégrafos brasileiros, requisito para qualquer atribuição confiável; e incorporar à cadeia a resposta dinâmica do litoral mediante modelos morfodinâmicos que superem as limitações da regra de Bruun. Recomenda-se, por fim, que séries maregráficas brasileiras sejam submetidas às reconstruções globais do orçamento do nível do mar, das quais hoje estão inteiramente ausentes.

## AGRADECIMENTOS

Os autores agradecem às instituições que mantêm e disponibilizam publicamente os conjuntos de dados utilizados: Permanent Service for Mean Sea Level, University of Hawaii Sea Level Center, Nevada Geodetic Laboratory, Met Office Hadley Centre, NASA/JPL e os consórcios IMBIE e IPCC. Conforme a política de uso da fonte, registra-se que os dados de altimetria são fornecidos pelo NOAA Laboratory for Satellite Altimetry (*Altimetry data are provided by NOAA Laboratory for Satellite Altimetry*). Agradecem igualmente ao Prof. Dr. Renato Gonçalves Rocha pela orientação.

## REFERÊNCIAS

AYINDE, A. S. et al. Review of machine learning methods for sea level change modeling and prediction. **Science of the Total Environment**, v. 954, art. 176410, 2024. DOI: https://doi.org/10.1016/j.scitotenv.2024.176410.

BLEWITT, G. et al. MIDAS robust trend estimator for accurate GPS station velocities without step detection. **Journal of Geophysical Research: Solid Earth**, v. 121, n. 3, p. 2054-2068, 2016. DOI: https://doi.org/10.1002/2015JB012552.

BRUUN, P. Sea-level rise as a cause of shore erosion. **Journal of the Waterways and Harbors Division**, v. 88, n. 1, p. 117-130, 1962.

CALDWELL, P. C.; MERRIFIELD, M. A.; THOMPSON, P. R. **Sea level measured by tide gauges from global oceans**: the Joint Archive for Sea Level holdings (NCEI Accession 0019568), Version 5.5. NOAA National Centers for Environmental Information, 2015. DOI: https://doi.org/10.7289/V5V40S7W.

CARVALHO, B. C.; ARAUJO, T. A. A.; GUERRA, J. V.; REIS, A. T. dos. Mean sea level trends based on tide gauge records and their possible morphological effects on the coastline of southern Rio de Janeiro (SE Brazil). **Thalassas**, v. 40, p. 261-272, 2024. DOI: https://doi.org/10.1007/s41208-023-00618-6.

CHURCH, J. A.; WHITE, N. J. Sea-level rise from the late 19th to the early 21st century. **Surveys in Geophysics**, v. 32, p. 585-602, 2011. DOI: https://doi.org/10.1007/s10712-011-9119-1.

COOPER, J. A. G.; PILKEY, O. H. Sea-level rise and shoreline retreat: time to abandon the Bruun Rule. **Global and Planetary Change**, v. 43, n. 3-4, p. 157-171, 2004. DOI: https://doi.org/10.1016/j.gloplacha.2004.07.001.

EDWARDS, T. L. et al. Projected land ice contributions to twenty-first-century sea level rise. **Nature**, v. 593, p. 74-82, 2021. DOI: https://doi.org/10.1038/s41586-021-03302-y.

FOX-KEMPER, B. et al. Ocean, cryosphere and sea level change. In: IPCC. **Climate Change 2021**: The Physical Science Basis. Cambridge: Cambridge University Press, 2021. p. 1211-1362.

FREDERIKSE, T. et al. The causes of sea-level rise since 1900. **Nature**, v. 584, p. 393-397, 2020. DOI: https://doi.org/10.1038/s41586-020-2591-3.

GARNER, G. G. et al. **IPCC AR6 Sea Level Projections**. Zenodo, 2021. DOI: https://doi.org/10.5281/zenodo.6382554.

GREGORY, J. M. et al. Concepts and terminology for sea level: mean, variability and change, both local and global. **Surveys in Geophysics**, v. 40, p. 1251-1289, 2019. DOI: https://doi.org/10.1007/s10712-019-09525-z.

HOLGATE, S. J. et al. New data systems and products at the Permanent Service for Mean Sea Level. **Journal of Coastal Research**, v. 29, n. 3, p. 493-504, 2013. DOI: https://doi.org/10.2112/JCOASTRES-D-12-00175.1.

IPCC. Summary for Policymakers. In: **Climate Change 2021**: The Physical Science Basis. Cambridge: Cambridge University Press, 2021. p. 3-32.

LEVITUS, S. et al. World ocean heat content and thermosteric sea level change (0-2000 m), 1955-2010. **Geophysical Research Letters**, v. 39, L10603, 2012. DOI: https://doi.org/10.1029/2012GL051106.

MITROVICA, J. X.; TAMISIEA, M. E.; DAVIS, J. L.; MILNE, G. A. Recent mass balance of polar ice sheets inferred from patterns of global sea-level change. **Nature**, v. 409, p. 1026-1029, 2001. DOI: https://doi.org/10.1038/35059054.

MORICE, C. P. et al. An updated assessment of near-surface temperature change from 1850: the HadCRUT5 data set. **Journal of Geophysical Research: Atmospheres**, v. 126, e2019JD032361, 2021. DOI: https://doi.org/10.1029/2019JD032361.

MUEHE, D. Critérios morfodinâmicos para o estabelecimento de limites da orla costeira para fins de gerenciamento. **Revista Brasileira de Geomorfologia**, v. 2, n. 1, p. 35-44, 2001. DOI: https://doi.org/10.20502/rbg.v2i1.6.

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

WIESE, D. N. et al. **JPL GRACE and GRACE-FO Mascon Ocean, Ice, and Hydrology Equivalent Water Height RL06.3M CRI Filtered Version 4.0**. PO.DAAC, 2022. DOI: https://doi.org/10.5067/TEMSC-3JC634.

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
