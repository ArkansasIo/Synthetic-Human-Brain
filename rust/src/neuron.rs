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
        // Parameters match the Python reference (src/synthetic_brain/algorithms.py
        // LIFNeuron defaults: resistance=10, tau=20) so the two sides agree.
        let mut state = LifState {
            voltage: -65.0,
            rest: -65.0,
            threshold: -50.0,
            reset: -65.0,
            tau_ms: 20.0,
            resistance: 10.0,
        };
        // dv/dt = (-(v-rest) + R*I) / tau; with I=20, dt=10 one step goes
        // -65 + 10 * ((0 + 200)/20) = +35 -> well past threshold, fires,
        // exactly like the Python LIFNeuron.step with the same numbers.
        assert!(lif_step(&mut state, 20.0, 10.0));
        assert_eq!(state.voltage, -65.0); // reset
    }
}
