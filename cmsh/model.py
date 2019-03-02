from pycryptosat import Solver

from .var import Variable
from .var import NamedVariable

from .vec import Vector


class Model:
    variables = None
    constraints = None

    clauses = None
    added_clauses = None

    solver = None
    sat = None
    solution = None

    true = None
    false = None

    def __init__(self):
        self.variables = {}
        self.constraints = {}

        self.clauses = set()

        self.solver = Solver()

        self.true = self.var()
        self.false = self.neg_var(self.true)
        self.add_clause([self.true])

    def named_var(self, name):
        assert isinstance(name, str)

        new_variable = NamedVariable(self, name)
        self.variables[name] = new_variable

        return new_variable

    def var(self):
        new_variable = Variable(self)
        self.variables[new_variable.identifier] = new_variable

        return new_variable

    def to_vector(self, arr):
        return Vector(self, vector=arr)

    def vector(self, width):
        return Vector(self, width=width)

    def neg_var(self, var):
        new_variable = Variable(self, identifier=-var.identifier)
        return new_variable

    def next_var_identifier(self):
        return len(self.variables) + 1

    def has_constraint(self, transform):
        return transform in self.constraints

    def add_constraint(self, transform, result):
        self.constraints[transform] = result

    def get_constraint(self, transform):
        return self.constraints[transform]

    def build_transform(self, operator, left, right):
        if abs(int(left)) < abs(int(right)):
            return '(' + str(left.identifier) + operator + str(right.identifier) + ')'
        return '(' + str(right.identifier) + operator + str(left.identifier) + ')'

    def add_assert(self, var):
        if isinstance(var, bool):
            raise ValueError("Expected Variable or int; got bool: %s" % var)

        self.add_clause([var])

    def add_clause(self, clause):
        resolved_clause = []
        for var in clause:
            if isinstance(var, bool):
                if var:
                    resolved_clause.append(self.true.identifier)
                else:
                    resolved_clause.append(self.false.identifier)
            elif isinstance(var, int):
                resolved_clause.append(var)
            else:
                resolved_clause.append(var.identifier)

        self.clauses.add(tuple(resolved_clause))

    def add_clauses(self, clauses):
        resolved_clauses = []
        for clause in clauses:
            resolved_clause = []
            for var in clause:
                if isinstance(var, bool):
                    if var:
                        resolved_clause.append(self.true.identifier)
                    else:
                        resolved_clause.append(self.false.identifier)
                elif isinstance(var, int):
                    resolved_clause.append(var)
                else:
                    resolved_clause.append(var.identifier)
            resolved_clauses.append(tuple(resolved_clause))

        self.clauses.update(set(resolved_clauses))

    def negate_solution(self, variables):
        assert variables
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
            self.solver.add_clauses(list(self.clauses))
            self.clauses = set()

        self.sat, self.solution = self.solver.solve()
        return self.sat

    def get_value(self, identifier):
        if self.clauses or not self.sat:
            return None

        if identifier >= 0:
            return self.solution[identifier]

        return not self.solution[abs(identifier)]
