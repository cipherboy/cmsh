#include <cmath>
#include <vector>
#include <unordered_map>
#include <cryptominisat5/cryptominisat.h>

#include "cmsh.h"

using std::vector;
using std::unordered_map;

using CMSat::SATSolver;
using CMSat::Lit;
using CMSat::lbool;

using namespace cmsh;

model_t::model_t() {
    solver = new SATSolver();
    solver->set_num_threads(1);
}

model_t::~model_t() {
    for (constraint_t *con : constraints) {
        delete con;
    }

    delete solver;
}

int model_t::var() {
    return next_constraint();
}

int model_t::next_constraint() {
    int result = constraint_var;
    constraint_var += 1;
    return result;
}

int model_t::next_cnf() {
    int result = cnf_var;
    cnf_var += 1;
    return result;
}

int model_t::cnf_from_constraint(int constraint_var) {
    if (constraint_cnf_map.contains(constraint_var)) {
        return constraint_cnf_map[constraint_var];
    } else if (constraint_cnf_map.contains(-constraint_var)) {
        return -constraint_cnf_map[-constraint_var];
    }

    int cnf_var = next_cnf();
    constraint_cnf_map[constraint_var] = cnf_var;
    cnf_constraint_map[cnf_var] = constraint_var;
    return cnf_var;
}

int model_t::v_op(int left, op_t op, int right) {
    constraint_t *con = new constraint_t(this, left, op, right);
    constraints.push_back(con);
    return con->value;
}

int model_t::v_and(int left, int right) {
    return v_op(left, op_t::AND, right);
}

int model_t::v_nand(int left, int right) {
    return v_op(left, op_t::NAND, right);
}

int model_t::v_or(int left, int right) {
    return v_op(left, op_t::OR, right);
}

int model_t::v_nor(int left, int right) {
    return v_op(left, op_t::NOR, right);
}

int model_t::v_xor(int left, int right) {
    return v_op(left, op_t::XOR, right);
}

void model_t::v_assert(int var) {
    int cnf_var = cnf_from_constraint(var);
    asserts.insert(cnf_var);
}

void model_t::update_max_vars() {
    int to_add = cnf_var - solver->nVars();
    if (to_add > 0) {
        solver->new_vars(to_add);
    }
}

lbool model_t::solve(const std::vector<Lit>* assumptions, bool only_indep_solution) {
    for (constraint_t *con : constraints) {
        con->assign_vars(this);
    }
    update_max_vars();

    for (constraint_t *con : constraints) {
        con->add(this);
    }
    for (int cnf_assert : asserts) {
        constraint_t::add_clause(solver, clause, cnf_assert);
    }

    return solver->solve(assumptions, only_indep_solution);
}
