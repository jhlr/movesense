# BOM inicial — MoveSense (por bracelete, x2 para o par bilateral)

| Item | Sugestão | Obs |
|---|---|---|
| MCU | ESP32 devkit (ex.: ESP32-WROOM-32, DevKitC) | BLE + Wi-Fi nativos, GPIO suficiente, barato |
| IMU | MPU6050 (I2C) | 6 eixos (accel+gyro), biblioteca Adafruit madura. MPU9250 se precisar de magnetômetro (heading absoluto) |
| Bateria | LiPo 3.7V 500-1000mAh | Depende de autonomia desejada por sessão de avaliação |
| Carregamento/proteção | Módulo TP4056 com proteção | Simplifica carga via USB |
| Case | Impressão 3D, bracelete ajustável | Ajuste de tensão importa pro sinal (folga = ruído) |
| Fixação do sensor | Velcro/elástico ajustável | Precisa ficar rígido contra o braço, sem deslizar |

## Pontos em aberto para validar
1. MPU6050 vs MPU9250 — se assimetria/ROM não precisar de heading absoluto (norte magnético),
   MPU6050 é suficiente e mais barato/simples.
2. Frequência de amostragem alvo (firmware atual: 100Hz) — suficiente para tremor
   (tremor patológico tipicamente 3-12Hz, fisiológico até ~20Hz; Nyquist pede >=40Hz, 100Hz dá margem).
3. Posição de fixação no braço (punho vs antebraço) muda o que a métrica de "ROM" representa
   fisiologicamente — decisão clínica, não técnica.
