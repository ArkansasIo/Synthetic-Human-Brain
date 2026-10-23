"""End-to-end local CL1 software experiment."""
from __future__ import annotations

from synthetic_brain.cl1_analysis import functional_connectivity, network_bursts
from synthetic_brain.cl1_clone import ChannelSet, StimDesign
from synthetic_brain.cl1_experiment import CL1Experiment, ExperimentConfig


config = ExperimentConfig(
    name="demo-network",
    channel_count=8,
    seed=42,
    ticks_per_second=1000,
    ticks=20,
)
experiment = CL1Experiment(config)
result = experiment.stimulated(
    ChannelSet(0, 1),
    StimDesign(160, -1.0, 160, 1.0),
)

print("ticks:", len(result.ticks))
print("spikes:", len(result.spikes))
print("firing:", result.firing_stats())
print("bursts:", network_bursts(result.spikes).bursts)
print("connectivity:", functional_connectivity(result.spikes, channel_count=config.channel_count).edge_count)
