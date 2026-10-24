# Desktop Pages & Sub-Pages Reference (Complete)

Every page (tab) and sub-page in the desktop researcher client, its UI
components, and the information source files it reads. Menus and sub-menus
that reach each page are documented in `GUI_MENUS_REFERENCE.md`.

## Main tabs

| Tab | Sub-pages (inner tabs) | Components | Information source files |
| --- | --- | --- | --- |
| Dashboard | — | Stats grid, refresh button, log panel | `GET /api/v1/about`, `/api/v1/health` |
| CL1 Clone | Control Panel, Session, Stimulation, Stim Designer, Recording, Run, Graphics & Charts, Session Info, Information Source Files, Modules | Buttons, spinboxes, forms, tree, canvases, live status strip | `synthetic_brain/cl1_clone.py`, `cl1_simulator.py` |
| Network Simulation | Example, Connectivity Graph, Activity Chart | Run button, `NetworkGraphCanvas`, `ActivityLineCanvas` | `synthetic_brain/network.py`, `network_simulation.py`, `neuron.py`, `synapse.py` |
| BrainScript | — | Code editor, compile/run button | `synthetic_brain/brainlang.py`, `brainscript.py` |
| Projects | — | Table, create form | `GET/POST /api/v1/projects` |
| Experiments | — | Table, create form | `/api/v1/projects/{id}/experiments` |
| Brain Regions | — | Tree of regions | `synthetic_brain/regions/` |
| Telemetry | — | Chart, append form | `/api/v1/experiments/{id}/telemetry` |
| Jobs | — | Table, refresh | `/api/v1/jobs` |
| Servers | — | Table, register form | `/api/v1/servers`, `/api/v1/workers` |

## CL1 Clone sub-pages

| Sub-page | Contents | Source files |
| --- | --- | --- |
| Session | Open/close simulator, neuron count | `cl1_clone.py` (`open`, `Neurons`) |
| Control Panel | 8 primary action buttons, live status strip (session/channels/recording/timestamp) | `Neurons`, `Recording` |
| Stim Designer | Form: channels, amplitude, pulse count, burst frequency, waveform mode; deliver button | `StimDesign`, `BurstDesign`, `ChannelSet` |
| Session Info | Live property tree (session, channels, sample rate, recording counters) + research boundary note | `Neurons.timestamp`, `Recording` |
| Stimulation | Single / burst pulse designers | `StimDesign`, `BurstDesign`, `ChannelSet` |
| Recording | Start/stop, spike list, report | `Recording`, `Spike`, `Stim` |
| Run | Loop controls, tick table | `Neurons.loop`, `Loop`, `LoopTick` |
| Graphics & Charts | Spike Raster, Channel Histogram, Activity Trace canvases | `SpikeRasterCanvas`, `ChannelHistogramCanvas`, `ActivityLineCanvas` |
| Information Source Files | Tree of CL1 docs & code files | `docs/CL1_CLONE_INFORMATION.md` |
| Modules | CL1 module/sub-module map | `cl1_*.py`, `brainlang_cl1.py` |

## Network Simulation sub-pages

| Sub-page | Contents | Source files |
| --- | --- | --- |
| Example | Runs the documented 3-neuron example (seed 42, 10 steps) | `NeuralNetwork`, `NetworkSimulation`, `SimulationConfig` |
| Connectivity Graph | Directed graph, edge color = sign, thickness = \|weight\| | `NetworkGraphCanvas` |
| Activity Chart | Mean population activity per step | `ActivityLineCanvas` |

## Custom canvas widgets

| Widget | File | Purpose |
| --- | --- | --- |
| `NetworkGraphCanvas` | `desktop/python/app.py` | Signed weighted directed-graph rendering. |
| `SpikeRasterCanvas` | `desktop/python/app.py` | Per-channel spike raster over time. |
| `ChannelHistogramCanvas` | `desktop/python/app.py` | Spike counts per channel. |
| `ActivityLineCanvas` | `desktop/python/app.py` | Generic activity/trace line chart. |

## Menus & sub-menus

See `GUI_MENUS_REFERENCE.md` for the full action-level table
(File / CL1 / Simulation / BrainLang / View / Help).
