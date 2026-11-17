# Median investigation

I checked the three implementations in [candidates.py](candidates.py) against the screenshot and kept their bodies intact. The only adaptation is a distinct function name for each candidate so they can be exercised side by side.

## Expected behavior

For a sorted numeric sequence with odd length, the median is the element at zero-based index `n // 2`. For even length, it is the arithmetic mean of the values at `n // 2 - 1` and `n // 2`. I used a sequence contract with conventional truthiness and treated `None` as an acceptable empty result because the question does not prescribe an empty-input policy.

## Observations

I ran all three functions on fresh inputs with Python 3.14.4. Giving each candidate its own input matters because A can change the list before the other candidates see it.

| Input | A | B | C |
| --- | --- | --- | --- |
| Unsorted list `[3, 0]` | `1`, list becomes `[0, 3]` | `1.5`, list unchanged | `1.5`, list unchanged |
| Negative midpoint `[0, -3]` | `-2`, list becomes `[-3, 0]` | `-1.5`, list unchanged | `-1.5`, list unchanged |
| Odd list `[9, 1, 5]` | `5`, list becomes `[1, 5, 9]` | `5`, list unchanged | `5`, list unchanged |
| Tuple `(9, 1, 5)` | `AttributeError` | `5` | `5` |
| Empty list `[]` | `IndexError` | `IndexError` | `None` |
| Empty iterator `iter(())` | `AttributeError` | `IndexError` | `IndexError` |
| `Decimal("0.20")` and `Decimal("0.30")` | `Decimal('0')` | `TypeError` | `Decimal('0.25')` |

The even integer cases show the effect of `// 2`. The sum is 3 in the first row and -3 in the second, so A gives 1 and -2 where the arithmetic means are 1.5 and -1.5. The tuple checks whether the implementation requires a mutating `.sort()` method. The Decimal case shows that B's float divisor is incompatible with Decimal arithmetic.

For an empty list, A and B enter the even-length branch and try to index an empty collection. C returns early because the list is falsey. An empty iterator is truthy, so C skips its guard and still indexes an empty list after sorting. In an API that accepts arbitrary iterables, the empty check would need to run after materializing the iterable.

The five [characterization tests](test_candidates.py) codify the central observations, including the defects. A green test run means the candidate behavior was reproduced.
