# Multiscale Brain Architecture

Version 0.4.0 extends the simulator from neuron/synapse primitives into explicit morphology, connectomics, and validation observables.

## Model hierarchy

```text
ion-channel / receptor kinetics
          |
          v
membrane + point neuron models
          |
          v
compartment tree + passive cable
          |
          v
synapses + plasticity + neuromodulation
          |
          v
neural populations / microcircuits
          |
          v
brain-region graph
          |
          v
sparse connectome
          |
          v
population activity + behavioral experiments
          |
          v
validation metrics
```

This is a software architecture for composing models at different scales. It does not assert that each anatomical region is a homogeneous computational unit or that the resulting system is a biologically complete human brain.

## Research basis

Modern simulation-neuroscience workflows combine multiple scales, including ion channels, detailed cells, microcircuits, regions, and whole-brain/network representations. Blue Brain describes this explicitly and also documents morphology, electrophysiology, cell-type, connectome, and synaptic data products. citeturn0search0turn0search1

Large-scale mechanistic modeling literature likewise describes multicompartment morphologies, cable theory, conductance-based channels, experimentally constrained connectivity, and receptor kinetics as components of detailed circuit models. citeturn0search6

Whole-brain network models add graph-theoretic connectivity, parcellation, node dynamics, and parameter fitting at a larger scale. citeturn0search9

## New modules

### `morphology.py`

Provides:

- `Compartment`
- `CompartmentTree`
- `MorphologyEdge`
- `NeuronMorphology`
- compartment dimensions and surface area
- explicit parent/child topology
- passive cable stepping through existing cable-diffusion mathematics

### `connectome.py`

Provides:

- sparse directed graph representation
- weighted edges
- conduction delays
- excitatory/inhibitory edge labels
- in/out degree
- weighted out-strength
- delay-based shortest paths
- graph validation

The representation is intentionally independent of a specific connectome file format so adapters for SONATA or other research datasets can be added without coupling the simulation core to a storage format.

### `metrics.py`

Provides:

- firing rate
- coefficient of variation of inter-event intervals
- population synchrony proxy
- Shannon activity entropy
- mean absolute prediction error

These metrics are intended for experiment validation and regression tests, not as clinical biomarkers.

## Next research layer

The next implementation stage should add:

1. explicit ion-channel objects and channel-state kinetics;
2. receptor-specific rise/decay states and calcium-dependent mechanisms;
3. dendritic active channels and back-propagating spikes;
4. synapse placement on morphology compartments;
5. cell-type metadata and parameter provenance;
6. connectome import/export adapters;
7. sensory and motor pathway abstractions;
8. LFP/EEG/MEG forward-model proxies;
9. parameter fitting and uncertainty quantification;
10. benchmark datasets and reproducible experiment manifests.
