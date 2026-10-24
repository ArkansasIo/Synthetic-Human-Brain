# CL1 Clone — Information Source Files

Reference index for the source files that back the CL1 clone pages in the
desktop researcher client (`desktop/python/app.py`).

## Primary source files

| Source file | Contents exposed in the UI |
| --- | --- |
| `src/synthetic_brain/cl1_clone.py` | In-process deterministic neural event simulator: `open()`, `CL1Clone`, `Neurons`, `Loop`, `LoopTick`, `Recording`, `DetectionResult`, `Spike`, `Stim`, `StimDesign`, `BurstDesign`, `ChannelSet`, `SAMPLE_RATE_HZ`. |
| `src/synthetic_brain/cl1_simulator.py` | Standalone simulator loop implementation with recording serialization (`format: synthetic-brain-cl1-simulator-v1`). |
| `src/synthetic_brain/cl1.py` | CL1 research adapter surface used by higher-level experiment code. |
| `src/synthetic_brain/cl1_recording.py` | Recording helpers consumed by analysis pages. |
| `src/synthetic_brain/cl1_analysis.py` | Spike/stim analysis routines used by the Recording report page. |
| `src/synthetic_brain/cl1_benchmark.py` | Benchmark scenarios surfaced under Simulation → Core Engine. |
| `src/synthetic_brain/cl1_data_source.py` | Data-source abstractions for importing/exporting CL1 recordings. |
| `src/synthetic_brain/cl1_experiment.py` | Experiment definitions wired to Projects/Experiments pages. |

## API summary (from `cl1_clone.py`)

- `SAMPLE_RATE_HZ = 25_000` — simulator sample rate in Hz.
- `open(channel_count=64, seed=0)` → `CL1Clone` context manager; `__enter__` returns a `Neurons` instance.
- `Neurons.stim(channels, stim_design, burst_design, lead_time_us=80)` — queue stimulation events.
- `Neurons.record(**attributes)` → `Recording` (captures spikes and stims while open).
- `Neurons.loop(ticks_per_second, stop_after_ticks=…, stop_after_seconds=…)` → `Loop` of `LoopTick(iteration, iteration_timestamp, analysis=DetectionResult(spikes, stims), loop)`.
- `Recording.stop()` finalizes the recording; inspect `recording.spikes` and `recording.stims`.

## Research boundary

The CL1 clone is a software simulation for research prototyping. It is not a
biological neural culture, not a Cortical Labs CL1 dish, and not a medical
device. See `LICENSES/CL1_NOTICE.md` and `docs/SAFETY_AND_LIMITATIONS.md`.
