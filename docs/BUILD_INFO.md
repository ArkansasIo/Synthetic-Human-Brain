# Build Information

## Current build

| Field | Value |
|---|---|
| Project name | Synthetic Human Brain |
| Build name | Synthetic Human Brain Research Platform |
| Build version | 0.7.0 |
| Build ID | SHB-20261023-UI01 |
| Developer | ArkansasIo |
| Release channel | research |
| Minimum Python | 3.11 |

## Product identity

This build identifies the repository as a research-oriented software platform for computational neuroscience, synthetic neural-system simulation, BrainScript, and CL1-compatible software interfaces.

The build metadata is exposed programmatically by `synthetic_brain.about` so the browser-style UI, terminal interface, API responses, logs, and About panel can use the same source of truth.

## About panel

The planned UI About panel should display:

1. Project name
2. Build name
3. Version
4. Build ID
5. Developer
6. Release channel
7. Python/runtime compatibility
8. Repository and documentation links
9. Scientific scope and limitations
10. Third-party and CL1 licensing notices

## Terminal/API contract

The metadata object returned by `synthetic_brain.about.about()` is the canonical application metadata shape. Frontends should not duplicate build constants; they should consume this metadata from the backend/API layer.
