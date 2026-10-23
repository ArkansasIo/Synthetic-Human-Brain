# Software / Hardware Mapping

| Software interface | Hardware concept | Primary data |
|---|---|---|
| `SensorArray` | external sensor array | sampled signals |
| `SignalChannel` | physical acquisition channel | channel samples |
| `AcquisitionDevice` | acquisition electronics | timestamped frames |
| `AmplifierInterface` | analog front end | conditioned signal |
| `DigitizerInterface` | ADC/digitizer | digital samples |
| `SignalStream` | transport link | ordered sample/event stream |
| `ArtifactFilter` | software DSP/quality stage | cleaned/flagged signals |
| `RegionMapper` | registration/atlas layer | anatomical mapping |
| `NeuralSubstrate` | simulator/biological/replay backend | neural events/state |
| `StimulationInterface` | approved research stimulation system | experiment command |
| `SynchronizationInterface` | shared timing hardware/software | clock alignment |

## Region mapping

```text
Cortex       -> cortical sensor mappings -> cortical state estimator
Hippocampus  -> localized research mapping -> hippocampal state estimator
Thalamus     -> regional mapping -> thalamic state estimator
Basal ganglia-> regional mapping -> action-selection model
Cerebellum   -> regional mapping -> motor-learning model
Brainstem    -> regional mapping -> autonomic/arousal model
Spinal       -> peripheral/central mapping -> reflex/motor model
```

## Representation rule

A hardware channel is never treated as a neuron by default. A channel is an observation with a modality, location, resolution, calibration, and uncertainty. The model layer may infer latent population or regional state from observations.
