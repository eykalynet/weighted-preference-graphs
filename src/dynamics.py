"""Basic finite-game dynamics."""

from __future__ import annotations

from dataclasses import dataclass
from random import Random
from typing import Callable, Literal, Union

from .games import NormalFormGame, Profile

TieBreaking = Literal["deterministic", "random"]
DynamicsStatus = Literal["fixed_point", "cycle", "max_steps"]
StepFunction = Callable[[NormalFormGame, Profile], Profile]
Attractor = Union[Profile, tuple[Profile, ...]]


@dataclass(frozen=True)
class DynamicsResult:
    """Result of iterating a deterministic dynamic."""

    path: list[Profile]
    status: DynamicsStatus
    attractor: Attractor


def _profile_key(profile: Profile) -> tuple[str, ...]:
    """Return a deterministic ordering key for arbitrary hashable strategies."""

    return tuple(repr(strategy) for strategy in profile)


def _choose_profile(
    candidates: list[Profile],
    tie_breaking: TieBreaking,
    rng: Random,
) -> Profile:
    """Choose one profile from ``candidates`` using the requested tie-breaking."""

    if not candidates:
        raise ValueError("Cannot choose from an empty candidate list.")
    if tie_breaking == "deterministic":
        return min(candidates, key=_profile_key)
    if tie_breaking == "random":
        return rng.choice(candidates)
    raise ValueError(f"Unknown tie-breaking rule: {tie_breaking!r}")


def asynchronous_better_response_step(
    game: NormalFormGame,
    profile: Profile,
    tie_breaking: TieBreaking = "deterministic",
    seed: int | None = None,
    rng: Random | None = None,
) -> Profile:
    """Take one asynchronous better-response step.

    The candidates are all strictly improving unilateral deviations. A sink
    vertex of the preference graph is fixed.
    """

    random_generator = rng if rng is not None else Random(seed)
    improvements = game.improving_deviations(profile)
    if not improvements:
        return profile
    candidates = [target for _player, target, _gain in improvements]
    return _choose_profile(candidates, tie_breaking, random_generator)


def payoff_sensitive_better_response_step(
    game: NormalFormGame,
    profile: Profile,
    tie_breaking: TieBreaking = "deterministic",
    seed: int | None = None,
    rng: Random | None = None,
) -> Profile:
    """Take one max-gain asynchronous better-response step.

    Among all strictly improving unilateral deviations, this dynamic first
    keeps only those with maximum payoff gain. It then applies the requested
    tie-breaking rule.
    """

    random_generator = rng if rng is not None else Random(seed)
    improvements = game.improving_deviations(profile)
    if not improvements:
        return profile

    max_gain = max(gain for _player, _target, gain in improvements)
    candidates = [
        target
        for _player, target, gain in improvements
        if gain == max_gain
    ]
    return _choose_profile(candidates, tie_breaking, random_generator)


def _best_response_profiles(
    game: NormalFormGame,
    profile: Profile,
    player: int,
) -> list[Profile]:
    """Return profiles obtained when ``player`` chooses a best response."""

    candidates: list[tuple[Profile, float]] = []
    for strategy in game.strategy_sets[player]:
        candidate = list(profile)
        candidate[player] = strategy
        candidate_profile = tuple(candidate)
        payoff = float(game.payoff(candidate_profile, player))
        candidates.append((candidate_profile, payoff))

    best_payoff = max(payoff for _candidate, payoff in candidates)
    return [
        candidate
        for candidate, payoff in candidates
        if payoff == best_payoff and payoff > float(game.payoff(profile, player))
    ]


def asynchronous_best_response_step(
    game: NormalFormGame,
    profile: Profile,
    tie_breaking: TieBreaking = "deterministic",
    seed: int | None = None,
    rng: Random | None = None,
) -> Profile:
    """Take one asynchronous best-response step.

    The candidates are strictly payoff-improving best-response updates by a
    single player. If every player is already best responding, the profile is
    fixed.
    """

    random_generator = rng if rng is not None else Random(seed)
    candidates: list[Profile] = []
    for player in range(game.num_players):
        candidates.extend(_best_response_profiles(game, profile, player))
    if not candidates:
        return profile
    return _choose_profile(candidates, tie_breaking, random_generator)


def simultaneous_best_response_step(
    game: NormalFormGame,
    profile: Profile,
    tie_breaking: TieBreaking = "deterministic",
    seed: int | None = None,
    rng: Random | None = None,
) -> Profile:
    """Take one simultaneous best-response step.

    Each player chooses a best response to the current strategies of the other
    players. Several coordinates may change at once.
    """

    random_generator = rng if rng is not None else Random(seed)
    next_profile = list(profile)
    for player in range(game.num_players):
        candidates: list[tuple[object, float]] = []
        for strategy in game.strategy_sets[player]:
            candidate = list(profile)
            candidate[player] = strategy
            candidate_profile = tuple(candidate)
            payoff = float(game.payoff(candidate_profile, player))
            candidates.append((strategy, payoff))

        best_payoff = max(payoff for _strategy, payoff in candidates)
        best_strategies = [
            strategy for strategy, payoff in candidates if payoff == best_payoff
        ]
        if tie_breaking == "deterministic":
            next_profile[player] = min(best_strategies, key=repr)
        elif tie_breaking == "random":
            next_profile[player] = random_generator.choice(best_strategies)
        else:
            raise ValueError(f"Unknown tie-breaking rule: {tie_breaking!r}")

    return tuple(next_profile)


def iterate_dynamics(
    game: NormalFormGame,
    initial_profile: Profile,
    step_function: StepFunction,
    max_steps: int = 100,
) -> DynamicsResult:
    """Iterate a deterministic dynamic with cycle detection."""

    path = [initial_profile]
    first_seen = {initial_profile: 0}
    current = initial_profile

    for _step in range(max_steps):
        next_profile = step_function(game, current)
        path.append(next_profile)

        if next_profile == current:
            return DynamicsResult(path, "fixed_point", next_profile)

        if next_profile in first_seen:
            cycle_start = first_seen[next_profile]
            cycle = tuple(path[cycle_start:-1])
            return DynamicsResult(path, "cycle", cycle)

        first_seen[next_profile] = len(path) - 1
        current = next_profile

    return DynamicsResult(path, "max_steps", tuple(path))


def deterministic_basins(
    game: NormalFormGame,
    step_function: StepFunction,
    max_steps: int = 100,
) -> dict[Attractor, list[Profile]]:
    """Compute basins of attraction for a deterministic dynamic."""

    basins: dict[Attractor, list[Profile]] = {}
    for profile in game.profiles():
        result = iterate_dynamics(
            game,
            profile,
            step_function,
            max_steps=max_steps,
        )
        basins.setdefault(result.attractor, []).append(profile)
    return basins
