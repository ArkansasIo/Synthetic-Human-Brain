use synthetic_brain_core::{lif_step, LifState};

pub struct BackendServiceFixed {
    pub neuron: LifState,
    pub simulation_time_ms: f64,
    pub spikes_emitted: u64,
}

impl BackendServiceFixed {
    pub fn new() -> Self {
        Self { neuron: LifState::default(), simulation_time_ms: 0.0, spikes_emitted: 0 }
    }
    pub fn step(&mut self, input_current: f64, dt_ms: f64) -> bool {
        let spike = lif_step(&mut self.neuron, input_current, dt_ms);
        self.simulation_time_ms += dt_ms;
        if spike { self.spikes_emitted += 1; }
        spike
    }
}
