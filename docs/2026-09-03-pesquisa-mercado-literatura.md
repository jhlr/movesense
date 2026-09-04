# Pesquisa de mercado e literatura — MoveSense
**Data:** 2026-09-03

Pesquisa via WebSearch (achados de página, sem leitura de artigo completo) cobrindo três frentes: produtos existentes, literatura científica de metodologia, e gaps de mercado. Todo número de preço/técnico não confirmado está marcado como "não encontrado" — nenhum valor foi estimado.

## Soluções existentes

| Produto/Empresa | O que mede | Preço | Observações (diferenciação vs MoveSense) |
|---|---|---|---|
| **DorsaVi** (ViMove+) | Movimento lombar/postura, biofeedback em tempo real, usado em fisioterapia e ergonomia ocupacional | Hardware ~US$1.490 + licença de software US$149–249/mês (mais pacotes de US$59–550/mês) | Foco em coluna/postura, não é bilateral braço-a-braço; modelo de assinatura recorrente caro para clínica pequena. MoveSense é hardware próprio sem licença mensal. |
| **Kinvent** (K-Move, K-Push, K-Myo, K-Grip) | K-Move: goniômetro inercial (ROM); K-Push: dinamometria; K-Myo: EMG; K-Grip: força de preensão/fadiga | K-Push V3 ≈ €981,75; Starter Pack ≈ €2.667,98; preço completo da linha não encontrado | Ecossistema modular forte (força + ROM + EMG), mas cada sensor é vendido separado e caro para setup completo. Não há assimetria bilateral simultânea nativa entre dois membros no mesmo teste — normalmente compara medições sequenciais. |
| **Movella / Xsens** (MVN Awinda, MVN Link, Movella DOT) | Motion capture full-body com múltiplos IMUs, cinemática articular completa | Preço não encontrado (não disponível publicamente nos resultados de busca) | Padrão-ouro de motion capture inercial usado em pesquisa; caro e complexo (17+ sensores, traje completo) — não é um produto de bolso para consulta rotineira de fisioterapia. |
| **Notch** | Motion capture corporal com IMUs Bluetooth para smartphone | Kit padrão (6 IMUs) ≈ US$379 (dado de 2019); pacote full-body com 12 sensores + licença 1 ano ≈ US$699 | Mais acessível que mocap tradicional, mas voltado a animação/esporte geral, não a métricas clínicas de reabilitação (ROM articular formal, assimetria, fadiga). |
| **VALD** (ForceDecks, NordBord, HumanTrak, ForceFrame, DynaMo, SmartSpeed) | Força (plataformas de força, dinamometria isométrica/excêntrica), assimetria de força entre membros, motion capture markerless (HumanTrak) | Faixa ampla US$360–US$12.360 conforme sistema/config; HumanTrak US$350–US$12.000; modelo de assinatura com reajuste anual de 3% | Detecta assimetria de **força**, não de cinemática de movimento (ROM/tremor) via IMU vestível; equipamento de bancada/lab, não wearable portátil bilateral. Investimento alto, mais voltado a clubes esportivos profissionais. |
| **Delsys Trigno** | EMG de superfície + IMU embutido (acelerômetro/giroscópio/magnetômetro) por sensor | Orçamento encontrado: sistema completo ~US$111.000 (lista), com desconto chegando a ~US$69.350; aluguel US$18–68/hora | Padrão-ouro de pesquisa em EMG+IMU, mas preço proibitivo para clínica; MoveSense não faz EMG, mas cobre cinemática bilateral a fração do custo. |
| **RunScribe** | Cinemática de corrida (pé/sacral): shock, eficiência, motion, symmetry — já usa "symmetry" como métrica de marca | Preço não encontrado | É o concorrente mais próximo em conceito de "assimetria via IMU bilateral", mas focado só em corrida (pé), não em membros superiores nem em ROM articular geral de reabilitação. |
| **Blast Motion** | Sensor de swing (beisebol, golfe): velocidade de taco, ângulo de ataque | A partir de US$149,95 | Nicho de performance esportiva específica (swing), não aplicável a ROM/tremor/fadiga clínica. |
| **Catapult** (Catapult One / GPS wearables) | GPS + carga de treino, monitoramento de atletas em campo | Catapult One individual: US$179/ano + kit inicial US$34 (~US$213 no 1º ano); planos de time US$180/jogador/ano (mín. 10, contrato 2 anos) | Foco em GPS/carga externa de campo (futebol etc.), não em cinemática articular fina nem reabilitação. |
| **Hawkin Dynamics** (TruStrength, force plates) | Força/potência via plataforma de força sem fio, força isométrica, reabilitação | Base Kit US$99/mês (assinatura) | Equipamento de bancada (força), não wearable IMU bilateral de membro. |
| **Kinetisense** | Avaliação de movimento funcional 3D (câmera + módulos), ROM, postura | Preço do produto não encontrado; praticantes cobram US$30–120 por avaliação ao paciente | Base em câmera/visão computacional (não é wearable IMU) — modelo de negócio diferente (clínica compra sistema, cobra por avaliação). |
| **Physimax** | Avaliação de movimento markerless via visão computacional 2D/3D (cloud) | "A partir de grátis" (freemium, conforme SourceForge) | Não é wearable — visão computacional. Concorre indiretamente pelo mesmo caso de uso (avaliação de movimento em clínica) mas sem hardware vestível nem dado bilateral de IMU. |
| **Cala kIQ** (tremor, não é o foco do MoveSense mas referência de mercado tremor) | Detecção e supressão de tremor postural/cinético em mão (estimulação, não só medição) | Custo inicial ~US$7.150 (coberto por Medicare/veteranos em alguns casos nos EUA) | Foco em tratamento (neuroestimulação) de tremor essencial/Parkinson, não em quantificação para fisioterapia geral — mercado adjacente, não concorrente direto. |
| **Encora X1** | Neuroestimulação para tremor essencial, com análise de tremor em tempo real | Preço não encontrado | Mesma observação: dispositivo terapêutico de tremor, não de avaliação funcional bilateral. |
| **GonioPi** (projeto acadêmico open-source) | Goniômetro digital portátil com MPU-6050 + Raspberry Pi Pico | Não comercial / custo de componentes, não uma "preço de produto" | Prova de conceito acadêmica próxima da filosofia do MoveSense (hardware barato, MPU6050), mas não é bilateral nem tem fusão de dados entre dois membros. |
| **Romiumeter** (projeto open-source) | ROM de pescoço/ombro com um único IMU | Não comercial | Mesma observação — validado com erro máximo <5° vs padrão, mas escopo de um sensor único, sem par bilateral. |
| **Biokin** | ROM de ombro via IMU sem fio | Preço não encontrado | Validade concorrente apenas quando medido pelo mesmo avaliador (teste único) — limitação de confiabilidade inter-avaliador relatada na literatura. |
| **Kinexon Perform IMU** | Rastreamento de atleta, biomecânica, carga, "infraestrutura livre" (funciona fora de quadra/laboratório) | Preço não encontrado | Foco em performance esportiva de elite/carga externa, não em ROM/assimetria clínica bilateral. |
| **Vicon Blue Trident** | IMU de alta performance, IP68, usado em pesquisa e esporte de elite | Preço não encontrado | Sensor de pesquisa validado (referência de RMSE ~8,77° vs VICON em orientação de membro superior encontrada na literatura), preço tipicamente de nível pesquisa/laboratório — fora do alcance de clínica pequena. |

