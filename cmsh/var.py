"""
This module includes the Variable class, which represents a single boolean
variable in a SAT model.
"""

from .logic import b_and, b_xor, b_or, b_not, b_lt, b_le, b_eq, b_ne, b_gt, b_ge


class Variable:
    """
    The Variable class represents a single variable in the CNF model. Its
    identifier is positive when the variable represents a positive value, and
    negative when refering to its negation.
    """
    identifier = 0
    value = None
    model = None

    def __init__(self, model, identifier=None):
        if identifier:
            self.identifier = identifier
        else:
            self.identifier = model._next_var_identifier_()
        self.model = model

    def get_value(self):
        """
        Get the value of the variable: True, False, or None, and updated to
        reflect the sign of the identifier. If negative, the value is negated.
        None when the model is not solved, else a bool when the model has been
        solved.

        Returns:
            bool: value of the variable after solving.
        """
        self.value = self.model._get_value_(self.identifier)
        return self.value

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
            msg = "Can't compare Variable with %s" % type(other)
            raise TypeError(msg)
        return b_eq(self, other)

    def __ne__(self, other):
        if not isinstance(other, (Variable, bool)):
            msg = "Can't compare Variable with %s" % type(other)
            raise TypeError(msg)
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
        return abs(self.identifier)

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
