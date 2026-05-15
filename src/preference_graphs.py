"""Preference graph construction for finite games."""

from __future__ import annotations

from typing import Any

import networkx as nx

from .games import NormalFormGame, Profile


def preference_graph(game: NormalFormGame) -> nx.DiGraph:
    """Construct the unweighted preference graph of ``game``.

    Vertices are strategy profiles. There is a directed edge ``s -> t`` when
    ``t`` differs from ``s`` in exactly one player's strategy and that player
    strictly improves their payoff by switching from ``s`` to ``t``.
    """

    graph = nx.DiGraph(name=game.name)
    graph.add_nodes_from(game.profiles())
    for profile in game.profiles():
        for player, new_profile, _gain in game.improving_deviations(profile):
            graph.add_edge(profile, new_profile, player=player)
    return graph


def weighted_preference_graph(game: NormalFormGame) -> nx.DiGraph:
    """Construct the weighted preference graph of ``game``.

    The edge set is the same as the unweighted preference graph, and each edge
    has attributes ``player`` and ``weight``. The weight is the deviating
    player's payoff gain.
    """

    graph = nx.DiGraph(name=game.name)
    graph.add_nodes_from(game.profiles())
    for profile in game.profiles():
        for player, new_profile, gain in game.improving_deviations(profile):
            graph.add_edge(profile, new_profile, player=player, weight=gain)
    return graph


def pure_nash_equilibria(game: NormalFormGame) -> list[Profile]:
    """Return pure Nash equilibria as sink vertices of the preference graph."""

    graph = preference_graph(game)
    return [node for node in graph.nodes if graph.out_degree(node) == 0]


def graph_summary(game: NormalFormGame) -> str:
    """Return a short text summary of the core graph data."""

    graph = weighted_preference_graph(game)
    weights: dict[tuple[Any, Any], float] = {
        (source, target): data["weight"]
        for source, target, data in graph.edges(data=True)
    }
    return "\n".join(
        [
            f"Game: {game.name}",
            f"Number of vertices: {graph.number_of_nodes()}",
            f"Number of improving edges: {graph.number_of_edges()}",
            f"Pure Nash equilibria: {pure_nash_equilibria(game)}",
            f"Weighted edges: {weights}",
        ]
    )
