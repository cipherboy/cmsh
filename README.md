# `cmsh`

High-level Python interface over [Mate Soos's](https://github.com/msoos)
[`CryptoMiniSat`](https://github.com/msoos/cryptominisat).

	Copyright (C) 2019 Alexander Scheel
	Licensed under the terms of the GPLv3.

[GPLv3](LICENSE) | [Building Instructions](docs/building.md) |
[API Documentation](docs/api.md) | [Design](docs/design.md) |
[Version 0.4](https://github.com/cipherboy/cmsh/releases)

## Dependencies

The only dependencies are CryptoMiniSat, Python, and a working C++ compiler
with C++20 support.

## Building

(For more complete documentation, refer to [`building.md`](docs/building.md))

To build `cmsh`, first build CryptoMiniSat with Gaussian Elimination support:

	make cms

This will pull down the latest CryptoMiniSat and build it with Gaussian
Elimination support. If you wish to build at a specific release version
instead of latest HEAD, run:

	cd msoos_cryptominisat && git checkout <REVISION> && cd ..
	make distclean cms

Then, build `cmsh`:

	make clean all check

To install:

	cd build/
	pip3 install --user -e .

## Usage

(For more complete documentation, refer to [`api.md`](docs/api.md))

A single CryptoMiniSat SATSolver instance is exposed by a `Model`:

```python
import cmsh

m = cmsh.Model()
```

Variables can be created with `Model.var()`:

```python
a = m.var()
b = m.var()
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

There are also vectors!

```python
vec = m.vec(4)
m.add_assert(vec == 3)
m.solve()

print(vec, int(vec))
```

## Contributing

Cool! \o/ Happy to have help. The core of `cmsh` is done; mostly it is the
hard parts that remain (see the shortcomings section in the design document
for ideas). Nearly every project could use more tests and benchmarks so I'd
definitely merge those. I wouldn't be too adverse to build system improvements
either. Send a PR, file an issue, or shoot me an email if your interested, I'm
not particularly picky about these types of things or processes. I'd also take
constructive code review comments or feedback about using it in your own
projects.

Happy hacking!
