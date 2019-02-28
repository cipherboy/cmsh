# cmsh

High level Python interfaces over `pycryptosat` from [Mate Soos's](https://github.com/msoos)
[`CryptoMiniSat`](https://github.com/msoos/cryptominisat).

## Dependencies

The only dependency is `pycryptosat`.

## Usage

A single CMS Solver instance is exposed by a `Model`:

```python
import cmsh

m = cmsh.Model()
```

Variables can be created with `Model.var()` or `Model.named_var()`:

```python
a = m.var()
b = m.named_var("b")
```

Asserting a variable is true is done via `Model.add_assert(...)`:

```python
stmt = a ^ -b
m.add_assert(stmt)
```

Solutions can be seen by calling `Model.solve()` and printing the
corresponding variables:

```python
print(a, b)
print(m.solve())
print(a, b)
```

Variables can also be coerced to `int` (to get the corresponding CNF
identifier) or `bool` (to get the value after solving):

```python
print(int(a))
print(bool(b))
```

Note that `int(Variable)` can be less than zero if Variable is a negation of
another value:

```python
c = m.var()
not_c = -c

print(int(c), int(not_c))
```

Logic also works with mixed types:

```python
stmt2 = (c == True) | (c == -a)
m.add_assert(stmt2)
m.solve()
print(a, b, c)
```
