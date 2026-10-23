# CL1 File Map

This document maps the public CL1 API learning material into the Synthetic Human Brain architecture without copying third-party implementation.

| Upstream public example | Local project component | Purpose |
|---|---|---|
| `CL-00. Hello, Neurons.ipynb` | `cl1_clone.py` | session and neuron API concepts |
| `CL-01. Detecting and Reacting to Spikes.ipynb` | `cl1_analysis.py`, `cl1.py` | spike observation and event handling |
| `CL-01A...UDP Spike Receiver.ipynb` | future `cl1/transport/` adapter | external event transport boundary |
| `CL-02. Recording.ipynb` | `cl1_recording.py` | recording/provenance model |
| `CL-03. Data Streams.ipynb` | `cl1_data_source.py` | stream abstraction and replay |
| `CL-04. Real-Time Visualisation.ipynb` | future GUI/telemetry layer | live neural activity presentation |
| `CL-05. Reading Raw Data.ipynb` | future raw-data adapter | raw recording ingestion |
| `CL-06. Stimulation.ipynb` | `cl1_clone.py`, stimulation interface | stimulation command abstraction |

## Integration rule

Every upstream concept is translated into a project-owned interface. The translation layer must remain usable without CL1 hardware and must support synthetic simulation and replay.

## Planned package layout

```text
src/synthetic_brain/cl1/
├── __init__.py
├── backend.py
├── session.py
├── neurons.py
├── spikes.py
├── stimulation.py
├── recording.py
├── streams.py
├── transport.py
├── simulator.py
├── replay.py
└── closed_loop.py
```

The existing legacy CL1 modules remain supported during migration. New APIs should depend on the compatibility interfaces rather than importing third-party SDK internals directly.
