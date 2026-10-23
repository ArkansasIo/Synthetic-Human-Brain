//! Fast deterministic neuron kernels.

#[derive(Debug, Clone, Copy, PartialEq)]
pub struct LifState {
    pub voltage: f64,
    pub rest: f64,
    pub threshold: f64,
    pub reset: f64,
    pub tau_ms: f64,
    pub resistance: f64,
}

/// Advance one leaky-integrate-and-fire neuron by `dt_ms`.
///
/// Returns `true` when the neuron crosses threshold and emits a spike.
pub fn lif_step(state: &mut LifState, input_current: f64, dt_ms: f64) -> bool {
    assert!(state.tau_ms > 0.0, "tau_ms must be positive");
    assert!(dt_ms >= 0.0, "dt_ms must be non-negative");

    let dv = (-(state.voltage - state.rest) + state.resistance * input_current)
        / state.tau_ms;
    state.voltage += dt_ms * dv;

    if state.voltage >= state.threshold {
        state.voltage = state.reset;
        true
    } else {
        false
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn emits_spike_and_resets() {
        let mut state = LifState {
            voltage: -65.0,
            rest: -65.0,
            threshold: -50.0,
            reset: -65.0,
            tau_ms: 10.0,
            resistance: 1.0,
        };
        assert!(!lif_step(&mut state, 20.0, 10.0));
        assert!(lif_step(&mut state, 20.0, 10.0));
        assert_eq!(state.voltage, -65.0);
    }
}
