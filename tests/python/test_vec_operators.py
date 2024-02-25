import pytest

import cmsh
from cmsh.var import b_xor
from cmsh.vec import *
from cmsh.vec import sum_array, splat


def test_op_add():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(4)
    c = mod.vector(4)

    constraint = ((a + b) == (4 + c)) & (a < 4) & (4 > b) & (c < 4) & (a != b)
    mod.add_assert(constraint)
    assert mod.solve()

    assert (int(a) + int(b)) == (4 + int(c))


def test_op_mul():
    mod = cmsh.Model()
    a = mod.vector(16)
    b = mod.vector(16)
    c = mod.vector(16)

    constraint = ((a * b) == (c * 3)) & ((a * b) == 30) & (a > 0) & (a < 3) & (b > 10) & (b < 30) & (c < 15)
    mod.add_assert(constraint)
    assert mod.solve()

    assert (int(a) * int(b)) == (3 * int(c))
    assert int(a) == 2
    assert int(b) == 15
    assert int(c) == 10

    mod.add_assert((a != 2) | (b != 15) | (c != 10))
    assert not mod.solve()


def test_op_div():
    mod = cmsh.Model()
    a = mod.vector(16)
    b = mod.vector(16)
    c = mod.vector(16)

    constraint = ((a / b) == (c * 3)) & ((a / b) == 6) & (a > 29) & (a < 31) & (b > 3) & (b < 8) & (c < 4) & (c > 1)
    mod.add_assert(constraint)
    assert mod.solve()

    assert (int(a) / int(b)) == (int(c) * 3)
    assert int(a) == 30
    assert int(b) == 5
    assert int(c) == 2

    mod.add_assert((a != 30) | (b != 5) | (c != 2))
    assert not mod.solve()


def test_op_and():
    mod = cmsh.Model()
    a = mod.vector(2)
    b = mod.vector(2)

    constraint = (a & b) == 2
    constraint2 = (2 & a) == 2
    constraint3 = (b & 1) == 1

    mod.add_assert(constraint & constraint2 & constraint3)
    assert mod.solve()
    assert int(a) == 2
    assert int(b) == 3


def test_op_xor():
    mod = cmsh.Model()
    a = mod.vector(2)
    b = mod.vector(2)

    constraint = (a ^ b) == 3
    constraint2 = (2 ^ a) == 3
    constraint3 = (b ^ 1) == 3

    mod.add_assert(constraint & constraint2 & constraint3)
    assert mod.solve()
    assert int(a) == 1
    assert int(b) == 2


def test_op_or():
    mod = cmsh.Model()
    a = mod.vector(2)
    b = mod.vector(2)

    c1 = (a | b) == 3
    c2 = (2 | a) == 2
    c3 = (b | 1) == 1
    c4 = a > b

    mod.add_assert(c1 & c2 & c3 & c4)
    assert mod.solve()
    assert int(a) == 2
    assert int(b) == 1


def test_op_bits():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(4)

    constraint = (a.bit_sum() <= 3) & (a.bit_odd() == b.bit_even())
    constraint2 = (a + b) >= 0
    constraint3 = a.odd() & b.even()
    mod.add_assert(constraint & constraint2)
    assert mod.solve()
    assert (int(a) + int(b)) >= 0


def test_op_flatten():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(4)
    c = mod.vector(4)
    d = mod.vector(4)
    e = mod.vector(4)

    constraint = (a.bit_and() & b.bit_or() & c.bit_nor() &
                  d.bit_nand() & e.bit_xor())

    mod.add_assert(constraint)
    assert mod.solve()

    assert int(a) == 0b1111
    assert int(b) >= 1
    assert int(c) != int(b)
    assert int(d) != 0b1111
    assert int(e) != 0


def test_sum_array():
    mod = cmsh.Model()
    a = mod.var()
    b = mod.var()
    my_list = [False, True, a, b]

    assume = sum_array(my_list) == 3
    mod.add_assert(assume)
    assert mod.solve()
    assert bool(a) == True
    assert bool(b) == True

    assert sum_array([]) == [False]
    assert sum_array([False]) == [False]
    assert sum_array([True]) == [True]


