# Approach B — relatório de validação (2026-10-01)

Critério do design doc: "as 5 métricas calculadas corretamente". **Cumprido só no nível sintético.** Nenhuma métrica foi validada contra dado real ou mocap: os datasets candidatos (IEEE DataPort, StrengthSense, Mendeley) ficaram inacessíveis, ver `2026-10-01-datasets-validacao.md`. Validação real passa para o Approach A (captura própria).

Suíte: 36 testes passando (`analysis/tests`). Dado sintético: `generate_elbow_flexion_session`, 5 variantes de sessão (tremor forte, amplitude pequena/grande, rep lenta/rápida).

| Métrica | O que foi verificado (sintético) | O que NÃO foi verificado |
|---|---|---|
| Bias de gyro | Recupera o bias injetado (unitário + integração) | Estabilidade do bias real entre nós/temperatura |
| Fusão + ROM | ROM dentro de 10% do injetado; RMSE < 5° contra a trajetória exata | Aceleração linear real (o sintético não tem), montagem real do sensor, mocap |
| Contagem de reps | Contagem exata nas 5 variantes, com calibração adaptativa | Movimento real irregular; limiares (fração 0,25, banda 0,1-3 Hz) são defaults de design sem dado real |
| Fadiga | Sinal do slope (negativo quando fadiga injetada) | Magnitude do slope não foi checada contra o decaimento injetado |
| Tremor | Potência na banda injetada > fora da banda | Frequência e amplitude do tremor não são recuperadas, só comparação relativa de banda |
| Assimetria | Sinal correto (lado mais fraco) com ROM sintético | Qualquer valor clínico; corte de "assimetria significativa" depende da Pamela |

Achado real do processo: tremor sozinho gerava picos falsos em `repetition_count`; só o teste de integração pegou. Limiares fixos falhavam com tremor forte (8 reps contadas em vez de 5), por isso a calibração adaptativa.

Próximo: Approach A (captura com a Pamela). Pré-requisito clínico: as 5 perguntas em aberto de `2026-09-03-protocolo-avaliacao-draft.md` (degrau 11).
