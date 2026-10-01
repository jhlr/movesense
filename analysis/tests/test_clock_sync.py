from __future__ import annotations

import numpy as np
import pytest

from movesense.clock_sync import PingPong, align_to_hub_clock, estimate_clock_model

TRUE_OFFSET_MS = 12_345.0
TRUE_DRIFT_PPM = 40.0


def _simulate_pings(n=120, session_s=300.0, seed=0, jitter_ms=12.0, asym_ms=0.0):
    """Nó com offset e deriva conhecidos; atrasos de ida/volta aleatórios com cauda pesada (fila BLE)."""
    rng = np.random.default_rng(seed)
    pings = []
    for hub_t in np.linspace(1000.0, session_s * 1000.0, n):
        d_out = 4.0 + asym_ms + rng.exponential(jitter_ms)
        d_back = 4.0 + rng.exponential(jitter_ms)
        node_at_rx = (hub_t + d_out) - TRUE_OFFSET_MS - TRUE_DRIFT_PPM * 1e-6 * (hub_t - 1000.0)
        pings.append(PingPong(hub_t, node_at_rx, hub_t + d_out + d_back))
    return pings


def test_recovers_known_offset_within_a_few_ms():
    model = estimate_clock_model(_simulate_pings())
    node_t = np.array([5_000.0, 150_000.0, 290_000.0])
    true_hub = node_t + TRUE_OFFSET_MS + TRUE_DRIFT_PPM * 1e-6 * (node_t - 0.0)
    assert np.abs(model.to_hub_ms(node_t) - true_hub).max() < 4.0


def test_estimates_crystal_drift():
    model = estimate_clock_model(_simulate_pings())
    assert model.drift_ppm == pytest.approx(TRUE_DRIFT_PPM, abs=25.0)


def test_low_rtt_selection_beats_using_every_ping():
    pings = _simulate_pings(seed=3)
    selective = estimate_clock_model(pings, keep_fraction=0.25)
    everything = estimate_clock_model(pings, keep_fraction=1.0)
    node_t = np.linspace(5_000.0, 290_000.0, 50)
    true_hub = node_t + TRUE_OFFSET_MS + TRUE_DRIFT_PPM * 1e-6 * node_t

    def err(m):
        return np.abs(m.to_hub_ms(node_t) - true_hub).mean()

    assert err(selective) < err(everything)


def test_asymmetric_path_bias_is_bounded_by_half_rtt():
    # ida 20 ms mais lenta que a volta: viés inevitável do método, até RTT/2
    model = estimate_clock_model(_simulate_pings(asym_ms=20.0))
    node_t = np.array([150_000.0])
    true_hub = node_t + TRUE_OFFSET_MS + TRUE_DRIFT_PPM * 1e-6 * node_t
    assert abs(model.to_hub_ms(node_t)[0] - true_hub[0]) <= model.min_rtt_ms / 2 + 4.0


def test_two_nodes_land_on_the_same_axis():
    import pandas as pd

    # 2 nós com relógios diferentes (hub = node + offset) lendo o MESMO instante físico do hub
    instant_hub_ms = 20_000.0
    offset_a, offset_b = 5_000.0, 12_000.0

    def pings_for(offset):
        # atraso simétrico de 2 ms em cada sentido
        return [PingPong(t, t + 2.0 - offset, t + 4.0) for t in np.linspace(0, 60_000, 30)]

    node_a = pd.DataFrame({"timestamp_ms": [instant_hub_ms - offset_a]})
    node_b = pd.DataFrame({"timestamp_ms": [instant_hub_ms - offset_b]})
    a = align_to_hub_clock(node_a, estimate_clock_model(pings_for(offset_a)))["timestamp_ms"].iloc[0]
    b = align_to_hub_clock(node_b, estimate_clock_model(pings_for(offset_b)))["timestamp_ms"].iloc[0]
    assert a == pytest.approx(instant_hub_ms, abs=1.0)
    assert b == pytest.approx(instant_hub_ms, abs=1.0)


def test_needs_at_least_two_pings():
    with pytest.raises(ValueError):
        estimate_clock_model([PingPong(0.0, 0.0, 4.0)])
