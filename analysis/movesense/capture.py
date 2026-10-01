"""Camada 0 — ingestão: pacote BLE do firmware -> DataFrame que o pipeline consome.

Formato do pacote (firmware/movesense_node, struct ImuSample, little-endian,
packed, 30 bytes): uint16 seq_num, uint32 timestamp_ms, 6x float32
(ax, ay, az em m/s^2; gx, gy, gz em rad/s). Esta é a ÚNICA camada que conhece
o formato de fio e as unidades do firmware: o resto do código assume gyro em
deg/s (ver `signal.complementary_filter`), então a conversão rad/s -> deg/s
acontece aqui, uma vez.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass

import numpy as np
import pandas as pd

PACKET_FORMAT = "<HIffffff"
PACKET_SIZE = struct.calcsize(PACKET_FORMAT)  # 30

_SEQ_MODULUS = 1 << 16
_TIMESTAMP_MODULUS = 1 << 32


@dataclass(frozen=True)
class CaptureQuality:
    n_received: int
    n_lost: int  # amostras ausentes inferidas de buracos no seq_num
    n_duplicates_or_reordered: int


def parse_packet(payload: bytes) -> tuple[int, int, float, float, float, float, float, float]:
    """Decodifica 1 notify. Levanta ValueError se o tamanho não for 30 bytes.

    Tamanho diferente é o sintoma do bug de MTU (notify truncado em 20 bytes),
    então falha alto em vez de preencher com zeros.
    """
    if len(payload) != PACKET_SIZE:
        raise ValueError(f"pacote com {len(payload)} bytes, esperado {PACKET_SIZE} (MTU negociado menor que o necessário?)")
    return struct.unpack(PACKET_FORMAT, payload)


def _unwrap(values: np.ndarray, modulus: int) -> np.ndarray:
    """Desfaz o wrap de um contador que reinicia em `modulus`, assumindo passos pequenos."""
    deltas = np.diff(values.astype(np.int64))
    deltas = np.where(deltas < -modulus // 2, deltas + modulus, deltas)
    return np.concatenate([[values[0]], values[0] + np.cumsum(deltas)]).astype(np.int64)


def packets_to_dataframe(payloads: list[bytes]) -> tuple[pd.DataFrame, CaptureQuality]:
    """Converte uma lista de notifies em DataFrame (timestamp_ms, ax..gz) + qualidade da captura.

    gx/gy/gz saem em deg/s. `timestamp_ms` é o relógio do nó (millis desde o
    boot, com wrap de 32 bits desfeito) — NÃO está alinhado entre nós, isso é
    papel de `clock_sync`. `seq_num` desfeito vira coluna `sample_index`, útil
    pra ver onde houve perda.
    """
    if not payloads:
        raise ValueError("nenhum pacote")
    rows = [parse_packet(p) for p in payloads]
    seq, ts, ax, ay, az, gx, gy, gz = (np.array(col) for col in zip(*rows))

    sample_index = _unwrap(seq, _SEQ_MODULUS)
    timestamp_ms = _unwrap(ts, _TIMESTAMP_MODULUS)

    steps = np.diff(sample_index)
    quality = CaptureQuality(
        n_received=len(rows),
        n_lost=int(np.sum(steps[steps > 1] - 1)),
        n_duplicates_or_reordered=int(np.sum(steps <= 0)),
    )

    df = pd.DataFrame(
        {
            "timestamp_ms": timestamp_ms.astype(float),
            "sample_index": sample_index,
            "ax": ax,
            "ay": ay,
            "az": az,
            "gx": np.degrees(gx),
            "gy": np.degrees(gy),
            "gz": np.degrees(gz),
        }
    )
    return df, quality
