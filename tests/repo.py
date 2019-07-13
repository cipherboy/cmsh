from cmsh import Model
from cmsh.var import *

def test_mixed_ge():
    for left in [False, True]:
        for right in [False, True]:
            mod = Model()
            l_var = mod.var()
            r_var = mod.var()
            l_answer = b_ge(l_var, right)
            r_answer = b_ge(left, r_var)

            if left:
                mod.add_assert(l_var)
            else:
                mod.add_assert(-l_var)

            if right:
                mod.add_assert(r_var)
            else:
                mod.add_assert(-r_var)

            mod.solve()
            assert bool(l_var) == left
            assert bool(r_var) == right
            assert bool(l_answer) == b_ge(left, right)
            assert bool(r_answer) == b_ge(left, right)


test_mixed_ge()
