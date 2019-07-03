#include <cmath>
#include <vector>
#include <unordered_map>
#include <cryptominisat5/cryptominisat.h>

#include "cmsh.h"

using std::vector;
using std::unordered_map;

using CMSat::SATSolver;
using CMSat::Lit;

using namespace cmsh;

constraint_t::constraint_t(model_t *m, int l, op_t o, int r) {
    if (l < r) {
        left = l;
        right = r;
    } else {
        left = r;
        right = l;
    }

    value = m->next_constraint();
    assert(value > 0);

    op = o;
    cnf_left = 0;
    cnf_right = 0;
    cnf_value = 0;
}

void constraint_t::add(model_t *m) {
    tseitin(m);
}

bool constraint_t::operator==(const constraint_t& other) {
    return (left == other.left && op == other.op && right == other.right);
}

bool constraint_t::assigned() {
    return cnf_left != 0 && cnf_right != 0 && cnf_value != 0;
}

void constraint_t::assign_vars(model_t *m) {
    cnf_left = m->cnf_from_constraint(left);
    cnf_right = m->cnf_from_constraint(right);
    cnf_value = m->cnf_from_constraint(value);
}

bool constraint_t::eval(bool left, bool right) const {
    switch (op) {
        case op_t::AND:
            return left && right;
            break;
        case op_t::NAND:
            return !(left && right);
            break;
        case op_t::OR:
            return left || right;
            break;
        case op_t::NOR:
            return !(left || right);
            break;
        case op_t::XOR:
            return left != right;
            break;
    }

    assert(false);
    return false;
}

void constraint_t::tseitin(model_t *m) {
    switch (op) {
        case op_t::AND:
            tseitin_and(m);
            break;
        case op_t::NAND:
            tseitin_nand(m);
            break;
        case op_t::OR:
            tseitin_or(m);
            break;
        case op_t::NOR:
            tseitin_nor(m);
            break;
        case op_t::XOR:
            tseitin_xor(m);
            break;
    }
}

void constraint_t::tseitin_and(model_t *m) {
    m->add_clause(-cnf_left, -cnf_right, cnf_value);
    m->add_clause(cnf_left, -cnf_value);
    m->add_clause(cnf_right, -cnf_value);
}

void constraint_t::tseitin_nand(model_t *m) {
    m->add_clause(-cnf_left, -cnf_right, -cnf_value);
    m->add_clause(cnf_left, cnf_value);
    m->add_clause(cnf_right, cnf_value);
}

void constraint_t::tseitin_or(model_t *m) {
    m->add_clause(cnf_left, cnf_right, -cnf_value);
    m->add_clause(-cnf_left, cnf_value);
    m->add_clause(-cnf_right, cnf_value);
}

void constraint_t::tseitin_nor(model_t *m) {
    m->add_clause(cnf_left, cnf_right, cnf_value);
    m->add_clause(-cnf_left, -cnf_value);
    m->add_clause(-cnf_right, -cnf_value);
}

void constraint_t::tseitin_xor(model_t *m) {
    m->add_clause(-cnf_left, -cnf_right, -cnf_value);
    m->add_clause(cnf_left, cnf_right, -cnf_value);
    m->add_clause(cnf_left, -cnf_right, cnf_value);
    m->add_clause(-cnf_left, cnf_right, cnf_value);
}

size_t constraint_t::hash() const {
    size_t result = 0x74FDCBED;
    result *= left;
    result *= op;
    result *= right;
    result *= value;
    return result;
}

namespace std {
    template<> struct hash<constraint_t> {
        size_t operator()(constraint_t const& object) {
            return object.hash();
        }
    };
}
