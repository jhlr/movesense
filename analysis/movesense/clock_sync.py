"""Camada 0 — alinhamento de relógio nó <-> hub por ping-pong (RTT).

Protocolo (a implementar no firmware, ver docs/2026-10-01-firmware-revisao-e-protocolo.md):
o hub escreve um ping numa característica do nó no instante `hub_send_ms`; o
nó responde (notify) com o `node_rx_ms` = seu millis() no instante em que
recebeu o ping; o hub registra `hub_recv_ms` na chegada. Assumindo atraso
simétrico, o relógio do nó em `node_rx_ms` equivale ao hub em
(hub_send_ms + hub_recv_ms) / 2, com erro máximo de RTT/2.

Dois nós sincronizados cada um contra o MESMO relógio do hub ficam alinhados
entre si; o erro de cada um soma.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass(frozen=True)
class PingPong:
    hub_send_ms: float
    node_rx_ms: float
    hub_recv_ms: float

    @property
    def rtt_ms(self) -> float:
        return self.hub_recv_ms - self.hub_send_ms

    @property
    def offset_ms(self) -> float:
        """hub_time - node_time estimado por este ping."""
        return (self.hub_send_ms + self.hub_recv_ms) / 2 - self.node_rx_ms


@dataclass(frozen=True)
class ClockModel:
    """hub_time = node_time + offset0_ms + drift_ppm * 1e-6 * (node_time - ref_node_ms)."""

    offset0_ms: float
    drift_ppm: float
    ref_node_ms: float
    min_rtt_ms: float  # incerteza prática: erro típico fica abaixo de min_rtt/2

    def to_hub_ms(self, node_ms: np.ndarray | pd.Series | float) -> np.ndarray | pd.Series | float:
        node = node_ms
        return node + self.offset0_ms + self.drift_ppm * 1e-6 * (node - self.ref_node_ms)


def estimate_clock_model(pings: list[PingPong], keep_fraction: float = 0.25) -> ClockModel:
    """Ajusta offset + deriva do cristal usando só os pings de menor RTT.

    Pings com RTT alto são os que sofreram atraso assimétrico (fila BLE,
    retransmissão), e é esse atraso que vira erro de offset; descartar a
    maioria deles e ajustar uma reta nos restantes dá o offset e a deriva
    (cristal de ESP32 tem dezenas de ppm: ~1 ms por minuto a 20 ppm, que já
    é o tamanho de uma amostra a 100 Hz numa sessão longa).

    Precisa de >= 2 pings; com poucos, a deriva não é estimável e vira 0.
    """
    if len(pings) < 2:
        raise ValueError("preciso de pelo menos 2 pings")
    rtts = np.array([p.rtt_ms for p in pings])
    n_keep = max(2, int(round(keep_fraction * len(pings))))
    best = np.argsort(rtts)[:n_keep]

    node_t = np.array([pings[i].node_rx_ms for i in best])
    offsets = np.array([pings[i].offset_ms for i in best])
    ref = float(node_t.mean())

    if np.ptp(node_t) < 1.0:  # pings agrupados no tempo: deriva não identificável
        return ClockModel(float(offsets.mean()), 0.0, ref, float(rtts.min()))

    slope, intercept = np.polyfit(node_t - ref, offsets, 1)
    return ClockModel(float(intercept), float(slope * 1e6), ref, float(rtts.min()))


def align_to_hub_clock(df: pd.DataFrame, model: ClockModel) -> pd.DataFrame:
    """Devolve cópia de `df` com `timestamp_ms` no relógio do hub (mesmo eixo para os 2 nós)."""
    aligned = df.copy()
    aligned["timestamp_ms"] = model.to_hub_ms(aligned["timestamp_ms"])
    return aligned
