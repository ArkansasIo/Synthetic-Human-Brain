from synthetic_brain.cl1_analysis import firing_stats, functional_connectivity, information_entropy, network_bursts
from synthetic_brain.cl1_clone import Spike


def test_firing_stats() -> None:
    stats = firing_stats([Spike(0, 0), Spike(25_000, 0), Spike(12_500, 1)], duration_frames=25_000)
    assert stats.total_spikes == 3
    assert stats.active_channels == 2
    assert stats.channel_rates_hz[0] == 2.0


def test_network_bursts() -> None:
    spikes = [Spike(i, 0) for i in range(0, 2500, 50)]
    result = network_bursts(spikes, bin_size_seconds=0.1, threshold_hz=5.0)
    assert result.bursts


def test_entropy_and_connectivity() -> None:
    spikes = [Spike(i * 2500, i % 2) for i in range(20)]
    entropy = information_entropy(spikes, bin_size_seconds=0.1)
    connectivity = functional_connectivity(spikes, bin_size_seconds=0.1, channel_count=2, threshold=0.0)
    assert entropy.values
    assert len(connectivity.adjacency) == 2
