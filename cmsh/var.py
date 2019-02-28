from .tseitin import *


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
        return v_or(self, other)

    def __mul__(self, other):
        return v_and(self, other)

    def __str__(self):
        return str(self.get_value())

    def __bool__(self):
        return self.get_value()


class NamedVariable(Variable):
    name = ""

    def __init__(self, model, name):
        super().__init__(model)
        self.name = name


class BitVector():
    variables = []
    model = None

    def __init__(self, model, width=None, variables=None):
        self.model = model
        self.variables = []

        if width and variables:
            raise ValueError("Cannot specify both width and variables!")

        if width:
            for i in range(0, width):
                self.variables.append(self.model.var())

        if variables:
            self.variables = variables[:]
