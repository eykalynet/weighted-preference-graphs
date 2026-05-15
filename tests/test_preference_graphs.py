from src.examples import coordination_game, prisoners_dilemma
from src.preference_graphs import (
    format_preference_graphs,
    preference_graph,
    pure_nash_equilibria,
    weighted_preference_graph,
)


def test_unweighted_preference_graph_for_coordination_game() -> None:
    game = coordination_game()
    graph = preference_graph(game)
    assert graph.number_of_nodes() == 4
    assert set(graph.edges()) == {
        (("A", "B"), ("A", "A")),
        (("A", "B"), ("B", "B")),
        (("B", "A"), ("A", "A")),
        (("B", "A"), ("B", "B")),
    }


def test_weighted_preference_graph_for_coordination_game() -> None:
    game = coordination_game()
    graph = weighted_preference_graph(game)
    assert graph[("A", "B")][("A", "A")]["weight"] == 2
    assert graph[("A", "B")][("B", "B")]["weight"] == 1
    assert graph[("B", "A")][("A", "A")]["weight"] == 2
    assert graph[("B", "A")][("B", "B")]["weight"] == 1


def test_pure_nash_equilibria_are_sink_vertices() -> None:
    game = coordination_game()
    graph = preference_graph(game)
    equilibria = pure_nash_equilibria(game)
    assert set(equilibria) == {("A", "A"), ("B", "B")}
    assert all(graph.out_degree(profile) == 0 for profile in equilibria)


def test_prisoners_dilemma_preference_graph() -> None:
    game = prisoners_dilemma()
    graph = weighted_preference_graph(game)
    assert graph.number_of_nodes() == 4
    assert graph.number_of_edges() == 4
    assert pure_nash_equilibria(game) == [("D", "D")]
    assert graph[("C", "C")][("D", "C")]["weight"] == 2
    assert graph[("C", "C")][("C", "D")]["weight"] == 2


def test_format_preference_graphs_is_hand_inspectable() -> None:
    output = format_preference_graphs(coordination_game())
    assert "Vertices:" in output
    assert "Unweighted preference graph edges:" in output
    assert "Weighted preference graph edges:" in output
    assert "('A', 'B') -> ('A', 'A')  (player 2, weight 2)" in output
