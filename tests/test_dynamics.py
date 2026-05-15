from src.dynamics import (
    asynchronous_better_response_step,
    asynchronous_best_response_step,
    deterministic_basins,
    iterate_dynamics,
    simultaneous_best_response_step,
)
from src.examples import coordination_game, prisoners_dilemma


def test_asynchronous_better_response_step_deterministic() -> None:
    game = coordination_game()
    assert asynchronous_better_response_step(game, ("A", "B")) == ("A", "A")
    assert asynchronous_better_response_step(game, ("A", "A")) == ("A", "A")


def test_asynchronous_better_response_step_random_seed() -> None:
    game = coordination_game()
    first = asynchronous_better_response_step(
        game, ("A", "B"), tie_breaking="random", seed=3
    )
    second = asynchronous_better_response_step(
        game, ("A", "B"), tie_breaking="random", seed=3
    )
    assert first == second
    assert first in {("A", "A"), ("B", "B")}


def test_asynchronous_best_response_step_deterministic() -> None:
    game = prisoners_dilemma()
    assert asynchronous_best_response_step(game, ("C", "C")) == ("C", "D")
    assert asynchronous_best_response_step(game, ("D", "D")) == ("D", "D")


def test_simultaneous_best_response_step() -> None:
    game = prisoners_dilemma()
    assert simultaneous_best_response_step(game, ("C", "C")) == ("D", "D")
    assert simultaneous_best_response_step(game, ("D", "D")) == ("D", "D")


def test_cycle_detection_for_simultaneous_best_response() -> None:
    game = coordination_game()
    result = iterate_dynamics(
        game,
        ("A", "B"),
        simultaneous_best_response_step,
    )
    assert result.status == "cycle"
    assert result.attractor == (("A", "B"), ("B", "A"))


def test_basin_computation_for_coordination_better_response() -> None:
    game = coordination_game()
    basins = deterministic_basins(game, asynchronous_better_response_step)
    assert basins == {
        ("A", "A"): [("A", "A"), ("A", "B"), ("B", "A")],
        ("B", "B"): [("B", "B")],
    }
