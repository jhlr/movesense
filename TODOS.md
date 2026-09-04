# TODOS

## Analysis

### Detecção de anomalia via ML

**What:** Um classificador/detector treinado em cima das features já extraídas por `metrics.py` (tremor, ROM, assimetria, fadiga) pra sinalizar padrões fora do esperado, em vez de só threshold fixo.

**Why:** Threshold fixo calibrado em poucas sessões reais tende a ser frágil (overfit ao pequeno N inicial); anomalia aprendida escala melhor conforme mais pacientes passam pelo sistema e a distribuição real de "normal" fica mais clara.

**Context:** Ideia levantada durante a revisão de engenharia do design doc v0 (2026-09-03). Hoje não há dado real suficiente pra treinar nada — Approach A (captura real com a Pamela) ainda não rodou. Quando houver sessões reais suficientes, o ponto de entrada natural é sobre as saídas de `analysis/movesense/metrics.py` (já com 11 testes cobrindo as 4 métricas base). Risco a evitar: construir isso antes de validar as métricas base é o mesmo padrão "plataforma completa antes de validar" que a sessão de office hours já identificou como red flag pro projeto — não puxar essa TODO antes do Approach A gerar dado real.

**Effort:** M
**Priority:** P3
**Depends on:** Approach A rodando com volume real de sessões (design doc: `docs/designs/movesense-v0-wearable-bilateral.md`)
