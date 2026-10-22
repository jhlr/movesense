"""Camada 0 — hub de captura: BLE dos 2 nós -> CSVs alinhados no relógio do hub.

Dono do ciclo de aquisição. Para cada nó: conecta, assina o stream de IMU,
roda pings de sync (rajada no início, periódicos durante, rajada no fim) e,
ao fim, ajusta o modelo de relógio (`clock_sync`) e decodifica os pacotes
(`capture`). Os dois nós saem no MESMO eixo de tempo (o do hub).

`bleak` só é importado ao abrir conexão real, então o resto do pacote e os
testes não dependem dele. Uso:

    python -m movesense.hub --duration 40 --out data/raw/sessao1
"""

from __future__ import annotations

import argparse
import asyncio
import json
import time
from contextlib import AbstractAsyncContextManager
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Callable, Protocol

import pandas as pd

from movesense.capture import CaptureQuality, packets_to_dataframe
from movesense.clock_sync import (
    ClockModel,
    PingPong,
    align_to_hub_clock,
    build_ping,
    estimate_clock_model,
    parse_pong,
)

# UUIDs espelham firmware/movesense_node/movesense_node.ino
IMU_CHAR_UUID = "6e400002-b5a3-f393-e0a9-e50e24dcca9e"
SYNC_CHAR_UUID = "6e400003-b5a3-f393-e0a9-e50e24dcca9e"
SIDES = ("LEFT", "RIGHT")


class GattClient(Protocol):
    """O que o hub usa de um cliente BLE (bleak.BleakClient satisfaz; o teste usa um falso)."""

    async def start_notify(self, uuid: str, callback: Callable[[object, bytearray], None]) -> None: ...
    async def stop_notify(self, uuid: str) -> None: ...
    async def write_gatt_char(self, uuid: str, data: bytes, response: bool = ...) -> None: ...


ClientFactory = Callable[[str], AbstractAsyncContextManager[GattClient]]


@dataclass(frozen=True)
class NodeCapture:
    side: str
    data: pd.DataFrame  # timestamp_ms já no relógio do hub
    quality: CaptureQuality
    clock: ClockModel
    n_pings: int


def hub_now_ms() -> float:
    return time.monotonic() * 1000.0


async def capture_node(
    client: GattClient,
    side: str,
    duration_s: float,
    ping_interval_s: float = 2.0,
    burst_pings: int = 20,
) -> NodeCapture:
    payloads: list[bytes] = []
    sent: dict[int, float] = {}
    pings: list[PingPong] = []

    def on_imu(_: object, payload: bytearray) -> None:
        payloads.append(bytes(payload))

    def on_pong(_: object, payload: bytearray) -> None:
        recv = hub_now_ms()
        ping_id, node_rx_ms = parse_pong(bytes(payload))
        if ping_id in sent:
            pings.append(PingPong(sent.pop(ping_id), float(node_rx_ms), recv))

    next_id = 0

    async def ping() -> None:
        nonlocal next_id
        pid = next_id & 0xFFFF
        next_id += 1
        sent[pid] = hub_now_ms()
        await client.write_gatt_char(SYNC_CHAR_UUID, build_ping(pid), response=False)

    async def burst() -> None:
        for _ in range(burst_pings):
            await ping()
            await asyncio.sleep(0.1)

    await client.start_notify(SYNC_CHAR_UUID, on_pong)
    await client.start_notify(IMU_CHAR_UUID, on_imu)
    try:
        await burst()
        t_end = time.monotonic() + duration_s
        while time.monotonic() < t_end:
            await ping()
            await asyncio.sleep(min(ping_interval_s, max(0.0, t_end - time.monotonic())))
        await burst()
        await asyncio.sleep(0.3)  # deixa os últimos pongs chegarem
    finally:
        await client.stop_notify(IMU_CHAR_UUID)
        await client.stop_notify(SYNC_CHAR_UUID)

    df, quality = packets_to_dataframe(payloads)
    clock = estimate_clock_model(pings)
    return NodeCapture(side, align_to_hub_clock(df, clock), quality, clock, len(pings))


async def capture_session(
    client_factory: ClientFactory,
    duration_s: float,
    sides: tuple[str, ...] = SIDES,
    ping_interval_s: float = 2.0,
    burst_pings: int = 20,
) -> dict[str, NodeCapture]:
    """Conecta nos nós e captura simultaneamente."""

    async def one(side: str) -> NodeCapture:
        async with client_factory(side) as client:
            return await capture_node(client, side, duration_s, ping_interval_s, burst_pings)

    results = await asyncio.gather(*(one(s) for s in sides))
    return {r.side: r for r in results}


def save_session(captures: dict[str, NodeCapture], out_dir: Path) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    summary: dict[str, dict] = {}
    for side, cap in captures.items():
        cap.data.to_csv(out_dir / f"{side}.csv", index=False)
        summary[side] = {
            "quality": asdict(cap.quality),
            "clock": asdict(cap.clock),
            "n_pings": cap.n_pings,
            "n_samples": len(cap.data),
        }
    (out_dir / "session.json").write_text(json.dumps(summary, indent=2))


def ble_client_factory(scan_timeout_s: float = 10.0) -> ClientFactory:
    """Fábrica real: acha 'MoveSense-<LADO>' por nome e devolve um BleakClient."""

    def factory(side: str) -> AbstractAsyncContextManager[GattClient]:
        from bleak import BleakClient, BleakScanner

        class _Connect:
            async def __aenter__(self) -> GattClient:
                name = f"MoveSense-{side}"
                device = await BleakScanner.find_device_by_name(name, timeout=scan_timeout_s)
                if device is None:
                    raise RuntimeError(f"nó {name} não encontrado (ligado? já conectado em outro lugar?)")
                self._client = BleakClient(device)
                await self._client.connect()
                return self._client

            async def __aexit__(self, *exc: object) -> None:
                await self._client.disconnect()

        return _Connect()

    return factory


def main() -> None:
    parser = argparse.ArgumentParser(description="Captura bilateral MoveSense (2 nós BLE)")
    parser.add_argument("--duration", type=float, default=40.0, help="segundos de captura")
    parser.add_argument("--out", type=Path, required=True, help="pasta de saída (ex.: data/raw/sessao1)")
    parser.add_argument("--sides", nargs="+", choices=SIDES, default=list(SIDES))
    args = parser.parse_args()

    print("Braço relaxado e parado nos primeiros 2 s (calibração do giroscópio).")
    captures = asyncio.run(capture_session(ble_client_factory(), args.duration, tuple(args.sides)))
    save_session(captures, args.out)
    for side, cap in captures.items():
        q = cap.quality
        print(
            f"{side}: {q.n_received} amostras, {q.n_lost} perdidas, "
            f"sync {cap.n_pings} pings, RTT mín {cap.clock.min_rtt_ms:.1f} ms, deriva {cap.clock.drift_ppm:.1f} ppm"
        )
    print(f"Salvo em {args.out}")


if __name__ == "__main__":
    main()
