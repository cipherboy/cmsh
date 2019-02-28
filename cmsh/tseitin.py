from .var import Variable

def and(left, right):
    assert isinstance(left, Variable)
    assert isinstance(right, Variable)
    assert left.model == right.model

    mod = left.model
    new_var = mod.var()

    mod.add_clauses([
        (-left.identifier, -right.identifier, new_var.identifier),
        (left.identifier, -new_var.identifier),
        (right.identifier, -new_var.identifier)
    ])

    return new_var


def nand(left, right):
    assert isinstance(left, Variable)
    assert isinstance(right, Variable)
    assert left.model == right.model

    mod = left.model
    new_var = mod.var()

    mod.add_clauses([
        (-left.identifier, -right.identifier, -new_var.identifier),
        (left.identifier, new_var.identifier),
        (right.identifier, new_var.identifier)
    ])

    return new_var


def or(left, right):
    assert isinstance(left, Variable)
    assert isinstance(right, Variable)
    assert left.model == right.model

    mod = left.model
    new_var = mod.var()

    mod.add_clauses([
        (left.identifier, right.identifier, -new_var.identifier),
        (-left.identifier, new_var.identifier),
        (-right.identifier, new_var.identifier)
    ])

    return new_var


def nor(left, right):
    assert isinstance(left, Variable)
    assert isinstance(right, Variable)
    assert left.model == right.model

    mod = left.model
    new_var = mod.var()

    mod.add_clauses([
        (left.identifier, right.identifier, new_var.identifier),
        (-left.identifier, -new_var.identifier),
        (-right.identifier, -new_var.identifier)
    ])

    return new_var


def not(var):
    assert isinstance(var, Variable)

    mod = var.model
    new_var = mod.var()

    mod.add_clauses([
        (var.identifier, new_var.identifier),
        (-var.identifier, -new_var.identifier)
    ])

    return new_var


def xor(left, right):
    assert isinstance(left, Variable)
    assert isinstance(right, Variable)
    assert left.model == right.model

    mod = left.model
    new_var = mod.var()

    mod.add_clauses([
        (-left.identifier, -right.identifier, -new_var.identifier),
        (left.identifier, right.identifier, -new_var.identifier),
        (left.identifier, -right.identifier, new_var.identifier),
        (-left.identifier, right.identifier, new_var.identifier),
    ])

    return new_var