**Não encontrados / não confirmados nesta busca:** IMeasureU (pouco material específico retornado — aparece hoje como parte da marca Catapult/Vicon, dados de preço não localizados), Zephyr Performance Systems (preço não encontrado), Output Sports (não foi possível confirmar produto/preço nos resultados retornados), Sparta Science (não pesquisado diretamente — recomenda-se busca adicional se relevante), Halo Sport (não pesquisado — fora do escopo, é estimulação, não IMU).

## Literatura relevante

- **"Romiumeter: An Open-Source Inertial Measurement Unit-Based Goniometer for Range of Motion Measurements"** — bioRxiv, 2024. Achado-chave: goniômetro de IMU único (open-source) para pescoço/ombro, testado em 34 indivíduos assintomáticos, erro absoluto máximo <5°. Relevante como referência direta de validação de ROM com IMU único e baixo custo. https://www.biorxiv.org/content/10.1101/2024.05.29.596353v2.full

- **"GonioPi: Towards Developing a Scalable, Versatile, Reliable and Accurate Handheld..."** — IJACSA. Achado-chave: goniômetro digital portátil usando MPU-6050 e Raspberry Pi Pico — mesma família de sensor (MPU) que o MoveSense propõe usar, prova de viabilidade de hardware barato. https://thesai.org/Downloads/Volume13No6/Paper_40-GonioPi_Towards_Developing_a_Scalable_Versatile_Reliable_and_Accurate_Handheld.pdf

