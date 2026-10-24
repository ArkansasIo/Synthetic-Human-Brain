# Desktop Client Pages Reference

Every page (tab) in the desktop researcher client maps to one or more source
files. Pages and sub-pages are reachable from the menu bar
(File / CL1 / Simulation / BrainLang / View / Help) and from the main tab bar.

## Page → source-file map

| Page (tab) | Sub-pages / panels | Information source files |
| --- | --- | --- |
| Dashboard | Server status | `server/python/app/main.py`, `src/synthetic_brain/about.py` |
| CL1 Clone | Session, Stimulation, Recording, Run | `src/synthetic_brain/cl1_clone.py`, `src/synthetic_brain/cl1_simulator.py` |
| CL1 Clone → Session | Open / Close simulator | `src/synthetic_brain/cl1_clone.py` (`open`, `CL1Clone`, `Neurons`) |
| CL1 Clone → Stimulation | Single pulse, Burst | `src/synthetic_brain/cl1_clone.py` (`StimDesign`, `BurstDesign`, `ChannelSet`) |
| CL1 Clone → Recording | Start / Stop / Report | `src/synthetic_brain/cl1_clone.py` (`Recording`, `DetectionResult`), `src/synthetic_brain/cl1_analysis.py` |
| CL1 Clone → Run | Loop runner | `src/synthetic_brain/cl1_clone.py` (`Loop`, `LoopTick`) |
| BrainScript | Editor + runtime | `src/synthetic_brain/brainlang.py`, `src/synthetic_brain/brainscript.py`, `src/synthetic_brain/brainlang_cl1.py` |
| Projects | List projects | `server/python/app/main.py` (`/api/v1/projects`), `server/python/app/models.py` |
| Experiments | List experiments | `server/python/app/main.py` (`/api/v1/experiments`), `src/synthetic_brain/cl1_experiment.py` |
| Brain Regions | Cortical lobes | `src/synthetic_brain/regions/` (frontal, parietal, temporal, occipital), `src/synthetic_brain/_regions_core.py` |
| Telemetry | Metrics feed | `server/python/app/telemetry.py`, `server/python/app/main.py` (`/api/v1/telemetry`) |
| Jobs | Job list | `server/python/app/jobs.py`, `server/python/app/job_router.py`, `server/python/app/job_executor.py` |
| Servers | Registered servers/workers | `server/python/app/worker_registry.py`, `src/synthetic_brain/cl1_data_source.py` |

## Menu → action map

- **File** — Connect to Server (`change_server`), Exit.
- **CL1** — Session (Open/Close), Stimulation (Single/Burst), Recording (Start/Stop/Report), Run (Loop). All backed by `cl1_clone.py`.
- **Simulation** — Core Engine demo (`src/synthetic_brain/simulation.py`, `network_simulation.py`), Network (`network.py`), Regions (`regions/`).
- **BrainLang** — Compile & Run, Load Example (`brainlang.py`).
- **View** — focus any page.
- **Help** — About, CL1 API Reference (`docs/CL1_CLONE_INFORMATION.md`).
