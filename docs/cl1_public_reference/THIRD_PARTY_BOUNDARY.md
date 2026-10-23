# CL1 Third-Party Boundary

The project integrates with publicly documented Cortical Labs CL1 concepts through an independent adapter. The external CL SDK Simulator is not copied into this repository.

The public `Cortical-Labs/cl-sdk` repository is licensed CC BY-NC 4.0. Its license permits non-commercial reproduction/adaptation subject to attribution and other conditions. This project therefore keeps the SDK as an external dependency/reference rather than silently merging its source into the Apache-2.0 project codebase.

Public references:

- CL API documentation: https://docs.corticallabs.com/
- Public API documentation repository: https://github.com/Cortical-Labs/cl-api-doc
- Public SDK Simulator repository: https://github.com/Cortical-Labs/cl-sdk

The project-owned compatibility code lives under `src/synthetic_brain/cl1/` and implements project interfaces without copying proprietary firmware or private device implementation.
