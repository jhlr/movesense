from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from movesense.signal import apply_gyro_bias_correction, complementary_filter, estimate_gyro_bias
from movesense.synthetic import generate_elbow_flexion_session
from movesense.validation import segment_angle_deg, validate_angle


def test_segment_angle_recovers_known_angle_in_plane():
    theta = np.radians([0.0, 30.0, 90.0, 135.0])
    proximal = np.zeros((4, 3))
    distal = np.stack([np.cos(theta), np.zeros(4), np.sin(theta)], axis=1) * 0.3
    assert segment_angle_deg(proximal, distal) == pytest.approx([0.0, 30.0, 90.0, 135.0])


def test_segment_angle_uses_requested_plane_axes():
    proximal = np.zeros((1, 3))
    distal = np.array([[0.0, 1.0, 1.0]])
    assert segment_angle_deg(proximal, distal, plane_axes=(1, 2)) == pytest.approx([45.0])


def test_validate_angle_ignores_constant_offset():
    reference = np.linspace(0, 90, 200)
    result = validate_angle(pd.Series(reference + 17.0), reference)
    assert result.rmse_deg == pytest.approx(0.0, abs=1e-9)
    assert result.rom_error_deg == pytest.approx(0.0, abs=1e-9)


def test_validate_angle_reports_rom_underestimate():
    reference = np.linspace(0, 90, 200)
    result = validate_angle(pd.Series(reference * 0.8), reference)
    assert result.rom_error_deg == pytest.approx(-18.0)
    assert result.rmse_deg > 0


def test_validate_angle_rejects_length_mismatch():
    with pytest.raises(ValueError):
        validate_angle(pd.Series(np.zeros(5)), np.zeros(6))


def test_fused_synthetic_angle_matches_its_own_ground_truth_trajectory():
    df, truth = generate_elbow_flexion_session()
    n_rest = int(truth.rest_duration_s * 100)
    corrected = apply_gyro_bias_correction(df, estimate_gyro_bias(df.iloc[:n_rest]))
    fused = complementary_filter(corrected)
    reference = np.degrees(np.arctan2(df["az"], df["ax"]))  # trajetória exata injetada
    result = validate_angle(fused, reference.to_numpy())
    assert result.rmse_deg < 5.0
    assert abs(result.rom_error_deg) < 0.1 * truth.base_amplitude_deg
