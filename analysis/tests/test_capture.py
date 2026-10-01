from __future__ import annotations

import math
import struct

import pytest

from movesense.capture import PACKET_FORMAT, PACKET_SIZE, packets_to_dataframe, parse_packet


def _pkt(seq: int, ts: int, accel=(0.0, 0.0, 9.81), gyro=(0.0, 0.0, 0.0)) -> bytes:
    return struct.pack(PACKET_FORMAT, seq, ts, *accel, *gyro)


def test_packet_is_30_bytes_as_firmware_struct():
    assert PACKET_SIZE == 30


def test_truncated_packet_fails_loudly():
    with pytest.raises(ValueError, match="20 bytes"):
        parse_packet(_pkt(1, 10)[:20])


def test_gyro_converted_from_rad_to_deg_per_s_and_accel_untouched():
    df, _ = packets_to_dataframe([_pkt(0, 0, accel=(1.0, 2.0, 3.0), gyro=(math.pi, 0.0, math.pi / 2))])
    assert df["gx"].iloc[0] == pytest.approx(180.0, rel=1e-5)
    assert df["gz"].iloc[0] == pytest.approx(90.0, rel=1e-5)
    assert df["ay"].iloc[0] == pytest.approx(2.0)


def test_seq_wrap_is_unwrapped_without_reporting_loss():
    df, quality = packets_to_dataframe([_pkt(65534, 0), _pkt(65535, 10), _pkt(0, 20), _pkt(1, 30)])
    assert list(df["sample_index"]) == [65534, 65535, 65536, 65537]
    assert quality.n_lost == 0


def test_gap_in_seq_counts_lost_samples():
    _, quality = packets_to_dataframe([_pkt(0, 0), _pkt(1, 10), _pkt(5, 50), _pkt(6, 60)])
    assert quality.n_lost == 3
    assert quality.n_received == 4


def test_duplicate_or_reordered_packet_is_flagged():
    _, quality = packets_to_dataframe([_pkt(0, 0), _pkt(1, 10), _pkt(1, 10), _pkt(2, 20)])
    assert quality.n_duplicates_or_reordered == 1


def test_timestamp_wrap_32bit_is_unwrapped():
    df, _ = packets_to_dataframe([_pkt(0, 2**32 - 10), _pkt(1, 0)])
    assert df["timestamp_ms"].iloc[1] - df["timestamp_ms"].iloc[0] == pytest.approx(10.0)


def test_parsed_session_feeds_the_pipeline():
    from movesense.pipeline import analyze_session
    from movesense.synthetic import generate_elbow_flexion_session

    synth, truth = generate_elbow_flexion_session()
    payloads = [
        _pkt(
            i % 65536, int(r.timestamp_ms),
            accel=(r.ax * 9.81, r.ay * 9.81, r.az * 9.81),
            gyro=tuple(math.radians(v) for v in (r.gx, r.gy, r.gz)),
        )
        for i, r in enumerate(synth.itertuples())
    ]
    df, quality = packets_to_dataframe(payloads)
    assert quality.n_lost == 0
    result = analyze_session(df, rest_duration_s=truth.rest_duration_s)
    assert result.n_reps == truth.n_reps
