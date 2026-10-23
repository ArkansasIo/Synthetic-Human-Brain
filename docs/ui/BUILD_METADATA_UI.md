# Build Metadata UI

The browser-style Synthetic Human Brain interface uses a single metadata contract for the top navigation, About panel, terminal, and backend API.

## Header

The application header should expose:

- **Synthetic Human Brain** — product name
- **Research Platform** — build family
- **v0.7.0** — build version
- **SHB-20261023-UI01** — build ID
- **ArkansasIo** — developer

## About menu

```text
About
├── Product
│   ├── Name
│   ├── Build Name
│   ├── Version
│   └── Build ID
├── Developer
│   └── ArkansasIo
├── Runtime
│   └── Python >= 3.11
├── Research Scope
│   ├── Neural Models
│   ├── Brain Regions
│   ├── BrainScript
│   ├── Simulation
│   └── CL1 Compatibility
├── Documentation
│   ├── Architecture
│   ├── Algorithms
│   ├── API Reference
│   └── Research
└── Legal & Safety
    ├── Licenses
    ├── CL1 Notice
    └── Scientific Limitations
```

## Backend endpoint shape

The future HTTP/API layer should expose the same values under an application metadata endpoint, for example:

```json
{
  "project_name": "Synthetic Human Brain",
  "build_name": "Synthetic Human Brain Research Platform",
  "build_version": "0.7.0",
  "build_id": "SHB-20261023-UI01",
  "developer_name": "ArkansasIo",
  "release_channel": "research",
  "python_min_version": "3.11"
}
```

The example is a contract illustration. The authoritative values live in `src/synthetic_brain/about.py`.
