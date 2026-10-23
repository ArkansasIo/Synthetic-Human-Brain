# Brain Region Examples

These examples are executable design examples for the computational brain model. Each anatomical system has its own folder and follows the same contract:

1. define region/population state
2. accept normalized input
3. update local dynamics
4. emit neural events
5. expose measurements
6. optionally bind to a CL1-compatible backend

The examples model computational functions; they do not claim to reproduce a human brain.

## Tree

```text
examples/brain_regions/
├── cortex/
│   ├── frontal.py
│   ├── parietal.py
│   ├── temporal.py
│   ├── occipital.py
│   └── insula.py
├── hippocampus/
│   ├── entorhinal.py
│   ├── dentate_gyrus.py
│   ├── ca3.py
│   ├── ca2.py
│   ├── ca1.py
│   └── subiculum.py
├── limbic/
│   ├── amygdala.py
│   ├── fornix.py
│   └── mammillary_bodies.py
├── basal_ganglia/
│   ├── caudate.py
│   ├── putamen.py
│   ├── globus_pallidus.py
│   ├── subthalamic_nucleus.py
│   └── substantia_nigra.py
├── diencephalon/
│   ├── thalamus.py
│   ├── hypothalamus.py
│   └── pituitary.py
├── cerebellum/
│   ├── cortex.py
│   └── deep_nuclei.py
├── brainstem/
│   ├── midbrain.py
│   ├── pons.py
│   └── medulla.py
├── spinal/
│   ├── spinal_cord.py
│   └── reflex.py
├── sensory/
│   ├── vision.py
│   ├── auditory.py
│   ├── somatosensory.py
│   ├── olfactory.py
│   └── gustatory.py
└── motor/
    ├── motor_system.py
    ├── corticospinal.py
    └── autonomic.py
```

## CL1 mapping

Each example can run against a synthetic backend first. The CL1 layer is an interchangeable experimental substrate: region models produce/consume normalized spike, stimulus, recording, and loop-tick events. It is not a claim that CL1 contains a human anatomical region or that a biological culture is equivalent to one.
