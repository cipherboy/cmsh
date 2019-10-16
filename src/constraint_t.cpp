/*
 * Implementation of constraint_t for cmsh's native interface.
 *
 * Copyright (C) 2019 Alexander Scheel <alexander.m.scheel@gmail.com>
 *
 * See LICENSE in the root of the repository for license information.
 *
 * https://github.com/cipherboy/cmsh
 * High level bindings for Mate Soos's CryptoMiniSat.
 */

#include "cmsh.h"

using namespace cmsh;

constraint_t::constraint_t(model_t *m, int l, op_t o, int r) {
    op = o;

    if (l < r) {
        left = l;
        right = r;
    } else {
        left = r;
        right = l;
    }

    assert(left <= right);

    // Allow constructing a constraint without a model reference: this
    // will prevent us from assigning a value, but still lets us use the
    // equality check. Two constraint_t's are equal <=> all inputs are
    // equal and the operator is equal.
    if (m != NULL) {
        value = m->next_constraint();
        assert(value > 0);
    }
}

void constraint_t::add(model_t *m) {
    // Add the constraint to the model by doing the tseitin transformation
    // on the gate.
    tseitin(m);
}

bool constraint_t::operator==(const constraint_t& other) {
    // Two constraint_t instances are equal <=> the operands are equal and
    // the operator are equal. The output of the gate may or may not be
    // present in either of these instances, so ignore it in this check.
    return (left == other.left && op == other.op && right == other.right);
}

bool constraint_t::assigned() {
    // Return true if all CNF variables are assigned. Otherwise, a call
    // to assign_vars is necessary.
    return cnf_left != 0 && cnf_right != 0 && cnf_value != 0;
}

void constraint_t::assign_vars(model_t *m) {
    // Assign and allocate CNF variables from the constraint variables.
    // Note that calling m->cnf_from_constraint(...) will return the same
    // value, so at worst we incur slight overhead versus an if check.
    cnf_left = m->cnf_from_constraint(left);
    cnf_right = m->cnf_from_constraint(right);
    cnf_value = m->cnf_from_constraint(value);

    // Validate that we actually got assignments.
    assert(cnf_left != 0);
    assert(cnf_right != 0);
    assert(cnf_value != 0);
}

bool constraint_t::eval(bool left, bool right) const {
    // Evaluate the value of a constraint based on boolean assignments for
    // its variables.
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

    // Not reachable as the above switch statement handles all possible
    // values of operator and returns.
    assert(false);
    return false;
}

void constraint_t::tseitin(model_t *m) {
    // Convert the constraint to a CNF form by performing a Tseitin
    // transformation.
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
        default:
            // Not reachable as our switch statement handles all possible
            // operator values.
            assert(false);
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
            // Enable a constraint to be hashable for direct inclusion in an
            // ordered map. Note however that this is presently unused; only
            // pointers to constraints are added to maps currently.
            return object.hash();
        }
    };
}
