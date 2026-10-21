"""Command-line entry point for the sample simulation."""

from __future__ import annotations

import argparse

from synthetic_brain import Simulation, SimulationConfig


def main() -> None:
    parser = argparse.ArgumentParser(description="Run a small abstract neural activity simulation.")
    parser.add_argument("--steps", type=int, default=5, help="Number of update steps.")
    parser.add_argument("--neurons", type=int, default=8, help="Number of abstract units.")
    parser.add_argument("--seed", type=int, default=7, help="Reproducible initialization seed.")
    args = parser.parse_args()
    if args.steps < 0:
        parser.error("--steps must be non-negative")

    simulation = Simulation(SimulationConfig(neuron_count=args.neurons, seed=args.seed))
    print(f"initial: step={simulation.step_count}, activity={simulation.snapshot().activity}")
    for _ in range(args.steps):
        state = simulation.step()
        print(f"step={state.step}, activity={state.activity}")


if __name__ == "__main__":
    main()
