from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from movesense.metrics import (
    asymmetry_index,
    fatigue_slope,
    peak_angular_velocity,
    repetition_count,
    rom,
    tremor_power,
)
from movesense.signal import (
    apply_gyro_bias_correction,
    complementary_filter,
    estimate_gyro_bias,
    gyro_magnitude,
    sampling_rate_hz,
)


def _make_df(timestamps_ms: list[float], gx: list[float], gy: list[float], gz: list[float]) -> pd.DataFrame:
    n = len(timestamps_ms)
    return pd.DataFrame(
        {
            "timestamp_ms": timestamps_ms,
            "ax": np.zeros(n),
            "ay": np.zeros(n),
            "az": np.zeros(n),
            "gx": gx,
            "gy": gy,
            "gz": gz,
        }
    )


def test_sampling_rate_hz_uniform():
    df = _make_df(list(range(0, 1000, 10)), gx=[0] * 100, gy=[0] * 100, gz=[0] * 100)
    assert sampling_rate_hz(df) == pytest.approx(100.0)


def test_sampling_rate_hz_irregular_uses_median():
    # Um gap grande não deve dominar a mediana do intervalo.
    timestamps = [0, 10, 20, 30, 200, 210, 220]
    df = _make_df(timestamps, gx=[0] * 7, gy=[0] * 7, gz=[0] * 7)
    assert sampling_rate_hz(df) == pytest.approx(100.0)


def testgyro_magnitude_happy_path():
    df = _make_df([0, 10], gx=[3.0, 0.0], gy=[4.0, 0.0], gz=[0.0, 5.0])
    result = gyro_magnitude(df)
    assert result.iloc[0] == pytest.approx(5.0)
    assert result.iloc[1] == pytest.approx(5.0)


def test_tremor_power_detects_known_tremor_band():
    fs = 100.0
    n = 500
    t = np.arange(n) / fs
    tremor_freq_hz = 6.0  # dentro da banda padrão 3-12Hz
    signal = np.sin(2 * np.pi * tremor_freq_hz * t)
    df = _make_df((t * 1000).tolist(), gx=signal.tolist(), gy=[0.0] * n, gz=[0.0] * n)
    assert tremor_power(df) > 0


def test_tremor_power_near_zero_without_tremor_component():
    fs = 100.0
    n = 500
    df = _make_df((np.arange(n) / fs * 1000).tolist(), gx=[0.0] * n, gy=[0.0] * n, gz=[0.0] * n)
    assert tremor_power(df) == pytest.approx(0.0, abs=1e-9)


def test_peak_angular_velocity_happy_path():
    df = _make_df([0, 10, 20], gx=[1.0, 3.0, 2.0], gy=[0.0, 0.0, 0.0], gz=[0.0, 0.0, 0.0])
    assert peak_angular_velocity(df) == pytest.approx(3.0)


def test_repetition_count_counts_clear_peaks():
    # 3 picos claros e isolados em gy, separados por zero.
    gy = [0, 5, 0, 0, 5, 0, 0, 5, 0]
    n = len(gy)
    df = _make_df(list(range(0, n * 10, 10)), gx=[0] * n, gy=gy, gz=[0] * n)
    assert repetition_count(df) == 3


def test_repetition_count_ignores_small_wobble_below_prominence():
    # Ruído pequeno não deve contar como repetição com a prominence default.
    gy = [0, 0.1, 0, 0.1, 0]
    n = len(gy)
    df = _make_df(list(range(0, n * 10, 10)), gx=[0] * n, gy=gy, gz=[0] * n)
    assert repetition_count(df) == 0


def test_repetition_count_flat_signal_is_zero():
    df = _make_df([0, 10, 20], gx=[0, 0, 0], gy=[0, 0, 0], gz=[0, 0, 0])
    assert repetition_count(df) == 0


def test_asymmetry_index_left_greater():
    assert asymmetry_index(metric_left=120.0, metric_right=100.0) > 0


def test_asymmetry_index_right_greater():
    assert asymmetry_index(metric_left=100.0, metric_right=120.0) < 0


def test_asymmetry_index_equal_is_zero():
    assert asymmetry_index(metric_left=100.0, metric_right=100.0) == pytest.approx(0.0)


def test_asymmetry_index_both_zero_returns_zero():
    assert asymmetry_index(metric_left=0.0, metric_right=0.0) == 0.0