- **"Assessment of Shoulder Range of Motion Using a Wireless Inertial Motion Capture Device — A Validation Study"** — PMC. Achado-chave: concordância excelente entre IMU e goniômetro para ROM de ombro quando medido pelo mesmo avaliador (ICC > 0,90; limites de concordância < ±5°) — mas concordância cai com avaliadores diferentes, ponto de atenção para protocolo de uso clínico do MoveSense. https://pmc.ncbi.nlm.nih.gov/articles/PMC6514956/

- **"Agreement Between a Wireless Sleeve and a Goniometer in Measuring Elbow and Knee Range of Motion"** — PMC. Achado-chave: mangas/sleeves vestíveis com IMU mostram promessa para ROM clínico e monitoramento remoto, mas "requerem refinamento para reduzir viés antes de aplicação clínica" — evidência de gap de maturidade de produto, não só de conceito. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12500481/

- **"Validation of a Commercially Available IMU-Based System Against an Optoelectronic System for Full-Body Motor Tasks"** — PMC, 2026 (via PMC12196846). Achado-chave: sistema IMU comercial validado contra motion capture óptico, RMSE geralmente <7° e viés sistemático ≤3,9° em tarefas de corpo inteiro — referência de benchmark de acurácia esperada para um sistema IMU bem calibrado. https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12196846/

- **"Bilateral mode exoskeleton for hand rehabilitation with wireless control using 3D printing technology based on IMU sensor"** — HardwareX/PMC. Achado-chave: hardware quase idêntico ao proposto pelo MoveSense (ESP32 mini Wemos D1 + multiplexador I2C TCA9548 + 5 IMUs GY-521/MPU6050) para controle bilateral em reabilitação de mão, com mão saudável controlando exoesqueleto na mão parética — prova de conceito de arquitetura ESP32+MPU6050 bilateral open-source já publicada. https://www.hardware-x.com/article/S2468-0672(23)00039-1/fulltext

- **"Limb Symmetry Index"** — Physiopedia / ScienceForSport. Achado-chave: definição padrão do índice de simetria de membros LSI = (valor do membro afetado / valor do membro não afetado) × 100, com critérios de "aprovação" clínica tipicamente entre 80–95% conforme o teste e a fase de reabilitação. Base direta para a métrica de "assimetria trófica" do MoveSense. https://www.physio-pedia.com/Limb_Symmetry_Index

- **"Comparison of different symmetry indices for the quantification of dynamic joint angles"** — BMC Sports Science, Medicine and Rehabilitation, 2021. Achado-chave: existem múltiplas fórmulas de índice de simetria (não há um único "padrão-ouro" de cálculo) e a escolha da fórmula afeta a interpretação — ponto de atenção metodológica para o MoveSense decidir e documentar sua própria fórmula de assimetria. https://bmcsportsscimedrehabil.biomedcentral.com/articles/10.1186/s13102-021-00355-4

- **"Gait symmetry measures: A review of current and prospective methods"** — ScienceDirect, revisão. Achado-chave: revisão de métodos de simetria de marcha, útil como referência para adaptar métricas de simetria de marcha para membros superiores (o caso de uso principal do MoveSense parece ser braços). https://www.sciencedirect.com/science/article/abs/pii/S1746809418300193

