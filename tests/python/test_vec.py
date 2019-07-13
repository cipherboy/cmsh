import cmsh


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


def test_subindex():
    mod = cmsh.Model()
    a = mod.vec(10)
    assert isinstance(a, cmsh.Vector)
    assert isinstance(a[0], cmsh.Variable)
    assert isinstance(a[1:3], cmsh.Vector)
    assert int(a[1:3][0]) == int(a[1])
    assert int(a[1:3][1]) == int(a[2])
