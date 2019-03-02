import pytest

import cmsh


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

    assert a.get_value() is None
    assert b.get_value() is None

    assert mod.solve() == False


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

    assert str(a) == str(a.identifier)
    assert str(b) == str(b.identifier)

    assert mod.solve() == False


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

    with pytest.raises(NotImplementedError):
        bool(a)
    with pytest.raises(NotImplementedError):
        bool(b)

    assert mod.solve() == False
