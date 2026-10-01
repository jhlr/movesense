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

from movesense.metrics import (
    apply_gyro_bias_correction,
    complementary_filter,
    estimate_gyro_bias,
    fatigue_slope,
    repetition_count,
    rom,
    tremor_power,
)
from movesense.synthetic import generate_elbow_flexion_session


def test_full_pipeline_recovers_known_ground_truth():
    df, truth = generate_elbow_flexion_session()
    n_rest = int(round(truth.rest_duration_s * 100))
    rest_df = df.iloc[:n_rest]

    bias = estimate_gyro_bias(rest_df)
    corrected = apply_gyro_bias_correction(df, bias)

    fused = complementary_filter(corrected)
    assert rom(fused) == pytest.approx(truth.base_amplitude_deg, rel=0.1)

    # prominence acima de 2x a amplitude do tremor (2*3=6): o tremor sozinho,
    # oscilando em torno de zero no repouso e nas transições entre reps,
    # produz ondulações com prominence de até ~6 — abaixo disso, cada
    # ondulação vira uma "repetição" falsa (achado real do teste de
    # integração: min_prominence=5.0 sozinho não bastava, ver git log).
    # distância mínima maior que 1 período de tremor (1/6Hz ~= 17 amostras a
    # 100Hz) e menor que a duração de 1 repetição (150 amostras).
    min_prominence = 8.0
    min_distance_samples = 50

    assert (
        repetition_count(corrected, min_prominence=min_prominence, min_distance_samples=min_distance_samples)
        == truth.n_reps
    )

    slope = fatigue_slope(corrected, min_prominence=min_prominence, min_distance_samples=min_distance_samples)
    assert slope < 0, "fadiga foi injetada (amplitude decaindo a cada rep) — slope deveria ser negativo"

    power_in_band = tremor_power(
        corrected, band_hz=(truth.tremor_freq_hz - 1.0, truth.tremor_freq_hz + 1.0)
    )
    power_out_of_band = tremor_power(corrected, band_hz=(20.0, 40.0))
    assert power_in_band > power_out_of_band, "tremor devia se concentrar na banda injetada, não em ruído genérico"
