import pytest

import cmsh


def test_invalid_usages():
    mod = cmsh.Model()

    with pytest.raises(ValueError):
        mod.add_assert(False)


def test_basic_clauses():
    mod = cmsh.Model()
    a = mod.var()

    mod.add_clause([True])
    mod.add_clause([False])
    mod.add_clause([1])
    mod.add_clause([-1])
    mod.add_clauses([[True, 1, a]])
    mod.add_clauses([[False, -1, a]])


def test_negate_solution():
    mod = cmsh.Model()
    a = mod.var()
    b = mod.var()

    constraint = (a | b) == True
    mod.add_assert(constraint)
    assert mod.solve()

    current_sol = [bool(a), bool(b)]

    negated = mod.negate_solution([a, b])
    assert isinstance(negated, cmsh.Variable)

    mod.add_assert(negated)
    assert mod.solve()

    next_sol = [bool(a), bool(b)]
    assert current_sol != next_sol
