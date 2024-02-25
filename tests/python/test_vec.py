import cmsh
import pytest


def test_add_extensive():
    k = 4
    for left in range(0, 1<<k):
        for right in range(0, 1<<k):
            mod = cmsh.Model()
            a = mod.vec(k)
            b = mod.vec(k)
            answer = mod.vec(k)

            constraint = (answer == (a + b)) & (a == left) & (right == b)
            mod.add_assert(constraint)
            assert mod.solve()

            assert int(a) == left
            assert int(b) == right
            assert int(answer) == ((left + right) & ((1 << k) - 1))

            negated = mod.negate_solution(a.variables + b.variables + answer.variables)
            mod.add_assert(negated)

            assert not mod.solve()


def test_mul_extensive():
    k = 4
    for left in range(0, 1<<k):
        for right in range(0, 1<<k):
            mod = cmsh.Model()
            a = mod.vec(k)
            b = mod.vec(k)
            answer = mod.vec(k)

            constraint = (answer == (a * b)) & (a == left) & (b == right)
            mod.add_assert(constraint)
            assert mod.solve()

            assert int(a) == left
            assert int(b) == right
            assert int(answer) == ((left * right) & ((1 << k) - 1))

            negated = mod.negate_solution(a.variables + b.variables + answer.variables)
            mod.add_assert(negated)

            assert not mod.solve()


def test_div_expensive():
    k = 4
    for left in range(0, 1<<k):
        for right in range(1, 1<<k):
            mod = cmsh.Model()
            a = mod.vec(k)
            b = mod.vec(k)
            answer_quotient = mod.vec(k)
            answer_remainder = mod.vec(k)

            ab_quotient, ab_remainder = divmod(a, b)

            constraint = (answer_quotient == ab_quotient) & (answer_remainder == ab_remainder) & (a == left) & (b == right)
            mod.add_assert(constraint)
            assert mod.solve()

            lr_quotient, lr_remainder = divmod(left, right)

            assert int(a) == left
            assert int(b) == right
            assert left == (((int(answer_quotient) * right) + int(answer_remainder)) & ((1 << k) - 1))

            negated = mod.negate_solution(a.variables + b.variables + answer_quotient.variables + answer_remainder.variables)
            mod.add_assert(negated)

            while mod.solve():
                assert int(a) == left
                assert int(b) == right
                assert left == (((int(answer_quotient) * right) + int(answer_remainder)) & ((1 << k) - 1))

                negated = mod.negate_solution(a.variables + b.variables + answer_quotient.variables + answer_remainder.variables)
                mod.add_assert(negated)

            assert not mod.solve()


def test_subindex():
    mod = cmsh.Model()
    a = mod.vec(10)
    assert isinstance(a, cmsh.Vector)
    assert isinstance(a[0], cmsh.Variable)
    assert isinstance(a[1:3], cmsh.Vector)
    assert int(a[1:3][0]) == int(a[1])
    assert int(a[1:3][1]) == int(a[2])


def test_incorrect_comparisons():
    mod = cmsh.Model()

    a = mod.vec(1)

    with pytest.raises(TypeError):
        if a == None:
            pass
    with pytest.raises(TypeError):
        if a != None:
            pass
    with pytest.raises(TypeError):
        b = None
        if a == b:
            pass
    with pytest.raises(TypeError):
        b == None
        if a != b:
            pass

def test_equals_not_equals():
    mod = cmsh.Model()

    a = mod.vec(2)
    b = mod.vec(2)

    assert not a.equals(None)
    assert a.not_equals(None)

    assert not a.equals(1)
    assert a.not_equals(1)

    assert not a.equals(b)
    assert a.not_equals(b)

    assert a.equals([a.variables[0], a.variables[1]])
    assert not a.not_equals([a.variables[0], a.variables[1]])

    assert not a.equals([a.variables[1], a.variables[0]])
    assert a.not_equals([a.variables[1], a.variables[0]])

    assert a.equals([int(a.variables[0]), int(a.variables[1])])
    assert not a.not_equals([int(a.variables[0]), int(a.variables[1])])

    assert not a.equals([int(a.variables[1]), int(a.variables[0])])
    assert a.not_equals([int(a.variables[1]), int(a.variables[0])])
