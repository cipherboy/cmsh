import pytest

import cmsh
from cmsh.array import *


def test_vec_and():
    mod = cmsh.Model()
    a = mod.vector(2)
    b = mod.vector(2)

    model = (a & b) == 2
    mod.add_assert(model)
    mod.solve()

    assert int(a) == 2
    assert int(b) == 2


def test_vec_nand():
    mod = cmsh.Model()
    a = mod.vector(2)
    b = mod.vector(2)

    model = l_nand(a, b) == 2
    mod.add_assert(model)
    mod.solve()

    assert int(a) == 1
    assert int(b) == 1


def test_vec_or():
    mod = cmsh.Model()
    a = mod.vector(2)
    b = mod.vector(2)

    model = (a | b) == 2
    unique = (a > b) & (a <= 2)
    mod.add_assert(model & unique)
    mod.solve()

    assert int(a) == 2
    assert int(b) == 0


def test_vec_nor():
    mod = cmsh.Model()
    a = mod.vector(2)
    b = mod.vector(2)

    model = l_nor(a, b) == 2
    unique = (a > b) & (a <= 2)
    mod.add_assert(model & unique)
    mod.solve()

    assert int(a) == 1
    assert int(b) == 0


def test_vec_not():
    mod = cmsh.Model()
    a = mod.vector(2)

    model = l_not(a) == 2
    mod.add_assert(model)
    mod.solve()

    assert int(a) == 1


def test_vec_xor():
    mod = cmsh.Model()
    a = mod.vector(2)
    b = mod.vector(2)

    model = (a ^ b) == 2
    unique = (a > b) & (a <= 2)
    mod.add_assert(model & unique)
    mod.solve()

    assert int(a) == 2
    assert int(b) == 0


def test_vec_le():
    mod = cmsh.Model()
    a = mod.vector(4)

    model = a <= 4
    mod.add_assert(model)
    mod.solve()

    assert int(a) <= 4
