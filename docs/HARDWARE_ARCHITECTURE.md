# Hardware Architecture Plan

## Design principle

The hardware layer is a distributed neural measurement and research-interface platform, not a single implant. The first implementation target is external/non-invasive acquisition and simulation-compatible electronics.

## Hardware blocks

```text
Sensors / research interfaces
        |
        v
Analog front end
        |
        v
Amplification + filtering
        |
        v
Digitization
        |
        v
Local FPGA / edge processor
        |
        v
Time-synchronized neural data bus
        |
        +--> storage
        +--> analysis workstation
        +--> Synthetic Human Brain engine
        +--> experiment controller
```

## Modules

### Sensor interface

Generic inputs for validated research sensors. The interface must expose channel count, sampling metadata, units, timing, calibration, and provenance.

### Analog front end

Responsible for conditioning weak biological signals before digitization. Exact circuit design is a later hardware-engineering task and must be validated against the selected sensor modality.

### Digitizer

Converts conditioned signals into timestamped digital samples. The API must support synchronization and dropped-sample detection.

### Synchronization

A common timebase is required to align multiple sensor systems and software simulation state.

### Edge compute

Optional FPGA/MCU/SoC processing for timestamping, packetization, filtering, quality flags, and transport. Keep high-level brain modeling on the host compute system initially.

### Data transport

Use a versioned packet schema with channel identity, timestamp, sample data, units, quality flags, and source metadata.

### Storage

Store immutable raw data separately from derived data. Preserve processing provenance so derived datasets can be regenerated.

## Hardware development stages

1. **H0:** simulator-only interface.
2. **H1:** prerecorded neural-data replay hardware/API.
3. **H2:** external sensor acquisition prototype.
4. **H3:** synchronized multi-modality research acquisition.
5. **H4:** validated research interface integration under appropriate institutional controls.
6. **H5:** future specialized interfaces only after separate engineering, safety, ethics, and regulatory work.

## CL1 relationship

CL1 compatibility belongs at the adapter boundary. The project should reproduce application-level concepts such as recording, stimulation commands, timing, experiment configuration, and closed-loop orchestration without copying proprietary implementation or claiming ownership of CL1 technology.

## Safety boundary

This document deliberately avoids surgical implantation instructions, stimulation parameters, electrode fabrication recipes, or clinical operating procedures. Those belong to qualified biomedical-device and clinical research workflows.
