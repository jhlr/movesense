from __future__ import annotations

import asyncio
import struct
import time
from contextlib import asynccontextmanager

import numpy as np

from movesense.capture import PACKET_FORMAT
from movesense.clock_sync import PING_FORMAT, PONG_FORMAT
from movesense.hub import IMU_CHAR_UUID, SYNC_CHAR_UUID, capture_session, hub_now_ms, save_session

NODE_OFFSETS_MS = {"LEFT": 50_000.0, "RIGHT": -20_000.0}  # hub - node, conhecido


class FakeNode:
    """Nó simulado: stream de IMU a ~100 Hz e pong com o relógio próprio."""

    def __init__(self, side: str):
        self.side = side
        self.cb: dict[str, object] = {}
        self.task: asyncio.Task | None = None

    def node_ms(self) -> int:
        return int(hub_now_ms() - NODE_OFFSETS_MS[self.side]) & 0xFFFFFFFF

    async def start_notify(self, uuid, callback):
        self.cb[uuid] = callback
        if uuid == IMU_CHAR_UUID:
            self.task = asyncio.create_task(self._stream())

    async def _stream(self):
        seq = 0
        while True:
            pkt = struct.pack(PACKET_FORMAT, seq & 0xFFFF, self.node_ms(), 0.0, 0.0, 9.8, 0.0, 0.0, 0.0)
            self.cb[IMU_CHAR_UUID](None, bytearray(pkt))
            seq += 1
            await asyncio.sleep(0.01)

    async def stop_notify(self, uuid):
        if uuid == IMU_CHAR_UUID and self.task:
            self.task.cancel()

    async def write_gatt_char(self, uuid, data, response=False):
        assert uuid == SYNC_CHAR_UUID
        (ping_id,) = struct.unpack(PING_FORMAT, data)
        rx = self.node_ms()
        self.cb[SYNC_CHAR_UUID](None, bytearray(struct.pack(PONG_FORMAT, ping_id, rx)))


def _factory(side):
    @asynccontextmanager
    async def ctx():
        yield FakeNode(side)

    return ctx()


def test_two_nodes_end_to_end_aligned_on_hub_clock(tmp_path):
    t0 = hub_now_ms()
    caps = asyncio.run(capture_session(_factory, duration_s=1.5, ping_interval_s=0.3, burst_pings=6))
    t1 = hub_now_ms()

    assert set(caps) == {"LEFT", "RIGHT"}
    for cap in caps.values():
        assert cap.quality.n_lost == 0 and len(cap.data) > 100
        # alinhado: timestamps caem dentro da janela real do hub, não no relógio do nó
        assert t0 - 50 < cap.data["timestamp_ms"].min() and cap.data["timestamp_ms"].max() < t1 + 50
    # mesmo eixo para os 2 nós: amostras simultâneas diferem de poucos ms
    l, r = caps["LEFT"].data["timestamp_ms"], caps["RIGHT"].data["timestamp_ms"]
    assert abs(l.iloc[len(l) // 2] - r.iloc[len(r) // 2]) < 30

    save_session(caps, tmp_path / "s")
    assert (tmp_path / "s" / "LEFT.csv").exists() and (tmp_path / "s" / "session.json").exists()
