from pycryptosat import Solver

from .var import Variable
from .var import NamedVariable


class Model:
    variables = None
    clauses = None
    constraints = None

    solver = None
    sat = None
    solution = None

    true = None
    false = None

    def __init__(self):
        self.variables = {}
        self.clauses = set()
        self.constraints = {}
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
        return '(' + str(left.identifier) + operator + str(right.identifier) + ')'

    def add_clause(self, clause):
        resolved_clause = []
        for var in clause:
            if isinstance(var, int):
                resolved_clause.append(var)
            else:
                resolved_clause.append(var.identifier)

        self.clauses.add(tuple(resolved_clause))
        self.solver.add_clause(resolved_clause)

    def add_clauses(self, clauses):
        resolved_clauses = []
        for clause in clauses:
            resolved_clause = []
            for var in clause:
                if isinstance(var, int):
                    resolved_clause.append(var)
                else:
                    resolved_clause.append(var.identifier)
            resolved_clauses.append(tuple(resolved_clause))

        self.clauses.update(set(resolved_clauses))
        self.solver.add_clauses(resolved_clauses)

    def solve(self):
        self.sat, self.solution = self.solver.solve()

    def print_cnf(self):
        print("p cnf " + str(len(self.variables)) + " " + str(len(self.clauses)))
        for clause in self.clauses:
            print(" ".join(map(str, list(clause) + [0])))

    def get_value(self, identifier):
        if not self.sat:
            return None

        return self.solution[identifier]
