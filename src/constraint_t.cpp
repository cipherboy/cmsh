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
    tseitin(m->solver, m->clause);
}

bool constraint_t::operator==(const constraint_t& other) {
    if (left == other.left && op == other.op && right == other.right) {
        assert(value == other.value);
        return true;
    }

    return false;
}

bool constraint_t::assigned() {
    return cnf_left != 0 && cnf_right != 0 && cnf_value != 0;
}

void constraint_t::assign_vars(model_t *m) {
    cnf_left = m->cnf_from_constraint(left);
    cnf_right = m->cnf_from_constraint(right);
    cnf_value = m->cnf_from_constraint(value);
}

bool constraint_t::valueOf(bool left, bool right) const {
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

void constraint_t::tseitin(SATSolver *s, vector<Lit>& c) {
    switch (op) {
        case op_t::AND:
            tseitin_and(s, c);
            break;
        case op_t::NAND:
            tseitin_nand(s, c);
            break;
        case op_t::OR:
            tseitin_or(s, c);
            break;
        case op_t::NOR:
            tseitin_nor(s, c);
            break;
        case op_t::XOR:
            tseitin_xor(s, c);
            break;
    }
}

void constraint_t::tseitin_and(SATSolver *s, vector<Lit>& c) {
    add_clause(s, c, -cnf_left, -cnf_right, cnf_value);
    add_clause(s, c, cnf_left, -cnf_value);
    add_clause(s, c, cnf_right, -cnf_value);
}

void constraint_t::tseitin_nand(SATSolver *s, vector<Lit>& c) {
    add_clause(s, c, -cnf_left, -cnf_right, -cnf_value);
    add_clause(s, c, cnf_left, cnf_value);
    add_clause(s, c, cnf_right, cnf_value);
}

void constraint_t::tseitin_or(SATSolver *s, vector<Lit>& c) {
    add_clause(s, c, cnf_left, cnf_right, -cnf_value);
    add_clause(s, c, -cnf_left, cnf_value);
    add_clause(s, c, -cnf_right, cnf_value);
}

void constraint_t::tseitin_nor(SATSolver *s, vector<Lit>& c) {
    add_clause(s, c, cnf_left, cnf_right, cnf_value);
    add_clause(s, c, -cnf_left, -cnf_value);
    add_clause(s, c, -cnf_right, -cnf_value);
}

void constraint_t::tseitin_xor(SATSolver *s, vector<Lit>& c) {
    add_clause(s, c, -cnf_left, -cnf_right, -cnf_value);
    add_clause(s, c, cnf_left, cnf_right, -cnf_value);
    add_clause(s, c, cnf_left, -cnf_right, cnf_value);
    add_clause(s, c, -cnf_left, cnf_right, cnf_value);
}

void constraint_t::add_clause(SATSolver *s, vector<Lit>& c, int var_1) {
    c.clear();
    c.push_back(to_lit(var_1));
    s->add_clause(c);
}

void constraint_t::add_clause(SATSolver *s, vector<Lit>& c, int var_1, int var_2) {
    c.clear();
    c.push_back(to_lit(var_1));
    c.push_back(to_lit(var_2));
    s->add_clause(c);
}

void constraint_t::add_clause(SATSolver *s, vector<Lit>& c, int var_1, int var_2, int var_3) {
    c.clear();
    c.push_back(to_lit(var_1));
    c.push_back(to_lit(var_2));
    c.push_back(to_lit(var_3));
    s->add_clause(c);
}

Lit constraint_t::to_lit(int var, bool neg) {
    assert(var != 0);

    bool sign = neg;
    if (var < 0) {
        sign = !sign;
    }

    return Lit(abs(var), sign);
}

size_t constraint_t::hash() const {
    size_t result = 0x74FDCBED;
    result *= left;
    result *= op;
    result *= right;
    result *= value;
    return result;
}

void constraint_t::print(void) const {
    std::cout << "(" << left;
    if (cnf_left != 0) {
        std::cout << "[" << cnf_left << "]";
    }

    switch (op) {
        case op_t::AND:
            std::cout << " AND ";
            break;
        case op_t::NAND:
            std::cout << " NAND ";
            break;
        case op_t::OR:
            std::cout << " OR ";
            break;
        case op_t::NOR:
            std::cout << " NOR ";
            break;
        case op_t::XOR:
            std::cout << " XOR ";
            break;
    }
    std::cout << right;
    if (cnf_right != 0) {
        std::cout << "[" << cnf_right << "]";
    }
    std::cout << ") == " << value;
    if (cnf_value != 0) {
        std::cout << "[" << cnf_value << "]";
    }
    std::cout << std::endl;
}

namespace std {
    template<> struct hash<constraint_t> {
        size_t operator()(constraint_t const& object) {
            return object.hash();
        }
    };
}
