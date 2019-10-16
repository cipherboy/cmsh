# `cmsh` Python API reference

## Using

```python
import cmsh

model = cmsh.Model()
var = model.variablem()
vec = model.vector(32)

assert isinstance(var, cmsh.Variable)
assert isinstance(vec, cmsh.Vector)
```

## Terminology

A `cmsh.Variable` is an input or output in a logic gate. These are sometimes
backed by variables in the CNF, but always passed through to the native layer.
Operations taking variables can transparently handle `bool`s as well. They may
return a `bool` instead of a variable depending on the operation (e.g.,
`var & True == var`, but `var & False == False`).

A `cmsh.Vector` is composed of multiple `cmsh.Variable` instances, to form a
vector of a specified width. These have bitwise operators defined over them,
along with addition and bitwise summation. They can be used interchangeably
with lists or tuples of variables (or `bool`s) or integers (assuming the value
of the `int` doesn't exceed the width of the vector). Any operation returning
a vector will return an instance of `cmsh.Vector`; this is true even when all
members are instances of `bool` and not `cmsh.Variable`.

## Classes

We expose three classes in `cmsh`:

 1. [`cmsh.Model`](#cmshmodel)
 2. [`cmsh.Variable`](#cmshvariable)
 3. [`cmsh.Vector`](#cmshvector)

### `cmsh.Model`

Central state for solving. Note that values (variables, vectors, etc.) from
other models cannot mix.

To use the model, construct a new instance. No member functions are static;
all apply to a specific model instance.

```python
m = cmsh.Model()
```

#### Creating Objects

##### `cmsh.Model.variable() -> cmsh.Variable`

alias: `cmsh.Model.var`

Use to create a new variable. See description above on the specifics of a
variable or refer to later documentation on `cmsh.Variable` and its members.

Example:

```python
model = cmsh.Model()
left = model.variable()
right = model.variable()
assert left.identifier != right.identifier
model.add_assert(left | right)
model.solve()
print(bool(left), bool(right), bool(left) or bool(right))
```

##### `cmsh.Model.vector(width: int) -> cmsh.Vector`

alias: `cmsh.Model.vec`

Use to construct a new vector of the specified width. See description above
on the specifics of a Vector or refer to later documentation on `cmsh.Vector`
and its members.

Example:

```python
model = cmsh.Model()
vec = model.vector(4)
model.add_assert(vec == 3)
model.solve()
print(int(vec))
```

##### `cmsh.Model.to_vector(other, width=None) -> cmsh.Vector`

alias: `cmsh.Model.to_vec`

Converts a vector-like `object` (usually a `list` or `tuple` of variable-like
objects or an `int`) to a `cmsh.Vector` class instance. Optionally, make the
resulting vector of a specific `width`.

This lets you upcast into a vector, to use all the methods defined by it on
objects not originally created through `cmsh.Model.vec`.

Example:

```python
model = cmsh.Model()
four = model.to_vec(4, width=8)
vec = model.vector(8)

model.add_assert(vec == four)
model.solve()
print(int(vec))
```

#### Reshaping Vectors

Often you'll want to reshape a `cmsh.Vector` from being flat to a list of
`cmsh.Vector`s of a smaller size, or visa-versa. These methods help with that.

##### `cmsh.Model.split_vec(vector, width: int) -> List[cmsh.Vector]`

Split a single vector into multiple vectors with the specified `width`. Note
that the input vector must have a width that is a multiple of `width`.

Example:

```python
model = cmsh.Model()
uint32_t = model.vector(32)
uint8_ts = model.split_vec(uint32_t, 8)

model.add_assert(uint8_ts[0] == 0x12)
model.add_assert(uint8_ts[1] == 0x34)
model.add_assert(uint8_ts[2] == 0x56)
model.add_assert(uint8_ts[3] == 0x78)
model.solve()

assert int(uint32_t) == 0x12345678
```

##### `cmsh.Model.join_vec(vectors) -> cmsh.Vector`

Join multiple vectors (or, vector-like objects) into a single `cmsh.Vector`
of the combined width of all of them. This preserves the relative order
between them.

Example:

```python
model = cmsh.Model()
left = model.vector(16)
right = model.vector(16)
whole = model.join_vec((left, right))

model.add_assert(left == 0x90ab)
model.add_assert(right == 0xcdef)
model.solve()

assert int(whole) == 0x90abcdef
```

#### Building a Model

##### `cmsh.Model.add_assert(var: Union[int, cmsh.Variable])`

Add an assertion to the underlying model. Assertions is how you ground the
model and tell it what to solve for: any clause which is required to derive
the assertion is added to the CNF. This is usually a component of the
high-level goal you're trying to solve for, e.g., that there's a collision or
that the Sudoku is valid.

Once added, assertions cannot be removed; for removable assertions, see
assumptions.

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()
output = left | right

model.add_assert(output)
model.add_assert(left)
model.solve()

assert bool(left) or bool(right)
assert bool(output)
assert bool(left)
```

##### `cmsh.Model.add_assume(var: Union[int, cmsh.Variable])`

Add an assumption about the value of a variable to the underlying model. This
is similar to assertions in that they'll also get clauses added, but are
removable. These are passed to the solver each time: if an assumption causes
the model to be unsatisfiable, a latter call without that assumption can
result in a satisfiable model.

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()
output = left | right

model.add_assume(output)
model.add_assume(left)
model.solve()

assert bool(left) or bool(right)
assert bool(output)
assert bool(left)
```

##### `cmsh.Model.remove_assume(var: Union[int, cmsh.Variable])`

Remove both polarity assumptions about the value of a variable.

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()
output = left | right

model.add_assert(output)
model.add_assume(-left)
model.solve()

assert bool(output)
assert not bool(left)

model.remove_assume(left)
model.add_assume(left)
model.solve()

assert bool(output)
assert bool(left)
```

#### Solving

##### `cmsh.Model.solve() -> Optional[bool]`

Solve the current model and return its satisfiability: `True` if the model is
SAT, `False` if the model is UNSAT, and `None` if a conclusion wasn't reached,
likely due to hitting a limit.

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()

model.add_assert(left & right)
assert model.solve()

model.add_assert(left ^ right)
assert not model.solve()
```

##### `cmsh.Model.negate_solution(variables) -> cmsh.Variable`

Helper method to negate a solution. Given a collection of variables, negate
the solution to find a different one in incremental solving. This is
equivalent to the following statement:

    !((variables[0] == bool(variables[0])) &
      (variables[1] == bool(variables[1])) & ... )

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()

model.add_assert(left | right)
assert model.solve()

negated = model.negate_solution([left, right])
model.add_assert(negated)

assert model.solve()

negated = model.negate_solution([left, right])
model.add_assert(negated)

assert model.solve()

negated = model.negate_solution([left, right])
model.add_assert(negated)

assert not model.solve()
```

##### `cmsh.Model.cleanup()`

Clean up all internal memory allocated by the model, preventing its future
usability. Call this only when the model (and all its variables and vectors)
are no longer needed, if you can't wait for the garbage collector.

Some models grow large; when doing parallel solving on separate instances,
it is useful to be able to explicitly free the memory before continuing on to
the next problem. Since a lot of the memory allocated isn't in Python, it is
nice to be able to explicitly discard it when it isn't needed. This includes
data in both the native `cmsh` portion and in CryptoMiniSat.

#### Members

##### `cmsh.Model.sat: Optional[bool]`

Instance variable. Whether or not the model has been solved. Has one of three
values:

	- `None` when the model hasn't been fully solved yet.
	- `True` when the model has been solved and is satisfiable.
	- `False` when the model has been solved and unsatisfiable.

Note that if new clauses are added to the model, `cmsh.Model.sat` will remain
at its previous value and will not go to `None`. If however, `solve(...)` is
called but interrupted (e.g., due to reaching a limit), it will again take
the value `None`.

Example:

```python
model = cmsh.Model()
left = model.var()
model.add_assert(left)
model.solve()

assert model.sat
```

#### Internal Methods

##### `cmsh.Model.neg_var(var: Union[int, cmsh.Variable]) -> cmsh.Variable`

Negate and upcast a variable (or its identifier) into a `cmsh.Variable`,
returning the result. It is preferential to use the `__neg__` operator on the
variable instead (`-var`).

##### `cmsh.Model.add_constraint(left: int, operator: str, right: int) -> cmsh.Variable`

Add a constraint to the underlying native model. Shouldn't be used, instead
use the member functions of `cmsh.Variable`.

### `cmsh.Variable`

This represents a known or unknown boolean value in the overall model.
Operations performed on Variables instances are automatically added to the
model. Each operation returns a new variable instance when appropriate, unless
it is a duplicate instance of the same operation:

```python
model = cmsh.Model()
left = model.var()
right = model.var()

op1 = left & right
op2 = right & left

assert isinstance(op1, cmsh.Variable)
assert op1.identifier == op2.identifier
```

The identifier of a variable in the underlying circuit can be found via
checking the value of `identifier` or by coercing the variable to an `int`.
Once the model is solved, its solved value can be found through `get_value()`
or by coercing the variable to a `bool`. However, when the model hasn't been
solved, `get_value()` will return None and `bool` will be forced to throw an
exception. For example:

```python
model = cmsh.Model()

left = model.var()
assert left.identifier == int(left.identifier)

assert left.get_value() == None
bool(left) # -- throws an exception

model.add_assert(left)
model.solve()

assert left.get_value() == bool(left) == True
```

The overall philosophy of both `cmsh.Variable` and `cmsh.Vector` is to be as
friendly as possible to constructing models. The process of constructing a
model should be exactly the same as evaluating the model under a given set of
values. Partial evaluation of models should result in simplified models by
propagating literal values as far as possible without invoking the solver.

#### Native Python Operators

##### `cmsh.Variables.__and__(other) -> cmsh.Variable`

Compute the logical AND operation between this variable and the `other`
variable-like object. Other can either be another `cmsh.Variable`, an `int`
(representing the identifier of a variable in the model), or a `bool`
(representing a literal value).

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()

model.add_assert(left & right)
model.add_assert(left & True)
model.solve()

print(left, right)
```

##### `cmsh.Variables.__or__(other) -> cmsh.Variable`

Compute the logical OR operation between this variable and the `other`
variable-like object. Other can either be another `cmsh.Variable`, an `int`
(representing the identifier of a variable in the model), or a `bool`
(representing a literal value).

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()

model.add_assert(left | right)
model.add_assert(left | False)
model.solve()

print(left, right)
```

##### `cmsh.Variables.__xor__(other) -> cmsh.Variable`

Compute the logical XOR operation between this variable and the `other`
variable-like object. Other can either be another `cmsh.Variable`, an `int`
(representing the identifier of a variable in the model), or a `bool`
(representing a literal value).

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()

model.add_assert(left ^ right)
model.add_assert(left ^ True)
model.solve()

print(left, right)
```

##### `cmsh.Variables.__pos__() -> cmsh.Variable`

Take the positive form of a variable, i.e., the variable as it is. Provided
for parity with `__neg__`.

Example:

```python
model = cmsh.Model()
left = model.var()

model.add_assert(+left)
model.solve()

print(left)
```

##### `cmsh.Variables.__neg__() -> cmsh.Variable`

Negative a variable, returning a new instance. This is done by changing the
sign on the identifier and does not touch the underlying model.

Example:

```python
model = cmsh.Model()
left = model.var()

model.add_assert(-left)
model.solve()

print(left, int(left), int (-left))
```

#### Comparison Operators

##### `cmsh.Variables.__lt__(other) -> cmsh.Variable`

Creates a series of gates representing whether or not this variable is
strictly less than `other`. Other can either be another `cmsh.Variable`, an
`int` (representing the identifier of a variable in the model), or a `bool`
(representing a literal value).

Truth Table:

```
self  | other | self < other
----------------------------
False | False | False
False | True  | True
True  | False | False
True  | True  | False
```

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()

model.add_assert(left < right)
model.solve()

print(left, right)
```

##### `cmsh.Variables.__le__(other) -> cmsh.Variable`

Creates a series of gates representing whether or not this variable is less
than or equal to `other`. Other can either be another `cmsh.Variable`, an
`int` (representing the identifier of a variable in the model), or a `bool`
(representing a literal value).

Truth Table:

```
self  | other | self <= other
----------------------------
False | False | True
False | True  | True
True  | False | False
True  | True  | True
```

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()

model.add_assert(left < right)
model.solve()

print(left, right)
```

##### `cmsh.Variables.__eq__(other) -> cmsh.Variable`

Creates a series of gates representing whether or not this variable is equal
to `other`. Other can either be another `cmsh.Variable`, an `int`
(representing the identifier of a variable in the model), or a `bool`
(representing a literal value).

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()

model.add_assert(left == right)
model.solve()

print(left, right)
```

##### `cmsh.Variables.__ne__(other) -> cmsh.Variable`

Creates a series of gates representing whether or not this variable is unequal
to `other`. Other can either be another `cmsh.Variable`, an `int`
(representing the identifier of a variable in the model), or a `bool`
(representing a literal value).

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()

model.add_assert(left != right)
model.solve()

print(left, right)
```

##### `cmsh.Variables.__ge__(other) -> cmsh.Variable`

Creates a series of gates representing whether or not this variable is greater
than or equal to `other`. Other can either be another `cmsh.Variable`, an
`int` (representing the identifier of a variable in the model), or a `bool`
(representing a literal value).

Truth Table:

```
self  | other | self >= other
----------------------------
False | False | True
False | True  | False
True  | False | True
True  | True  | True
```

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()

model.add_assert(left >= right)
model.solve()

print(left, right)
```

##### `cmsh.Variables.__gt__(other) -> cmsh.Variable`

Creates a series of gates representing whether or not this variable is
strictly greater than `other`. Other can either be another `cmsh.Variable`, an
`int` (representing the identifier of a variable in the model), or a `bool`
(representing a literal value).

Truth Table:

```
self  | other | self > other
----------------------------
False | False | False
False | True  | False
True  | False | True
True  | True  | False
```

Example:

```python
model = cmsh.Model()
left = model.var()
right = model.var()

model.add_assert(left > right)
model.solve()

print(left, right)
```

#### Introspection

##### `cmsh.Variables.__int__() -> int`

Coerce the instance to an `int`, getting its identifier. This is equivalent
to accessing the `identifier` member.

Example:

```python
model = cmsh.Model()
left = model.var()
print(int(left), int(-left))
```

##### `cmsh.Variables.__abs__() -> int`

Coerce the instance to an `int`, getting the absolute value of its identifier. This is equivalent to accessing the `identifier` member and taking the
absolute value of it.

Example:

```python
model = cmsh.Model()
left = model.var()
print(abs(left), abs(-left))
```

##### `cmsh.Variables.get_value() -> Optional[bool]`

Safely get the solved value of a variable; returns `None` if not available,
else `True` or `False` if available.

```python
model = cmsh.Model()
left = model.var()

assert left.get_value() == None
model.add_assert(left)
model.solve()
assert left.get_value() == True
```

##### `cmsh.Variables.__bool__() -> bool`

Unsafely get the solved value of a variable. When the variable isn't solved
for (either because the entire model hasn't been solved or it isn't derived
from an added assertion or assumption), raises an exception due to the
contract of implementing `__bool__`.

Example:

```python
model = cmsh.Model()
left = model.var()

bool(left) # -- raises an exception
model.add_assert(left)
model.solve()
assert bool(left) == True # works, since it has been solved for
```

##### `cmsh.Variables.__str__() -> str`

Coerce the variable to a string. When `get_value()` returns None, this is the
identifier of the variable. Otherwise, returns the value of the varialbe.

Example:

```python
model = cmsh.Model()
left = model.var()

print(str(left)) # -- prints 1
model.add_assert(left)
model.solve()
print(str(left)) # -- prints True
```

#### Members

##### `cmsh.Variables.identifier`

The identifier of the variable in the underlying model.

### `cmsh.Vector`

This represents a fixed-size, ordered list of `cmsh.Variable`-like objects.
While the size of a vector can be modified directly via `insert` or `truncate`,
operations between vectors will require equal-sized operators.

#### Bitwise Vector Operators

##### `cmsh.Vector.__and__(other) -> cmsh.Vector`

Compute the bitwise logical AND operation between this vector and the `other`
vector-like object. Other can either be another `cmsh.Vector`, an `int`, or a
list or tuple of variable-like objects (`bool`, `int`, or `cmsh.Variable`).

Example:

```python
model = cmsh.Model()
left = model.vec(4)
right = model.vec(4)

model.add_assert((left & right) == 3)
model.solve()

print(left, right)
```

##### `cmsh.Vector.__or__(other) -> cmsh.Vector`

Compute the bitwise logical OR operation between this vector and the `other`
vector-like object. Other can either be another `cmsh.Vector`, an `int`, or a
list or tuple of variable-like objects (`bool`, `int`, or `cmsh.Variable`).

Example:

```python
model = cmsh.Model()
left = model.vec(4)
right = model.vec(4)

model.add_assert((left | right) == 3)
model.solve()

print(left, right)
```

##### `cmsh.Vector.__xor__(other) -> cmsh.Vector`

Compute the bitwise logical XOR operation between this vector and the `other`
vector-like object. Other can either be another `cmsh.Vector`, an `int`, or a
list or tuple of variable-like objects (`bool`, `int`, or `cmsh.Variable`).

Example:

```python
model = cmsh.Model()
left = model.vec(4)
right = model.vec(4)

model.add_assert((left & right) == 3)
model.solve()

print(left, right)
```

##### `cmsh.Vector.__pos__() -> cmsh.Vector`

Take the positive form of each elements in a vector, i.e., the vector as it
is. Provided for parity with `__neg__`.

Example:

```python
model = cmsh.Model()
left = model.var()

model.add_assert(+left)
model.solve()

print(left)
```

##### `cmsh.Vector.__neg__() -> cmsh.Vector`

Compute the bitwise negation of the vector.

Example:

```python
model = cmsh.Model()
left = model.vec(4)

model.add_assert((-left) == 4)
model.solve()

print(left)
```

#### Comparison Operators

##### `cmsh.Vector.__lt__(other) -> cmsh.Variable`

Computes whether this instance is less than the vector-like `other`.

Example:

```python
model = cmsh.Model()
left = model.vec(3)
right = model.vec(3)

model.add_assert(left < right)
model.solve()

print(left, right)
```

##### `cmsh.Vector.__le__(other) -> cmsh.Variable`

Computes whether this instance is less than or equal to the vector-like
`other`.

Example:

```python
model = cmsh.Model()
left = model.vec(3)
right = model.vec(3)

model.add_assert(left <= right)
model.solve()

print(left, right)
```

##### `cmsh.Vector.__eq__(other) -> cmsh.Variable`

Computes whether this instance is equal to the vector-like `other`.

Example:

```python
model = cmsh.Model()
left = model.vec(3)
right = model.vec(3)

model.add_assert(left == right)
model.solve()

print(left, right)
```

##### `cmsh.Vector.__neq__(other) -> cmsh.Variable`

Computes whether this instance is not equal to the vector-like `other`.

Example:

```python
model = cmsh.Model()
left = model.vec(3)
right = model.vec(3)

model.add_assert(left != right)
model.solve()

print(left, right)
```

##### `cmsh.Vector.__ge__(other) -> cmsh.Variable`

Computes whether this instance is grater than or equal to the vector-like
`other`.

Example:

```python
model = cmsh.Model()
left = model.vec(3)
right = model.vec(3)

model.add_assert(left >= right)
model.solve()

print(left, right)
```

##### `cmsh.Vector.__gt__(other) -> cmsh.Variable`

Computes whether this instance is greater than the vector-like `other`.

Example:

```python
model = cmsh.Model()
left = model.vec(3)
right = model.vec(3)

model.add_assert(left > right)
model.solve()

print(left, right)
```

#### Arithmetic Operators

##### `cmsh.Vector.__add__(other) -> cmsh.Vector`

Computes the addition of this vector to the vector-like `other`, returning
the result as a new `cmsh.Vector` of magnitude equal to the size of this
instance.

Example:

```python
model = cmsh.Model()
left = model.vec(3)
right = model.vec(3)

model.add_assert((left + right) == 3)
model.solve()

print(int(left), int(right))
```

#### Internal Vector Operators

##### `cmsh.Vector.bit_sum() -> cmsh.Vector`

Computes the sum over all bits inside the vector, returning the result as a
new `cmsh.Vector` instance. That is, how many bits in this vector are set to
`True`.

Example:

```python
model = cmsh.Model()
left = model.vec(3)

model.add_assert(left.bit_sum() == 1)
model.solve()

print(left)
```

##### `cmsh.Vector.bit_odd() -> Union[bool, cmsh.Variable]`

Computes whether or not an odd number of bits are set in this vector,
returning the result as a cmsh.Variable-like object (a `bool` if the result is
known, `cmsh.Variable` otherwise).

Example:

```python
model = cmsh.Model()
left = model.vec(3)

model.add_assert(left.bit_odd())
model.solve()

print(left)
```

##### `cmsh.Vector.bit_even() -> Union[bool, cmsh.Variable]`

Computes whether or not an even number of bits are set in this vector,
returning the result as a cmsh.Variable-like object (a `bool` if the result is
known, `cmsh.Variable` otherwise).

Example:

```python
model = cmsh.Model()
left = model.vec(3)

model.add_assert(left.bit_even())
model.add_assert(left > 1)
model.solve()

print(left)
```

##### `cmsh.Vector.bit_and() -> Union[bool, cmsh.Variable]`

Compresses the vector into a single variable-like result by applying the AND
function between all members of the vector.

Example:

```python
model = cmsh.Model()
left = model.vec(3)

model.add_assert(left.bit_and())
model.solve()

print(left)
```

##### `cmsh.Vector.bit_nand() -> Union[bool, cmsh.Variable]`

Compresses the vector into a single variable-like result by applying the NAND
function between all members of the vector.

Example:

```python
model = cmsh.Model()
left = model.vec(3)

model.add_assert(left.bit_nand())
model.solve()

print(left)
```

##### `cmsh.Vector.bit_or() -> Union[bool, cmsh.Variable]`

Compresses the vector into a single variable-like result by applying the OR
function between all members of the vector.

Example:

```python
model = cmsh.Model()
left = model.vec(3)

model.add_assert(left.bit_or())
model.solve()

print(left)
```

##### `cmsh.Vector.bit_nor() -> Union[bool, cmsh.Variable]`

Compresses the vector into a single variable-like result by applying the NOR
function between all members of the vector.

Example:

```python
model = cmsh.Model()
left = model.vec(3)

model.add_assert(left.bit_nor())
model.solve()

print(left)
```

##### `cmsh.Vector.bit_xor() -> Union[bool, cmsh.Variable]`

Compresses the vector into a single variable-like result by applying the XOR
function between all members of the vector.

Example:

```python
model = cmsh.Model()
left = model.vec(3)

model.add_assert(left.bit_xor())
model.solve()

print(left)
```

##### `cmsh.Vector.odd() -> Union[bool, cmsh.Variable]`

Computes whether the `cmsh.Vector` instance is odd, that is, whether its last
element is True.

Example:

```python
model = cmsh.Model()
left = model.vec(3)

model.add_assert(left.odd())
model.add_assert(left > 1)
model.solve()

print(left)
```

##### `cmsh.Vector.even() -> Union[bool, cmsh.Variable]`

Computes whether the `cmsh.Vector` instance is even, that is, whether its last
element is False.

Example:

```python
model = cmsh.Model()
left = model.vec(3)

model.add_assert(left.even())
model.add_assert(left > 1)
model.solve()

print(left)
```

#### Shifts and Rotations

##### `cmsh.Vector.shiftl(amount: int = 1, filler: Union[bool, cmsh.Variable] = False) -> cmsh.Vector`

Returns a new `cmsh.Vector` of the same length as this vector, created by
removing the leading `amount` items and appending `amount` new copies of
`filler` to the end. By default `amount` is 1 and `filler` is `False`, so this
function behaves like the left shift operator (`<< 1`).

Example:

```python
model = cmsh.Model()
left = model.vec(4)
right = model.vec(4)

model.add_assert(left == right.shiftl(2))
model.add_assert(right > 1)
model.solve()

print(left, right)
```

##### `cmsh.Vector.rotl(amount: int = 1) -> cmsh.Vector`

Returns a new `cmsh.Vector` of the same length as this vector, created by
removing the leading `amount` items and appending them to the end of the
vector.

Example:

```python
model = cmsh.Model()
left = model.vec(4)
right = model.vec(4)

model.add_assert(left == right.rotl(2))
model.add_assert(right.odd())
model.add_assert(right > 1)
model.solve()

print(left, right)
```

##### `cmsh.Vector.rotr(amount: int = 1) -> cmsh.Vector`

Returns a new `cmsh.Vector` of the same length as this vector, created by
removing the trailing `amount` items and prepending them to the start of the
vector.

Example:

```python
model = cmsh.Model()
left = model.vec(4)
right = model.vec(4)

model.add_assert(left == right.rotr(2))
model.add_assert(right.odd())
model.add_assert(right > 1)
model.solve()

print(left, right)
```


##### `cmsh.Vector.shiftr(amount: int = 1, filler: Optional[Union[bool, cmsh.Variable]] = None) -> cmsh.Vector`

Returns a new `cmsh.Vector` of the same length as this vector, created by
removing the trailing `amount` items and prepending `amount` new copies of
`filler` to the start. By default `amount` is 1 and `filler` is `None`, so this
function truncates by keeping the leading `len(self) - amount` bits.

Example:

```python
model = cmsh.Model()
left = model.vec(4)
right = model.vec(4)

model.add_assert(left == right.shiftr(2, filler=False))
model.add_assert(right > 1)
model.solve()

print(left, right)
```

#### Resizing Operations

##### `cmsh.Vector.truncate(width: int) -> cmsh.Vector`

Resize the vector to `width` by keeping only the trailing bits, returning the
result as a new `cmsh.Vector`.

Example:

```python
model = cmsh.Model()
left = model.vec(2)
right = model.vec(4)

model.add_assert(left == right.truncate(2))
model.add_assert(right >= 4)
model.solve()

print(left, right)
```

##### `cmsh.Vector.insert(index: int, obj: Union[bool, cmsh.Variable])`

Insert the corresponding `obj` into the vector at location `index`, growing
the size of the vector by one.

Example:

```python
model = cmsh.Model()
vec = model.vec(4)

print(vec)
vec.insert(2, True)
print(vec)
```

#### Vector-Variable Convolutions

##### `cmsh.Vector.splat_and(var: Union[bool, cmsh.Variable]) -> cmsh.Vector`

Bitwise apply the AND function to `var` and each member of this vector,
returning the result as a new `cmsh.Vector`.

Example:

```python
model = cmsh.Model()
vec = model.vec(4)
var = model.var()

model.add_assert(vec.splat_and(var) == 3)
model.solve()

print(var, vec)
```

##### `cmsh.Vector.splat_nand(var: Union[bool, cmsh.Variable]) -> cmsh.Vector`

Bitwise apply the NAND function to `var` and each member of this vector,
returning the result as a new `cmsh.Vector`.

Example:

```python
model = cmsh.Model()
vec = model.vec(4)
var = model.var()

model.add_assert(vec.splat_nand(var) == 3)
model.solve()

print(var, vec)
```

##### `cmsh.Vector.splat_or(var: Union[bool, cmsh.Variable]) -> cmsh.Vector`

Bitwise apply the OR function to `var` and each member of this vector,
returning the result as a new `cmsh.Vector`.

Example:

```python
model = cmsh.Model()
vec = model.vec(4)
var = model.var()

model.add_assert(vec.splat_or(var) == 3)
model.solve()

print(var, vec)
```

##### `cmsh.Vector.splat_nor(var: Union[bool, cmsh.Variable]) -> cmsh.Vector`

Bitwise apply the NOR function to `var` and each member of this vector,
returning the result as a new `cmsh.Vector`.

Example:

```python
model = cmsh.Model()
vec = model.vec(4)
var = model.var()

model.add_assert(vec.splat_nor(var) == 3)
model.solve()

print(var, vec)
```

##### `cmsh.Vector.splat_xor(var: Union[bool, cmsh.Variable]) -> cmsh.Vector`

Bitwise apply the XOR function to `var` and each member of this vector,
returning the result as a new `cmsh.Vector`.

Example:

```python
model = cmsh.Model()
vec = model.vec(4)
var = model.var()

model.add_assert(vec.splat_xor(var) == 3)
model.solve()

print(var, vec)
```

#### Introspection

##### `cmsh.Vector.__getitem__(key: Union[int, slice]) -> Union[bool, cmsh.Variable, cmsh.Vector]`

Allows the vector instance to be indexed, both with integers and with ranges
to extract a slice. Returns the result as a new `cmsh.Vector` (if indexed
with a slice), else as the underlying type at the index (a variable-like)
item.

Example:

```python
model = cmsh.Model()
vec = model.vec(3)

model.add_assert(vec[0])
model.add_assert(vec[1:] == 2)
model.solve()

print(vec)
```

##### `cmsh.Vector.__len__() -> int`

Returns the length of this vector instance.

Example:

```python
model = cmsh.Model()
vec = model.vec(4)

assert len(vec) == 4
```

##### `cmsh.Vector.__int__() -> int`

When solved or when only containing instances of `bool` (i.e., a literal
vector), returns its integer representation.

Example:

```python
model = cmsh.Model()
vec = model.vec(4)
eleven = model.to_vec([True, False, True, True])

model.add_assert(vec == eleven)
model.solve()

assert int(vec) == int(eleven) == 11
```

##### `cmsh.Vector.__str__() -> str`

Return a string representation of the vector from coercing each member to a
`str` This will never return the integer value of the vector; for that, use
`int`.

Example:

```python
model = cmsh.Model()
eleven = model.to_vec([True, False, True, True])

print(str(eleven))
```
