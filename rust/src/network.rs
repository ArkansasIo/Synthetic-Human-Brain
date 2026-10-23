//! Network-level stepping primitives.

#[derive(Debug, Clone, Copy, PartialEq, Eq)]
pub struct NetworkStep {
    pub events_processed: u64,
    pub spikes_emitted: u64,
}

impl NetworkStep {
    pub const fn empty() -> Self {
        Self {
            events_processed: 0,
            spikes_emitted: 0,
        }
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn empty_step_is_deterministic() {
        assert_eq!(NetworkStep::empty().spikes_emitted, 0);
    }
}
