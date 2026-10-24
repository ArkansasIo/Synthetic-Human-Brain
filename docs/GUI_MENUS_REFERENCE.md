# Desktop GUI Menu & Sub-Menu Reference

Complete map of every menu, sub-menu, and action in the desktop researcher
client (`desktop/python/app.py`), with the source file or handler behind it.

## File

| Action | Shortcut | Handler / source |
| --- | --- | --- |
| Connect to Server… | Ctrl+O | `ResearchClient.change_server` |
| Exit | Ctrl+Q | closes the window |

## CL1

| Sub-menu | Action | Handler | Source |
| --- | --- | --- | --- |
| Session | Open Simulator… | `cl1_open` | `synthetic_brain/cl1_clone.py` (`open`, `Neurons`) |
| Session | Close Session | `cl1_close` | `synthetic_brain/cl1_clone.py` |
| Stimulation | Single Pulse… | `cl1_stim_single` | `StimDesign`, `ChannelSet` |
| Stimulation | Burst… | `cl1_stim_burst` | `StimDesign`, `BurstDesign` |
| Recording | Start Recording | `cl1_record` | `Neurons.record` |
| Recording | Stop Recording | `cl1_stop_recording` | `Recording.stop` |
| Recording | Show Report | `cl1_report` | `Recording.spikes`/`stims` |
| Run | Run Loop… | `cl1_run_loop` | `Neurons.loop`, `Loop`, `LoopTick` |

All CL1 actions are also available as buttons on the CL1 Clone → Control Panel
page, which additionally shows a live status strip (session state, channel
count, recording state, simulator timestamp) and the stim-designer form on the
Stim Designer sub-page.

## Simulation

| Sub-menu | Action | Handler / source |
| --- | --- | --- |
| Core Engine | Run Synthetic Brain Demo | `synthetic_brain/simulation.py` (`Simulation`, `SimulationConfig`) |
| Network | Build Default Network | `synthetic_brain/network.py`, `network_simulation.py` |
| Regions | List Brain Regions | `synthetic_brain/regions/` |
| Graphics & Charts | Show Spike Raster | CL1 → Graphics & Charts sub-page |
| Graphics & Charts | Show Channel Histogram | CL1 → Graphics & Charts sub-page |
| Graphics & Charts | Show Activity Trace | CL1 → Graphics & Charts sub-page |
| Network Simulation | Run Network Example | Network Simulation page (docs/NETWORK_SIMULATION.md) |
| Network Simulation | Show Connectivity Graph | `NetworkGraphCanvas` |
| Network Simulation | Show Activity Chart | `ActivityLineCanvas` |
| Modules | CL1 Module Map | CL1 → Modules sub-page |

## BrainLang

| Action | Handler | Source |
| --- | --- | --- |
| Compile & Run Script | `run_brainscript` | `synthetic_brain/brainlang.py` (`BrainRuntime`) |
| Load Example | `load_example_script` | embedded example |

## View

| Sub-menu | Entries |
| --- | --- |
| CL1 Clone Pages | Session, Stimulation, Recording, Run, Graphics & Charts, Information Source Files, Modules |
| Pages | Dashboard, CL1 Clone, BrainScript, Projects, Experiments, Brain Regions, Telemetry, Jobs, Servers, Network Simulation |

## Help

| Action | Source |
| --- | --- |
| About | embedded message |
| CL1 API Reference | `docs/CL1_CLONE_INFORMATION.md` |
