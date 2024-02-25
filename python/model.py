"""
This module contains the main Module class.
"""

# pylint: disable=line-too-long,no-name-in-module

import functools
from typing import List, Optional

from ._vec_typing import VariableIs, VariableSoft, VectorLike
from ._model_typing import IVariableHard, IVector, VariableHard, VectorSized

from ._native import model as native_model

from .var import Variable
from .vec import Vector

def _int_to_vector_(number: int):
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

    solver: native_model
    sat: Optional[bool] = None

    def __init__(self):
        """
        Constructor for Model. Must be called, but no configuration currently.
        """
        self.solver = native_model()

    def __enter__(self):
        return self

    def __exit__(self, exception_type=None, value=None, traceback=None):
        self.cleanup()
        return False

    def var(self) -> Variable:
        """
        Create a new variable.

        Returns:
            Variable: the newly created variable.
        """
        return self.variable()

    def variable(self) -> Variable:
        """
        Create a new variable.

        Returns:
            Variable: the newly created variable.
        """
        return Variable(self, self.solver.var())

    def to_vec(self, other: VectorLike, width: Optional[int] = None) -> Vector:
        """
        Converts the specified object into a Vector of width, if present.

        Args:
            other (list, tuple, int): object to coerce to Vector.

        Returns:
            Vector: A vector representing the input parameter.
        """
        return self.to_vector(other, width=width)

    def to_vector(self, other: VectorLike, width: Optional[int] = None) -> Vector:
        """
        Converts the specified object into a Vector of width, if present.

        Args:
            other (list, tuple, int): object to coerce to Vector.

        Returns:
            Vector: A vector representing the input parameter.
        """

        if isinstance(other, Vector):
            if width:
                return self.to_vector(other.variables, width)
            return other

        if isinstance(other, int):
            return self.to_vector(_int_to_vector_(other), width)

        if width:
            l_other: int = len(other)
            if l_other > width:
                raise ValueError("Length of object exceeds width")

            difference: List[VariableIs] = [False]*(width - l_other)
            return Vector(self, vector=difference + list(other))

        return Vector(self, vector=other)

    def vec(self, width: int) -> Vector:
        """
        Create a new vector of the specified width.

        Args:
            width (int): width of the new vector.

        Returns:
            Vector: A new vector of the specified width.
        """
        return self.vector(width)

    def vector(self, width: int) -> Vector:
        """
        Create a new vector of the specified width.

        Args:
            width (int): width of the new vector.

        Returns:
            Vector: A new vector of the specified width.
        """
        return Vector(self, width=width)

    def join_vec(self, vectors: IVector) -> Vector:
        """
        Returns a single Vector out of a list or tuple of Vectors, appending
        them together.

        Args:
            vectors (list of Vector, tuple of Vector): collection of Vectors
            to combine.

        Returns:
            Vector: a single vector of all passed Vectors.
        """
        interior: List[VariableSoft] = []
        for vec in vectors:
            interior.extend(vec.variables)

        return self.to_vector(interior)

    def split_vec(self, vector: VectorSized, width: int) -> List[Vector]:
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

    def neg_var(self, var: VariableHard) -> Variable:
        """
        Negate the specified variable. e.g., var -> -var

        Args:
            var (int or Variable): the variable or its identifier to negate.

        Returns:
            Variable: the negation of var.
        """
        if isinstance(var, int):
            return Variable(self, identifier=-var)
        if isinstance(var, Variable):
            return Variable(self, identifier=-var.identifier)

        raise TypeError(f"Unknown type to negate: {type(var)}")

    def add_constraint(self, left: int, operator: str, right: int) -> Variable:
        """
        Add a constraint to the model.

        Args:
            left (int): the left variable identifier for the gate
            operator (str): the gate to add
            right (int): the right variable identifier for the gate

        Returns:
            Variable: the result of the gate
        """
        assert isinstance(left, int)
        assert isinstance(operator, str)
        assert isinstance(right, int)

        if abs(left) > self.solver.num_constraint_vars():
            msg = f"Passed left identifier {left} exceeds number of vars: "
            msg += f"{self.solver.num_constraint_vars()}"
            raise ValueError(msg)
        if abs(right) > self.solver.num_constraint_vars():
            msg = f"Passed right identifier {right} exceeds number of vars: "
            msg += f"{self.solver.num_constraint_vars()}"
            raise ValueError(msg)

        if operator == 'and':
            return Variable(self, self.solver.v_and(left, right))
        if operator == 'nand':
            return Variable(self, self.solver.v_nand(left, right))
        if operator == 'or':
            return Variable(self, self.solver.v_or(left, right))
        if operator == 'nor':
            return Variable(self, self.solver.v_nor(left, right))
        if operator == 'xor':
            return Variable(self, self.solver.v_xor(left, right))

        raise ValueError(f"Unknown operator: {operator}")

    def add_assert(self, var: VariableHard) -> None:
        """
        Add an assertion that a single Variable is true via adding a clause
        with only that variable. Note that clauses cannot be removed.

        Args:
            var (int or Variable): variable or its identifier to assert.
        """
        if isinstance(var, bool):
            raise ValueError(f"Expected Variable or int; got bool: {var}")
        self.solver.v_assert(int(var))

    def add_assume(self, var: VariableHard) -> None:
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
        if isinstance(var, bool):
            raise ValueError(f"Expected Variable or int; got bool: {var}")
        if isinstance(var, int):
            if abs(var) > self.solver.num_constraint_vars():
                msg = f"Passed identifier {var} exceeds number of vars: "
                msg += f"{self.solver.num_constraint_vars()}"
                raise ValueError(msg)
            self.solver.v_assume(var)
        else:
            if abs(var.identifier) > self.solver.num_constraint_vars():
                msg = f"Passed identifier {var.identifier} exceeds number of vars: "
                msg += f"{self.solver.num_constraint_vars()}"
                raise ValueError(msg)
            self.solver.v_assume(var.identifier)

    def remove_assume(self, var: VariableHard) -> None:
        """
        Removes an assumption about the truthiness of a variable.

        Args:
            var (int or Variable): variable or its identifier to assume.
        """
        if isinstance(var, bool):
            raise ValueError(f"Expected Variable or int; got bool: {var}")
        if isinstance(var, int):
            self.solver.v_unassume(var)
        else:
            self.solver.v_unassume(var.identifier)


    def __to_ident__(self, var: VariableHard) -> int:
        if isinstance(var, bool):
            msg = "Cannot pass bool as an identifier into CNF clause"
            raise ValueError(msg)
        if isinstance(var, int):
            if abs(var) > self.solver.num_constraint_vars():
                msg = f"Passed identifier {var} exceeds number of vars: "
                msg += f"{self.solver.num_constraint_vars()}"
                raise ValueError(msg)
            return var
        if abs(var.identifier) > self.solver.num_constraint_vars():
            msg = f"Passed identifier {var.identifier} exceeds number of vars: "
            msg += f"{self.solver.num_constraint_vars()}"
            raise ValueError(msg)
        return var.identifier

    def negate_solution(self, variables: IVariableHard) -> VariableIs:
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
        result = False

        for _index, var in enumerate(var_list):
            result = result | (var != bool_vars[_index])

        return result

    def solve(self, max_conflicts: Optional[int] = None,
              max_time: Optional[float] = None) -> Optional[bool]:
        """
        Solve the current model. This adds all new clauses to the solver and
        runs CMS under the present assumptions.

        Returns:
            bool: whether or not the model is satisfiable.
        """
        if max_conflicts:
            self.solver.config_conflicts(max_conflicts)
        else:
            self.solver.config_conflicts(-1)

        if max_time:
            self.solver.config_timeout(max_time)
        else:
            self.solver.config_timeout(-1)

        self.sat = self.solver.solve()
        return self.sat

    def _get_value_(self, identifier: VariableHard) -> Optional[bool]:
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

        return None

    def cleanup(self):
        """
        Clean up the solver after use, destroying all internal variables. This
        helps when you know that you won't be using this particular solver
        instance any more, freeing all used memory allocated by CryptoMiniSat,
        and the cmsh native bindings. Otherwise, this memory will stay
        allocated until a Python GC pass is performed.

        You cannot use this instance after calling cleanup().
        """
        self.solver.delete_model()
        self.solver = None


def with_model(func):
    """
    Decorator to automatically wrap the specified function with a temporary
    Model instance.
    """
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with Model() as model:
            all_args = [model] + list(args)
            return func(*all_args, **kwargs)

    return wrapper
