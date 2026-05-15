"""Search for games with identical unweighted graphs but different weights."""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Iterable

from .dynamics import (
    Attractor,
    deterministic_basins,
    payoff_sensitive_better_response_step,
)
from .games import NormalFormGame, Profile
from .preference_graphs import (
    format_preference_graphs,
    preference_graph,
    pure_nash_equilibria,
    weighted_preference_graph,
)


@dataclass(frozen=True)
class GamePairComparison:
    """A pair of games with the same unweighted graph and comparison data."""

    first: NormalFormGame
    second: NormalFormGame
    same_unweighted_graph: bool
    different_weighted_edges: bool
    first_basin_sizes: tuple[tuple[Attractor, int], ...]
    second_basin_sizes: tuple[tuple[Attractor, int], ...]

    @property
    def different_basin_sizes(self) -> bool:
        """Return whether payoff-sensitive basin-size signatures differ."""

        return self.first_basin_sizes != self.second_basin_sizes


@dataclass(frozen=True)
class UniqueMaxFlipComparison:
    """A no-tie pair where the max-gain edge flips at one profile."""

    comparison: GamePairComparison
    profile: Profile
    first_max_target: Profile
    second_max_target: Profile


def two_by_two_games(
    payoff_values: Iterable[int] = (-2, -1, 0, 1, 2),
) -> Iterable[NormalFormGame]:
    """Generate all 2x2 games with payoffs in ``payoff_values``."""

    values = tuple(payoff_values)
    strategy_sets = ((0, 1), (0, 1))
    profiles = list(product(*strategy_sets))

    for index, payoff_tuple in enumerate(product(values, repeat=8)):
        payoffs = {
            profile: (
                float(payoff_tuple[2 * profile_index]),
                float(payoff_tuple[2 * profile_index + 1]),
            )
            for profile_index, profile in enumerate(profiles)
        }
        yield NormalFormGame(
            strategy_sets,
            payoffs,
            name=f"2x2 integer game {index}",
        )


def unweighted_edge_signature(game: NormalFormGame) -> tuple[tuple[Profile, Profile], ...]:
    """Return a canonical directed-edge signature for the unweighted graph."""

    return tuple(sorted(preference_graph(game).edges()))


def weighted_edge_signature(
    game: NormalFormGame,
) -> tuple[tuple[Profile, Profile, float], ...]:
    """Return a canonical directed-edge-and-weight signature."""

    graph = weighted_preference_graph(game)
    return tuple(
        sorted(
            (source, target, data["weight"])
            for source, target, data in graph.edges(data=True)
        )
    )


def payoff_sensitive_basin_sizes(
    game: NormalFormGame,
) -> tuple[tuple[Attractor, int], ...]:
    """Return deterministic max-gain better-response basin sizes."""

    basins = deterministic_basins(game, payoff_sensitive_better_response_step)
    return tuple(
        sorted(
            ((attractor, len(initial_profiles)) for attractor, initial_profiles in basins.items()),
            key=repr,
        )
    )


def unique_max_gain_target(game: NormalFormGame, profile: Profile) -> Profile | None:
    """Return the unique max-gain improving target from ``profile``, if any."""

    improvements = game.improving_deviations(profile)
    if len(improvements) < 2:
        return None

    max_gain = max(gain for _player, _target, gain in improvements)
    targets = [
        target
        for _player, target, gain in improvements
        if gain == max_gain
    ]
    if len(targets) != 1:
        return None
    return targets[0]


def compare_games(first: NormalFormGame, second: NormalFormGame) -> GamePairComparison:
    """Compare two games by graph weights and payoff-sensitive basins."""

    first_edges = unweighted_edge_signature(first)
    second_edges = unweighted_edge_signature(second)
    return GamePairComparison(
        first=first,
        second=second,
        same_unweighted_graph=first_edges == second_edges,
        different_weighted_edges=weighted_edge_signature(first)
        != weighted_edge_signature(second),
        first_basin_sizes=payoff_sensitive_basin_sizes(first),
        second_basin_sizes=payoff_sensitive_basin_sizes(second),
    )


