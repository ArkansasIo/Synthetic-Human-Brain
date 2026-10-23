use synthetic_brain_core::{lif_step, LifState};

/// Deterministic simulation service used by the Rust backend worker.
#[derive(Debug, Clone)]
pub struct BackendService {
    pub neuron: LifState,
    pub simulation_time_ms: f64,
    pub spikes_emitted: u64,
}

impl BackendService {
    pub fn new() -> Self {
        Self {
            neuron: LifState {
                voltage: -65.0,
                rest: -65.0,
                threshold: -50.0,
                reset: -65.0,
                tau_ms: 10.0,
                resistance: 1.0,
            },
            simulation_time_ms: 0.0,
            spikes_emitted: 0,
        }
    }

    pub fn step(&mut self, input_current: f64, dt_ms: f64) -> bool {
        let spike = lif_step(&mut self.neuron, input_current, dt_ms);
        self.simulation_time_ms += dt_ms;
        if spike {
            self.spikes_emitted += 1;
        }
        spike
    }
}

impl Default for BackendService {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn service_advances_time() {
        let mut service = BackendService::new();
        service.step(0.0, 1.0);
        assert_eq!(service.simulation_time_ms, 1.0);
    }
}