- **"A standardized accelerometry method for characterizing tremor: Application and validation in an ageing population with postural and action tremor"** — PMC, 2026 (via PMC9386269). Achado-chave: metodologia padronizada de acelerometria para tremor, incluindo filtragem passa-banda 1–20 Hz (Butterworth de terceira ordem, fase zero) e filtragem em torno da frequência central ±2 Hz. Diretamente aplicável ao pipeline de processamento de sinal do MoveSense se o produto vier a quantificar tremor. https://pmc.ncbi.nlm.nih.gov/articles/PMC9386269/

- **Bandas de frequência de tremor (múltiplas fontes, ex. J Neuroscience / PMC6055592 / PLOS ONE)** — Achado-chave consolidado: tremor de repouso clássico em Parkinson ≈ 4–6 Hz; tremor postural/cinético de tremor essencial ≈ 4–8 Hz (uma fonte reporta pico médio 4,57 ± 1,8 Hz em ET). Tremor fisiológico normal tende a ficar em faixa mais alta (~8–12 Hz, citado de forma consistente na literatura geral de tremor, embora não tenha aparecido um número exato nesta busca específica — checar se necessário antes de publicar). Útil como referência de banda para separar tremor patológico de ruído/tremor fisiológico no MoveSense. https://www.jneurosci.org/content/35/2/795

- **"IMU/UWB Fusion Method Using a Complementary Filter and a Kalman Filter for Hybrid Upper Limb Motion Estimation"** — PMC, 2023. Achado-chave: RMSE de 8,77° para estimativa de orientação de membro superior comparado a VICON (padrão-ouro óptico) usando fusão de filtro complementar (Madgwick RK4) + Kalman com UWB. Referência de acurácia esperada e de arquitetura de fusão (Kalman é mais preciso mas caro computacionalmente; complementar é mais rápido) — decisão de trade-off relevante para o firmware do ESP32. https://pmc.ncbi.nlm.nih.gov/articles/PMC10422251/

- **"Data-Driven Approach for Upper Limb Fatigue Estimation Based on Wearable Sensors"** — MDPI Sensors, PMC10674769. Achado-chave: modelos de fadiga do membro superior a partir de sensores vestíveis (não-EMG), usando features cinemáticas (média, desvio padrão, RMS, amplitude por ciclo) combinadas com escalas subjetivas (Borg) como alternativa prática ao EMG para monitoramento de longo prazo. Base direta para a métrica de "fadiga estimada por cinemática" do MoveSense. http://dx.doi.org/10.3390/s23229291

- **"A dataset for fatigue estimation during shoulder internal and external rotation movements using wearables"** — Scientific Data (Nature), 2024. Achado-chave: dataset público de fadiga de ombro coletado com wearables — útil como possível benchmark/dataset de referência ou inspiração metodológica para validar o algoritmo de fadiga do MoveSense. https://www.nature.com/articles/s41597-024-03254-8

- **"Detection of Sets and Repetitions in Strength Exercises Using IMU-Based Wristband Wearables"** — ResearchGate. Achado-chave: detecção de séries e repetições em exercícios de força usando wearables IMU de pulso — abordagem de contagem de repetição por thresholding de picos em acelerômetro/giroscópio, com relato de acurácia de até 99,4% em outra abordagem citada (amplitude thresholding via smartwatch). Aplicável direto à métrica de "contagem de repetições" do MoveSense. https://www.researchgate.net/publication/375903173_Detection_of_Sets_and_Repetitions_in_Strength_Exercises_Using_IMU-Based_Wristband_Wearables

- **"A Review of Barriers to the Adoption of Wearable Devices in Healthcare"** — Springer, capítulo de livro. Achado-chave: barreiras de adoção incluem custo de sistemas proprietários, procedimentos de setup longos, necessidade de expertise especializada, falta de confiança/treinamento clínico — e "menos de 18% dos clínicos usam IMU" apesar de ser a tecnologia de monitoramento mais usada dentre as disponíveis. Evidência direta do gap de adoção clínica citado na seção de oportunidades abaixo. https://link.springer.com/chapter/10.1007/978-3-032-24807-7_9

## Gaps e oportunidades

