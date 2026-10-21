# Roadmap

This list describes proposed work; an item is not complete merely because it appears here.

## Repository foundation

- [x] Document current scaffold status and scientific boundaries.
- [x] Document architecture, experiment protocol, and development expectations.
- [ ] Add package metadata and a minimal runnable package.
- [ ] Add automated tests and continuous integration.

## Deterministic simulation core

- [ ] Define and validate configuration types.
- [ ] Implement a minimal state container and explicit simulation step.
- [ ] Ensure deterministic behavior for fixed inputs and seeds.
- [ ] Test invalid values and numerical boundaries.

## Experiment runner

- [ ] Add a CLI with clear usage and error messages.
- [ ] Export metrics and provenance to a documented JSON schema.
- [ ] Add parameter sweeps and baseline comparisons.
- [ ] Preserve null and failed runs in experiment reports.

## Analysis and validation

- [ ] Add optional plots with units and provenance.
- [ ] Define use-case-specific validation criteria.
- [ ] Compare against analytical or established computational baselines.
- [ ] Document parameter sensitivity and numerical stability.
- [ ] Require expert review before biological interpretation.

## Release gate

Do not describe the repository as a functioning simulation package until source, packaging metadata, tests, and CI exist and their documented checks pass. No roadmap item implies medical or biological validation.
