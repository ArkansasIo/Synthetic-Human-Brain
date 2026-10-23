# UML Documentation

Each core API has a dedicated PlantUML source file. These diagrams are architectural contracts, not clinical-device schematics.

- `01_anatomy_api.puml` — anatomical hierarchy
- `02_neuron_api.puml` — neuron and membrane model
- `03_synapse_api.puml` — synaptic transmission
- `04_connectivity_api.puml` — connectome and pathways
- `05_dynamics_api.puml` — mathematical neural dynamics
- `06_plasticity_api.puml` — learning/plasticity
- `07_simulation_api.puml` — simulation engine
- `08_sensory_api.puml` — sensory interfaces
- `09_motor_api.puml` — motor interfaces
- `10_cognition_api.puml` — cognitive abstractions
- `11_experiment_api.puml` — experiment/data pipeline
- `12_neural_substrate_api.puml` — simulator/CL1/replay boundary
- `13_neural_interface_api.puml` — external acquisition/stimulation boundary
- `14_whole_brain_composition.puml` — regional composition
- `15_hardware_data_path.puml` — sensor-to-software path

Render with PlantUML or a compatible UML renderer. The `.puml` files are intentionally text-based so they can be reviewed and versioned alongside source code.
