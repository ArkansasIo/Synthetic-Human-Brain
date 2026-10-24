"""Hardware device registry and plugins for the Synthetic Human Brain server.

Each device implements :class:`HardwarePlugin` — a uniform interface the
desktop GUI and web front end query through the server's hardware endpoints.
The registry ships with:

* :class:`Cl1LabsVirtualPlugin` — the CL1-Neural-labs 64-channel simulated
  dish (protocol ported from ``integration/cl1_labs_ts/server.ts``).
* :class:`SerialMEAPlugin` — a real serial-attached MEA/headstage: any device
  presenting a COM/tty port that streams the CL1 binary frame format or a
  newline-delimited JSON stream.
* :class:`KeyboardInputPlugin` — a human-input device for manual events.

Devices are discovered, enabled/disabled, and polled through
``HardwareRegistry``; the server exposes them at ``/api/v1/hardware``.
"""

from __future__ import annotations

import json
import time
from dataclasses import dataclass, field
from typing import Any, Iterator

from synthetic_brain.cl1_labs_bridge import (
    FLAG_HAS_SPIKE,
    FLAG_HAS_STIM,
    FRAME_BYTES,
    TOTAL_CHANNELS,
    UV_PER_RAW_ADC,
    decode_frame,
    is_stim_channel,
)


@dataclass
class HardwareInfo:
    """Description returned to clients for each device."""

    id: str
    name: str
    kind: str  # "virtual" | "serial" | "input"
    channels: int
    connected: bool
    capabilities: dict[str, Any] = field(default_factory=dict)


class HardwareError(Exception):
    pass


class HardwarePlugin:
    """Uniform interface every device plugin implements."""

    id: str = "plugin"
    name: str = "device"
    kind: str = "virtual"

    def connect(self) -> None:
        raise NotImplementedError

    def disconnect(self) -> None:
        raise NotImplementedError

    def is_connected(self) -> bool:
        raise NotImplementedError

    def read(self) -> list[dict[str, Any]]:
        """Return the latest per-channel frame data."""
        raise NotImplementedError

    def stim(self, channels: list[int]) -> None:
        raise NotImplementedError

    def info(self) -> HardwareInfo:
        return HardwareInfo(
            id=self.id,
            name=self.name,
            kind=self.kind,
            channels=TOTAL_CHANNELS,
            connected=self.is_connected(),
            capabilities=self.capabilities(),
        )

    def capabilities(self) -> dict[str, Any]:
        return {}


class Cl1LabsVirtualPlugin(HardwarePlugin):
    """Simulated CL1 dish — same channel map and frame format as server.ts."""

    id = "cl1-labs-virtual"
    name = "CL1-Neural-labs Virtual Dish"
    kind = "virtual"

    def __init__(self) -> None:
        self._connected = False
        self._stim_queue: list[int] = []
        self._last_frame: list[dict[str, Any]] = []

    def connect(self) -> None:
        self._connected = True

    def disconnect(self) -> None:
        self._connected = False

    def is_connected(self) -> bool:
        return self._connected

    def stim(self, channels: list[int]) -> None:
        invalid = [ch for ch in channels if not is_stim_channel(ch)]
        if invalid:
            raise HardwareError(f"invalid stim channels: {invalid}")
        self._stim_queue.extend(channels)

    def read(self) -> list[dict[str, Any]]:
        if not self._connected:
            raise HardwareError(f"device {self.id} not connected")
        stims = self._stim_queue[:TOTAL_CHANNELS]
        self._stim_queue = self._stim_queue[TOTAL_CHANNELS:]
        frames = []
        for channel in range(TOTAL_CHANNELS):
            has_stim = channel in stims
            has_spike = not has_stim and (channel * 7 + time.time_ns() % 97) % 23 == 0
            frames.append(
                {
                    "channel": channel,
                    "min_uv": -80.0 if has_spike else 0.0,
                    "max_uv": 35.0 if has_spike else 0.0,
                    "has_spike": has_spike,
                    "has_stim": has_stim,
                }
            )
        self._last_frame = frames
        return frames

    def capabilities(self) -> dict[str, Any]:
        return {
            "protocol": "cl1-labs-binary-v1",
            "frame_bytes": FRAME_BYTES,
            "uv_per_raw_adc": UV_PER_RAW_ADC,
            "flags": {"spike": FLAG_HAS_SPIKE, "stim": FLAG_HAS_STIM},
        }


