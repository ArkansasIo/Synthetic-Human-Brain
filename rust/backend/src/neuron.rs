//! Pluggable neuron update models for abstract network simulations.
//!
//! Mirrors `src/synthetic_brain/neuron.py` so the Rust edge compute and the
//! Python host share the same `NeuronModel` contract:
//!
//! ```text
//! NeuronModel.update(activity, input_signal, time_step) -> float
//! ```
//!
//! The default leaky-rate unit clamps activity to [minimum, maximum]; a
//! custom model may use any range as long as outputs stay finite. Used by
//! `NetworkSimulation` (Python) and the network stage of the backend service.

/// Contract for a deterministic single-unit update, mirroring the Python
/// `NeuronModel` protocol.
pub trait NeuronModel {
    /// Return the next activity value for one abstract unit.
    fn update(&self, activity: f64, input_signal: f64, time_step: f64) -> f64;

    /// Whether the model output is acceptable (finite by contract).
    fn is_valid_output(&self, value: f64) -> bool {
        value.is_finite()
    }
}

/// Simple bounded leaky rate model.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct LeakyRateNeuron {
    pub decay: f64,
    pub minimum: f64,
    pub maximum: f64,
}

impl LeakyRateNeuron {
    pub fn new(decay: f64, minimum: f64, maximum: f64) -> Self {
        assert!(
            (0.0..=1.0).contains(&decay),
            "decay must be between 0 and 1"
        );
        assert!(minimum < maximum, "minimum must be less than maximum");
        Self { decay, minimum, maximum }
    }
}

impl Default for LeakyRateNeuron {
    fn default() -> Self {
        Self { decay: 0.9, minimum: 0.0, maximum: 1.0 }
    }
}

impl NeuronModel for LeakyRateNeuron {
    fn update(&self, activity: f64, input_signal: f64, time_step: f64) -> f64 {
        let value = self.decay * activity + time_step * input_signal;
        value.clamp(self.minimum, self.maximum)
    }
}

/// Integrate-and-fire style unit: accumulates until `threshold`, then emits
/// and resets. `update` returns post-update activity; `fired_last` reports
/// whether a spike occurred on the previous step.
#[derive(Debug, Clone)]
pub struct IntegrateAndFireNeuron {
    pub threshold: f64,
    pub reset_level: f64,
    pub leak: f64,
    activity: f64,
    fired: bool,
}

impl IntegrateAndFireNeuron {
    pub fn new(threshold: f64, reset_level: f64, leak: f64) -> Self {
        Self { threshold, reset_level, leak, activity: 0.0, fired: false }
    }

    pub fn activity(&self) -> f64 {
        self.activity
    }

    pub fn fired_last(&self) -> bool {
        self.fired
    }

    pub fn update_state(&mut self, input_signal: f64, time_step: f64) -> f64 {
        let candidate = self.activity * (1.0 - self.leak) + time_step * input_signal;
        self.fired = candidate >= self.threshold;
        self.activity = if self.fired { self.reset_level } else { candidate };
        self.activity
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn leaky_rate_matches_python_reference_values() {
        // Same computation as src/synthetic_brain/neuron.py::LeakyRateNeuron.update
        let neuron = LeakyRateNeuron::default();
        assert_eq!(neuron.update(0.5, 1.0, 0.1), 0.55);
        assert_eq!(neuron.update(1.5, 0.0, 0.1), 1.0); // clamped to maximum
        assert_eq!(neuron.update(-1.0, 0.0, 0.1), 0.0); // clamped to minimum
    }

    #[test]
    fn decay_bounds_enforced() {
        assert!(std::panic::catch_unwind(|| LeakyRateNeuron::new(1.5, 0.0, 1.0)).is_err());
        assert!(std::panic::catch_unwind(|| LeakyRateNeuron::new(0.9, 1.0, 0.0)).is_err());
    }

    #[test]
    fn integrate_and_fire_resets_after_threshold() {
        let mut neuron = IntegrateAndFireNeuron::new(1.0, 0.0, 0.0);
        neuron.update_state(0.3, 1.0); // 0.3
        neuron.update_state(0.3, 1.0); // 0.6
        neuron.update_state(0.3, 1.0); // 0.9
        let value = neuron.update_state(0.3, 1.0); // 1.2 -> fires, resets
        assert_eq!(value, 0.0);
        assert!(neuron.fired_last());
    }

    #[test]
    fn outputs_are_finite() {
        let neuron = LeakyRateNeuron::default();
        assert!(neuron.is_valid_output(neuron.update(1.0, 1.0, 0.1)));
        assert!(!neuron.is_valid_output(f64::NAN));
    }
}
