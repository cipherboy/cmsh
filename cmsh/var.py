class Variable:
    identifier = 0
    value = None
    model = None

    def __init__(self, model):
        self.identifier = model.next_var_identifier()
        self.model = model

    def get_value(self):
        self.value = self.model.get_value(self.identifier)
        return self.value

    def __str__(self):
        return str(self.get_value())

    def __bool__(self):
        return self.get_value()


class NamedVariable(Variable):
    name = ""

    def __init__(self, model, name):
        super().__init__(model)
        self.name = name