def test_estimate_gyro_bias_recovers_known_offset():
    rng = np.random.default_rng(seed=0)
    n = 500
    noise = rng.normal(scale=0.01, size=n)
    df = _make_df(
        list(range(0, n * 10, 10)),
        gx=(1.5 + noise).tolist(),
        gy=(-0.3 + noise).tolist(),
        gz=(0.0 + noise).tolist(),
    )
    bias_x, bias_y, bias_z = estimate_gyro_bias(df)
    assert bias_x == pytest.approx(1.5, abs=0.01)
    assert bias_y == pytest.approx(-0.3, abs=0.01)
    assert bias_z == pytest.approx(0.0, abs=0.01)


def test_apply_gyro_bias_correction_subtracts_bias():
    df = _make_df([0, 10, 20], gx=[1.5, 1.6, 1.4], gy=[-0.3, -0.2, -0.4], gz=[0.1, 0.0, -0.1])
    corrected = apply_gyro_bias_correction(df, bias=(1.5, -0.3, 0.0))
    assert corrected["gx"].tolist() == pytest.approx([0.0, 0.1, -0.1])
    assert corrected["gy"].tolist() == pytest.approx([0.0, 0.1, -0.1])
    assert corrected["gz"].tolist() == pytest.approx([0.1, 0.0, -0.1])


def test_apply_gyro_bias_correction_does_not_mutate_input():
    df = _make_df([0, 10], gx=[1.5, 1.6], gy=[0.0, 0.0], gz=[0.0, 0.0])
    original_gx = df["gx"].copy()
    apply_gyro_bias_correction(df, bias=(1.5, 0.0, 0.0))
    assert df["gx"].tolist() == original_gx.tolist()


def test_complementary_filter_static_holds_accel_angle():
    # Sensor parado a 45 graus (ax=az=1) e gyro sem rotação: o ângulo fundido
    # não deve derivar, deve ficar em 45 o tempo todo.
    n = 50
    df = _make_df(list(range(0, n * 10, 10)), gx=[0.0] * n, gy=[0.0] * n, gz=[0.0] * n)
    df["ax"] = 1.0
    df["az"] = 1.0
    fused = complementary_filter(df)
    assert fused.tolist() == pytest.approx([45.0] * n, abs=1e-9)


def test_complementary_filter_tracks_known_constant_rotation():
    # Rotação real de 0 a 90 graus em 1s a taxa constante de 90 deg/s,
    # com o accel consistente com a mesma trajetória (sem ruído).
    n = 100
    timestamps = list(range(0, n * 10, 10))
    rate_deg_s = 90.0
    angles_deg = [rate_deg_s * (t / 1000.0) for t in timestamps]
    ax = [np.cos(np.radians(a)) for a in angles_deg]
    az = [np.sin(np.radians(a)) for a in angles_deg]
    df = _make_df(timestamps, gx=[0.0] * n, gy=[rate_deg_s] * n, gz=[0.0] * n)
    df["ax"] = ax
    df["az"] = az
    fused = complementary_filter(df)
    assert fused.iloc[-1] == pytest.approx(angles_deg[-1], abs=1.0)


def test_rom_max_minus_min():
    angle = pd.Series([10.0, 20.0, 95.0, 40.0, 15.0])
    assert rom(angle) == pytest.approx(85.0)


def test_rom_constant_angle_is_zero():
    angle = pd.Series([30.0] * 20)
    assert rom(angle) == pytest.approx(0.0)


def test_fatigue_slope_detects_declining_peaks():
    # 4 picos claros e decrescentes: 10, 8, 6, 4 — fadiga esperada, slope negativo.
    gy = [0, 10, 0, 0, 8, 0, 0, 6, 0, 0, 4, 0]
    n = len(gy)
    df = _make_df(list(range(0, n * 10, 10)), gx=[0] * n, gy=gy, gz=[0] * n)
    assert fatigue_slope(df) == pytest.approx(-2.0)


def test_fatigue_slope_stable_peaks_is_near_zero():
    gy = [0, 10, 0, 0, 10, 0, 0, 10, 0]
    n = len(gy)
    df = _make_df(list(range(0, n * 10, 10)), gx=[0] * n, gy=gy, gz=[0] * n)
    assert fatigue_slope(df) == pytest.approx(0.0, abs=1e-9)


def test_fatigue_slope_nan_with_fewer_than_two_reps():
    gy = [0, 10, 0]
    n = len(gy)
    df = _make_df(list(range(0, n * 10, 10)), gx=[0] * n, gy=gy, gz=[0] * n)
    assert np.isnan(fatigue_slope(df))
