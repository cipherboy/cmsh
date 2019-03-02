import pytest

import cmsh
from cmsh.array import *


def test_op_add():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(4)

    constraint = (a + b == 4) & (a < 4) & (b < 4)
    mod.add_assert(constraint)
    mod.solve()

    assert (int(a) + int(b)) == 4


def test_invalid_usages():
    mod = cmsh.Model()
    a = mod.vector(4)
    b = mod.vector(8)

    with pytest.raises(TypeError):
        a + set()
    with pytest.raises(TypeError):
        a & set()
    with pytest.raises(TypeError):
        a ^ set()
    with pytest.raises(TypeError):
        a | set()
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
