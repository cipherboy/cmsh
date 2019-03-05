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
