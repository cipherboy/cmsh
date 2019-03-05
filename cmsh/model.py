from pycryptosat import Solver

from .var import Variable
from .var import NamedVariable

from .vec import Vector

from .logic import b_or, b_not


class Model:
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
        self.variables = 0
        self.constraints = {}

        self.clauses = set()
        self.assumptions = set()

        self.solver = Solver()

        self.true = self.var()
        self.false = self.neg_var(self.true)
        self.add_clause([self.true])

    def named_var(self, name):
        return self.named_variable(name)

    def named_variable(self, name):
        assert isinstance(name, str)

        new_variable = NamedVariable(self, name)
        self.variables += 1

        return new_variable

    def var(self):
        return self.variable()

    def variable(self):
        new_variable = Variable(self)
        self.variables += 1

        return new_variable

    def __int_to_vector(self, number, width=None):
        return list(map(lambda x: bool(int(x)), bin(number)[2:]))

    def to_vec(self, other, width=None):
        return self.to_vector(other, width=width)

    def to_vector(self, other, width=None):
        if isinstance(other, int):
            other = self.__int_to_vector(other, width=width)

        if width:
            if len(other) > width:
                raise ValueError("Length of object exceeds width")
            difference = [False]*(width - len(other))
            other = difference + other

        return Vector(self, vector=other)

    def vec(self, width):
        return self.vector(width)

    def vector(self, width):
        return Vector(self, width=width)

    def join_vec(self, vectors):
        interior = []
        for vec in vectors:
            interior.extend(vec.variables)

        return self.to_vector(interior)

    def split_vec(self, vector, width):
        assert len(vector) % width == 0

        vectors = []
        for index in range(0, len(vector), width):
            vectors.append(self.to_vec(vector[index:index+width]))

        return vectors

    def neg_var(self, var):
        if isinstance(var, int):
            if var > self.variables:
                msg = "Passed identifier %d exceeds number of vars: %d" % (var, self.variables)
                raise ValueError(msg)
            return Variable(self, identifier=-var)
        elif isinstance(var, Variable):
            return Variable(self, identifier=-var.identifier)

        raise TypeError("Unknown type to negate: %s" % type(var))

    def next_var_identifier(self):
        return self.variables + 1

    def has_constraint(self, transform):
        assert isinstance(transform, str)

        return transform in self.constraints

    def add_constraint(self, transform, result):
        assert isinstance(transform, str)
        assert isinstance(result, Variable)

        self.constraints[transform] = result

    def get_constraint(self, transform):
        assert isinstance(transform, str)

        return self.constraints[transform]

    def build_transform(self, operator, left, right):
        assert isinstance(operator, str)
        assert isinstance(left, Variable)
        assert isinstance(right, Variable)

        if abs(int(left)) < abs(int(right)):
            return '(' + str(left.identifier) + operator + str(right.identifier) + ')'
        return '(' + str(right.identifier) + operator + str(left.identifier) + ')'

    def add_assert(self, var):
        if isinstance(var, bool):
            raise ValueError("Expected Variable or int; got bool: %s" % var)
        self.add_clause([var])

    def add_assume(self, var):
        if isinstance(var, bool):
            raise ValueError("Expected Variable or int; got bool: %s" % var)
        elif isinstance(var, int):
            if var > self.variables:
                msg = "Passed identifier %d exceeds number of vars: %d" % (var, self.variables)
                raise ValueError(msg)
            self.assumptions.add(var)
            v = Variable(self, identifier=var)
            self.add_assert(v | -v)
        else:
            self.assumptions.add(var.identifier)
            self.add_assert(var | -var)

    def remove_assume(self, var):
        if isinstance(var, bool):
            raise ValueError("Expected Variable or int; got bool: %s" % var)
        elif isinstance(var, int):
            self.assumptions.remove(var)
        else:
            self.assumptions.remove(var.identifier)

    def add_clause(self, clause):
        resolved_clause = []
        for var in clause:
            if isinstance(var, bool):
                if var:
                    resolved_clause.append(self.true.identifier)
                else:
                    resolved_clause.append(self.false.identifier)
            elif isinstance(var, int):
                if var > self.variables:
                    msg = "Passed identifier %d exceeds number of vars: %d" % (var, self.variables)
                    raise ValueError(msg)
                resolved_clause.append(var)
            else:
                resolved_clause.append(var.identifier)

        self.clauses.add(tuple(resolved_clause))

    def add_clauses(self, clauses):
        resolved_clauses = set()
        for clause in clauses:
            resolved_clause = []
            for var in clause:
                if isinstance(var, bool):
                    if var:
                        resolved_clause.append(self.true.identifier)
                    else:
                        resolved_clause.append(self.false.identifier)
                elif isinstance(var, int):
                    if var > self.variables:
                        msg = "Passed identifier %d exceeds number of vars: %d" % (var, self.variables)
                        raise ValueError(msg)
                    resolved_clause.append(var)
                else:
                    resolved_clause.append(var.identifier)
            resolved_clauses.add(tuple(resolved_clause))

        self.clauses.update(resolved_clauses)

    def negate_solution(self, variables):
        assert variables
        assert len(variables) > 0

        var_list = list(variables)
        bool_vars = list(map(bool, var_list))
        result = None

        for _index in range(0, len(var_list)):
            if result is None:
                result = var_list[_index] != bool_vars[_index]
            else:
                result = result | (var_list[_index] != bool_vars[_index])

        return result

    def solve(self):
        if self.clauses:
            self.solver.add_clauses(self.clauses)
            self.clauses = set()

        self.sat, self.solution = self.solver.solve(assumptions=self.assumptions)
        return self.sat

    def get_value(self, identifier):
        if not self.sat:
            return None

        if identifier >= 0:
            return self.solution[identifier]

        return not self.solution[abs(identifier)]
