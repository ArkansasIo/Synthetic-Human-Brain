# Brain Region ↔ CL1 Mapping Contract

CL1 is treated as a neural-substrate interface, not as a one-to-one anatomical replacement for brain regions.

| Brain system | Computational role | CL1-compatible interface |
|---|---|---|
| Cortex | perception, association, planning | spike streams + stimulation |
| Hippocampus | episodic/spatial memory models | recording + replay |
| Amygdala/limbic | salience and affective-state models | event streams |
| Basal ganglia | action selection/reinforcement | closed-loop controller |
| Thalamus | routing/gating | event router |
| Hypothalamus | homeostatic state | state controller |
| Cerebellum | timing/error correction | prediction-error stream |
| Brainstem | arousal/reflex models | state/event gateway |
| Spinal system | reflex/motor pathways | motor event gateway |
| Sensory systems | modality-specific input | stimulus adapter |
| Motor systems | action generation | output adapter |

The same region example can therefore be tested with synthetic simulation, CL1 simulator/replay, or an authorized real CL1 backend without changing its high-level experiment definition.
