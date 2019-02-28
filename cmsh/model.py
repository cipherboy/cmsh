from .var import Variable
from .var import NamedVariable

class Model:
    variables = None
    clauses = None

    def __init__(self):
        self.variables = {}
        self.clauses = []

    def named_var(self, name):
        assert isinstance(name, str)

        new_variable = NamedVariable(self, name)
        self.variables[name] = new_variable

        return new_variable

    def var(self):
        new_variable = Variable(self)
        self.variables[new_var.identifier] = new_variable

        return new_variable

    def next_var_identifier(self):
        return len(self.variables) + 1

    def add_clause(self, clause):
        assert isinstance(clause, tuple)
        self.clauses.append(clause)

    def add_clauses(self, clauses):
        for clause in clauses:
            self.add_clause(clause)

    def get_value(self, identifier):
        return None
