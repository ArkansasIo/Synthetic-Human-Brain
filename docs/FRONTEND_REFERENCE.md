# Desktop & Web Front End — Source Reference

Complete map of both front ends: the PySide6 desktop client and the
TypeScript web client, with every source file and the build outputs.

## Desktop client (`desktop/python/`)

| File | Contents |
| --- | --- |
| `app.py` | The entire desktop application (~700 lines): `LoginDialog`, `ResearcherClient` main window, 6 menus, 10 main tabs, CL1 sub-pages, 4 custom chart canvases. |
| `README.md` | Client responsibilities and platform targets. |

### Widget inventory

| Widget | Kind | Purpose |
| --- | --- | --- |
| `LoginDialog` | QDialog | Server URL + credentials + registration; returns JWT. |
| `ResearcherClient` | QMainWindow | Tabs, menus, output log, status bar. |
| `SpikeRasterCanvas` | QWidget | QPainter spike raster from a `Recording`. |
| `ChannelHistogramCanvas` | QWidget | Per-channel spike counts bar chart. |
| `ActivityLineCanvas` | QWidget | Population activity line chart (CL1 loops and network steps). |
| `NetworkGraphCanvas` | QWidget | Signed weighted directed-graph rendering. |

### Pages and menus

Documented in detail in [GUI_PAGES_REFERENCE.md](GUI_PAGES_REFERENCE.md) and
[GUI_MENUS_REFERENCE.md](GUI_MENUS_REFERENCE.md).

## Web client (`web-client/`)

| File | Contents |
| --- | --- |
| `package.json` | Vite + TypeScript build (`npm run build` → `tsc && vite build`). |
| `index.html` | Single-page shell. |
| `src/main.ts` | Entry point: login form, dashboard, API calls to the Python server. |
| `dist/` | Build output (`index.html`, hashed JS/CSS). |

The web client talks to the same Python API server; it never connects to the
database or the Rust backend directly.

## Build & packaging

```bash
# desktop dev run
cd desktop/python && python app.py

# desktop exe (PyInstaller, one-dir)
python -m PyInstaller --onedir --windowed --name SyntheticBrainResearcher \
    --paths src --paths desktop/python --collect-submodules synthetic_brain \
    desktop/python/app.py
# output: dist/exe/SyntheticBrainResearcher/SyntheticBrainResearcher.exe

# web client
cd web-client && npm install && npm run build   # dist/
```

## Connection endpoints

| Front end | Talks to | Purpose |
| --- | --- | --- |
| Desktop GUI | `http://<server>:8787` | REST + WebSocket (auth, projects, jobs, telemetry). |
| Web client | `http://<server>:8787` | Same API, browser session. |
| Both | CL1 clone | Local in-process simulation (`synthetic_brain.cl1_clone`) — no server required. |

## Research boundary

Both front ends are research tools. They display simulated data and server
state; they do not diagnose, treat, or measure any biological system.
