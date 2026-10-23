//! Lightweight telemetry emitted by the Rust core.

#[derive(Debug, Clone, Copy, Default, PartialEq)]
pub struct CoreTelemetry {
    pub simulation_time_ms: f64,
    pub events_processed: u64,
    pub spikes_emitted: u64,
    pub queue_depth: u64,
}

impl CoreTelemetry {
    pub fn record_step(&mut self, dt_ms: f64, step: crate::NetworkStep) {
        self.simulation_time_ms += dt_ms;
        self.events_processed += step.events_processed;
        self.spikes_emitted += step.spikes_emitted;
    }
}
