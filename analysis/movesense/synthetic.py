"""Geração de sessões sintéticas de captura IMU para testes de integração.

Não é dado real — serve para validar que o pipeline completo (calibração →
fusão → as 5 métricas) compõe corretamente sobre valores conhecidos, algo que
nenhum dataset real disponível oferece para tremor_power()/fatigue_slope()
(sem ground truth de frequência de tremor ou taxa de fadiga).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class SyntheticSessionGroundTruth:
    n_reps: int
    rest_duration_s: float
    rep_duration_s: float
    base_amplitude_deg: float
    fatigue_decay_per_rep: float
    tremor_freq_hz: float
    gyro_bias: tuple[float, float, float]


def generate_elbow_flexion_session(
    n_reps: int = 5,
    base_amplitude_deg: float = 90.0,
    fatigue_decay_per_rep: float = 0.08,
    tremor_freq_hz: float = 6.0,
    tremor_amplitude_deg_s: float = 3.0,
    gyro_bias: tuple[float, float, float] = (0.4, -0.6, 0.1),
    fs_hz: float = 100.0,
    rep_duration_s: float = 1.5,
    rest_duration_s: float = 2.0,
) -> tuple[pd.DataFrame, SyntheticSessionGroundTruth]:
    """Simula 1 sessão de flexão de cotovelo (1 nó) com bias, tremor e fadiga conhecidos.

    Trajetória: repouso (janela pra calibração de bias) seguido de `n_reps`
    repetições em meio-cosseno (0 -> amplitude -> 0), com a amplitude
    decaindo `fatigue_decay_per_rep` a cada repetição (fadiga real
    injetada, não ruído). Um tremor senoidal de `tremor_freq_hz` é somado à
    taxa angular durante toda a sessão, inclusive no repouso — como um
    tremor essencial real se comportaria.

    Assume rotação em 1 eixo (gy/ax/az) — mesma convenção default de
    `complementary_filter()`.
    """
    dt_s = 1.0 / fs_hz
    n_rest = int(round(rest_duration_s * fs_hz))
    n_per_rep = int(round(rep_duration_s * fs_hz))

    t_local_rep = np.arange(n_per_rep) * dt_s
    omega = 2 * np.pi / rep_duration_s

    theta_segments = [np.zeros(n_rest)]
    theta_dot_segments = [np.zeros(n_rest)]
    for i in range(n_reps):
        amplitude = base_amplitude_deg * (1 - fatigue_decay_per_rep) ** i
        theta_rep = (amplitude / 2) * (1 - np.cos(omega * t_local_rep))
        theta_dot_rep = (amplitude / 2) * omega * np.sin(omega * t_local_rep)
        theta_segments.append(theta_rep)
        theta_dot_segments.append(theta_dot_rep)

    theta_deg = np.concatenate(theta_segments)
    theta_dot_deg_s = np.concatenate(theta_dot_segments)
    n = len(theta_deg)
    t_global_s = np.arange(n) * dt_s

    tremor = tremor_amplitude_deg_s * np.sin(2 * np.pi * tremor_freq_hz * t_global_s)

    bias_x, bias_y, bias_z = gyro_bias
    gx = np.full(n, bias_x)
    gy = theta_dot_deg_s + tremor + bias_y
    gz = np.full(n, bias_z)

    ax = np.cos(np.radians(theta_deg))
    az = np.sin(np.radians(theta_deg))
    ay = np.zeros(n)

    df = pd.DataFrame(
        {
            "timestamp_ms": t_global_s * 1000.0,
            "ax": ax,
            "ay": ay,
            "az": az,
            "gx": gx,
            "gy": gy,
            "gz": gz,
        }
    )
    ground_truth = SyntheticSessionGroundTruth(
        n_reps=n_reps,
        rest_duration_s=rest_duration_s,
        rep_duration_s=rep_duration_s,
        base_amplitude_deg=base_amplitude_deg,
        fatigue_decay_per_rep=fatigue_decay_per_rep,
        tremor_freq_hz=tremor_freq_hz,
        gyro_bias=gyro_bias,
    )
    return df, ground_truth