- **Nenhum produto encontrado nesta busca combina IMU bilateral simultâneo (par sincronizado nos dois membros) com assimetria + fadiga num único wearable de baixo custo.** RunScribe chega mais perto do conceito (mede "symmetry" via par de sensores nos pés), mas é exclusivo para corrida/marcha, não membros superiores nem contexto de reabilitação geral. Isso é o diferencial mais concreto e defensável do MoveSense encontrado na pesquisa — mas é uma afirmação baseada em não ter encontrado o concorrente direto, não em uma prova exaustiva de que ele não existe em algum lugar não indexado nesta busca.

- **A adoção clínica de IMU em fisioterapia é documentada como baixa apesar do interesse acadêmico:** a revisão da Springer cita menos de 18% dos clínicos usando IMU rotineiramente, com custo, setup longo e falta de treinamento como barreiras centrais. Isso é evidência direta (não estimativa) de espaço para um produto mais barato e mais simples de operar do que os sistemas de pesquisa/lab (Xsens, Delsys, Vicon) e mais barato que os sistemas comerciais de assinatura (VALD, DorsaVi, Kinvent).

- **Preço é o eixo de diferenciação mais claro e verificável.** Onde há dado de preço: DorsaVi (hardware ~US$1.490 + assinatura mensal), Kinvent (Starter Pack ~€2.668), Delsys Trigno (dezenas de milhares de dólares), VALD (até US$12.360). O extremo barato (Notch ~US$379–699, GonioPi/Romiumeter como projetos acadêmicos não comerciais) tende a ser voltado a um único membro ou a animação, não a avaliação clínica bilateral formal. Há um vácuo entre "brinquedo de US$300 sem validação clínica" e "sistema profissional de US$1.500–12.000+" — é aí que um produto ESP32/MPU6050 bilateral, se validado, pode se posicionar.

- **Grande parte da literatura de ROM/tremor/fadiga com IMU valida contra motion capture ou entre avaliadores, e reporta perda de confiabilidade quando o avaliador muda** (achado explícito no estudo de ROM de ombro via IMU sem fio, PMC6514956, e no sleeve de cotovelo/joelho, PMC12500481). Isso é um risco de validação a ser endereçado no MoveSense desde o design — não um gap de mercado a explorar, mas um problema técnico real que os concorrentes também enfrentam e que precisa aparecer explicitamente em qualquer paper.

- **Fadiga a partir de cinemática (sem EMG) é uma área ativa mas ainda não empacotada como produto comercial rotineiro.** A literatura (MDPI Sensors 23(22):9291, dataset Nature Scientific Data 2024) mostra modelos de fadiga do membro superior usando apenas features cinemáticas + escala de Borg — mas nenhum dos produtos comerciais levantados (Kinvent, DorsaVi, VALD, Delsys) anuncia "fadiga estimada por cinemática pura" como métrica de saída direta ao usuário; Delsys e Kinvent (K-Myo) fazem fadiga via EMG, que é outra classe de sensor e custo. Isso é o segundo ângulo de diferenciação mais forte: MoveSense estimando fadiga sem precisar de eletrodos de EMG.

- **Não há evidência, nesta busca, de nenhum produto comercial descrito explicitamente como "avaliação de assimetria trófica entre membros via par de IMUs vestíveis de baixo custo para fisioterapia".** Isso não prova ausência de mercado — só que a busca não encontrou. Recomenda-se, antes de finalizar o ângulo do artigo/produto, uma busca adicional em bases de patentes (não coberta aqui) e em Google Scholar direto (esta pesquisa usou WebSearch geral, que cobre parcialmente Scholar/PubMed via resultados indexados, não uma consulta direta à API do PubMed/Scholar).

- **Cautela epistemológica:** vários preços vêm de fontes desatualizadas (ex. Notch: dado de 2019) ou de revendedores terceiros, não do fabricante direto — tratar como indicativo de faixa, não como preço atual exato. Da mesma forma, "IMeasureU", "Zephyr", "Output Sports" e "Sparta Science" não tiveram preço nem detalhe de produto confirmado nesta rodada — não afirmar nada sobre eles além do que está registrado como "não encontrado".

## Fontes

