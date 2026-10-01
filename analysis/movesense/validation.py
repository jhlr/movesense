"""Camada 5 — validação contra ground truth externo (mocap).

Converte marcadores ópticos (VICON) em ângulo articular de referência e mede
o erro do ângulo fundido pelo pipeline contra ele. Independente de dataset:
cada loader (por dataset) entrega marcadores e ângulo já na mesma taxa de
amostragem; o alinhamento temporal fica no loader, não aqui.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from movesense.metrics import rom


def segment_angle_deg(
    proximal: np.ndarray,
    distal: np.ndarray,
    plane_axes: tuple[int, int] = (0, 2),
) -> np.ndarray:
    """Ângulo (graus) do segmento proximal->distal projetado num plano de movimento.

    `proximal`/`distal`: (n, 3) posições dos marcadores (ex: ombro e cotovelo
    para o braço). `plane_axes`: índices das 2 coordenadas do plano do
    movimento, na ordem (x, y) do `arctan2(y, x)` — mesma convenção de
    `complementary_filter` (`accel_axes`), para que fusão e referência sejam
    comparáveis. Escolher o plano certo depende do exercício e do referencial
    do VICON (ver README do dataset).
    """
    segment = np.asarray(distal, dtype=float) - np.asarray(proximal, dtype=float)
    x_axis, y_axis = plane_axes
    return np.degrees(np.arctan2(segment[:, y_axis], segment[:, x_axis]))


@dataclass(frozen=True)
class AngleValidation:
    rmse_deg: float
    rom_error_deg: float


def validate_angle(fused_deg: pd.Series, reference_deg: np.ndarray) -> AngleValidation:
    """Erro do ângulo fundido contra a referência de mocap (mesma taxa, mesmo comprimento).

    O zero do IMU e o do referencial do VICON diferem, então o RMSE é medido
    depois de remover o offset médio entre as séries (erro de forma, não de
    zero). `rom_error_deg` = ROM fundido - ROM de referência, já invariante a
    offset; é o erro que importa clinicamente.
    """
    fused = np.asarray(fused_deg, dtype=float)
    reference = np.asarray(reference_deg, dtype=float)
    if fused.shape != reference.shape:
        raise ValueError(f"séries com tamanhos diferentes: {fused.shape} vs {reference.shape}")
    residual = fused - reference
    residual = residual - residual.mean()
    return AngleValidation(
        rmse_deg=float(np.sqrt(np.mean(residual**2))),
        rom_error_deg=rom(pd.Series(fused)) - rom(pd.Series(reference)),
    )
