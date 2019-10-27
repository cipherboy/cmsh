import pytest

import cmsh


def test_invalid_usages():
    mod = cmsh.Model()

    with pytest.raises(ValueError):
        mod.add_assert(False)
    with pytest.raises(ValueError):
        mod.to_vector(1024, 2)
    with pytest.raises(TypeError):
        mod.neg_var(set())
    with pytest.raises(ValueError):
        mod.add_assume(True)
    with pytest.raises(ValueError):
        mod.add_assume(1024)
    with pytest.raises(ValueError):
        mod.remove_assume(True)


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


def test_int_to_vec():
    mod = cmsh.Model()
    a = mod.to_vec(0, 2)
    b = mod.to_vec(1, 2)
    c = mod.to_vec(2, 2)
    d = mod.to_vec(3, 2)
    assert a.variables == [False, False]
    assert b.variables == [False, True]
    assert c.variables == [True, False]
    assert d.variables == [True, True]


def test_vector_shaping():
    mod = cmsh.Model()
    a1, a2, a3, a4 = mod.var(), mod.var(), mod.var(), mod.var()

    left, right = mod.to_vec([a1, a2]), mod.to_vec([a3, a4])
    assert left.variables == [a1, a2]
    assert right.variables == [a3, a4]

    a = mod.join_vec([left, right])
    assert len(a) == 4
    assert a.variables == [a1, a2, a3, a4]

    b, c = mod.split_vec(a, 2)
    assert len(b) == 2
    assert len(c) == 2
    assert b.variables == left.variables
    assert c.variables == right.variables


def test_misc():
    mod = cmsh.Model()
    a = mod.var()
    assert (-a).identifier == mod.neg_var(a.identifier).identifier


def test_assumptions():
    mod = cmsh.Model()
    a = mod.var()
    b = mod.var()
    c = a ^ b

    mod.add_assert(c)
    mod.add_assume(a)

    assert mod.solve()
    assert bool(a) == True
    assert bool(b) == False

    mod.remove_assume(a)
    mod.add_assume(b)

    assert mod.solve()
    assert bool(a) == False
    assert bool(b) == True

    mod.add_assume(a.identifier)
    assert not mod.solve()

    mod.remove_assume(a.identifier)

def test_context():
    with cmsh.Model() as model:
        a = model.var()
        b = model.var()

        model.add_assert((a^b) == True)
        assert model.solve()

        assert ((not bool(a)) and bool(b)) or (bool(a) and (not bool(b)))
