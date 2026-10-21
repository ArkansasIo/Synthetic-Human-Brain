# Experiment protocol

Each experiment should record enough information for another researcher to reproduce the run.

## Required metadata

- Experiment identifier and research question
- Code revision / commit SHA
- Model type and version
- Full parameters and units
- Random seed
- Input schedule
- Initialization procedure
- Number of steps and sampling cadence
- Metrics and aggregation rules
- Observations separated from interpretation
- Known limitations and failed runs

## Starter experiments

### A. Deterministic replay

Run twice with the same configuration and seed. Compare every activity snapshot.

**Expected outcome:** both runs match in the same Python/runtime version.

### B. Decay sensitivity

Run configurations with decay values 0.1, 0.5, and 0.9, keeping other parameters constant. Compare trajectories. Ask how this update rule changes short-term smoothing.

### C. External input saturation

Apply positive and negative constant input. Record the first step at which any unit reaches a boundary. Ask how often clipping dominates the dynamics.

## Interpretation rules

A successful software test is not evidence of biological validity. A visually plausible trajectory is not evidence of cognition or consciousness. Claims about biological systems require suitable experimental data, explicit model comparison, and independent review.
