# Development Roadmap

## Phase 1 — Foundation

- [x] Reproducible abstract simulation core
- [x] Configuration validation
- [x] Immutable simulation snapshots
- [x] Automated tests and CI
- [x] Initial architecture and UML documentation
- [x] Weighted graph connectivity primitives

## Phase 2 — Network models

- [ ] Pluggable neuron/population models
- [ ] Configurable synapse models
- [ ] Sparse connectivity representation
- [ ] Network serialization
- [ ] Experiment configuration files
- [ ] Deterministic replay fixtures

## Phase 3 — Research tooling

- [ ] Experiment runner
- [ ] Dataset metadata and provenance records
- [ ] CSV/JSON result export
- [ ] Statistical analysis utilities
- [ ] Reproducible visualization pipeline
- [ ] Benchmark suite

## Phase 4 — Biologically grounded models

- [ ] Explicitly documented neuron dynamics
- [ ] Parameter provenance and units
- [ ] Reference datasets
- [ ] Quantitative validation against published results
- [ ] Model-comparison reports

Biological fidelity should be added only when each model has documented assumptions, evidence, numerical tests, and validation criteria.

## Phase 5 — Advanced research platform

- [ ] Large-scale sparse simulation backend
- [ ] Parallel experiment execution
- [ ] GPU acceleration as an optional backend
- [ ] Interactive network visualization
- [ ] Experiment registry
- [ ] Versioned model specifications

## Non-goals

This roadmap does not target a claim of reproducing a complete human brain, consciousness, subjective experience, or clinical functionality. Those claims require scientific evidence far beyond a software feature checklist.
