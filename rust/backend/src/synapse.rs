//! Pluggable synapse transformations for abstract network simulations.
//!
//! Mirrors `src/synthetic_brain/synapse.py` so the Rust edge compute and the
//! Python host share the same `SynapseModel` contract:
//!
//! ```text
//! SynapseModel.transmit(signal, weight) -> float
//! ```
//!
//! Used by `NetworkSimulation` (Python) and the network stage of the backend
//! service; both must produce identical outputs for identical inputs.

/// Contract for transforming a connection signal, mirroring the Python
/// `SynapseModel` protocol.
pub trait SynapseModel {
    /// Return the transmitted signal for the given input and weight.
    fn transmit(&self, signal: f64, weight: f64) -> f64;

    /// Whether the model produces finite outputs for finite inputs.
    fn is_valid_output(&self, value: f64) -> bool {
        value.is_finite()
    }
}

/// Pass a signal through a scalar connection weight.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct LinearSynapse {
    pub gain: f64,
}

impl Default for LinearSynapse {
    fn default() -> Self {
        Self { gain: 1.0 }
    }
}

impl LinearSynapse {
    pub fn new(gain: f64) -> Self {
        Self { gain }
    }
}

impl SynapseModel for LinearSynapse {
    fn transmit(&self, signal: f64, weight: f64) -> f64 {
        signal * weight * self.gain
    }
}

/// Synapse with a conductance-style nonlinearity: the transmitted signal
/// saturates at `max_signal`, mirroring bounded synaptic efficacy.
#[derive(Debug, Clone, Copy, PartialEq)]
pub struct SaturatingSynapse {
    pub gain: f64,
    pub max_signal: f64,
}

impl SaturatingSynapse {
    pub fn new(gain: f64, max_signal: f64) -> Self {
        Self { gain, max_signal }
    }
}

impl SynapseModel for SaturatingSynapse {
    fn transmit(&self, signal: f64, weight: f64) -> f64 {
        let transmitted = signal * weight * self.gain;
        transmitted.clamp(-self.max_signal, self.max_signal)
    }
}

/// Aggregate transmitted signals per target, as the network update step does.
pub fn aggregate(model: &dyn SynapseModel, connections: &[(usize, usize, f64)], signals: &[f64], targets: usize) -> Vec<f64> {
    let mut total = vec![0.0; targets];
    for &(source, target, weight) in connections {
        if source < signals.len() && target < targets {
            total[target] += model.transmit(signals[source], weight);
        }
    }
    total
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn linear_matches_python_contract() {
        // Same numbers as the Python doctest in src/synthetic_brain/synapse.py.
        let synapse = LinearSynapse::default();
        assert_eq!(synapse.transmit(0.5, 0.8), 0.4);
        assert_eq!(synapse.transmit(0.5, -0.2), -0.1);
    }

    #[test]
    fn saturating_clamps() {
        let synapse = SaturatingSynapse::new(10.0, 1.0);
        assert_eq!(synapse.transmit(1.0, 1.0), 1.0);
        assert_eq!(synapse.transmit(-5.0, 1.0), -1.0);
    }

    #[test]
    fn aggregation_sums_per_target() {
        let synapse = LinearSynapse::default();
        let connections = [(0usize, 1usize, 0.8), (1, 2, 0.5), (2, 0, -0.2)];
        let signals = [1.0, 1.0, 1.0];
        let totals = aggregate(&synapse, &connections, &signals, 3);
        assert_eq!(totals, vec![-0.2, 0.8, 0.5]);
    }

    #[test]
    fn outputs_are_finite() {
        let synapse = LinearSynapse::default();
        assert!(synapse.is_valid_output(synapse.transmit(1.0, 1.0)));
        assert!(!synapse.is_valid_output(f64::NAN));
    }
}
