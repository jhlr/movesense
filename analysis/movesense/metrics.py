"""Métricas extraídas de uma sessão de captura IMU bilateral.

Entrada esperada: DataFrame por lado (LEFT/RIGHT) com colunas
timestamp_ms, ax, ay, az, gx, gy, gz (ver firmware/movesense_node para o formato do pacote).

Este módulo é o esqueleto inicial — cada função abaixo ainda precisa de
validação com dados reais e com o critério clínico da educadora física.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sampling_rate_hz(df: pd.DataFrame) -> float:
    dt_ms = df["timestamp_ms"].diff().median()
    return 1000.0 / dt_ms


def tremor_power(df: pd.DataFrame, band_hz: tuple[float, float] = (3.0, 12.0)) -> float:
    """Potência espectral do giroscópio na banda de tremor (padrão: 3-12Hz)."""
    fs = sampling_rate_hz(df)
    gyro_mag = np.sqrt(df["gx"] ** 2 + df["gy"] ** 2 + df["gz"] ** 2)
    freqs = np.fft.rfftfreq(len(gyro_mag), d=1 / fs)
    spectrum = np.abs(np.fft.rfft(gyro_mag - gyro_mag.mean())) ** 2
    band_mask = (freqs >= band_hz[0]) & (freqs <= band_hz[1])
    return float(spectrum[band_mask].sum())


def peak_angular_velocity(df: pd.DataFrame) -> float:
    gyro_mag = np.sqrt(df["gx"] ** 2 + df["gy"] ** 2 + df["gz"] ** 2)
    return float(gyro_mag.max())


def repetition_count(df: pd.DataFrame, axis: str = "gy", min_prominence: float = 0.5) -> int:
    """Conta repetições via picos no eixo de giroscópio dominante do movimento.

    Placeholder — trocar por detecção de picos real (scipy.signal.find_peaks)
    assim que houver dados de captura para calibrar a prominence/distance.
    """
    raise NotImplementedError("Calibrar detecção de picos com dados reais antes de usar.")


def asymmetry_index(metric_left: float, metric_right: float) -> float:
    """Índice de assimetria simétrico: (L-R) / ((L+R)/2), em %.

    Positivo = lado esquerdo maior; negativo = lado direito maior.
    """
    mean = (metric_left + metric_right) / 2
    if mean == 0:
        return 0.0
    return (metric_left - metric_right) / mean * 100
