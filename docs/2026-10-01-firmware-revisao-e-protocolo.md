# Revisão do firmware do nó + protocolo de sync (2026-10-01)

Fonte: `firmware/movesense_node/movesense_node.ino` (134 linhas). Não compilado nem testado em hardware nesta revisão — leitura de código apenas. Nenhuma alteração no firmware; abaixo, o que recomendo mudar antes da primeira captura.

## Formato do pacote (spec única, implementada em `analysis/movesense/capture.py`)

`struct ImuSample`, little-endian, packed, **30 bytes** (o design doc dizia 29, corrigido): `uint16 seq_num`, `uint32 timestamp_ms` (millis desde o boot do nó), `float32 ax ay az` (m/s²), `float32 gx gy gz` (**rad/s**). O resto da análise assume gyro em **deg/s**; a conversão acontece só em `capture.py`.

## Achados

1. **Unidade do gyro (rad/s no fio, deg/s na análise).** Sem conversão, `complementary_filter` integraria ~57x menos ângulo. Resolvido na ingestão (testado).
2. **Sem protocolo de sync no firmware.** O design doc lista sync como o maior risco. Hoje o nó só transmite; falta uma característica de ping (ver abaixo). Hub-side pronto em `analysis/movesense/clock_sync.py`.
3. **Jitter de amostragem no `loop()`.** `lastSample = now` perde a fase a cada iteração (período real = 10 ms + latência do loop e do I2C). O timestamp enviado é o `now` real, então a análise não é enganada, mas a taxa efetiva fica < 100 Hz e irregular. Correção sugerida: `lastSample += SAMPLE_PERIOD_MS` (com reset se atrasar mais de 1 período).
4. **`deviceConnected` sem `volatile`.** Escrito no callback BLE, lido no `loop()` (tasks diferentes no ESP32). Marcar `volatile bool`.
5. **Congestionamento de notify.** 2 nós x 100 Hz x 30 B é pouco volume, mas com intervalo de conexão padrão do central (~30 ms) vários pacotes por intervalo competem; `notify()` não checa fila. `seq_num` detecta a perda (`CaptureQuality.n_lost`). Pedir intervalo de conexão curto (7,5-15 ms) no lado do hub.
6. **Resolução de timestamp.** `millis()` = 1 ms, ok para 100 Hz. O sync por RTT tem erro mínimo de ~RTT/2 (alguns ms em BLE) — esse é o piso real do alinhamento bilateral, não o 1 ms do timestamp.
7. **Identidade do nó hardcoded** (`NODE_SIDE`): já registrado como shortcut consciente.
8. Faixas do MPU (8 g, 1000 °/s, filtro 44 Hz) cobrem flexão de cotovelo e a banda de tremor (3-12 Hz).

## Protocolo de sync (a implementar no firmware)

Nova característica `SYNC_CHAR_UUID` (`6e400003-...`) com WRITE_NO_RESPONSE + NOTIFY.

- Hub escreve `[uint16 ping_id]` e anota `hub_send_ms` (relógio monotônico do hub).
- Nó, no callback de escrita, captura `node_rx_ms = millis()` ASSIM QUE recebe (antes de qualquer outra coisa) e responde por notify `[uint16 ping_id, uint32 node_rx_ms]`.
- Hub anota `hub_recv_ms` na chegada do notify e guarda `PingPong(hub_send, node_rx, hub_recv)`.
- Rodar ~100 pings espaçados ao longo da sessão (início, meio e fim: a deriva do cristal é ~dezenas de ppm). `estimate_clock_model` usa os 25% de menor RTT e ajusta offset + deriva; `align_to_hub_clock` leva o `timestamp_ms` de cada nó pro eixo do hub.

Limite assumido: atraso simétrico. Caminho assimétrico enviesa o offset em até RTT/2 e não dá para detectar só com esses dados.
