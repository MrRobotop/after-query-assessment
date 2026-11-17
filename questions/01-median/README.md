# Question 1 · Programming best practices

**Best to worst** · C → B → A

C and B preserve the input and compute fractional medians, with C ranking first because it handles empty sequences explicitly. A mutates the caller’s list, floors fractional medians, and raises `IndexError` on an empty list.

## Supporting reasoning

I assumed a Python 3 library API for numeric sequences where `None` is the documented result for an empty sequence. With `[3, 0]`, A changes the input to `[0, 3]` and returns `1` for a median of `1.5`. B and C both return `1.5` and leave the list in its original order. On pairs of `Decimal` values, C's division by the integer `2` also works, while B's float divisor raises `TypeError`.

C's `if not nums` guard depends on the input being a sequence with conventional truthiness. An empty generator is truthy, so C and B both raise `IndexError` after sorting it into an empty list. An iterable API with defined empty behavior would need to evaluate emptiness after materializing the input.

## Run

```sh
python3 -m unittest discover -s questions/01-median -v
```
