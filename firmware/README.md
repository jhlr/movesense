# Firmware do nó (ESP32 + MPU6050)

## Fiação (por nó)

| MPU6050 | ESP32 |
|---|---|
| VCC | 3V3 |
| GND | GND |
| SDA | GPIO 21 |
| SCL | GPIO 22 |

AD0 solto ou no GND (endereço 0x68). Pinos configuráveis em `I2C_SDA_PIN` / `I2C_SCL_PIN`.

## Preparar (uma vez)

```bash
arduino-cli core install esp32:esp32
arduino-cli lib install "Adafruit MPU6050"
```

## Gravar (um nó de cada vez)

Descubra a porta com `arduino-cli board list` (algo como `/dev/cu.usbserial-0001`).
O lado é definido na gravação, sem editar código. Pinte "L" ou "R" no bracelete.

```bash
# esquerdo
arduino-cli compile --fqbn esp32:esp32:esp32 firmware/movesense_node --build-property compiler.cpp.extra_flags=-DNODE_SIDE=LEFT
arduino-cli upload  --fqbn esp32:esp32:esp32 -p PORTA firmware/movesense_node

# direito
arduino-cli compile --fqbn esp32:esp32:esp32 firmware/movesense_node --build-property compiler.cpp.extra_flags=-DNODE_SIDE=RIGHT
arduino-cli upload  --fqbn esp32:esp32:esp32 -p PORTA firmware/movesense_node
```

Se o upload travar em "Connecting...", segure o botão BOOT da placa até começar.

## Conferir

```bash
arduino-cli monitor -p PORTA -c baudrate=115200
```

Esperado: `MoveSense node [LEFT] pronto.` e, ao conectar o hub, `MTU negociado: 247 bytes`.
LED piscando rápido = MPU6050 não respondeu (checar SDA/SCL e alimentação).

## Capturar (hub no Mac)

```bash
cd analysis && uv run --extra ble python -m movesense.hub --duration 40 --out ../data/raw/sessao1
```

Braço parado nos primeiros 2 s. Gera `LEFT.csv`, `RIGHT.csv` (relógio do hub) e `session.json`
(amostras perdidas, RTT mínimo, deriva). Pode rodar só um lado com `--sides LEFT`.
No macOS, dê permissão de Bluetooth ao Terminal na primeira execução.

## Estado

Compila para LEFT e RIGHT (85% da flash). **Ainda não testado em hardware**: o hub foi testado
só contra nós simulados.
