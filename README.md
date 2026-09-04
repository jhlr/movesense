# MoveSense

Wearable bilateral (par de braceletes) com acelerômetro + giroscópio para avaliação física
em fisioterapia e performance esportiva.

## Objetivo

Capturar movimento dos dois braços simultaneamente (bilateral) para extrair, por lado:

- **Amplitude de movimento (ROM)** — ângulo articular estimado por integração/fusão de sensores
- **Tremor** — análise espectral de vibração de alta frequência
- **Aceleração / velocidade** — pico e média por repetição
- **Contagem de repetições** — detecção de ciclos de movimento
- **Posição/orientação** — quaternion/Euler via fusão de sensor (Madgwick/Mahony)

E, cruzando os dois lados: **assimetria trófica** (diferença de amplitude/força entre membros)
e **fadiga muscular** (degradação de velocidade/tremor ao longo de uma série).

## Equipe

- João — médico (3 anos clínica, pediatria PS + atenção primária), engenharia de IA, firmware/C/Arduino/sistemas digitais
- Educadora física — protocolo de avaliação, validação clínica das métricas

## Estrutura do repositório

```
firmware/movesense_node/   # firmware ESP32 (leitura IMU + streaming BLE)
hardware/                  # BOM, esquema de fiação, datasheets referenciados
analysis/movesense/        # pipeline Python: processamento de sinal e métricas
data/raw/                  # capturas brutas (gitignored)
data/processed/            # dados processados (gitignored)
docs/                      # decisões, protocolo de avaliação, pesquisa de mercado
```

## Arquitetura (v0)

- **Nó**: ESP32 + IMU (MPU6050/MPU9250 via I2C), um por bracelete (2 nós, esquerdo/direito)
- **Link**: cada nó expõe um serviço BLE (GATT) com stream de IMU; um hub (celular/PC)
  conecta nos dois nós e alinha os timestamps na coleta
- **Análise**: dados brutos → Python (fusão de sensor, features, métricas) → relatório

Decisões e alternativas consideradas em [docs/](docs/).

## Status

Projeto em fase de pesquisa e prototipagem inicial (setup: 2026-09-03).
