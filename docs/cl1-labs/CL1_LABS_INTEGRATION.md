# CL1-Neural-labs — Integrated Front End Reference

Source: https://github.com/ArkansasIo/CL1-Neural-labs.git (React + TypeScript +
Vite + Express + WebSocket). This document maps that repo into the Synthetic
Human Brain project as the primary CL1 front end, both frontend (React UI) and
backend (Node/Express simulator server), and how it connects to the Python
API server and Rust compute layer.

## Component overview

| Layer | Technology | Role |
| --- | --- | --- |
| Front end | React 19 + TypeScript + Vite | CL1 live visualization: 64-channel spike/stim plots, burst analysis, functional connectivity, branching ratio, RC curves. |
| Back end (Node) | Express + ws (`server.ts`) | CL1 protocol simulator: 50 Hz binary chunk broadcast, stim queue, pause/resume, Cortical Labs `/_/config` discovery endpoint. |
| Python API server | FastAPI (`server/python/app/main.py`) | Auth, projects, experiments, jobs, telemetry. Bridges the two stacks. |
| Rust backend | axum server binary | Simulation compute behind `/jobs` and `/step`. |

## CL1 simulator protocol (`server.ts`)

- 64 channels; grounded channels `[0, 7, 56, 63]`; reference channel `[4]`.
- Binary frame layout per channel: `[min, max, flags]` as int16/int8 triples
  (`FLAG_HAS_SPIKE = 1<<0`, `FLAG_HAS_STIM = 1<<1`), raw ADC units scaled by
  `UV_PER_RAW_ADC = 0.195`.
- Broadcast loop at 50 Hz (20 ms); spontaneous spikes via Poisson draw (p=0.05).
- WebSocket actions from clients: `stimulate` (channel), `reset`, `pause`, `resume`.
- REST: `GET /_/config` (Cortical Labs discovery), `GET /api/build`,
  `GET /api/status`, `POST /api/stim` (validates channel list, rejects
  grounded/reference channels).

## Source files (from the CL1-Neural-labs repo)

| File | Layer | Purpose |
| --- | --- | --- |
| `server.ts` | Back end | Express + WebSocket CL1 simulator (above). |
| `src/main.tsx` | Front end | React entry point. |
| `src/App.tsx` | Front end | Layout and page switching. |
| `src/components/VirtualCL1ClusterServer.tsx` | Front end | Live dish view, connection state, control buttons. |
| `src/components/DevicePanel.tsx` | Front end | Device status/config readouts. |
| `src/components/SpikeChart.tsx` | Front end | Per-channel spike visualization. |
| `src/components/BurstAnalysisChart.tsx` | Front end | Burst detection metrics. |
| `src/components/FunctionalConnectivityMatrix.tsx` | Front end | Channel-to-channel connectivity grid. |
| `src/components/BranchingRatioChart.tsx` | Front end | Avalanche/branching ratio plot. |
| `src/components/RCurveChart.tsx` | Front end | Response curve visualization. |
| `src/components/InfoPanel.tsx` | Front end | Build info and help. |
| `src/client/wsClient.ts` | Front end | WebSocket client with binary frame parsing. |
| `src/client/authClient.ts` | Front end | Login/session calls. |
| `src/analysis/*.ts` | Front end | Burst, connectivity, branching-ratio, R-curve algorithms. |
| `src/config/labSettings.ts` | Front end | Server URL, playback speed, theme settings. |
| `src/config/buildInfo.ts` | Shared | Build identity consumed by `/api/build`. |

Original documentation: `README.md` (copied into this folder).

## Connection to the Synthetic Human Brain stack

```text
React UI (CL1-Neural-labs, :3000)
      |  ws binary frames + /api/stim
      v
CL1 simulator server (server.ts, :3000)         <-- dev/demo data source
      |  (option) the same UI can point at the Python bridge
      v
Python FastAPI (:8787)  --/api/v1/network/*-->  Rust backend (:7800)
```

Integration points already available:

- The desktop GUI's CL1 Clone pages use the same channel/stim semantics
  (`StimDesign`, `BurstDesign`, `ChannelSet`) as `POST /api/stim` here.
- `GET /api/status` fields map onto the desktop CL1 Session Info tree.
- The Python `/api/v1/network/simulate` endpoint can drive activity that the
  UI renders via its standard charts.

## Commands

```bash
npm install
npm run build     # vite production build -> dist/
npm test          # 16 tests
node --import tsx server.ts   # serve UI + CL1 simulator on :3000
```

## Research boundary

This is a simulator of the Cortical Labs CL1 protocol for research and
visualization. It is not connected to biological wetware, is not a Cortical
Labs product, and is not a medical device. See `LICENSES/CL1_NOTICE.md`.
