"""
This module contains the main Module class.
"""


from ._native import model as native_model

from .var import Variable
from .vec import Vector


def _int_to_vector_(number):
    """
    Converts an int to a list of bools.

    Args:
        number (int): number to convert to binary

    Returns:
        list of bool: A list of bools representing number.
    """
    return list(map(lambda x: bool(int(x)), bin(number)[2:]))


class Model:
    """
    An object describing a single SAT solver and its corresponding solver.
    Contains information about its variables, constraints, clauses, and
    solutions.

    Example usage:

    >>> m = Model()
    >>> a = m.var()
    >>> b = m.var()
    >>> m.add_assert(a & b)
    >>> m.solve()
        True
    >>> assert bool(a) and bool(b)
    """

    solver = None
    sat = None

    def __init__(self):
        """
        Constructor for Model. Must be called, but no configuration currently.
        """
        self.solver = native_model()

    def var(self):
        """
        Create a new variable.

        Returns:
            Variable: the newly created variable.
        """
        return self.variable()

    def variable(self):
        """
        Create a new variable.

        Returns:
            Variable: the newly created variable.
        """
        return Variable(self, self.solver.var())

    def to_vec(self, other, width=None):
        """
        Converts the specified object into a Vector of width, if present.

        Args:
            other (list, tuple, int): object to coerce to Vector.

        Returns:
            Vector: A vector representing the input parameter.
        """
        return self.to_vector(other, width=width)

    def to_vector(self, other, width=None):
        """
        Converts the specified object into a Vector of width, if present.

        Args:
            other (list, tuple, int): object to coerce to Vector.

        Returns:
            Vector: A vector representing the input parameter.
        """

        if isinstance(other, int):
            other = _int_to_vector_(other)

        if width:
            if len(other) > width:
                raise ValueError("Length of object exceeds width")
            difference = [False]*(width - len(other))
            other = difference + other

        return Vector(self, vector=other)

    def vec(self, width):
        """
        Create a new vector of the specified width.

        Args:
            width (int): width of the new vector.

        Returns:
            Vector: A new vector of the specified width.
        """
        return self.vector(width)

    def vector(self, width):
        """
        Create a new vector of the specified width.

        Args:
            width (int): width of the new vector.

        Returns:
            Vector: A new vector of the specified width.
        """
        return Vector(self, width=width)

    def join_vec(self, vectors):
        """
        Returns a single Vector out of a list or tuple of Vectors, appending
        them together.

        Args:
            vectors (list of Vector, tuple of Vector): collection of Vectors
            to combine.

        Returns:
            Vector: a single vector of all passed Vectors.
        """
        interior = []
        for vec in vectors:
            interior.extend(vec.variables)

        return self.to_vector(interior)

    def split_vec(self, vector, width):
        """
        Returns a list of Vectors splitting the specified vector into a series
        of different vectors.

        Args:
            vector (Vector): a vector to split.
            width (int): width to split the Vector at.

        Returns:
            list of Vector: a collection of Vectors of the specified width.
        """
        assert len(vector) % width == 0

        vectors = [
            self.to_vec(vector[index:index+width])
            for index in range(0, len(vector), width)
        ]

        return vectors

    def neg_var(self, var):
        """
        Negate the specified variable. e.g., var -> -var

        Args:
            var (int or Variable): the variable or its identifier to negate.

        Returns:
            Variable: the negation of var.
        """
        vtype = type(var)
        if vtype == int:
            return Variable(self, identifier=-var)
        if vtype == Variable:
            return Variable(self, identifier=-var.identifier)

        raise TypeError("Unknown type to negate: %s" % type(var))

    def add_constraint(self, left, op, right):
        assert isinstance(left, int)
        assert isinstance(right, int)

        if op == 'and':
            return Variable(self, self.solver.v_and(left, right))
        elif op == 'nand':
            return Variable(self, self.solver.v_nand(left, right))
        elif op == 'or':
            return Variable(self, self.solver.v_or(left, right))
        elif op == 'nor':
            return Variable(self, self.solver.v_nor(left, right))
        elif op == 'xor':
            return Variable(self, self.solver.v_xor(left, right))

        raise ValueError("Unknown operator: %s" % op)

    def add_assert(self, var):
        """
        Add an assertion that a single Variable is true via adding a clause
        with only that variable. Note that clauses cannot be removed.

        Args:
            var (int or Variable): variable or its identifier to assert.
        """
        if isinstance(var, bool):
            raise ValueError("Expected Variable or int; got bool: %s" % var)
        self.solver.v_assert(var)

    def add_assume(self, var):
        """
        Adds an assumption about the truthiness of a variable in the model.
        Assertions can be removed at a later time via remove_assume(...).
        Also adds an or clause in case the specified variable isn't otherwise
        present in the model (the clause `var | -var` will not impact the
        satisfiability of the overall model, but ensures that var is seen).
        Note that assumptions are slower in general than adding a clause,
        however, unlike clauses, they can be removed.

        Args:
            var (int or Variable): variable or its identifier to assume.
        """
        vtype = type(var)
        if vtype == bool:
            raise ValueError("Expected Variable or int; got bool: %s" % var)
        if vtype == int:
            if var > self.variables:
                msg = "Passed identifier %d exceeds number of vars: %d" % (var, self.variables)
                raise ValueError(msg)
            tmp_var = Variable(self, identifier=var)
            self.add_assert(tmp_var | -tmp_var)
        else:
            self.add_assert(var | -var)

    def remove_assume(self, var):
        """
        Removes an assumption about the truthiness of a variable.

        Args:
            var (int or Variable): variable or its identifier to assume.
        """
        vtype = type(var)
        if vtype == bool:
            raise ValueError("Expected Variable or int; got bool: %s" % var)

    def __to_ident__(self, var):
        vtype = type(var)
        if vtype == bool:
            msg = "Cannot pass bool as an identifier into CNF clause"
            raise ValueError(msg)
        if vtype == int:
            if var > self.variables:
                msg = "Passed identifier %d exceeds number of vars: %d" % (var, self.variables)
                raise ValueError(msg)
            return var
        return var.identifier

    def negate_solution(self, variables):
        """
        Given a set of variables, return a variable expressing the negation
        of their values. Used in incremental solving to find another solution.

        Args:
            variables (iterable of Variables): variables whose combined solution
            should be negated.

        Returns:
            Variable: var which describs the combined negation.
        """
        assert variables

        var_list = list(variables)
        bool_vars = list(map(bool, var_list))
        result = None

        for _index, var in enumerate(var_list):
            if result is None:
                result = var != bool_vars[_index]
            else:
                result = result | (var != bool_vars[_index])

        return result

    def solve(self):
        """
        Solve the current model. This adds all new clauses to the solver and
        runs CMS under the present assumptions.

        Returns:
            bool: whether or not the model is satisfiable.
        """
        self.sat = self.solver.solve()
        return self.sat

    def _get_value_(self, identifier):
        """
        Get the value of a variable by its identifier. Returns None if the
        model is unsatisfiable or unsolved.

        Args:
            identifier (int): identifier of the variable.

        Returns:
            bool: whether or not the variable is True, accounting for negation
            of the identifier
        """
        if self.sat:
            return self.solver.val(int(identifier))
