"""Camada 1 — condicionamento de sinal: primitivas sem conhecimento de exercício ou clínica.

Entrada: DataFrame por lado (LEFT/RIGHT) com colunas timestamp_ms, ax, ay, az,
gx, gy, gz (ver firmware/movesense_node para o formato do pacote). Saída:
sinais limpos (gyro sem bias, ângulo articular fundido) para as camadas acima.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def sampling_rate_hz(df: pd.DataFrame) -> float:
    dt_ms = df["timestamp_ms"].diff().median()
    return 1000.0 / dt_ms



def gyro_magnitude(df: pd.DataFrame) -> pd.Series:
    return np.sqrt(df["gx"] ** 2 + df["gy"] ** 2 + df["gz"] ** 2)



def estimate_gyro_bias(df: pd.DataFrame) -> tuple[float, float, float]:
    """Offset médio de gx, gy, gz sobre um trecho onde o sensor está parado."""
    return (
        float(df["gx"].mean()),
        float(df["gy"].mean()),
        float(df["gz"].mean()),
    )



def apply_gyro_bias_correction(df: pd.DataFrame, bias: tuple[float, float, float]) -> pd.DataFrame:
    """Subtrai o bias (de estimate_gyro_bias) de gx, gy, gz. Não modifica df in-place."""
    bias_x, bias_y, bias_z = bias
    corrected = df.copy()
    corrected["gx"] = corrected["gx"] - bias_x
    corrected["gy"] = corrected["gy"] - bias_y
    corrected["gz"] = corrected["gz"] - bias_z
    return corrected



def complementary_filter(
    df: pd.DataFrame,
    gyro_axis: str = "gy",
    accel_axes: tuple[str, str] = ("ax", "az"),
    alpha: float = 0.98,
) -> pd.Series:
    """Funde accel+gyro num ângulo articular (graus) via filtro complementar.

    1 grau de liberdade — assume o movimento acontece no plano definido por
    `accel_axes` e a taxa de rotação correspondente está em `gyro_axis`
    (deg/s). `alpha` pesa a confiança no giroscópio integrado (curto prazo,
    livre de gravidade mas deriva) contra o ângulo do acelerômetro (absoluto,
    mas ruidoso/sensível a aceleração linear). Default 0.98 é o valor clássico
    de Mahony/Madgwick simplificado — ainda não calibrado com dado real.

    Requer `apply_gyro_bias_correction` já aplicado — sem isso o termo
    integrado do giroscópio acumula deriva do próprio offset de hardware.
    """
    dt_s = df["timestamp_ms"].diff().fillna(df["timestamp_ms"].diff().median()) / 1000.0
    accel_x, accel_y = accel_axes
    accel_angle_deg = np.degrees(np.arctan2(df[accel_y], df[accel_x]))
    gyro_rate = df[gyro_axis]

    fused = np.empty(len(df))
    fused[0] = accel_angle_deg.iloc[0]
    for i in range(1, len(df)):
        gyro_angle = fused[i - 1] + gyro_rate.iloc[i] * dt_s.iloc[i]
        fused[i] = alpha * gyro_angle + (1 - alpha) * accel_angle_deg.iloc[i]

    return pd.Series(fused, index=df.index, name="joint_angle_deg")
