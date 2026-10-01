# TODOS

## Analysis

### Suavidade do movimento (smoothness)

**What:** Métrica de suavidade sobre a série fundida de `complementary_filter()`/gyro — ex. spectral arc length (SPARC) ou jerk normalizado.

**Why:** ROM normal não implica movimento saudável — um movimento espasmódico/descoordenado pode ter a mesma amplitude que um suave. Suavidade é usada na literatura de reabilitação como proxy de qualidade motora independente de amplitude.

**Context:** Levantado em conversa 2026-09-24 discutindo o que mais dá pra medir além das 5 métricas atuais (ROM, tremor, repetições, assimetria, fadiga). Não precisa de hardware novo — roda sobre dado que já é capturado.

**Effort:** S
**Priority:** P2
**Depends on:** `complementary_filter()` e `rom()` já existem (degraus 2-3 do staircase); essa métrica pode entrar direto na validação do Approach B junto com as outras 5.

### Variabilidade entre repetições

**What:** Desvio padrão do ROM (ou do pico de velocidade) entre repetições de uma série — diferente de `fatigue_slope()`, que só pega a tendência linear de queda.

**Why:** Um paciente instável varia rep a rep mesmo sem degradar ao longo da série (sem "fadiga" no sentido de tendência). Consistência bruta é um sinal clínico separado de degradação progressiva.

**Context:** Mesma conversa 2026-09-24. Reusa a mesma detecção de picos de `repetition_count()`/`fatigue_slope()` — só troca o ajuste de reta por um desvio padrão.

**Effort:** S
**Priority:** P2
**Depends on:** `repetition_count()` e `fatigue_slope()` (degraus 4-5, já implementados).

### Tempo até o pico / assimetria temporal

**What:** Tempo (ou fração do ciclo) até cada repetição atingir seu pico de velocidade, comparado entre os dois lados — timing, não magnitude.

**Why:** `asymmetry_index()` atual compara magnitude (ex. ROM esquerdo vs. direito). Isso é um eixo diferente: dois lados podem ter magnitude igual mas ritmo diferente (um lado mais lento pra acelerar), o que também é sinal clínico relevante.

**Context:** Mesma conversa 2026-09-24.

**Effort:** M
**Priority:** P2
**Depends on:** `repetition_count()` (pra segmentar reps) + captura bilateral sincronizada (Approach A) pra comparar os dois lados de verdade.

### Sincronia bilateral

**What:** Correlação cruzada (ou defasagem/lag) entre o sinal do lado esquerdo e do lado direito, para protocolos de movimento simultâneo dos dois braços.

**Why:** Detecta compensação de um lado pelo outro — um paciente pode "esperar" ou "seguir" o lado saudável, o que não aparece numa comparação de magnitude isolada por lado.

**Context:** Mesma conversa 2026-09-24. Só faz sentido em protocolos bilaterais simultâneos — verificar com a Pamela se o protocolo de flexão de cotovelo prevê isso (ver as 5 perguntas em aberto, `docs/2026-09-03-protocolo-avaliacao-draft.md`).

**Effort:** M
**Priority:** P3
**Depends on:** Approach A (captura real e sincronizada dos dois nós via RTT) — não dá pra validar de verdade sem os dois lados no mesmo timestamp real.

### Movimento compensatório (fora do eixo esperado)

**What:** Detectar aceleração linear ou rotação fora do plano/eixo esperado do cotovelo — sinal de que o paciente está compensando com ombro/tronco em vez de mover a articulação-alvo.

**Why:** Um paciente pode "fingir" ROM completo compensando com outra articulação. Isso invalida a métrica de ROM se não for sinalizado.

**Context:** Mesma conversa 2026-09-24. Mais especulativo que os outros 4 — depende de como o bracelete captura movimento fora do eixo principal (`accel_axes`/`gyro_axis` não usados por `complementary_filter()` hoje).

**Effort:** M
**Priority:** P3
**Depends on:** Dado real (Approach A) pra saber se o ruído fora do eixo é sinal real de compensação ou só ruído de fixação do bracelete no braço.

### Detecção de anomalia via ML

**What:** Um classificador/detector treinado em cima das features já extraídas por `metrics.py` (tremor, ROM, assimetria, fadiga) pra sinalizar padrões fora do esperado, em vez de só threshold fixo.

**Why:** Threshold fixo calibrado em poucas sessões reais tende a ser frágil (overfit ao pequeno N inicial); anomalia aprendida escala melhor conforme mais pacientes passam pelo sistema e a distribuição real de "normal" fica mais clara.

**Context:** Ideia levantada durante a revisão de engenharia do design doc v0 (2026-09-03). Hoje não há dado real suficiente pra treinar nada — Approach A (captura real com a Pamela) ainda não rodou. Quando houver sessões reais suficientes, o ponto de entrada natural é sobre as saídas de `analysis/movesense/metrics.py` (já com 11 testes cobrindo as 4 métricas base). Risco a evitar: construir isso antes de validar as métricas base é o mesmo padrão "plataforma completa antes de validar" que a sessão de office hours já identificou como red flag pro projeto — não puxar essa TODO antes do Approach A gerar dado real.

**Effort:** M
**Priority:** P3
**Depends on:** Approach A rodando com volume real de sessões (design doc: `docs/designs/movesense-v0-wearable-bilateral.md`)
