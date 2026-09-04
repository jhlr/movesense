from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from movesense.metrics import (
    _gyro_magnitude,
    asymmetry_index,
    peak_angular_velocity,
    repetition_count,
    sampling_rate_hz,
    tremor_power,
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


def test_gyro_magnitude_happy_path():
    df = _make_df([0, 10], gx=[3.0, 0.0], gy=[4.0, 0.0], gz=[0.0, 5.0])
    result = _gyro_magnitude(df)
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


def test_repetition_count_raises_not_implemented():
    df = _make_df([0, 10], gx=[0, 0], gy=[0, 0], gz=[0, 0])
    with pytest.raises(NotImplementedError):
        repetition_count(df)


def test_asymmetry_index_left_greater():
    assert asymmetry_index(metric_left=120.0, metric_right=100.0) > 0


def test_asymmetry_index_right_greater():
    assert asymmetry_index(metric_left=100.0, metric_right=120.0) < 0


def test_asymmetry_index_equal_is_zero():
    assert asymmetry_index(metric_left=100.0, metric_right=100.0) == pytest.approx(0.0)


def test_asymmetry_index_both_zero_returns_zero():
    assert asymmetry_index(metric_left=0.0, metric_right=0.0) == 0.0
