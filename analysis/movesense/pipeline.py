"""Camada 4 — orquestração: dono único do ciclo sessão -> métricas.

Encadeia calibração de bias -> fusão -> calibração de repetições -> as 5
métricas. As camadas abaixo (`signal`, `reps`, `metrics`) são primitivas
chamadas daqui; quem consome uma sessão chama só `analyze_session`.
"""

from __future__ import annotations

from dataclasses import dataclass

import pandas as pd

from movesense.metrics import (
    asymmetry_index,
    fatigue_slope,
    repetition_count,
    rom,
    tremor_power,
)
from movesense.reps import calibrate_rep_detection
from movesense.signal import (
    apply_gyro_bias_correction,
    complementary_filter,
    estimate_gyro_bias,
    sampling_rate_hz,
)


@dataclass(frozen=True)
class SessionMetrics:
    rom_deg: float
    n_reps: int
    fatigue_slope: float
    tremor_power: float


def analyze_session(
    df: pd.DataFrame,
    rest_duration_s: float,
    warmup_s: float | None = None,
    tremor_band_hz: tuple[float, float] = (3.0, 12.0),
) -> SessionMetrics:
    """Roda o ciclo completo sobre 1 nó.

    `rest_duration_s`: janela inicial com o sensor parado, usada para o bias
    do giroscópio. `warmup_s`: limita a calibração de repetições às primeiras
    N segundos (None = sessão inteira).
    """
    n_rest = int(round(rest_duration_s * sampling_rate_hz(df)))
    bias = estimate_gyro_bias(df.iloc[:n_rest])
    corrected = apply_gyro_bias_correction(df, bias)

    calibration = calibrate_rep_detection(corrected, warmup_s=warmup_s)
    return SessionMetrics(
        rom_deg=rom(complementary_filter(corrected)),
        n_reps=repetition_count(corrected, calibration=calibration),
        fatigue_slope=fatigue_slope(corrected, calibration=calibration),
        tremor_power=tremor_power(corrected, band_hz=tremor_band_hz),
    )


def bilateral_asymmetry(left: SessionMetrics, right: SessionMetrics) -> dict[str, float]:
    """Assimetria (%) por métrica entre os dois lados; positivo = esquerdo maior."""
    return {
        "rom": asymmetry_index(left.rom_deg, right.rom_deg),
        "tremor_power": asymmetry_index(left.tremor_power, right.tremor_power),
    }
