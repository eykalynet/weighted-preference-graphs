"""Finite normal-form games.

Profiles are represented as tuples, one entry per player. Payoffs are stored as
a dictionary from profiles to payoff tuples.
"""

from __future__ import annotations

from dataclasses import dataclass
from itertools import product
from typing import Any, Iterable, Mapping

Profile = tuple[Any, ...]
Payoff = tuple[float, ...]


@dataclass(frozen=True)
class NormalFormGame:
    """A finite normal-form game.

    Parameters
    ----------
    strategy_sets:
        A sequence whose ``i``th entry is the finite strategy set of player
        ``i``. Strategies may be any hashable Python objects.
    payoffs:
        A mapping from every strategy profile to a tuple of player payoffs.
    name:
        Optional human-readable name.
    """

    strategy_sets: tuple[tuple[Any, ...], ...]
    payoffs: Mapping[Profile, Payoff]
    name: str = "finite game"

    def __post_init__(self) -> None:
        object.__setattr__(
            self,
            "strategy_sets",
            tuple(tuple(strategies) for strategies in self.strategy_sets),
        )
        n = len(self.strategy_sets)
        expected_profiles = set(product(*self.strategy_sets))
        actual_profiles = set(self.payoffs)

        missing = expected_profiles - actual_profiles
        extra = actual_profiles - expected_profiles
        if missing or extra:
            raise ValueError(
                "Payoff table must contain exactly all strategy profiles. "
                f"Missing={sorted(missing)!r}, extra={sorted(extra)!r}."
            )

        for profile, payoff in self.payoffs.items():
            if len(profile) != n:
                raise ValueError(f"Profile {profile!r} has wrong length.")
            if len(payoff) != n:
                raise ValueError(f"Payoff {payoff!r} for {profile!r} has wrong length.")

    @property
    def num_players(self) -> int:
        """Return the number of players."""

        return len(self.strategy_sets)

    def profiles(self) -> list[Profile]:
        """Return all strategy profiles in lexicographic product order."""

        return list(product(*self.strategy_sets))

    def payoff(self, profile: Profile, player: int | None = None) -> float | Payoff:
        """Return a payoff tuple, or a single player's payoff."""

        value = self.payoffs[profile]
        if player is None:
            return value
        return value[player]

    def unilateral_deviations(self, profile: Profile) -> Iterable[tuple[int, Profile]]:
        """Yield all unilateral deviations from ``profile``.

        Each yielded pair is ``(player, new_profile)``.
        """

        for player, strategies in enumerate(self.strategy_sets):
            for strategy in strategies:
                if strategy == profile[player]:
                    continue
                new_profile = list(profile)
                new_profile[player] = strategy
                yield player, tuple(new_profile)

    def improving_deviations(self, profile: Profile) -> list[tuple[int, Profile, float]]:
        """Return profitable unilateral deviations from ``profile``.

        Each entry is ``(player, new_profile, payoff_gain)``.
        """

        improvements: list[tuple[int, Profile, float]] = []
        for player, new_profile in self.unilateral_deviations(profile):
            gain = float(self.payoff(new_profile, player) - self.payoff(profile, player))  # type: ignore[operator]
            if gain > 0:
                improvements.append((player, new_profile, gain))
        return improvements

    def is_pure_nash(self, profile: Profile) -> bool:
        """Return whether ``profile`` is a pure Nash equilibrium."""

        return not self.improving_deviations(profile)
