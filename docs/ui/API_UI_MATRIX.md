# API-to-UI Matrix

| API section | Primary tab | Submenus | Main panels | Primary actions |
|---|---|---|---|---|
| Anatomy | Brain | Overview, regions, atlas | hierarchy, region inspector, metadata | select, inspect, compare |
| Neuron | Brain | models, populations, state | membrane graph, spikes, parameters | stimulate, step, reset |
| Synapse | Brain | receptors, dynamics, plasticity | conductance, weight, delay, history | edit, test, trace |
| Connectivity | Connectome | graph, projections, paths | network graph, adjacency, projections | connect, disconnect, filter |
| Dynamics | Simulation | engines, clocks, schedulers | state plots, event queue, timing | run, pause, step |
| Plasticity | Algorithms | STDP, Hebbian, Oja, BCM, homeostasis | weight history, rule parameters | enable, fit, validate |
| Learning | Cognition | TD, prediction, associative, working memory | traces, errors, values | train, replay, evaluate |
| Sensory | Brain | vision, auditory, somatosensory, olfactory, gustatory | input stream, feature maps, latency | inject, record, decode |
| Motor | Brain | motor, corticospinal, autonomic | output stream, commands, latency | stimulate, trace, export |
| Neuromodulation | Brain | dopamine, serotonin, acetylcholine, norepinephrine, reward | modulator state, diffusion, targets | inject model signal, trace |
| Cognition | Cognition | memory, attention, decision, global state | working state, traces, decisions | inspect, replay, compare |
| CL1 | CL1 | connection, channels, spikes, stimulation, recording, closed loop, analysis, replay | spike raster, channels, loop telemetry | connect, stimulate, record, replay |
| BrainScript | BrainScript | editor, AST, compiler, runtime, console | code editor, AST, diagnostics, variables | compile, run, step |
| Experiments | Experiments | protocols, stimuli, recordings, replay | timeline, metrics, provenance | start, stop, replay, export |
| Data | Data | datasets, schemas, provenance, database | table/grid, metadata, lineage | import, query, export |
| Validation | Tools | unit, regression, simulator, cross-backend, biological | test results, comparisons, reports | run, compare, publish report |
| Telemetry | View | runtime, performance, backend | CPU, memory, event rate, latency | pause, sample, export |

## Standard panel layout

```text
┌─ Section toolbar ───────────────────────────────────────────────────────┐
│ API name │ status │ version │ search │ filter │ settings │             │
├─ Tabs ─────────────────────────────────────────────────────────────────┤
│ Overview │ Model │ State │ Graph │ Metrics │ Experiments │ Logs         │
├──────────────────────────────┬──────────────────────────────────────────┤
│ Primary visualization         │ Inspector                                │
│                              │ parameter/value                          │
│ graph / raster / timeline    │ provenance                               │
│                              │ history                                  │
├──────────────────────────────┴──────────────────────────────────────────┤
│ Events / diagnostics / telemetry                                       │
├─────────────────────────────────────────────────────────────────────────┤
│ Step │ Run │ Pause │ Reset │ Record │ Replay │ Export │ Validate       │
└─────────────────────────────────────────────────────────────────────────┘
```

The matrix is an interface contract for the eventual web client; it does not require every panel to be implemented in the same release.
