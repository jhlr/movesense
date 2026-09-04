# Protocolo de avaliação — rascunho inicial (2026-09-03)

> Rascunho técnico para discussão com a educadora física. Nada aqui é definitivo —
> a validade clínica de cada métrica precisa ser revisada por ela antes de qualquer uso real.

## Métricas propostas e como o firmware/análise as sustenta

| Métrica | Fonte do sinal | Método (planejado) |
|---|---|---|
| Amplitude de movimento (ROM) | Fusão accel+gyro (Madgwick/Mahony) → ângulo articular | Integração de quaternion, corrigida por accel (drift) |
| Tremor | Giroscópio, banda 3-12Hz | Densidade espectral de potência (FFT) |
| Aceleração/velocidade | Acelerômetro/giroscópio brutos | Pico e média por repetição |
| Repetições | Giroscópio no eixo dominante do movimento | Detecção de picos (find_peaks), calibrar com dados reais |
| Posição/orientação | Fusão de sensor | Quaternion → Euler |
| Assimetria trófica | ROM ou amplitude L vs R | Índice de assimetria simétrico (ver `asymmetry_index`) |
| Fadiga muscular | Degradação de velocidade/tremor ao longo de uma série | Slope de pico de velocidade ou aumento de potência de tremor entre reps iniciais e finais |

## Perguntas em aberto (para a educadora física)

1. Quais movimentos/testes específicos entram no protocolo inicial? (ex.: flexão de cotovelo,
   abdução de ombro, rotação de punho — cada um muda o eixo dominante e a fixação do sensor)
2. Qual referência clínica usar para "assimetria significativa" — existe corte padrão na
   literatura de fisioterapia (%) ou isso é caso a caso?
3. Fadiga: o protocolo vai ser "N repetições até falha" ou "tempo fixo"? Isso muda a métrica
   de fadiga (slope por rep vs slope por tempo).
4. Posição de fixação do bracelete (punho vs antebraço) — depende do teste.

## Próximos passos
- Validar este rascunho com a educadora física
- Primeira captura piloto com o firmware atual (`firmware/movesense_node/`) para calibrar
  `repetition_count` e a banda de tremor com dados reais (hoje é placeholder)
