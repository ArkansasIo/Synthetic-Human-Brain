# Synthetic Human Brain Region Tree

Each anatomical category is isolated into its own package. Each package may contain subregion modules, computational models, CL1 mappings, examples, tests, and experiment fixtures.

```text
regions/
├── cortex/
│   ├── frontal/
│   ├── parietal/
│   ├── temporal/
│   ├── occipital/
│   ├── insula/
│   └── corpus_callosum/
├── hippocampus/
│   ├── entorhinal/
│   ├── dentate_gyrus/
│   ├── ca3/
│   ├── ca2/
│   ├── ca1/
│   └── subiculum/
├── limbic/
│   ├── amygdala/
│   ├── mammillary_bodies/
│   └── fornix/
├── basal_ganglia/
│   ├── caudate/
│   ├── putamen/
│   ├── globus_pallidus/
│   ├── subthalamic_nucleus/
│   └── substantia_nigra/
├── diencephalon/
│   ├── thalamus/
│   ├── hypothalamus/
│   └── pituitary/
├── cerebellum/
│   ├── cortex/
│   └── deep_nuclei/
├── brainstem/
│   ├── midbrain/
│   ├── pons/
│   └── medulla/
├── spinal/
│   ├── spinal_cord/
│   └── reflex/
├── sensory/
│   ├── vision/
│   ├── auditory/
│   ├── somatosensory/
│   ├── olfactory/
│   └── gustatory/
└── motor/
    ├── motor_system/
    ├── corticospinal/
    └── autonomic/
```

This is an engineering decomposition, not a claim that every folder corresponds to a complete biological equivalent. CL1 provides an experimental neural substrate interface; it does not provide one biological equivalent of every anatomical region.
