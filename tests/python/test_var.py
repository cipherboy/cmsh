import pytest

import cmsh
from cmsh.var import *


def test_get_value():
    mod = cmsh.Model()
    a = mod.var()
    b = mod.var()

    assert a.get_value() is None
    assert b.get_value() is None

    mod.add_assert(a)
    mod.add_assert(-b)

    assert a.get_value() is None
    assert b.get_value() is None

    mod.solve()

    assert a.get_value() == True
    assert b.get_value() == False

    mod.add_assert(-a)

    assert a.get_value() == True
    assert b.get_value() == False

    assert mod.solve() == False

    assert a.get_value() is None
    assert b.get_value() is None


def test_str():
    mod = cmsh.Model()
    a = mod.var()
    b = mod.var()

    assert str(a) == str(a.identifier)
    assert str(b) == str(b.identifier)

    mod.add_assert(a)
    mod.add_assert(-b)

    assert str(a) == str(a.identifier)
    assert str(b) == str(b.identifier)

    mod.solve()

    assert str(a) == str(True)
    assert str(b) == str(False)

    mod.add_assert(-a)

    assert str(a) == str(True)
    assert str(b) == str(False)

    assert mod.solve() == False

    assert str(a) == str(a.identifier)
    assert str(b) == str(b.identifier)


def test_bool():
    mod = cmsh.Model()
    a = mod.var()
    b = mod.var()

    with pytest.raises(NotImplementedError):
        bool(a)
    with pytest.raises(NotImplementedError):
        bool(b)

    mod.add_assert(a)
    mod.add_assert(-b)

    with pytest.raises(NotImplementedError):
        bool(a)
    with pytest.raises(NotImplementedError):
        bool(b)

    mod.solve()

    assert bool(a) == True
    assert bool(b) == False

    mod.add_assert(-a)

    assert bool(a) == True
    assert bool(b) == False

    assert mod.solve() == False

    with pytest.raises(NotImplementedError):
        bool(a)
    with pytest.raises(NotImplementedError):
        bool(b)


def test_repeated_gates():
    mod = cmsh.Model()
    a = mod.var()
    b = mod.var()

    first_gate = v_and(a, b)
    second_gate = v_and(a, b)
    assert int(first_gate) == int(second_gate)

    first_gate = v_nand(a, b)
    second_gate = v_nand(a, b)
    assert int(first_gate) == int(second_gate)

    first_gate = v_or(a, b)
    second_gate = v_or(a, b)
    assert int(first_gate) == int(second_gate)

    first_gate = v_nor(a, b)
    second_gate = v_nor(a, b)
    assert int(first_gate) == int(second_gate)

    first_gate = v_xor(a, b)
    second_gate = v_xor(a, b)
    assert int(first_gate) == int(second_gate)


def test_swapped_gates():
    mod = cmsh.Model()
    a = mod.var()
    b = mod.var()

    first_gate = a & b
    second_gate = b & a
    assert int(first_gate) == int(second_gate)


def test_abs():
    mod = cmsh.Model()
    a = mod.var()
    neg_a = -a

    assert int(a) > 0
    assert int(neg_a) < 0
    assert abs(a) == abs(neg_a)


def test_hashable():
    mod = cmsh.Model()
    a = mod.var()
    b = mod.var()
    c = mod.var()

    data = set([a, -b, c])
