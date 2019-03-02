from .array import *
from .arith import ripple_carry_adder, sum_array, flatten
from .var import Variable


class Vector:
    variables = None
    count = None
    model = None

    def __init__(self, model, width=None, vector=None):
        self.model = model

        if width and vector:
            raise ValueError("Cannot specify both width and vector!")
        elif not width and not vector:
            raise ValueError("Must specify either width or vector!")

        if width:
            self.variables = []
            for i in range(0, width):
                self.variables.append(self.model.var())

        if isinstance(vector, Vector):
            self.variables = vector.variables[:]
        elif isinstance(vector, (list, tuple)):
            self.variables = vector[:]

        self.count = len(self.variables)
        self.variables = tuple(self.variables)

    def bit_sum(self):
        return sum_array(self)

    def bit_odd(self):
        return self.bit_sum()[-1]

    def bit_even(self):
        return b_not(self.bit_odd())

    def odd(self):
        return self.variables[-1]

    def even(self):
        return b_not(self.odd())

    def bit_and(self):
        return flatten(self, b_and)

    def bit_nand(self):
        return flatten(self, b_nand)

    def bit_or(self):
        return flatten(self, b_or)

    def bit_nor(self):
        return flatten(self, b_nor)

    def bit_xor(self):
        return flatten(self, b_xor)

    def rotl(self, amount=1):
        amount = abs(amount) % (self.count+1)
        new_vec = self.variables[amount:] + self.variables[:amount]
        return self.model.to_vector(new_vec)

    def rotr(self, amount=1):
        amount = abs(amount) % (self.count+1)
        new_vec = self.variables[-amount:] + self.variables[:-amount]
        return self.model.to_vector(new_vec)

    def shiftl(self, amount=1, filler=False):
        amount = abs(amount) % (self.count+1)
        new_vec = self.variables[amount:] + tuple([filler]*amount)
        return self.model.to_vector(new_vec)

    def shiftr(self, amount=1, filler=False):
        amount = abs(amount) % (self.count+1)
        new_vec = tuple([filler]*amount) + self.variables[:-amount]
        return self.model.to_vector(new_vec)

    def __add__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        result, _ = ripple_carry_adder(self, other)
        return result

    def __and__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_and(self, other)

    def __xor__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_xor(self, other)

    def __or__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_or(self, other)

    def __radd__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        result, _ = ripple_carry_adder(self, other)
        return result

    def __rand__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_and(self, other)

    def __rxor__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_xor(self, other)

    def __ror__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_or(self, other)

    def __lt__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_lt(self, other)

    def __le__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_le(self, other)

    def __eq__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            msg = "Can't compare Vector with %s" % type(other)
            raise TypeError(msg)
        return l_eq(self, other)

    def __ne__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            msg = "Can't compare Vector with %s" % type(other)
            raise TypeError(msg)
        return l_ne(self, other)

    def __gt__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_gt(self, other)

    def __ge__(self, other):
        if not isinstance(other, (Vector, int, list, tuple)):
            return NotImplemented
        return l_ge(self, other)

    def __len__(self):
        return self.count

    def __neg__(self):
        return l_not(self)

    def __pos__(self):
        return self

    def __abs__(self):
        return tuple(map(abs, self.variables))

    def __getitem__(self, key):
        return self.variables[key]

    def __hash__(self):
        return self.variables.__hash__()

    def __int__(self):
        b = map(lambda x: str(int(bool(x))), self.variables)
        return int("".join(b), 2)

    def __str__(self):
        result = "<"
        result += ", ".join(map(str, self.variables))
        result += ">"

        return result
