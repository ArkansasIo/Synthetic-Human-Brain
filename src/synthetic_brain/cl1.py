"""Cortical Labs CL1 integration boundary.

This module keeps the synthetic-brain simulator independent from the optional
Cortical Labs ``cl`` package while providing a small adapter for experiments
that use a real CL1 or the CL SDK Simulator.

The adapter deliberately does not prescribe biological stimulation parameters.
Experiment-specific stimulation, safety limits, and approvals remain outside
this research library.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from time import time_ns
from typing import Any, Callable, Iterable, Protocol, Sequence


@dataclass(frozen=True, slots=True)
class CL1Spike:
    """Normalized spike event independent of the CL1 Python package."""

    timestamp: int
    channel: int


@dataclass(frozen=True, slots=True)
class CL1Stimulus:
    """Normalized stimulation event independent of the CL1 Python package."""

    timestamp: int
    channel: int
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass(frozen=True, slots=True)
class CL1Tick:
    """A normalized closed-loop tick returned to the synthetic brain."""

    iteration: int
    timestamp: int
    spikes: tuple[CL1Spike, ...]
    stims: tuple[CL1Stimulus, ...]


class CL1Connection(Protocol):
    """Minimal connection contract used by higher-level experiments."""

    def record(self, **kwargs: Any) -> Any: ...

    def loop(self, ticks_per_second: float, **kwargs: Any) -> Iterable[Any]: ...

    def stim(self, channels: Any, stim_design: Any, burst_design: Any = None) -> None: ...


class CL1Bridge:
    """Optional bridge from the synthetic brain to the Cortical Labs CL API.

    The package is imported lazily so installing ``synthetic-brain`` does not
    require CL1 hardware or the proprietary/optional ``cl`` SDK.
    """

    def __init__(self, neurons: CL1Connection, *, simulator: bool = False) -> None:
        self.neurons = neurons
        self.simulator = simulator

    @classmethod
    def open(cls, *, take_control: bool = True, wait_until_recordable: bool = True) -> "CL1Bridge":
        """Open a CL1/SDK connection through ``cl.open()``.

        Raises ``ImportError`` with an actionable message when the CL SDK is
        not installed.
        """
        try:
            import cl  # type: ignore[import-not-found]
        except ImportError as exc:
            raise ImportError(
                "The Cortical Labs CL API is optional. Install the CL SDK on "
                "a development system or run this adapter on a CL1 device."
            ) from exc

        connection = cl.open(
            take_control=take_control,
            wait_until_recordable=wait_until_recordable,
        )
        neurons = connection.__enter__()
        bridge = cls(neurons, simulator=bool(cl.is_simulator()))
        bridge._context = connection
        return bridge

    def close(self) -> None:
        """Close a connection opened by :meth:`open`."""
        context = getattr(self, "_context", None)
        if context is not None:
            context.__exit__(None, None, None)
            self._context = None

    def __enter__(self) -> "CL1Bridge":
        return self

    def __exit__(self, exc_type: Any, exc: Any, tb: Any) -> None:
        self.close()

    def record(self, **kwargs: Any) -> Any:
        """Start a CL1 recording using the underlying SDK arguments."""
        return self.neurons.record(**kwargs)

    def stimulate(self, channels: Any, stim_design: Any, burst_design: Any = None) -> None:
        """Forward an explicitly configured stimulation to the CL API."""
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
        """Run a CL1 closed loop and normalize spike/stim events.

        ``on_tick`` is invoked immediately after normalization, making this a
        convenient boundary for a synthetic-brain controller or experiment.
        """
        ticks: list[CL1Tick] = []
        loop = self.neurons.loop(
            ticks_per_second,
            stop_after_ticks=stop_after_ticks,
            stop_after_seconds=stop_after_seconds,
            **loop_kwargs,
        )
        for raw_tick in loop:
            analysis = raw_tick.analysis
            spikes = tuple(
                CL1Spike(timestamp=int(spike.timestamp), channel=int(spike.channel))
                for spike in analysis.spikes
            )
            stims = tuple(
                CL1Stimulus(
                    timestamp=int(stim.timestamp),
                    channel=int(stim.channel),
                )
                for stim in analysis.stims
            )
            tick = CL1Tick(
                iteration=int(raw_tick.iteration),
                timestamp=int(raw_tick.iteration_timestamp),
                spikes=spikes,
                stims=stims,
            )
            ticks.append(tick)
            if on_tick is not None:
                on_tick(tick)
        return ticks


def cl1_available() -> bool:
    """Return whether the optional CL API can be imported."""
    try:
        import cl  # type: ignore[import-not-found]  # noqa: F401
    except ImportError:
        return False
    return True


def monotonic_event_timestamp() -> int:
    """Return a local nanosecond timestamp for simulator-side event logging."""
    return time_ns()


__all__ = [
    "CL1Bridge",
    "CL1Connection",
    "CL1Spike",
    "CL1Stimulus",
    "CL1Tick",
    "cl1_available",
    "monotonic_event_timestamp",
]