class SerialMEAPlugin(HardwarePlugin):
    """Real serial-attached MEA/headstage device.

    Speaks either the CL1 binary frame format or newline-delimited JSON on a
    COM/tty port. Requires the optional ``pyserial`` package; missing
    dependencies surface as :class:`HardwareError` so the GUI can show why.
    """

    id = "serial-mea"
    name = "Serial MEA / Headstage"
    kind = "serial"

    def __init__(self, port: str = "COM3", baudrate: int = 921_600) -> None:
        self.port = port
        self.baudrate = baudrate
        self._serial: Any = None
        self._buffer = b""

    def connect(self) -> None:
        try:
            import serial  # pyserial
        except ImportError as exc:  # pragma: no cover
            raise HardwareError("pyserial not installed — pip install pyserial") from exc
        try:
            self._serial = serial.Serial(self.port, self.baudrate, timeout=0.05)
        except (OSError, ValueError) as exc:
            raise HardwareError(f"cannot open {self.port}: {exc}") from exc

    def disconnect(self) -> None:
        if self._serial is not None:
            self._serial.close()
            self._serial = None

    def is_connected(self) -> bool:
        return self._serial is not None and self._serial.is_open

    def stim(self, channels: list[int]) -> None:
        if not self.is_connected():
            raise HardwareError(f"device {self.id} not connected")
        payload = json.dumps({"action": "stimulate", "channels": channels})
        self._serial.write(payload.encode("utf-8"))

    def read(self) -> list[dict[str, Any]]:
        if not self.is_connected():
            raise HardwareError(f"device {self.id} not connected")
        self._buffer += self._serial.read(FRAME_BYTES)
        # Prefer complete binary frames; fall back to JSON lines.
        while len(self._buffer) >= FRAME_BYTES:
            frame, self._buffer = self._buffer[:FRAME_BYTES], self._buffer[FRAME_BYTES:]
            return decode_frame(frame)
        if b"\n" in self._buffer:
            line, _, rest = self._buffer.partition(b"\n")
            self._buffer = rest
            try:
                data = json.loads(line.decode("utf-8"))
            except ValueError:
                return []
            return data if isinstance(data, list) else [data]
        return []

    def capabilities(self) -> dict[str, Any]:
        return {
            "transport": "serial",
            "port": self.port,
            "baudrate": self.baudrate,
            "frame_format": "cl1-binary-v1 or ndjson",
        }


class KeyboardInputPlugin(HardwarePlugin):
    """Human-input device: manual event markers from the GUI."""

    id = "keyboard-input"
    name = "Manual Event Input"
    kind = "input"

    def __init__(self) -> None:
        self._events: list[dict[str, Any]] = []

    def connect(self) -> None:
        self._events.clear()

    def disconnect(self) -> None:
        pass

    def is_connected(self) -> bool:
        return True

    def push_event(self, label: str) -> None:
        self._events.append({"channel": -1, "label": label, "t": time.time()})

    def read(self) -> list[dict[str, Any]]:
        events, self._events = self._events, []
        return events

    def stim(self, channels: list[int]) -> None:
        raise HardwareError("input device does not support stimulation")


class HardwareRegistry:
    """Owns device plugins; the server's hardware endpoints read from here."""

    def __init__(self) -> None:
        self._plugins: dict[str, HardwarePlugin] = {}
        self.register(Cl1LabsVirtualPlugin())
        self.register(SerialMEAPlugin())
        self.register(KeyboardInputPlugin())

    def register(self, plugin: HardwarePlugin) -> None:
        self._plugins[plugin.id] = plugin

    def get(self, plugin_id: str) -> HardwarePlugin:
        try:
            return self._plugins[plugin_id]
        except KeyError as exc:
            raise HardwareError(f"unknown device: {plugin_id}") from exc

    def list(self) -> list[HardwareInfo]:
        return [plugin.info() for plugin in self._plugins.values()]

    def connect(self, plugin_id: str) -> None:
        self.get(plugin_id).connect()

    def disconnect(self, plugin_id: str) -> None:
        self.get(plugin_id).disconnect()

    def read_all(self) -> Iterator[tuple[str, list[dict[str, Any]]]]:
        for plugin_id, plugin in self._plugins.items():
            if plugin.is_connected():
                try:
                    yield plugin_id, plugin.read()
                except HardwareError:
                    continue

    def stim(self, plugin_id: str, channels: list[int]) -> None:
        self.get(plugin_id).stim(channels)


hardware_registry = HardwareRegistry()


__all__ = [
    "Cl1LabsVirtualPlugin",
    "HardwareError",
    "HardwareInfo",
    "HardwarePlugin",
    "HardwareRegistry",
    "KeyboardInputPlugin",
    "SerialMEAPlugin",
    "hardware_registry",
]