def find_unique_max_flip_pair(
    payoff_values: Iterable[int] = (-2, -1, 0, 1, 2),
) -> UniqueMaxFlipComparison | None:
    """Find a same-graph pair where unique max-gain choices flip.

    The returned pair has the same unweighted preference graph and the same
    pure Nash equilibria. At a shared profile with at least two outgoing
    improving edges, both games have a unique maximum-gain edge, but those
    edges point to different sink vertices.
    """

    representatives: dict[
        tuple[tuple[tuple[Profile, Profile], ...], tuple[Profile, ...]],
        list[tuple[NormalFormGame, tuple[tuple[Profile, Profile, float], ...]]],
    ] = {}

    for game in two_by_two_games(payoff_values):
        pure_nash = tuple(sorted(pure_nash_equilibria(game)))
        edge_signature = unweighted_edge_signature(game)
        weight_signature = weighted_edge_signature(game)
        key = (edge_signature, pure_nash)

        current_targets = {
            profile: target
            for profile in game.profiles()
            if (target := unique_max_gain_target(game, profile)) is not None
        }
        if not current_targets:
            continue

        for previous_game, previous_weight_signature in representatives.get(key, []):
            if previous_weight_signature == weight_signature:
                continue

            previous_targets = {
                profile: target
                for profile in previous_game.profiles()
                if (target := unique_max_gain_target(previous_game, profile)) is not None
            }

            for profile, previous_target in previous_targets.items():
                current_target = current_targets.get(profile)
                if (
                    current_target is not None
                    and previous_target != current_target
                    and previous_target in pure_nash
                    and current_target in pure_nash
                ):
                    return UniqueMaxFlipComparison(
                        comparison=compare_games(previous_game, game),
                        profile=profile,
                        first_max_target=previous_target,
                        second_max_target=current_target,
                    )

        representatives.setdefault(key, []).append((game, weight_signature))

    return None


def format_payoff_table(game: NormalFormGame) -> str:
    """Format a game's payoff table in profile order."""

    lines = ["Payoff table:"]
    for profile in game.profiles():
        lines.append(f"  {profile}: {game.payoff(profile)}")
    return "\n".join(lines)


def format_unique_max_flip_comparison(result: UniqueMaxFlipComparison) -> str:
    """Format a no-tie unique-max flip witness."""

    comparison = result.comparison
    lines = [
        "=" * 72,
        "Unique max-gain flip witness",
        f"First: {comparison.first.name}",
        f"Second: {comparison.second.name}",
        f"Same unweighted preference graph: {comparison.same_unweighted_graph}",
        f"Same pure Nash equilibria: {pure_nash_equilibria(comparison.first) == pure_nash_equilibria(comparison.second)}",
        f"Different weighted edge data: {comparison.different_weighted_edges}",
        f"Different payoff-sensitive basin sizes: {comparison.different_basin_sizes}",
        f"Flip profile: {result.profile}",
        f"First unique max-gain target: {result.first_max_target}",
        f"Second unique max-gain target: {result.second_max_target}",
        "",
        "First game:",
        format_payoff_table(comparison.first),
        format_preference_graphs(comparison.first),
        f"Deterministic max-gain basin sizes: {comparison.first_basin_sizes}",
        "",
        "Second game:",
        format_payoff_table(comparison.second),
        format_preference_graphs(comparison.second),
        f"Deterministic max-gain basin sizes: {comparison.second_basin_sizes}",
    ]
    return "\n".join(lines)


def find_pairs_with_different_payoff_sensitive_basins(
    payoff_values: Iterable[int] = (-2, -1, 0, 1, 2),
    max_pairs: int = 3,
) -> list[GamePairComparison]:
    """Search 2x2 games for same graph, different weights, different basins."""

    representatives: dict[
        tuple[tuple[Profile, Profile], ...],
        dict[tuple[tuple[Attractor, int], ...], tuple[NormalFormGame, tuple[tuple[Profile, Profile, float], ...]]],
    ] = {}
    pairs: list[GamePairComparison] = []

    for game in two_by_two_games(payoff_values):
        edge_signature = unweighted_edge_signature(game)
        weight_signature = weighted_edge_signature(game)
        basin_signature = payoff_sensitive_basin_sizes(game)
        bucket = representatives.setdefault(edge_signature, {})

        for previous_basin_signature, (previous_game, previous_weight_signature) in bucket.items():
            if (
                previous_basin_signature != basin_signature
                and previous_weight_signature != weight_signature
            ):
                pairs.append(compare_games(previous_game, game))
                if len(pairs) >= max_pairs:
                    return pairs

        bucket.setdefault(basin_signature, (game, weight_signature))

    return pairs


def format_game_pair_comparison(comparison: GamePairComparison) -> str:
    """Format a game-pair comparison for terminal inspection."""

    lines = [
        "=" * 72,
        f"First: {comparison.first.name}",
        f"Second: {comparison.second.name}",
        f"Same unweighted preference graph: {comparison.same_unweighted_graph}",
        f"Different weighted edge data: {comparison.different_weighted_edges}",
        f"Different payoff-sensitive basin sizes: {comparison.different_basin_sizes}",
        "",
        "First game:",
        format_payoff_table(comparison.first),
        format_preference_graphs(comparison.first),
        f"Payoff-sensitive basin sizes: {comparison.first_basin_sizes}",
        "",
        "Second game:",
        format_payoff_table(comparison.second),
        format_preference_graphs(comparison.second),
        f"Payoff-sensitive basin sizes: {comparison.second_basin_sizes}",
    ]
    return "\n".join(lines)


if __name__ == "__main__":
    flip = find_unique_max_flip_pair()
    if flip is not None:
        print(format_unique_max_flip_comparison(flip))
