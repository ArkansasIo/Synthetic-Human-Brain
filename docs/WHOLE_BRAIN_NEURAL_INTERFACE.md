# Whole-Brain Neural Interface Architecture

## Purpose

Define a research architecture for connecting external neural measurements to the Synthetic Human Brain software without assuming that a living human brain can currently be measured at single-neuron/single-synapse resolution across the entire brain.

## Interface tiers

### Tier 0 — Non-invasive observation

Candidate modalities include EEG, MEG, MRI/fMRI, diffusion MRI, and other validated research modalities. These provide different spatial, temporal, and physiological information and therefore enter the software as different measurement types.

### Tier 1 — Surface research interfaces

Examples include scalp sensors and research cortical-surface recordings where legally and clinically appropriate. These should remain represented as generic `SensorArray` and `SignalStream` interfaces.

### Tier 2 — Specialized research interfaces

Depth or penetrating interfaces may provide more localized signals but are invasive and require specialized research/clinical infrastructure. The software architecture can represent them without prescribing how to implant or operate them.

## Whole-brain mapping model

```text
Measurement modality
        |
        v
Acquisition -> Calibration -> Quality control
        |
        v
Signal representation
        |
        +--> EEG / MEG features
        +--> MRI / fMRI features
        +--> diffusion/connectivity features
        +--> electrophysiology events
        |
        v
Anatomical registration
        |
        v
Brain-region mapper
        |
        v
Connectome + regional state estimator
        |
        v
Synthetic Human Brain model
```

## Region coverage

The logical model covers:

- frontal, parietal, temporal, occipital and insular cortex
- hippocampal formation
- amygdala and related limbic structures
- basal ganglia
- thalamus and hypothalamus
- cerebellum
- midbrain, pons, and medulla
- spinal pathways
- sensory and motor systems

Coverage means that the software can represent the region and map compatible observations to it; it does not imply that one physical sensor can directly observe every neuron in that region.

## Data contract

Every measurement should preserve:

- source modality
- sensor/channel identity
- sampling information
- units
- time synchronization metadata
- anatomical coordinates or region mapping
- preprocessing history
- quality/confidence flags
- provenance

## Closed-loop boundary

A future research closed loop may be represented as:

```text
measurement -> analysis -> model state -> experiment decision -> approved interface -> measurement
```

The repository should keep the decision logic and physical interface separate. Any real stimulation must be handled by appropriately qualified, safety-controlled research/clinical hardware rather than by a generic software model.

## Scientific limitation

No current external interface provides a complete, real-time, neuron-by-neuron and synapse-by-synapse scan of a living human brain. The project therefore uses a multimodal, multiscale inference architecture.
