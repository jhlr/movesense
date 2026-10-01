"""Teste de integração ponta a ponta: pipeline completo sobre 1 sessão sintética
com bias, tremor e fadiga conhecidos (ver movesense/synthetic.py).

Diferente dos testes unitários em test_metrics.py, aqui nenhuma função é
chamada isolada — o objetivo é confirmar que a composição calibração → fusão
→ as 5 métricas se comporta certo em conjunto, contra valores injetados que
nenhum dataset real disponível oferece (frequência de tremor e taxa de
fadiga conhecidas de antemão).
"""

from __future__ import annotations

import pytest

from movesense.pipeline import analyze_session, bilateral_asymmetry
from movesense.synthetic import generate_elbow_flexion_session

# Mesmo código adaptativo, sessões bem diferentes: se a calibração só
# funcionasse num ponto, a parametrização abaixo pegaria.
SESSION_VARIANTS = [
    {},
    {"tremor_amplitude_deg_s": 8.0, "tremor_freq_hz": 9.0},
    {"base_amplitude_deg": 40.0, "tremor_amplitude_deg_s": 1.0},
    {"base_amplitude_deg": 120.0, "rep_duration_s": 2.5, "n_reps": 6},
    {"rep_duration_s": 1.0, "n_reps": 8, "tremor_freq_hz": 5.0},
]


@pytest.mark.parametrize("variant", SESSION_VARIANTS, ids=lambda v: str(v) or "default")
def test_pipeline_recovers_known_ground_truth(variant):
    df, truth = generate_elbow_flexion_session(**variant)

    result = analyze_session(df, rest_duration_s=truth.rest_duration_s)

    assert result.rom_deg == pytest.approx(truth.base_amplitude_deg, rel=0.1)
    assert result.n_reps == truth.n_reps
    assert result.fatigue_slope < 0, "fadiga foi injetada (amplitude decaindo a cada rep)"

    in_band = analyze_session(
        df,
        rest_duration_s=truth.rest_duration_s,
        tremor_band_hz=(truth.tremor_freq_hz - 1.0, truth.tremor_freq_hz + 1.0),
    ).tremor_power
    out_of_band = analyze_session(
        df, rest_duration_s=truth.rest_duration_s, tremor_band_hz=(20.0, 40.0)
    ).tremor_power
    assert in_band > out_of_band, "tremor devia se concentrar na banda injetada"


def test_pipeline_warmup_window_still_counts_all_reps():
    df, truth = generate_elbow_flexion_session()
    result = analyze_session(df, rest_duration_s=truth.rest_duration_s, warmup_s=6.0)
    assert result.n_reps == truth.n_reps


def test_bilateral_asymmetry_detects_weaker_side():
    left_df, truth = generate_elbow_flexion_session(base_amplitude_deg=90.0)
    right_df, _ = generate_elbow_flexion_session(base_amplitude_deg=60.0)
    left = analyze_session(left_df, rest_duration_s=truth.rest_duration_s)
    right = analyze_session(right_df, rest_duration_s=truth.rest_duration_s)

    assert bilateral_asymmetry(left, right)["rom"] > 0
