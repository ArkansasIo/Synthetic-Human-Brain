# Universal 2026 Build System

## Goal

The project uses one source tree and one build specification to produce native artifacts for Windows, macOS, and Linux. A universal build does **not** mean one executable binary can run natively on every operating system; each OS/CPU target receives a native artifact.

## Deliverables

For each supported OS, CI builds:

1. Rust simulation/backend server.
2. Python research API/server package.
3. TypeScript researcher browser bundle.
4. Desktop researcher client package when the desktop UI is enabled.

## Primary targets

| OS | CPU target |
|---|---|
| Windows | x86_64-pc-windows-msvc |
| Windows | aarch64-pc-windows-msvc |
| macOS | x86_64-apple-darwin |
| macOS | aarch64-apple-darwin |
| Linux | x86_64-unknown-linux-gnu |
| Linux | aarch64-unknown-linux-gnu |

Availability of a target depends on the CI runner, compiler toolchain, native SDKs, and hardware/driver stack.

## Runtime layers

```text
Researcher Browser / Desktop Client
             |
          HTTPS/WSS
             |
       Python API Server
             |
       Job / Auth / DB layer
             |
      Rust Worker / Backend
             |
       CPU / GPU / Virtual HW
```

MySQL remains behind the server boundary. Clients never connect directly to the database.

## Build sequence

```text
checkout
  -> Python environment
  -> Rust toolchain
  -> npm install / npm run build
  -> cargo build --release
  -> Python package
  -> artifact assembly
  -> smoke tests
  -> release archive
```

## Hardware strategy

The runtime discovers hardware capabilities instead of assuming a particular GPU. CPU execution is the portable baseline. Accelerator adapters can target CUDA, ROCm, Metal, Vulkan/wgpu, or future backends without changing the research API contract.
