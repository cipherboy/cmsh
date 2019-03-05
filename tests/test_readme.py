import cmsh

def test_readme_contents():
    # Setup
    m = cmsh.Model()

    # Variables
    a = m.var()
    b = m.named_var("b")

    # Assertions
    stmt = a ^ -b
    m.add_assert(stmt)

    # Printing, Solving
    assert int(a) == 2
    assert int(b) == 3
    assert m.solve() == True

    assert bool(a) == False
    assert bool(b) == False

    # Type Coercion
    assert int(a) == 2

    # Negations
    c = m.var()
    not_c = -c

    assert int(c) == -1 * int(not_c)

    # Booleans
    stmt2 = (c == True) | (c == -a)
    m.add_assert(stmt2)
    m.solve()

    assert bool(a) == False
    assert bool(b) == False
    assert bool(c) == True
