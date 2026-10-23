# CL1 Public Reference Layer

This folder records the public Cortical Labs CL1 API/documentation structure used to design the Synthetic Human Brain integration.

## Source boundary

The project does **not** copy proprietary Cortical Labs implementation, firmware, hardware design files, or private SDK internals. Instead, it maintains an independent compatibility layer based on publicly documented application concepts.

The public reference repository is `Cortical-Labs/cl-api-doc` and currently documents example workflows for:

- Hello, Neurons
- detecting and reacting to spikes
- recording
- data streams
- real-time visualisation
- reading raw data
- stimulation

The source repository README describes these materials as a pre-release CL API documentation set. Preserve the upstream copyright and licensing terms for any third-party material that is separately incorporated; this project does not relicence it as project-owned material.

## Local compatibility mapping

| Public concept | Synthetic Human Brain abstraction |
|---|---|
| Neurons/session | `synthetic_brain.cl1_clone.Neurons` |
| Spike events | `Spike` / `CL1Spike` |
| Stimulation events | `Stim` / `CL1Stimulus` |
| Closed-loop ticks | `LoopTick` / `CL1Tick` |
| Recording | `Recording` / recording adapters |
| Data stream | replay/data-source interfaces |
| Simulator | `cl1_simulator.py` / `cl1_clone.py` |

## Documentation snapshots

The repository should contain project-authored explanations under `docs/cl1_public_reference/`, while links to the upstream public documentation remain the authoritative source for Cortical Labs API behavior.

## References

- Cortical Labs public API documentation repository: https://github.com/Cortical-Labs/cl-api-doc
- Cortical Labs developer documentation: https://docs.corticallabs.com/

## Safety and scientific boundary

This compatibility layer is for software development, simulation, replay, analysis, and controlled research integration. It is not a clinical interface and does not establish biological equivalence between CL1 neural cultures and a human brain.
