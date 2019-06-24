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

model_t::model_t(int threads, bool gauss) {
    solver = new SATSolver();
    solver->set_num_threads(threads);
    if (gauss) {
        solver->set_allow_otf_gauss();
    }
}

model_t::~model_t() {
    for (constraint_t *con : constraints) {
        delete con;
    }

    delete solver;
}

void model_t::config_timeout(double max_time) {
    solver->set_max_time(max_time);
}

void model_t::config_conflicts(int64_t max_conflicts) {
    solver->set_max_confl(max_conflicts);
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

void model_t::v_assert(const vector<int> vars) {
    for (int var : vars) {
        int cnf_var = cnf_from_constraint(var);
        asserts.insert(cnf_var);
    }
}

void model_t::update_max_vars() {
    int to_add = cnf_var - solver->nVars();
    if (to_add > 0) {
        solver->new_vars(to_add);
    }
}

lbool model_t::solve(const vector<Lit>* assumptions, bool only_indep_solution) {
    // Before adding constraints to the solver, we first need to figure out
    // the exact number of variables we have. Assign model variables to CNF
    // variables.
    for (constraint_t *con : constraints) {
        con->assign_vars(this);
    }

    // Inform the solver how many variables we have.
    update_max_vars();

    // Add all circuit-like constraints.
    for (constraint_t *con : constraints) {
        con->add(this);
    }

    // Add all asserts.
    for (int cnf_assert : asserts) {
        constraint_t::add_clause(solver, clause, cnf_assert);
    }

    // Solve the model.
    solved = solver->solve(assumptions, only_indep_solution);
    return solved;
}

inline bool model_t::to_bool(lbool var, bool negate) {
    if (var == l_True) {
        if (negate) {
            return false;
        }
        return true;
    } else if (var == l_False) {
        if (negate) {
            return true;
        }
        return false;
    }
    assert(false);
}

bool model_t::val(int constraint_var) {
    if (solved == l_True) {
        const vector<lbool>& result = solver->get_model();
        int cnf_var = 0;

        if (constraint_cnf_map.contains(constraint_var)) {
            cnf_var = constraint_cnf_map[constraint_var];
        } else if (constraint_cnf_map.contains(-constraint_var)) {
            cnf_var = -constraint_cnf_map[-constraint_var];
        } else {
            assert(false);
        }

        assert(result.size() > abs(cnf_var));
        return to_bool(result[cnf_var], cnf_var < 0);
    }

    assert(false);
    return false;
}
