# Design of `cmsh`

## Rationale

`cmsh` stemmed from an urge to improve an existing part of the
[`hash_framework`](https://github.com/cipherboy/hash_framework) solving
framework. The old workflow went something like this:

 1. Generate a circuit with associated lookup dictionary,
 2. Write all parts of the circuit to disk and assemble it,
 3. Pass the circuit to [`bc2cnf`](https://users.ics.aalto.fi/tjunttil/circuits/) to generate a CNF,
 4. Pass the CNF to [`cryptominisat5`](https://github.com/msoos/cryptominisat#command-line-usage),
 5. Parse the output and the input CNF into the solution.

There was significant overhead in serializing the circuit to disk, passing it
to `bc2cnf`, and deserializing the result. Additionally, the internal format
wasn't very efficient, leaving much to be desired.

From a personal perspective, I really dislike hand-writing CNF. My `bc2cnf`
transformation disabled all optimizations to simplify reconstructing the
original model and all values I was interested in. Anything that let me abuse
the Python type system to both evaluate and solve models with the same code
was a bonus.

Thus began `cmsh`. One issue though, was the speed of Python: if you naively
give `pycryptosat` all variables and clauses (including those inferable as
direct consequences from the assertions), the time to solve the model will be
far greater than walking the tree to remove those clauses, solving the reduced
model, and re-computing the values of those clauses.

## Design

This lead to the current split design of `cmsh` in three parts: a C++
component for speed, a Python binding library (`cmsh._native`), and the
high-level interface I wanted. Since most of the systems I've historically run
on lacked CryptoMiniSat (and `cryptominisat5` shipped in most distributions
lacks Guassian Elimination support), I decided to build CryptoMiniSat in-tree.

While some portions of `cmsh` (especially the `cmsh.Vector` code) resemble
something better suited for a SMT solver, I've largely stayed away from that.
I've yet to implement subtraction, multiplication, division, and modulus for
that reason. Plus, most cryptographic hash functions (the original project this
was written to support) don't require anything more than addition (or at worst,
multiplication). I've looked at [Z3](https://github.com/Z3Prover/z3) and was
never overly fond of it or the performance I got out of it for my instances.

### C++ API

This portion of `cmsh` is shipped within the `src/` folder.

The header file `cmsh.h` is well documented and provides order to the chaos
that is `constraint_t.cpp` and `model_t.cpp`. I happen to love the contains
method and a few other modern C++ techniques that makes it a touch more
Pythonic. With a few changes though, I'm sure the minimum C++ version could
be lowered a bit.

The `constraint_t` class is largely simple. It's hashable, though I'm not
sure any more that it needs to be (only pointers to `constraint_t` are added
in the hash maps).

The whole gate to CNF transformation is done by a simple Tseitin
transformation. I'm not too attached to it though--if there is a definitively
better transformation that operates on a gate level, I'd definitely go for it.
If it requires knowledge of multiple gates, I'm less fond, but would consider
it depending on the solving speed up. I also don't show xor clauses, leaving
that to be detected by CMS. In part that's because I'm adding a gate (with
explicit output) rather than a pure "clause". That could be a source for
improvements as well.

The `model_t` class is the more complicated class. It comprises most of the
public interface to `cmsh` (as `constraint_t`s instances are largely hidden
from the caller). I think a little of it is overkill, but I haven't cared
too much about pruning its memory usage lately.

### Python Bindings

This portion of `cmsh` is shipped within the `bindings/` folder.

This portion is relatively straight forward and provides opinionated
bindings over the C++ API. The documentation is largely a rewritten form of
the comments in `cmsh.h` and are a touch excessive for an internal binding
layer. However, if anyone wishes to reuse `cmsh._native` without using the
rest of the Python bindings, they're certainly free to. The bindings were
largely modeled after `pycryptosat`, but with a few simplifications and
improvements due to only supporting Python 3. These improvements were likely
taken from experimenting and looking at the CPython source code to see what
other binding modules did.

### Python

This portion of `cmsh` is shipped within the `python/` folder.

At one point it was a goal to provide [MyPy](http://mypy-lang.org/) typing for
everything here. That resulted in the lengthy `var.py` and `vec.py` including
everything relevant for those methods. I've given up (due to issues with
clarifying arguments and return types) on that project though.

There's three classes (`Model`, `Variable`, and `Vector`) and plenty of
comments and small helper methods. This is really what makes `cmsh` a nice,
usable library. A lot of errors can be detected prior to solving the model,
and most things "just work" (TM).

In `var.py`, I've separated out the class interface, the typing helpers, and
the call-back-into-the-native-library helpers. The typing helpers (to
abstract over the differences between `bool`, `int`, and `cmsh.Variables`)
begin with `b_`. The native helpers begin with `v_` as it originally stood
for "variable".

The same approach is applied to `vec.py` and perhaps wasn't the best of ideas,
but was luckily simplified: only one layer here, `l_` prefixed methods. These
handle the conversion of input arguments and apply `b_` methods as appropriate.
With a few upcasts, callers of `cmsh` can almost entirely ignore these methods
though (since `cmsh.Vector` can hold whole literals unlike `cmsh.Variables`).

There's only one adder implementation, a ripple carry adder. Earlier I had
done a performance comparison of solving hash functions with different adders
and found RCA was the best. Its simple to implement too. I suppose we could
make this configurable, but I'm not to eager to do that (especially since
`+` can't take an additional argument to override the choice of adder for
one call). Best to leave these external-but-adjacent to `cmsh.Vector` I think.

## Shortcomings

There's a few things I wish to improve, given the chance:

 1. Exposing conflicts up to the Python API.
 2. Improving the complexity and cost of building the CNF.
 3. Experimenting with the Cube and Conquer method.
 4. Saving intermediate forms.

Exposing conflicts is largely simple, but once done, would let me experiment
with the Cube and Conquer
[method](https://www.cs.utexas.edu/~marijn/publications/CCshort.pdf). If
there's performance improvements to be had by understanding the circuit
construction of the model (instead of the raw CNF), I could implement it in
`cmsh`. Otherwise, upstreaming this to CryptoMiniSat would be the best course
of action.

Additionally, the time cost of converting between the internal circuit and the
CNF is occasionally high and dominates the actual cost of solving the model.
This is largely a problem in the algorithms of `add_reachable` and
`extend_solution`, but it isn't immediately obvious (to me) how to improve them.
Perhaps this would also warrant converting `model_t::solution` to an map of
`int->lbool`, but I've not yet made that change internally (the logic for
applying operators changes as a result).

I'm not sure if saving intermediate forms is of wide interest to people. From
an academic perspective, it'd be nice to point to the specific CNF models that
were used. Beyond that, I don't think saving in the circuit language would
personally be of use, but perhaps it would be for someone else. I'd love graph
visualizations of circuits, but without names for variables (which aren't
surfaced down to the native layer), I'm not sure you'd be able to see much of
interest or have a way to intelligently filter things (especially for larger
models like hash functions).