### Produtos/soluções
- https://dorsavi.com/shop/
- https://dorsavi.com/vimove-plus/
- https://www.performancehealth.com/kinvent
- https://kinvent.com/
- https://jlwforce.com/collections/kinvent
- https://shop.movella.com/us/product-lines/motion-capture
- https://www.movella.com/health-sports/sports-performance
- https://sportstechnologyblog.com/2019/04/28/notch-wearable-sensor-review/
- https://wearnotch.com/
- https://animation.wearnotch.com/
- https://store.simplifaster.com/product-category/vald/
- https://valdperformance.com/products
- https://valdtactical.com/humantrak/
- https://valdtactical.com/forcedecks/
- https://delsys.com/trigno/
- https://www.adinstruments.com/products/trigno-emg-sensors
- https://runscribe.com/
- https://lermagazine.com/products/runscribe-wearable-sensors
- https://blastmotion.com/faq/
- https://www.catapult.com/pricing
- https://www.catapult.com/solutions/athlete-monitoring
- https://www.hawkindynamics.com/
- https://www.hawkindynamics.com/product-page
- https://www.kinetisense.com/
- https://www.kinetisense.com/resources/faq/
- https://sourceforge.net/software/product/Physimax/
- https://www.medscape.com/viewarticle/wearable-devices-parkinsons-disease-future-here-2024a1000ljg
- https://www.fiercebiotech.com/medtech/fda-clears-encora-therapeutics-wearable-wrist-device-essential-tremor
- https://www.apdaparkinson.org/article/wearable-devices-that-suppress-tremor/
- https://kinexon-sports.com/products/perform-imu/
- https://www.vicon.com/hardware/blue-trident/
- https://simplifaster.com/articles/buyers-guide-imu-sensor-devices/
- https://thesai.org/Downloads/Volume13No6/Paper_40-GonioPi_Towards_Developing_a_Scalable_Versatile_Reliable_and_Accurate_Handheld.pdf

### Literatura científica
- https://www.biorxiv.org/content/10.1101/2024.05.29.596353v2.full (Romiumeter)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC6514956/ (validação ROM ombro via IMU sem fio)
- https://www.ncbi.nlm.nih.gov/pmc/articles/PMC12500481/ (sleeve elbow/knee ROM vs goniômetro)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC12196846/ (validação sistema IMU comercial vs motion capture óptico)
- https://www.hardware-x.com/article/S2468-0672(23)00039-1/fulltext (exoesqueleto bilateral ESP32+MPU6050)
- https://www.physio-pedia.com/Limb_Symmetry_Index (LSI)
- https://bmcsportsscimedrehabil.biomedcentral.com/articles/10.1186/s13102-021-00355-4 (comparação de índices de simetria)
- https://www.sciencedirect.com/science/article/abs/pii/S1746809418300193 (revisão de métodos de simetria de marcha)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC9386269/ (metodologia padronizada de acelerometria de tremor)
- https://www.jneurosci.org/content/35/2/795 (drive central do tremor PD vs ET)
- https://ncbi.nlm.nih.gov/pmc/articles/PMC6055592 (acelerometria + genética PD vs ET)
- https://journals.plos.org/plosone/article?id=10.1371%2Fjournal.pone.0183843 (diagnóstico diferencial PD/ET via acelerômetro de smartphone)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC10422251/ (fusão complementar+Kalman, IMU/UWB, RMSE vs VICON)
- http://dx.doi.org/10.3390/s23229291 (estimativa de fadiga de membro superior via wearables)
- https://www.nature.com/articles/s41597-024-03254-8 (dataset de fadiga de ombro)
- https://www.researchgate.net/publication/375903173_Detection_of_Sets_and_Repetitions_in_Strength_Exercises_Using_IMU-Based_Wristband_Wearables (contagem de repetições)
- https://arxiv.org/html/2410.00407v1 (contagem de repetições few-shot)
- https://link.springer.com/chapter/10.1007/978-3-032-24807-7_9 (barreiras de adoção de wearables em saúde)
- https://rehab.jmir.org/2025/1/e69589 (revisão wearables para reabilitação de equilíbrio)
- https://pmc.ncbi.nlm.nih.gov/articles/PMC6158559/ (perspectiva de fisioterapeutas sobre tecnologia vestível)
