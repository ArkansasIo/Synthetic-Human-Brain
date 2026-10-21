## Purpose

Define a repeatable record for computational experiments. A software simulation is not automatically evidence about a biological brain.

## Required experiment record

Record the experiment ID, hypothesis, source revision, all parameters, random seed, runtime and dependency versions, procedure, metric definitions and units, results (including null/failed runs), and known limitations.

## Suggested workflow

1. State a testable question and expected outcome.
2. Define a baseline and metrics before execution.
3. Validate the configuration and edge conditions.
4. Run a small pilot.
5. Repeat stochastic trials with predeclared seeds when useful.
6. Report variability, failures, and results not matching expectations.
7. Compare with an analytical or established baseline where possible.
8. Save configuration and provenance with generated outputs.

## Reproducibility checklist

- [ ] Code revision recorded.
- [ ] Parameters and defaults explicit.
- [ ] Seeds recorded and used by the implementation.
- [ ] Metrics and output schema documented.
- [ ] Independent repeat attempted.
- [ ] Edge cases tested.
- [ ] Conclusions distinguish simulation from biological evidence.

## Example template

```yaml
experiment_id: EX-0001
question: "Does parameter A change metric B in this abstract network?"
model_revision: "<git-commit-sha>"
seed: 12345
configuration:
  parameter_a: 0.1
metrics:
  - name: metric_b
    definition: "Specify calculation and units"
results_file: "results/EX-0001.json"
limitations:
  - "Abstract simulation; not a biophysical model"
```

The template values are illustrative. A successful test demonstrates behavior under tested conditions; it does not establish biological fidelity, cognition, consciousness, or clinical utility.
