from .logic import *


class Variable:
    identifier = 0
    value = None
    model = None

    def __init__(self, model, identifier=None):
        if identifier:
            self.identifier = identifier
        else:
            self.identifier = model.next_var_identifier()
        self.model = model

    def get_value(self):
        self.value = self.model.get_value(self.identifier)
        return self.value

    def __add__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_or(self, other)

    def __sub__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_or(self, b_not(other))

    def __mul__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_and(self, other)

    def __div__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_and(self, b_not(other))

    def __and__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_and(self, other)

    def __xor__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_xor(self, other)

    def __or__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_or(self, other)

    def __radd__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_or(self, other)

    def __rsub__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_or(self, b_not(other))

    def __rmul__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_and(self, other)

    def __rdiv__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_and(self, b_not(other))

    def __rand__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_and(self, other)

    def __rxor__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_xor(self, other)

    def __ror__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_or(self, other)

    def __lt__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_lt(self, other)

    def __le__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_le(self, other)

    def __eq__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_eq(self, other)

    def __ne__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_ne(self, other)

    def __gt__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_gt(self, other)

    def __ge__(self, other):
        if not isinstance(other, (Variable, bool)):
            return NotImplemented
        return b_ge(self, other)

    def __neg__(self):
        return b_not(self)

    def __pos__(self):
        return self

    def __abs__(self):
        if self.identifier < 0:
            return b_not(self)
        return self

    def __hash__(self):
        return self.identifier.__hash__()

    def __int__(self):
        return self.identifier

    def __str__(self):
        val = self.get_value()
        if val is None:
            return str(self.identifier)

        return str(self.get_value())

    def __bool__(self):
        val = self.get_value()
        if val is None:
            msg = "Cannot call __bool__ before calling solve(). "
            msg += "If trying to negate a var, use -var."
            raise NotImplementedError(msg)

        return val


class NamedVariable(Variable):
    name = ""

    def __init__(self, model, name):
        super().__init__(model)
        self.name = name

    def __str__(self):
        return self.name + ":" + super().__str__()
