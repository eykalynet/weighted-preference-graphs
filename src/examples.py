"""Small example games."""

from __future__ import annotations

from .games import NormalFormGame
from .preference_graphs import graph_summary


def coordination_game() -> NormalFormGame:
    """Return a 2x2 coordination game with two pure Nash equilibria."""

    strategies = (("A", "B"), ("A", "B"))
    payoffs = {
        ("A", "A"): (2, 2),
        ("A", "B"): (0, 0),
        ("B", "A"): (0, 0),
        ("B", "B"): (1, 1),
    }
    return NormalFormGame(strategies, payoffs, name="2x2 coordination game")


def prisoners_dilemma() -> NormalFormGame:
    """Return the prisoner's dilemma."""

    strategies = (("C", "D"), ("C", "D"))
    payoffs = {
        ("C", "C"): (3, 3),
        ("C", "D"): (0, 5),
        ("D", "C"): (5, 0),
        ("D", "D"): (1, 1),
    }
    return NormalFormGame(strategies, payoffs, name="prisoner's dilemma")


def all_examples() -> list[NormalFormGame]:
    """Return the minimal example suite."""

    return [coordination_game(), prisoners_dilemma()]


if __name__ == "__main__":
    for example in all_examples():
        print(graph_summary(example))
        print()
