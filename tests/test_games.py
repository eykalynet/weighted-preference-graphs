from src.examples import coordination_game, prisoners_dilemma


def test_strategy_profile_enumeration() -> None:
    game = coordination_game()
    assert game.profiles() == [
        ("A", "A"),
        ("A", "B"),
        ("B", "A"),
        ("B", "B"),
    ]


def test_payoff_lookup() -> None:
    game = prisoners_dilemma()
    assert game.payoff(("C", "C")) == (3, 3)
    assert game.payoff(("D", "C"), player=0) == 5
    assert game.payoff(("C", "D"), player=1) == 5


def test_unilateral_deviations() -> None:
    game = coordination_game()
    deviations = set(game.unilateral_deviations(("A", "A")))
    assert deviations == {
        (0, ("B", "A")),
        (1, ("A", "B")),
    }


def test_improving_deviations_and_pure_nash() -> None:
    game = coordination_game()
    assert game.is_pure_nash(("A", "A"))
    assert game.is_pure_nash(("B", "B"))
    assert not game.is_pure_nash(("A", "B"))
    assert set(game.improving_deviations(("A", "B"))) == {
        (1, ("A", "A"), 2.0),
        (0, ("B", "B"), 1.0),
    }
