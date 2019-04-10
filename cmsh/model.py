"""
This module contains the main Module class.
"""


from pycryptosat import Solver

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

    variables = 0
    constraints = None

    clauses = None
    assumptions = None

    solver = None
    sat = None
    solution = None

    true = None
    false = None

    def __init__(self):
        """
        Constructor for Model. Must be called, but no configuration currently.
        """
        self.variables = 0
        self.constraints = {}

        self.clauses = set()
        self.assumptions = set()

        self.solver = Solver()

        self.true = self.var()
        self.false = self.neg_var(self.true)
        self.add_clause([self.true])

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
        new_variable = Variable(self)
        self.variables += 1

        return new_variable

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
            if var > self.variables:
                msg = "Passed identifier %d exceeds number of vars: %d" % (var, self.variables)
                raise ValueError(msg)
            return Variable(self, identifier=-var)
        if vtype == Variable:
            return Variable(self, identifier=-var.identifier)

        raise TypeError("Unknown type to negate: %s" % type(var))

    def _next_var_identifier_(self):
        """
        Get the next (free) variable identifier.

        Returns:
            int: the identifier for the next variable.
        """
        return self.variables + 1

    def _build_transform_(self, operator, left, right):
        """
        Build the canonical form of a transformation (boolean expression)
        from operators and left/right halves. Only to be called on Variables
        to cache the result (enabling consistency).

        Args:
            operator (str): name of the operator (e.g., and, or, etc.).
            left (Variable): left operand.
            right (Variable): right operand.

        Returns:
            str: canonical representation of operator applied to the operands.
        """
        if abs(left) < abs(right):
            return (operator, left.identifier, right.identifier)
        return (operator, right.identifier, left.identifier)

    def _has_constraint_(self, transform):
        """
        Checks if this model has seen the specified constraint before.

        Args:
            transform (str): built from __build_transform.

        Returns:
            bool: whether or not the specified transformation has been seen.
        """
        return transform in self.constraints

    def _add_constraint_(self, transform, result):
        """
        Adds a constraint and its result to the model.

        Args:
            transform (str): built from __build_transform.
            result (Variable): result of the constraints.
        """
        self.constraints[transform] = result

    def _get_constraint_(self, transform):
        """
        Gets the result of a constraint when already present.

        Args:
            transform (str): built from __build_transform

        Returns:
            Variable: result of the constraint.
        """
        return self.constraints[transform]

    def add_assert(self, var):
        """
        Add an assertion that a single Variable is true via adding a clause
        with only that variable. Note that clauses cannot be removed.

        Args:
            var (int or Variable): variable or its identifier to assert.
        """
        if isinstance(var, bool):
            raise ValueError("Expected Variable or int; got bool: %s" % var)
        self.add_clause([var])

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
        elif vtype == int:
            if var > self.variables:
                msg = "Passed identifier %d exceeds number of vars: %d" % (var, self.variables)
                raise ValueError(msg)
            self.assumptions.add(var)
            tmp_var = Variable(self, identifier=var)
            self.add_assert(tmp_var | -tmp_var)
        else:
            self.assumptions.add(var.identifier)
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
        elif vtype == int:
            self.assumptions.remove(var)
        else:
            self.assumptions.remove(var.identifier)

    def __to_ident__(self, var):
        vtype = type(var)
        if vtype == bool:
            if var:
                return self.true.identifier
            else:
                return self.false.identifier
        elif vtype == int:
            if var > self.variables:
                msg = "Passed identifier %d exceeds number of vars: %d" % (var, self.variables)
                raise ValueError(msg)
            return var
        else:
            return var.identifier

    def add_clause(self, clause):
        """
        Adds a clause to the CNF. A clause is a list of variables joined by OR
        gates. Each clause in the CNF is joined by AND gates. It is suggested
        not to call add_clause(...) directly, but instead call add_assert for
        a clause with a single variable. Note that operations on Variables
        automatically add clauses as necessary.

        Args:
            clause (iterable of bool, int, or Variable): clause to add to the
            CNF.
        """

        resolved_clause = tuple(map(self.__to_ident__, clause))
        self.clauses.add(resolved_clause)

    def add_clauses(self, clauses):
        """
        Adds list of clauses to the CNF. A clause is a list of variables
        joined by OR gates. Each clause in the CNF is joined by AND gates. It
        is suggested not to call add_clauses(...) directly, but instead call
        add_assert for a clause with a single variable, or directly use
        operations on Variables

        Args:
            clauses (iterable of iterables of bool, int, or Variable): set of
            clauses to add to the CNF.
        """

        resolved_clauses = [
            tuple(map(self.__to_ident__, clause))
            for clause in clauses
        ]
        self.clauses.update(resolved_clauses)

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
        if self.clauses:
            self.solver.add_clauses(self.clauses, max_var=self.variables)
            self.clauses = set()

        self.sat, self.solution = self.solver.solve(assumptions=self.assumptions)
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
        if not self.sat:
            return None

        if identifier >= 0:
            return self.solution[identifier]

        return not self.solution[abs(identifier)]
