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

    assert(m.solve() == l_True);

    m.v_assert(r1);
    assert(m.solve() == l_False);
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

    assert(m.solve() == l_True);

    assert(m.val(l1) == false);
    assert(m.val(l2) == false);
    assert(m.val(l3) == true);
    assert(m.val(r1) == false);
    assert(m.val(r2) == true);
}

int main() {
    test_incremental();
    test_values();

    return 0;
}
