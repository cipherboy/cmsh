def v_and(left, right):
    mod = left.model
    transform = mod.build_transform('and', left, right)
    if mod.has_constraint(transform):
        return mod.get_constraint(transform)

    new_var = mod.var()
    mod.add_clauses([
        (-left.identifier, -right.identifier, new_var.identifier),
        (left.identifier, -new_var.identifier),
        (right.identifier, -new_var.identifier)
    ])

    mod.add_constraint(transform, new_var)
    return new_var


def v_nand(left, right):
    mod = left.model
    transform = mod.build_transform('nand', left, right)
    if mod.has_constraint(transform):
        return mod.get_constraint(transform)

    new_var = mod.var()
    mod.add_clauses([
        (-left.identifier, -right.identifier, -new_var.identifier),
        (left.identifier, new_var.identifier),
        (right.identifier, new_var.identifier)
    ])

    mod.add_constraint(transform, new_var)
    return new_var


def v_or(left, right):
    mod = left.model
    transform = mod.build_transform('or', left, right)
    if mod.has_constraint(transform):
        return mod.get_constraint(transform)

    new_var = mod.var()

    mod.add_clauses([
        (left.identifier, right.identifier, -new_var.identifier),
        (-left.identifier, new_var.identifier),
        (-right.identifier, new_var.identifier)
    ])

    mod.add_constraint(transform, new_var)
    return new_var


def v_nor(left, right):
    mod = left.model
    transform = mod.build_transform('nor', left, right)
    if mod.has_constraint(transform):
        return mod.get_constraint(transform)

    new_var = mod.var()
    mod.add_clauses([
        (left.identifier, right.identifier, new_var.identifier),
        (-left.identifier, -new_var.identifier),
        (-right.identifier, -new_var.identifier)
    ])

    mod.add_constraint(transform, new_var)
    return new_var


def v_not(var):
    return var.model.neg_var(var)


def v_xor(left, right):
    mod = left.model
    transform = mod.build_transform('xor', left, right)
    if mod.has_constraint(transform):
        return mod.get_constraint(transform)

    new_var = mod.var()
    mod.add_clauses([
        (-left.identifier, -right.identifier, -new_var.identifier),
        (left.identifier, right.identifier, -new_var.identifier),
        (left.identifier, -right.identifier, new_var.identifier),
        (-left.identifier, right.identifier, new_var.identifier),
    ])

    mod.add_constraint(transform, new_var)
    return new_var
