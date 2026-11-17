# Question 1 · Programming best practices

**Best to worst** · C → B → A

C and B preserve the order of the caller’s numeric sequence and compute fractional medians, with C ranking first for its explicit handling of empty sequences. A mutates the caller’s list, floors fractional medians for integer inputs, and raises `IndexError` on an empty list.

[Investigation, observed outputs, and ranking assumptions](INVESTIGATION.md)

## Run

```sh
python3 -B -m unittest discover -s questions/01-median -v
```
