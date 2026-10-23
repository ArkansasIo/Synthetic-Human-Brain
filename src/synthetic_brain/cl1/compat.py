from __future__ import annotations

from collections.abc import Callable, Iterable
from dataclasses import dataclass, field
from time import time_ns
from typing import Any, Protocol


@dataclass(frozen=True, slots=True)
class CL1Spike:
    timestamp: int
    channel: int


@dataclass(frozen=True, slots=True)
class CL1Stimulus:
    timestamp: int
    channel: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CL1Tick:
    iteration: int
    timestamp: int
    spikes: tuple[CL1Spike, ...]
    stims: tuple[CL1Stimulus, ...]


class CL1Connection(Protocol):
    def record(self, **kwargs: Any) -> Any: ...
    def loop(self, ticks_per_second: float, **kwargs: Any) -> Iterable[Any]: ...
    def stim(self, channels: Any, stim_design: Any, burst_design: Any = None) -> None: ...


class CL1Bridge:
    def __init__(self, neurons: CL1Connection, *, simulator: bool = False) -> None:
        self.neurons = neurons
        self.simulator = simulator
        self._context: Any = None

    @classmethod
    def open(cls, *, take_control: bool = True, wait_until_recordable: bool = True) -> "CL1Bridge":
        try:
            import cl  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError("The optional Cortical Labs CL API is not installed.") from exc
        connection = cl.open(take_control=take_control, wait_until_recordable=wait_until_recordable)
        neurons = connection.__enter__()
        bridge = cls(neurons, simulator=bool(cl.is_simulator()))
        bridge._context = connection
        return bridge

    def close(self) -> None:
        if self._context is not None:
            self._context.__exit__(None, None, None)
            self._context = None

    def __enter__(self) -> "CL1Bridge":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def record(self, **kwargs: Any) -> Any:
        return self.neurons.record(**kwargs)

    def stimulate(self, channels: Any, stim_design: Any, burst_design: Any = None) -> None:
        self.neurons.stim(channels, stim_design, burst_design)

    def closed_loop(
        self,
        ticks_per_second: float,
        *,
        stop_after_ticks: int | None = None,
        stop_after_seconds: float | None = None,
        on_tick: Callable[[CL1Tick], None] | None = None,
        **loop_kwargs: Any,
    ) -> list[CL1Tick]:
        ticks: list[CL1Tick] = []
        loop = self.neurons.loop(
            ticks_per_second,
            stop_after_ticks=stop_after_ticks,
            stop_after_seconds=stop_after_seconds,
            **loop_kwargs,
        )
        for raw_tick in loop:
            analysis = raw_tick.analysis
            spikes = tuple(CL1Spike(int(spike.timestamp), int(spike.channel)) for spike in analysis.spikes)
            stims = tuple(CL1Stimulus(int(stim.timestamp), int(stim.channel)) for stim in analysis.stims)
            tick = CL1Tick(int(raw_tick.iteration), int(raw_tick.iteration_timestamp), spikes, stims)
            ticks.append(tick)
            if on_tick is not None:
                on_tick(tick)
        return ticks


def cl1_available() -> bool:
    try:
        import cl  # type: ignore[import-not-found]  # noqa: F401
    except ImportError:
        return False
    return True


def monotonic_event_timestamp() -> int:
    return time_ns()
