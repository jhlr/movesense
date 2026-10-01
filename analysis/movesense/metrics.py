"""Camada 3 — métricas clínicas: cada função devolve um número interpretável.

Consome sinais condicionados (`signal`) e picos de repetição (`reps`); não
faz calibração nem fusão por conta própria. A orquestração do ciclo completo
fica em `pipeline`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from movesense.reps import RepCalibration, rep_peaks
from movesense.signal import gyro_magnitude, sampling_rate_hz


def rom(joint_angle_deg: pd.Series) -> float:
    """Amplitude de movimento (ROM): max - min do ângulo articular fundido, em graus.

    Recebe a saída de `complementary_filter`, não o DataFrame bruto — ROM só
    faz sentido sobre o ângulo já fundido, não sobre accel/gyro isolados.
    """
    return float(joint_angle_deg.max() - joint_angle_deg.min())



def tremor_power(df: pd.DataFrame, band_hz: tuple[float, float] = (3.0, 12.0)) -> float:
    """Potência espectral do giroscópio na banda de tremor (padrão: 3-12Hz)."""
    fs = sampling_rate_hz(df)
    gyro_mag = gyro_magnitude(df)
    freqs = np.fft.rfftfreq(len(gyro_mag), d=1 / fs)
    spectrum = np.abs(np.fft.rfft(gyro_mag - gyro_mag.mean())) ** 2
    band_mask = (freqs >= band_hz[0]) & (freqs <= band_hz[1])
    return float(spectrum[band_mask].sum())



def peak_angular_velocity(df: pd.DataFrame) -> float:
    return float(gyro_magnitude(df).max())



def repetition_count(
    df: pd.DataFrame,
    axis: str = "gy",
    min_prominence: float = 0.5,
    min_distance_samples: int | None = None,
    calibration: RepCalibration | None = None,
) -> int:
    """Conta repetições via picos no eixo de giroscópio dominante do movimento.

    Cada repetição assume-se produzir um pico positivo dominante em `axis`
    (ex: flexão de cotovelo -> pico de velocidade angular na subida).

    Limiares: passe `calibration` (de `calibrate_rep_detection`) para usar
    limiares adaptativos ao sinal — é o caminho de uso real. Sem ele valem
    `min_prominence`/`min_distance_samples` fixos (0.5 é só um chute inicial,
    útil em teste unitário com sinal controlado). Tremor soma ondulações de
    curto período em cima do pico real; sem distância mínima entre picos cada
    ondulação com prominence suficiente vira repetição falsa.
    """
    peaks = rep_peaks(df[axis].to_numpy(), min_prominence, min_distance_samples, calibration)
    return int(len(peaks))



def fatigue_slope(
    df: pd.DataFrame,
    axis: str = "gy",
    min_prominence: float = 0.5,
    min_distance_samples: int | None = None,
    calibration: RepCalibration | None = None,
) -> float:
    """Degradação do pico de velocidade angular ao longo das repetições.

    Detecta os mesmos picos de `repetition_count` em `axis` (mesma lógica de
    limiares, via `rep_peaks`), pega a altura de cada pico como proxy de
    "esforço daquela repetição", e ajusta uma reta altura-do-pico vs.
    índice-da-repetição. O coeficiente angular é o retorno: negativo = picos
    caindo ao longo da série = fadiga; positivo/zero = sem degradação. NaN se
    houver menos de 2 repetições (reta indefinida).
    """
    signal = df[axis].to_numpy()
    peaks = rep_peaks(signal, min_prominence, min_distance_samples, calibration)
    if len(peaks) < 2:
        return float("nan")
    rep_index = np.arange(len(peaks))
    slope, _intercept = np.polyfit(rep_index, signal[peaks], 1)
    return float(slope)



def asymmetry_index(metric_left: float, metric_right: float) -> float:
    """Índice de assimetria simétrico: (L-R) / ((L+R)/2), em %.

    Positivo = lado esquerdo maior; negativo = lado direito maior.
    Assume metric_left e metric_right não-negativos (ROM, pico de velocidade,
    potência de tremor — todas as métricas atuais são por construção). Com
    valores de sinais opostos somando perto de zero, a fórmula degenera.
    """
    mean = (metric_left + metric_right) / 2
    if mean == 0:
        return 0.0
    return (metric_left - metric_right) / mean * 100
