"""Métricas extraídas de uma sessão de captura IMU bilateral.

Entrada esperada: DataFrame por lado (LEFT/RIGHT) com colunas
timestamp_ms, ax, ay, az, gx, gy, gz (ver firmware/movesense_node para o formato do pacote).

Este módulo é o esqueleto inicial — cada função abaixo ainda precisa de
validação com dados reais e com o critério clínico da educadora física.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.signal import find_peaks


def sampling_rate_hz(df: pd.DataFrame) -> float:
    dt_ms = df["timestamp_ms"].diff().median()
    return 1000.0 / dt_ms


def _gyro_magnitude(df: pd.DataFrame) -> pd.Series:
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


def rom(joint_angle_deg: pd.Series) -> float:
    """Amplitude de movimento (ROM): max - min do ângulo articular fundido, em graus.

    Recebe a saída de `complementary_filter`, não o DataFrame bruto — ROM só
    faz sentido sobre o ângulo já fundido, não sobre accel/gyro isolados.
    """
    return float(joint_angle_deg.max() - joint_angle_deg.min())


def tremor_power(df: pd.DataFrame, band_hz: tuple[float, float] = (3.0, 12.0)) -> float:
    """Potência espectral do giroscópio na banda de tremor (padrão: 3-12Hz)."""
    fs = sampling_rate_hz(df)
    gyro_mag = _gyro_magnitude(df)
    freqs = np.fft.rfftfreq(len(gyro_mag), d=1 / fs)
    spectrum = np.abs(np.fft.rfft(gyro_mag - gyro_mag.mean())) ** 2
    band_mask = (freqs >= band_hz[0]) & (freqs <= band_hz[1])
    return float(spectrum[band_mask].sum())


def peak_angular_velocity(df: pd.DataFrame) -> float:
    return float(_gyro_magnitude(df).max())


def repetition_count(
    df: pd.DataFrame,
    axis: str = "gy",
    min_prominence: float = 0.5,
    min_distance_samples: int | None = None,
) -> int:
    """Conta repetições via picos no eixo de giroscópio dominante do movimento.

    Cada repetição assume-se produzir um pico positivo dominante em `axis`
    (ex: flexão de cotovelo → pico de velocidade angular na subida). Prominence
    ainda não calibrada com dado real — 0.5 é um chute inicial, ajustar assim
    que houver captura real ou dado sintético mais realista que picos isolados.

    `min_distance_samples`: tremor (5-12Hz) soma ondulações de curto período
    em cima do pico real da repetição — sem uma distância mínima entre picos,
    cada ondulação do tremor com prominence suficiente conta como uma
    repetição falsa (achado do teste de integração sintético). Default None
    (sem filtro) mantém o comportamento antigo; passe algo maior que o
    período do tremor esperado e menor que a duração de uma repetição.
    """
    peaks, _ = find_peaks(df[axis].to_numpy(), prominence=min_prominence, distance=min_distance_samples)
    return int(len(peaks))


def fatigue_slope(
    df: pd.DataFrame,
    axis: str = "gy",
    min_prominence: float = 0.5,
    min_distance_samples: int | None = None,
) -> float:
    """Degradação do pico de velocidade angular ao longo das repetições.

    Detecta os mesmos picos de `repetition_count` em `axis` (mesmos parâmetros
    de prominence/distance — ver lá o porquê do `min_distance_samples`), pega
    a altura de cada pico como proxy de "esforço daquela repetição", e ajusta
    uma reta altura-do-pico vs. índice-da-repetição. O coeficiente angular é o
    retorno: negativo = picos caindo ao longo da série = fadiga;
    positivo/zero = sem degradação. NaN se houver menos de 2 repetições (reta
    indefinida).
    """
    signal = df[axis].to_numpy()
    peaks, _ = find_peaks(signal, prominence=min_prominence, distance=min_distance_samples)
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
