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

int model_t::cnf(int var) {
    return cnf_from_constraint(var);
}

int model_t::next_constraint() {
    int result = constraint_var;
    constraint_var += 1;

    operand_constraint_map[result] = unordered_set<constraint_t *>();
    return result;
}

int model_t::next_cnf() {
    int result = cnf_var;
    cnf_var += 1;

    return result;
}

int model_t::cnf_from_constraint(int constraint_var) {
    if (constraint_cnf_map.contains(constraint_var)) {
        assert(constraint_var > 0);
        return constraint_cnf_map[constraint_var];
    } else if (constraint_cnf_map.contains(-constraint_var)) {
        assert(constraint_var < 0);
        assert(constraint_cnf_map[-constraint_var] > 0);
        return -constraint_cnf_map[-constraint_var];
    }

    int cnf_var = next_cnf();
    constraint_cnf_map[abs(constraint_var)] = abs(cnf_var);
    cnf_constraint_map[abs(cnf_var)] = abs(constraint_var);

    if (constraint_var < 0) {
        return -cnf_var;
    }

    return cnf_var;
}

int model_t::v_op(int left, op_t op, int right) {
    assert(abs(left) < constraint_var);
    assert(abs(right) < constraint_var);
    assert(operand_constraint_map.contains(abs(left)));
    assert(operand_constraint_map.contains(abs(right)));

    constraint_t *con = new constraint_t(this, left, op, right);
    constraints.push_back(con);
    value_constraint_map[abs(con->value)] = con;
    operand_constraint_map[abs(left)].insert(con);
    operand_constraint_map[abs(right)].insert(con);
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

void model_t::add_reachable() {
    unordered_set<int> visited;
    unordered_set<int> queue;

    vector<constraint_t *> to_add;

    for (int cnf_assert : asserts) {
        int var_constraint = cnf_constraint_map[abs(cnf_assert)];
        queue.insert(abs(var_constraint));
    }

    while (!queue.empty()) {
        int var = queue.extract(queue.begin()).value();
        if (visited.contains(var)) {
            continue;
        }
        visited.insert(var);

        if (value_constraint_map.contains(var)) {
            constraint_t *con = value_constraint_map[var];
            if (!con->assigned()) {
                con->assign_vars(this);
                to_add.push_back(con);
            }

            queue.insert(abs(con->left));
            queue.insert(abs(con->right));
        }
    }

    update_max_vars();

    for (constraint_t *con : to_add) {
        con->add(this);
    }
}

void model_t::extend_solution() {
    const vector<lbool>& cnf_solution = solver->get_model();
    unordered_set<int> visited;
    unordered_set<int> queue;

    solution = unordered_map<int, bool>();

    for (int c_var = 1; c_var < cnf_var; c_var++) {
        if (!cnf_constraint_map.contains(c_var)) {
            assert(false);
        }

        int var = cnf_constraint_map[c_var];
        assert(var > 0);
        solution[var] = to_bool(cnf_solution[c_var], var < 0);

        if (operand_constraint_map.contains(var) && !operand_constraint_map[var].empty()) {
            queue.insert(var);
        }
    }

    while (!queue.empty()) {
        int var = queue.extract(queue.begin()).value();
        if (visited.contains(var)) {
            continue;
        }
        bool var_value = solution[var];
        visited.insert(var);

        for (constraint_t *con : operand_constraint_map[var]) {
            if (solution.contains(con->value)) {
                continue;
            }

            if (abs(con->left) == var) {
                if (!solution.contains(abs(con->right))) {
                    continue;
                }

                bool right_value = solution[abs(con->right)];
                bool con_value = con->valueOf(ubv(var_value, con->left < 0), ubv(right_value, con->right < 0));
                solution[con->value] = con_value;

                queue.insert(con->value);
            } else {
                if (!solution.contains(abs(con->left))) {
                    continue;
                }

                bool left_value = solution[abs(con->left)];
                bool con_value = con->valueOf(ubv(left_value, con->left < 0), ubv(var_value, con->right < 0));
                solution[con->value] = con_value;

                queue.insert(con->value);
            }
        }
    }
}

lbool model_t::solve(const vector<Lit>* assumptions, bool only_indep_solution) {
    // Add all clauses reachable from an assert or an asusmption.
    add_reachable();

    // Add all asserts.
    for (int cnf_assert : asserts) {
        constraint_t::add_clause(solver, clause, cnf_assert);
    }

    // Solve the model.
    solved = solver->solve(assumptions, only_indep_solution);

    // Calculate values for all values determined by the model.
    extend_solution();

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

inline bool model_t::ubv(bool value, bool negated) {
    return value ^ negated;
}

bool model_t::val(int constraint_var) {
    if (solved == l_True) {
        assert(solution.contains(constraint_var));
        return solution[constraint_var];
    }

    assert(false);
    return false;
}