def test_other_sum_array():
    for i in range(0, 128):
        mod = cmsh.Model()
        a = mod.vec(7)

        a_value = a == i
        a_sum = sum_array(a)
        num_ones = bin(i).count("1")
        assert len(a_sum) >= len(bin(num_ones)[2:])

        mod.add_assert(a_value)

        assert mod.solve()
        assert int(a) == i
        assert int(a_sum) == num_ones

        new_sol = mod.negate_solution(a_sum)
        mod.add_assert(new_sol)
        assert not mod.solve()


def test_misc():
    mod = cmsh.Model()
    a1 = mod.var()
    a2 = mod.var()
    a3 = mod.var()

    a = mod.to_vector([a1, -a2, a3])

    mod.add_assert((+a).bit_and())
    mod.add_assert(-a == 0)
    assert mod.solve()

    assert abs(a) == [int(a1), int(a2), int(a3)]
    truncation = a.truncate(1)
    assert len(truncation) == 1
    assert int(truncation.variables[0]) == int(a3)


def test_hashable():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(4)

    container = set()
    container.add(a)
    assert a in container
    assert len(container) == 1
    container.add(b)
    assert a in container
    assert b in container
    assert len(container) == 2

    for var in a.variables:
        assert str(var) in str(a)

    c = mod.to_vector(a)
    assert abs(a) == abs(c)


def test_splat():
    mod = cmsh.Model()
    a = mod.vector(2)
    b = mod.var()
    c = mod.var()
    d = a.splat_and(b) == 1
    e = a.splat_or(b) == 3
    f = a.splat_xor(b) == 2
    g = a.splat_nand(b) == 2
    h = a.splat_nor(b) == 0
    i = a.splat_nand(c) == 3
    j = splat(b, [True, True], b_xor) == 0

    mod.add_assert(d)
    mod.add_assert(e)
    mod.add_assert(f)
    mod.add_assert(g)
    mod.add_assert(h)
    mod.add_assert(i)
    mod.add_assert(j)
    assert mod.solve()

    assert int(a) == 1
    assert bool(b) == True
    assert bool(c) == False


def test_rotations():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(4)
    c = mod.vector(4)
    d = mod.vector(4)

    con = True
    for left in [a, b, c, d]:
        for right in [a, b, c, d]:
            if abs(right) == abs(left):
                continue
            con = b_and(con, left.rotl() == right.rotr())
            con = b_and(con, left.rotl(amount=2) == right.rotr(amount=2))
            con = b_and(con, left.shiftl() == right.shiftr(filler=False))
            con = b_and(con, left.shiftl(amount=2) == right.shiftr(amount=2, filler=False))

    mod.add_assert(con)
    assert mod.solve()
    assert int(a) == 0
    assert int(b) == 0
    assert int(c) == 0
    assert int(d) == 0


def test_invalid_usages():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(8)

    with pytest.raises(TypeError):
        a + set()
    with pytest.raises(TypeError):
        set() + a
    with pytest.raises(TypeError):
        a & set()
    with pytest.raises(TypeError):
        set() & a
    with pytest.raises(TypeError):
        a ^ set()
    with pytest.raises(TypeError):
        set() ^ a
    with pytest.raises(TypeError):
        a | set()
    with pytest.raises(TypeError):
        set() | a
    with pytest.raises(TypeError):
        a < set()
    with pytest.raises(TypeError):
        set() < a
    with pytest.raises(TypeError):
        a <= set()
    with pytest.raises(TypeError):
        set() <= a
    with pytest.raises(TypeError):
        a > set()
    with pytest.raises(TypeError):
        set() > a
    with pytest.raises(TypeError):
        a >= set()
    with pytest.raises(TypeError):
        set() >= a
    with pytest.raises(TypeError):
        a == set()
    with pytest.raises(TypeError):
        set() == a
    with pytest.raises(TypeError):
        a != set()
    with pytest.raises(TypeError):
        set() != a
    with pytest.raises(ValueError):
        a < 400
    with pytest.raises(ValueError):
        a < b
    with pytest.raises(ValueError):
        b < a
    with pytest.raises(ValueError):
        l_and(1000, a)
    with pytest.raises(ValueError):
        a & 10000
    with pytest.raises(ValueError):
        cmsh.Vector(mod)
    with pytest.raises(ValueError):
        cmsh.Vector(mod, width=True, vector=True)
