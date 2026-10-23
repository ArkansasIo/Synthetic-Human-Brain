//! Rust performance layer for Synthetic Human Brain.
//!
//! The Rust crate is intentionally small at first: numerical kernels live here,
//! while orchestration, research workflows, BrainScript, and UI remain in Python.

pub mod neuron;
pub mod network;
pub mod telemetry;

pub use neuron::{lif_step, LifState};
pub use network::NetworkStep;
pub use telemetry::CoreTelemetry;
