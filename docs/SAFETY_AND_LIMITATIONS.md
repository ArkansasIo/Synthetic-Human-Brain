## Intended use

This is an educational and research-oriented scaffold for abstract neural-system simulations. It does not reproduce a human brain, establish consciousness, diagnose or treat conditions, or validate a brain-computer interface.

## Scientific integrity

- Label simulated, measured, inferred, and hypothetical values distinctly.
- Publish assumptions, parameters, seeds, failures, and limitations.
- Do not claim biological accuracy without defined validation and evidence.
- Use baselines and report uncertainty where appropriate.

## Data protection

Use synthetic data and generated test fixtures by default. Do not commit clinical records, personal information, neural recordings, biometric identifiers, credentials, or private research datasets. Before working with identifiable or human-subject data, obtain appropriate consent, institutional review, security controls, and legal/ethical guidance.

## Security

- Never hard-code tokens or passwords.
- Validate imported configuration and data.
- Avoid executing untrusted serialized objects or downloaded scripts.
- Minimize logs and never log raw sensitive data.
- Review and constrain dependencies.

## Model limitations

Abstract neural simulations may omit cellular diversity, morphology, ion-channel dynamics, synaptic plasticity, glial interactions, biochemical signaling, development, body/environment interaction, and multi-scale organization. Conclusions are limited by the mechanisms represented and the validation performed.

## Reporting language

Prefer: "In this simplified simulation, metric X changed under the documented configuration." Avoid claims that a result proves how the human brain works or that the model is conscious or medically accurate.

## Incident response

If a commit exposes a credential, revoke or rotate it immediately and assess the exposure. Removing a file from the latest commit does not remove it from Git history or existing clones.
