# Research Log

## Example 1

Date: 2026-05-15

Game class: Two-player, two-strategy normal-form games with integer payoffs in `{-2, -1, 0, 1, 2}`.

Payoff matrices:

Game A:

|              | Player 2: 0 | Player 2: 1 |
|--------------|-------------|-------------|
| Player 1: 0  | `(-2, -2)` | `(-2, -1)` |
| Player 1: 1  | `(-1, -2)` | `(-2, -2)` |

Game B:

|              | Player 2: 0 | Player 2: 1 |
|--------------|-------------|-------------|
| Player 1: 0  | `(-2, -2)` | `(-2, -1)` |
| Player 1: 1  | `(0, -2)`  | `(-2, -2)` |

Unweighted graph structure:

Both games have the same strategy-profile vertex set:

```text
(0, 0), (0, 1), (1, 0), (1, 1)
```

Both games have the same unweighted improving edges:

```text
(0, 0) -> (0, 1)  by player 2
(0, 0) -> (1, 0)  by player 1
```

The sink vertices, hence pure Nash equilibria, are:

```text
(0, 1), (1, 0), (1, 1)
```

Weighted graph differences:

Game A has equal gain on the two outgoing edges from `(0, 0)`:

```text
(0, 0) -> (0, 1)  weight 1
(0, 0) -> (1, 0)  weight 1
```

Game B has a larger gain on the player 1 deviation:

```text
(0, 0) -> (0, 1)  weight 1
(0, 0) -> (1, 0)  weight 2
```

Dynamics tested:

Deterministic payoff-sensitive asynchronous better-response dynamics. At each profile, the dynamic chooses an improving edge of maximum payoff gain; ties are broken deterministically by profile order.

What happened:

The unweighted preference graphs are identical, but the payoff-sensitive basin sizes differ.

Game A basin sizes:

```text
(0, 1): 2
(1, 0): 1
(1, 1): 1
```

Game B basin sizes:

```text
(0, 1): 1
(1, 0): 2
(1, 1): 1
```

The difference occurs at `(0, 0)`. In Game A, the two improving deviations have equal weight, so deterministic tie-breaking sends `(0, 0)` to `(0, 1)`. In Game B, the edge to `(1, 0)` has larger weight, so the payoff-sensitive rule sends `(0, 0)` to `(1, 0)`.

Possible theorem/conjecture:

The unweighted preference graph is not sufficient to determine equilibrium selection for payoff-sensitive better-response dynamics. More specifically, even among `2x2` finite games, there exist ordinally equivalent games with different weighted preference graphs whose deterministic max-gain better-response basins differ.

## Example 2

Date: 2026-05-15

Game class: Two-player, two-strategy normal-form games with integer payoffs in `{-2, -1, 0, 1, 2}`.

Payoff matrices:

Game A:

|              | Player 2: 0 | Player 2: 1 |
|--------------|-------------|-------------|
| Player 1: 0  | `(-2, -2)` | `(-2, -1)` |
| Player 1: 1  | `(0, -2)`  | `(-2, -2)` |

Game B:

|              | Player 2: 0 | Player 2: 1 |
|--------------|-------------|-------------|
| Player 1: 0  | `(-2, -2)` | `(-2, 0)`  |
| Player 1: 1  | `(-1, -2)` | `(-2, -2)` |

Unweighted graph structure:

Both games have the same strategy-profile vertex set:

```text
(0, 0), (0, 1), (1, 0), (1, 1)
```

Both games have the same unweighted improving edges:

```text
(0, 0) -> (0, 1)  by player 2
(0, 0) -> (1, 0)  by player 1
```

The sink vertices, hence pure Nash equilibria, are the same in both games:

```text
(0, 1), (1, 0), (1, 1)
```

Weighted graph differences:

Game A has a unique maximum-gain edge from `(0, 0)` to `(1, 0)`:

```text
(0, 0) -> (0, 1)  weight 1
(0, 0) -> (1, 0)  weight 2
```

Game B has a unique maximum-gain edge from `(0, 0)` to `(0, 1)`:

```text
(0, 0) -> (0, 1)  weight 2
(0, 0) -> (1, 0)  weight 1
```

Dynamics tested:

Deterministic payoff-sensitive asynchronous better-response dynamics. At each profile, the dynamic chooses an improving edge of maximum payoff gain; ties are broken deterministically by profile order.

What happened:

The unweighted preference graphs and pure Nash equilibria are identical, but deterministic max-gain better-response dynamics selects different equilibria from `(0, 0)`.

Game A basin sizes:

```text
(0, 1): 1
(1, 0): 2
(1, 1): 1
```

Game B basin sizes:

```text
(0, 1): 2
(1, 0): 1
(1, 1): 1
```

Possible theorem/conjecture:

The unweighted preference graph, even together with the set of pure Nash equilibria, is not sufficient to determine equilibrium selection under deterministic max-gain better-response dynamics. This failure does not require tie-breaking: the unique maximum-gain improving edge can point to different sink equilibria in ordinally equivalent games.
