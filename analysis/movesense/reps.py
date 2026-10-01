"""Camada 2 — detecção de repetições: calibração adaptativa + picos.

Dono único de "onde estão as repetições". Depende só de `signal`; as métricas
(camada 3) consomem os picos daqui em vez de detectar por conta própria.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.signal import find_peaks

from movesense.signal import sampling_rate_hz


@dataclass(frozen=True)
class RepCalibration:
    """Parâmetros de detecção de repetições derivados do próprio sinal da sessão."""

    min_prominence: float
    min_distance_samples: int



def calibrate_rep_detection(
    df: pd.DataFrame,
    axis: str = "gy",
    warmup_s: float | None = None,
    prominence_fraction: float = 0.25,
    rep_band_hz: tuple[float, float] = (0.1, 3.0),
) -> RepCalibration:
    """Calibra a detecção de repetições a partir do sinal, sem constantes por paciente/exercício.

    - `min_prominence` = `prominence_fraction` x faixa robusta (p95 - p5) do
      sinal: escala com a amplitude do movimento de quem está fazendo, então
      um tremor pequeno fica abaixo e uma rep fraca (fadiga) fica acima.
    - `min_distance_samples` = meio período da frequência dominante de
      repetição (pico espectral em `rep_band_hz`, bem abaixo da banda de
      tremor de 3-12Hz): mais curto que 1 rep, mais longo que uma ondulação
      de tremor.

    `warmup_s` limita a calibração às primeiras N segundos (uso online: o
    sensor calibra nas primeiras reps e segue); None usa o sinal inteiro.
    Fração 0.25 e banda 0.1-3Hz são defaults de design, ainda sem dado real.
    """
    fs = sampling_rate_hz(df)
    signal = df[axis].to_numpy()
    if warmup_s is not None:
        signal = signal[: int(round(warmup_s * fs))]

    p5, p95 = np.percentile(signal, [5, 95])
    min_prominence = prominence_fraction * float(p95 - p5)

    freqs = np.fft.rfftfreq(len(signal), d=1 / fs)
    spectrum = np.abs(np.fft.rfft(signal - signal.mean())) ** 2
    band = (freqs >= rep_band_hz[0]) & (freqs <= rep_band_hz[1])
    if not band.any() or spectrum[band].max() == 0:
        return RepCalibration(min_prominence, 1)
    rep_freq_hz = float(freqs[band][np.argmax(spectrum[band])])
    min_distance = max(1, int(round(0.5 * fs / rep_freq_hz)))
    return RepCalibration(min_prominence, min_distance)



def rep_peaks(
    signal: np.ndarray,
    min_prominence: float,
    min_distance_samples: int | None,
    calibration: RepCalibration | None,
) -> np.ndarray:
    """Único dono da detecção de picos de repetição; `calibration` tem precedência sobre os fixos."""
    if calibration is not None:
        min_prominence = calibration.min_prominence
        min_distance_samples = calibration.min_distance_samples
    peaks, _ = find_peaks(signal, prominence=min_prominence, distance=min_distance_samples)
    return peaks
