"""CL1-Neural-labs protocol bridge for the Python layer.

Mirrors the TypeScript simulator protocol from
``integration/cl1_labs_ts/server.ts`` and ``src/simulation/neuralCulture.ts``
so the Python API server can:

* serve the same ``/_/config`` discovery payload shape,
* validate stim channel lists with the same grounded/reference rules,
* decode/encode the binary ``[min, max, flags]`` frame layout,
* drive the local ``synthetic_brain.cl1_clone`` simulator with the same
  channel semantics.

Constants and behaviour are ported 1:1 from the TypeScript sources; see
``docs/cl1-labs/CL1_LABS_INTEGRATION.md`` for the protocol description.
"""

from __future__ import annotations

import struct
from dataclasses import dataclass, field
from typing import Any

# --- constants (from integration/cl1_labs_ts/src/types/cl1.ts) ---------------

TOTAL_CHANNELS = 64
GROUNDED_CHANNELS = {0, 7, 56, 63}
REFERENCE_CHANNELS = {4}
UV_PER_RAW_ADC = 0.195
FLAG_HAS_SPIKE = 1 << 0
FLAG_HAS_STIM = 1 << 1

FRAME_STRIDE = 3  # min, max, flags per channel — all int16 little-endian
FRAME_BYTES = TOTAL_CHANNELS * FRAME_STRIDE * 2  # 384 bytes


def is_stim_channel(channel: int) -> bool:
    """A stim channel is any channel that is neither grounded nor reference."""
    return channel not in GROUNDED_CHANNELS and channel not in REFERENCE_CHANNELS


def validate_stim_channels(channels: list[int]) -> list[int]:
    """Return the invalid subset of a stim request (mirrors POST /api/stim)."""
    return [ch for ch in channels if not is_stim_channel(ch)]


@dataclass(slots=True)
class StimRequest:
    """Body of ``POST /api/stim`` in the CL1-Neural-labs server."""

    channels: list[int]

    def invalid_channels(self) -> list[int]:
        return validate_stim_channels(self.channels)

    def to_cl1_stim_design(self) -> dict[str, object]:
        """Convert to the synthetic_brain.cl1_clone stim parameters."""
        valid = [ch for ch in self.channels if is_stim_channel(ch)]
        return {
            "channels": sorted(valid),
            "stim_design": (160, -80.0, 160, 80.0),  # ±80 µA biphasic
            "burst_design": (1, 1.0),
        }


# --- binary frame codec -------------------------------------------------------


def encode_frame(payload: list[tuple[int, int, int]]) -> bytes:
    """Encode a per-channel ``(min, max, flags)`` frame the way server.ts does.

    The TS server builds ``new Int16Array(TOTAL_CHANNELS * 3)`` and wraps it
    with ``Buffer.from(payload.buffer)`` — three int16 values per channel,
    native (little-endian) byte order, 384 bytes total.
    """
    values: list[int] = []
    for channel in range(TOTAL_CHANNELS):
        if channel < len(payload):
            minimum, maximum, flags = payload[channel]
        else:
            minimum, maximum, flags = 0, 0, 0
        values.extend(
            (
                max(-32768, min(32767, minimum)),
                max(-32768, min(32767, maximum)),
                flags & 0x7FFF,
            )
        )
    return struct.pack(f"<{FRAME_STRIDE * TOTAL_CHANNELS}h", *values)


def decode_frame(data: bytes) -> list[dict[str, float]]:
    """Decode a binary broadcast frame into per-channel dicts."""
    raw = struct.unpack(f"<{FRAME_STRIDE * TOTAL_CHANNELS}h", data[:FRAME_BYTES])
    frames: list[dict[str, float]] = []
    for channel in range(TOTAL_CHANNELS):
        offset = channel * FRAME_STRIDE
        minimum, maximum, flags = raw[offset], raw[offset + 1], raw[offset + 2]
        frames.append(
            {
                "channel": channel,
                "min_uv": minimum * UV_PER_RAW_ADC,
                "max_uv": maximum * UV_PER_RAW_ADC,
                "has_spike": bool(flags & FLAG_HAS_SPIKE),
                "has_stim": bool(flags & FLAG_HAS_STIM),
            }
        )
    return frames


# --- discovery payload --------------------------------------------------------


@dataclass(slots=True)
class CL1Config:
    """Mirror of the ``GET /_/config`` response."""

    device_id: str = "CL1-SIM-001"
    name: str = "Cortical Labs CL1 Bio-Computer Simulator"
    channel_count: int = TOTAL_CHANNELS
    sampling_frequency: int = 25_000
    overview_url: str = "ws://localhost:3000/_/ws/overview"
    websocket_url: str = "ws://localhost:3000"

    def as_dict(self) -> dict[str, object]:
        return {
            "device_id": self.device_id,
            "name": self.name,
            "channel_count": self.channel_count,
            "sampling_frequency": self.sampling_frequency,
            "overview_url": self.overview_url,
            "websocket_url": self.websocket_url,
        }


@dataclass(slots=True)
class CultureParameters:
    """Port of ``NeuralCultureSimulator.params`` defaults."""

    cell_type: str = "Human iPSC Cortical"
    spontaneous_rate_hz: float = 4.5
    burst_probability: float = 0.18
    burst_synchrony: float = 0.75
    synaptic_plasticity: bool = True
    noise_rms_uv: float = 8.5
    extra: dict[str, float] = field(default_factory=dict)


def bridge_to_cl1_clone(channels: list[int]) -> Any | None:
    """Build a cl1_clone ChannelSet from a CL1-Neural-labs channel list."""
    try:
        from synthetic_brain.cl1_clone import ChannelSet
    except ImportError:  # pragma: no cover
        return None
    valid = [ch for ch in channels if is_stim_channel(ch)]
    return ChannelSet(*valid) if valid else None


__all__ = [
    "TOTAL_CHANNELS",
    "GROUNDED_CHANNELS",
    "REFERENCE_CHANNELS",
    "UV_PER_RAW_ADC",
    "FLAG_HAS_SPIKE",
    "FLAG_HAS_STIM",
    "CL1Config",
    "CultureParameters",
    "StimRequest",
    "decode_frame",
    "encode_frame",
    "is_stim_channel",
    "validate_stim_channels",
    "bridge_to_cl1_clone",
]
