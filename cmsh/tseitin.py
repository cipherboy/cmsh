"""
This module provides Tseitin transformations for Variables, adding the
resulting clauses to the CNF model.
"""

def v_and(left, right):
    """
    Computes the binary AND between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model

    transform = mod._build_transform_('and', left, right)
    if mod._has_constraint_(transform):
        return mod._get_constraint_(transform)

    new_var = mod.var()
    mod.add_clauses([
        (-left.identifier, -right.identifier, new_var.identifier),
        (left.identifier, -new_var.identifier),
        (right.identifier, -new_var.identifier)
    ])

    mod._add_constraint_(transform, new_var)
    return new_var


def v_nand(left, right):
    """
    Computes the binary NAND between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model

    transform = mod._build_transform_('nand', left, right)
    if mod._has_constraint_(transform):
        return mod._get_constraint_(transform)

    new_var = mod.var()
    mod.add_clauses([
        (-left.identifier, -right.identifier, -new_var.identifier),
        (left.identifier, new_var.identifier),
        (right.identifier, new_var.identifier)
    ])

    mod._add_constraint_(transform, new_var)
    return new_var


def v_or(left, right):
    """
    Computes the binary OR between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model

    transform = mod._build_transform_('or', left, right)
    if mod._has_constraint_(transform):
        return mod._get_constraint_(transform)

    new_var = mod.var()
    mod.add_clauses([
        (left.identifier, right.identifier, -new_var.identifier),
        (-left.identifier, new_var.identifier),
        (-right.identifier, new_var.identifier)
    ])

    mod._add_constraint_(transform, new_var)
    return new_var


def v_nor(left, right):
    """
    Computes the binary NOR between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model

    transform = mod._build_transform_('nor', left, right)
    if mod._has_constraint_(transform):
        return mod._get_constraint_(transform)

    new_var = mod.var()
    mod.add_clauses([
        (left.identifier, right.identifier, new_var.identifier),
        (-left.identifier, -new_var.identifier),
        (-right.identifier, -new_var.identifier)
    ])

    mod._add_constraint_(transform, new_var)
    return new_var


def v_not(var):
    """
    Computes the binary NOT operation on the operands.

    Args:
        var (Variable): operand.

    Returns:
        Variable: the result of the operation.
    """
    return var.model.neg_var(var)


def v_xor(left, right):
    """
    Computes the binary XOR between left and right operands.

    Args:
        left (Variable): left operand.
        right (Variable): right operand.

    Returns:
        Variable: the result of the operation.
    """
    mod = left.model

    transform = mod._build_transform_('xor', left, right)
    if mod._has_constraint_(transform):
        return mod._get_constraint_(transform)

    new_var = mod.var()
    mod.add_clauses([
        (-left.identifier, -right.identifier, -new_var.identifier),
        (left.identifier, right.identifier, -new_var.identifier),
        (left.identifier, -right.identifier, new_var.identifier),
        (-left.identifier, right.identifier, new_var.identifier),
    ])

    mod._add_constraint_(transform, new_var)
    return new_var
