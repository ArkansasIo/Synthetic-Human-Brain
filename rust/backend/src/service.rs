use synthetic_brain_core::network::Network;

pub struct BackendService {
    pub network: Network,
}

impl BackendService {
    pub fn new() -> Self {
        Self { network: Network::new() }
    }

    pub fn step(&mut self, dt_ms: f64) {
        self.network.step(dt_ms);
    }
}

impl Default for BackendService {
    fn default() -> Self { Self::new() }
}
