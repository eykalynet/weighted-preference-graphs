from src.search import (
    compare_games,
    find_pairs_with_different_payoff_sensitive_basins,
    find_unique_max_flip_pair,
    format_payoff_table,
    format_unique_max_flip_comparison,
    two_by_two_games,
)


def test_two_by_two_games_generates_expected_number_for_tiny_range() -> None:
    assert len(list(two_by_two_games((0, 1)))) == 2**8


def test_search_finds_pair_with_same_graph_different_weights_and_basins() -> None:
    pairs = find_pairs_with_different_payoff_sensitive_basins(
        payoff_values=(0, 1, 2),
        max_pairs=1,
    )
    assert len(pairs) == 1
    comparison = pairs[0]
    assert comparison.same_unweighted_graph
    assert comparison.different_weighted_edges
    assert comparison.different_basin_sizes


def test_compare_games_reports_pair_data() -> None:
    pair = find_pairs_with_different_payoff_sensitive_basins(
        payoff_values=(0, 1, 2),
        max_pairs=1,
    )[0]
    comparison = compare_games(pair.first, pair.second)
    assert comparison.same_unweighted_graph
    assert comparison.different_weighted_edges


def test_format_payoff_table() -> None:
    game = next(two_by_two_games((0,)))
    output = format_payoff_table(game)
    assert "Payoff table:" in output
    assert "(0, 0): (0.0, 0.0)" in output


def test_search_finds_unique_max_flip_pair() -> None:
    result = find_unique_max_flip_pair(payoff_values=(-2, -1, 0, 1, 2))
    assert result is not None
    assert result.comparison.same_unweighted_graph
    assert result.comparison.different_weighted_edges
    assert result.comparison.different_basin_sizes
    assert result.first_max_target != result.second_max_target


def test_format_unique_max_flip_comparison() -> None:
    result = find_unique_max_flip_pair(payoff_values=(-2, -1, 0, 1, 2))
    assert result is not None
    output = format_unique_max_flip_comparison(result)
    assert "Unique max-gain flip witness" in output
    assert "Flip profile:" in output
