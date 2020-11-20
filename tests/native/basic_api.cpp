#include "cmsh.h"
#include <iostream>

using namespace cmsh;
using namespace std;

void test_incremental(void) {
    model_t m;
    int l1 = m.var();
    int l2 = m.var();
    int l3 = m.var();

    int r1 = m.v_and(l1, l2);
    int r2 = m.v_or(r1, l3);

    m.v_assert(-r2);

    assert(m.solve() == CMSat::l_True);

    m.v_assert(r1);
    assert(m.solve() == CMSat::l_False);
}

void test_values(void) {
    model_t m;
    int l1 = m.var();
    int l2 = m.var();
    int l3 = m.var();

    int r1 = m.v_and(l1, l2);
    int r2 = m.v_or(r1, l3);

    m.v_assert(-r1);
    m.v_assert(r2);

    assert(m.solve() == CMSat::l_True);

    assert(m.val(l1) == false);
    assert(m.val(l2) == false);
    assert(m.val(l3) == true);
    assert(m.val(r1) == false);
    assert(m.val(r2) == true);
}

void test_solve() {
    model_t m;
    int l1 = m.var();
    int l2 = m.var();
    int l3 = m.var();

    int r1 = m.v_or(l1, l2);
    int r2 = m.v_xor(l1, l3);
    int r3 = m.v_nand(l2, l3);

    m.v_assert(-l2);
    m.v_assert(r1);
    m.v_assert(r2);
    m.v_assert(r3);

    int c1 = m.v_xor(m.v_xor(r1, r2), r3);

    assert(m.solve() == CMSat::l_True);

    assert(m.val(l1) == true);
    assert(m.val(l2) == false);
    assert(m.val(l3) == false);
    assert(m.val(r1) == true);
    assert(m.val(r2) == true);
    assert(m.val(r3) == true);
    assert(m.val(c1) == true);
}

int main() {
    test_incremental();
    test_values();
    test_solve();

    return 0;
}
