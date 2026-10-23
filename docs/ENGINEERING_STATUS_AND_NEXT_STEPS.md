# Synthetic Human Brain — Engineering Status and Next Steps

Updated: 2026-10-23  
Project: ArkansasIo/Synthetic-Human-Brain  
Status: Research prototype; not a complete human-brain simulation.

## Existing implementation

The current repository has substantial foundations:

- Multiple neuron models, including LIF, AdEx, Izhikevich, and Hodgkin–Huxley.
- Conductance and short-term plasticity synapse models.
- Learning and adaptation primitives such as Hebbian/Oja/BCM/STDP-style updates, homeostatic regulation, population dynamics, predictive coding, and simple memory traces.
- A custom BrainLang interpreter and a BrainScript language tree.
- An optional CL1 adapter boundary for recording and closed-loop event normalization.
- A package/test setup and GitHub Actions CI matrix.

These are modeling components, not a validated reproduction of the human brain, consciousness, or clinical neural function.

## Current CI issue

The latest CI run was failing in the lint step for all configured Python versions, and therefore tests and distribution packaging were skipped. The log shows many E701/E702 style violations in the BrainScript lexer and at least a few unused import/variable warnings. Fix lint separately from scientific behavior changes; do not apply unsafe automated fixes without checking the intended runtime semantics.

## Recommended sequence

1. **Restore CI signal.** Format the compact BrainScript lexer statements, remove only verified unused imports/locals, then run Ruff, pytest, and `python -m build` locally and in CI.
2. **Add experiment reproducibility.** Define a versioned JSON experiment configuration with RNG seed, model ID/version, units, time step, initial state, input protocol, and expected outputs.
3. **Make network simulation scalable.** Add sparse connectivity and serialization with schema/version checks; include deterministic replay fixtures and golden-output tests.
4. **Validate scientific models.** Attach model references, parameter units, documented assumptions, numerical stability constraints, and comparisons to published reference traces/summary statistics before claiming biological fidelity.
5. **Harden the CL1 boundary.** Keep the SDK optional; implement simulator/replay tests, recording provenance, safe resource cleanup, and explicit guardrails around stimulation operations. Live experiments require the device-specific protocol and appropriate oversight.
6. **Improve UI and API integration.** Treat UI inputs as untrusted, keep authentication secrets server-side, record audit events, and segregate user/project data by access control.
7. **Release artifacts.** After CI is green, build wheel/sdist, publish checksums and provenance metadata, and create a tagged prerelease. Do not mark a release as validated until tests and packaging pass.

## Validation checklist

- [ ] Ruff passes under supported Python versions.
- [ ] Unit tests pass under Python 3.11, 3.12, and 3.13.
- [ ] Package wheel and source distribution build successfully.
- [ ] Deterministic replay test matches its golden output.
- [ ] Numerical tests cover edge cases and finite/stable values.
- [ ] CL1 adapter simulator/replay integration test passes without physical hardware.
- [ ] Data exports include configuration, seed, software commit, units, and time metadata.
- [ ] Documentation distinguishes synthetic outputs from measured data and inferred states.

## Scientific and safety boundary

This is a research software project. It does not implement or reproduce an entire human brain, establish consciousness, diagnose or treat disease, or constitute a medical-device specification. Neural stimulation and human-subject experiments require device-specific safety procedures, qualified oversight, ethics approvals where applicable, and regulatory compliance.
