from .array import *
from .var import Variable


class Vector:
    variables = None
    model = None
    __allowed__ = (bool, int, list, tuple)

    def __init__(self, model, width=None, vector=None):
        self.model = model
        self.variables = []
        self.__allowed__ = (Vector, bool, int, list, tuple)

        if width and vector:
            raise ValueError("Cannot specify both width and vector!")
        elif not width and not vector:
            raise ValueError("Must specify either width or vector!")

        if width:
            for i in range(0, width):
                self.variables.append(self.model.var())

        if isinstance(vector, Vector):
            self.variables = tuple(vector.variables)[:]
        elif isinstance(vector, (list, tuple)):
            self.variables = tuple(vector)[:]

    def __and__(self, other):
        if not isinstance(other, self.__allowed__):
            return NotImplemented
        return l_and(self, other)

    def __xor__(self, other):
        if not isinstance(other, self.__allowed__):
            return NotImplemented
        return l_xor(self, other)

    def __or__(self, other):
        if not isinstance(other, self.__allowed__):
            return NotImplemented
        return l_or(self, other)

    def __rand__(self, other):
        if not isinstance(other, self.__allowed__):
            return NotImplemented
        return l_and(self, other)

    def __rxor__(self, other):
        if not isinstance(other, self.__allowed__):
            return NotImplemented
        return l_xor(self, other)

    def __ror__(self, other):
        if not isinstance(other, self.__allowed__):
            return NotImplemented
        return l_or(self, other)

    def __lt__(self, other):
        if not isinstance(other, self.__allowed__):
            return NotImplemented
        return l_lt(self, other)

    def __le__(self, other):
        if not isinstance(other, self.__allowed__):
            return NotImplemented
        return l_le(self, other)

    def __eq__(self, other):
        if not isinstance(other, self.__allowed__):
            return NotImplemented
        return l_eq(self, other)

    def __ne__(self, other):
        if not isinstance(other, self.__allowed__):
            return NotImplemented
        return l_ne(self, other)

    def __gt__(self, other):
        if not isinstance(other, self.__allowed__):
            return NotImplemented
        return l_gt(self, other)

    def __ge__(self, other):
        if not isinstance(other, self.__allowed__):
            return NotImplemented
        return l_ge(self, other)



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
