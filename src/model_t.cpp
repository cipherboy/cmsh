/*
 * Implementation of model_t for cmsh's native interface.
 *
 * Copyright (C) 2019 Alexander Scheel <alexander.m.scheel@gmail.com>
 *
 * See LICENSE in the root of the repository for license information.
 *
 * https://github.com/cipherboy/cmsh
 * High level bindings for Mate Soos's CryptoMiniSat.
 */

#include <set>
#include "cmsh.h"

using std::set;
using namespace cmsh;

// Define macros for building a visited "set": since most every variable
// will be visited under most models, it makes sense to put this in a uint64_t
// backed array instead of a complicated unordered_set instance.
//
// If the user wishes to use the unordered_set instance, they can comment
// out the second macro definitions and use those instead.
#define declare_visited uint64_t *visited = (uint64_t*)calloc((constraint_var / 64) + 1, sizeof(uint64_t))
#define bit(__pos) (((uint64_t) __pos) & 63ULL)
#define is_visited(__pos) ((visited[(__pos)/64] & (1ULL << bit(__pos))) == (1ULL << bit(__pos)))
#define visit(__pos) visited[(__pos)/64] = visited[(__pos)/64] | (1ULL << bit(__pos))
/*#define declare_visited unordered_set<int> visited
#define is_visited(pos) (visited.contains(pos))
#define visit(pos) visited.insert(pos)*/

model_t::model_t(int threads, bool gauss) {
    // Create a new SATSolver (the CryptoMiniSat interface) with the
    // specified configuration. Note that all other members are allocated
    // as needed.
    solver = new SATSolver();
    solver->set_num_threads(threads);
    if (gauss) {
        solver->set_allow_otf_gauss();
    }
}

model_t::~model_t() {
    // Free all constraints in this model. We allocate them in v_op and place
    // the primary pointer to them in vector<constraint_t *> constraints.
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
    // Map a constraint variable to its CNF equivalent. Returns 0 if the
    // variable is ont found.
    if (cnf_constraint_map.contains(var)) {
        return cnf_constraint_map[var];
    }

    return 0;
}

int model_t::next_constraint() {
    // Get the next constraint variable and increment the internal counter.
    int result = constraint_var;
    constraint_var += 1;

    // Explicitly create a new set for operands to place constraints they're
    // used in.
    operand_constraint_map[result] = unordered_set<constraint_t *>();
    return result;
}

int model_t::next_cnf() {
    // Get the next CNF variable and increment the internal counter.
    int result = cnf_var;
    cnf_var += 1;

    return result;
}

int model_t::cnf_from_constraint(int constraint_var) {
    // Convert a constraint variable to a CNF variable, allocating a new CNF
    // variable when one isn't assigned.
    if (constraint_cnf_map.contains(constraint_var)) {
        // When the map contains this variable directly, it should be
        // positive as the map only contains positive mappings.
        assert(constraint_var > 0);
        assert(constraint_cnf_map[constraint_var] > 0);
        return constraint_cnf_map[constraint_var];
    } else if (constraint_cnf_map.contains(-constraint_var)) {
        // When the map contains the negation of this variable, it should
        // be a negation of a variable and result in looking up a positive
        // CNF variable -- our resulting CNF variable will thus be negative
        // as well.
        assert(constraint_var < 0);
        assert(constraint_cnf_map[-constraint_var] > 0);
        return -constraint_cnf_map[-constraint_var];
    }

    // Allocate a new CNF variable and update the maps.
    int cnf_var = next_cnf();
    assert(cnf_var > 0);

    constraint_cnf_map[abs(constraint_var)] = cnf_var;
    cnf_constraint_map[cnf_var] = abs(constraint_var);

    if (constraint_var < 0) {
        return -cnf_var;
    }

    return cnf_var;
}

int model_t::find_constraint(int left, op_t op, int right) {
    constraint_t *us = new constraint_t(NULL, left, op, right);

    // Check the smaller of the two operand listings for this constraint.
    // Compare not the pointer value, but the object under the pointer.
    if (operand_constraint_map[abs(left)].size() < operand_constraint_map[abs(right)].size()) {
        for (constraint_t *candidate : operand_constraint_map[abs(left)]) {
            if (*candidate == *us) {
                return candidate->value;
            }
        }
    } else {
        for (constraint_t *candidate : operand_constraint_map[abs(right)]) {
            if (*candidate == *us) {
                return candidate->value;
            }
        }
    }

    return 0;
}

int model_t::v_op(int left, op_t op, int right) {
    assert(abs(left) < constraint_var);
    assert(abs(right) < constraint_var);
    assert(operand_constraint_map.contains(abs(left)));
    assert(operand_constraint_map.contains(abs(right)));

    // By checking if the constraint already exists, we can decrease the
    // size of the model in cases where many of the same operations are
    // performed. This can be seen in the sudoku native test case.
    int found_constraint = find_constraint(left, op, right);
    if (found_constraint != 0) {
        return found_constraint;
    }

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
    add_reachable(var);
}

void model_t::v_assert(const vector<int> vars) {
    for (int var : vars) {
        int cnf_var = cnf_from_constraint(var);
        asserts.insert(cnf_var);
        add_reachable(var);
    }
}

void model_t::v_assume(int var) {
    int cnf_var = cnf_from_constraint(var);
    assumptions.insert(cnf_var);
}

void model_t::v_unassume(int var) {
    int cnf_var = cnf_from_constraint(var);
    assumptions.erase(cnf_var);
    assumptions.erase(-cnf_var);
}

void model_t::update_max_vars() {
    int to_add = cnf_var - solver->nVars();
    if (to_add > 0) {
        solver->new_vars(to_add);
    }
}

inline Lit model_t::to_lit(int var, bool neg) const {
    bool sign = (var < 0) ^ neg;
    return Lit(abs(var), sign);
}


void model_t::add_clause(int var_1) {
    clause.clear();
    clause.push_back(to_lit(var_1));
    solver->add_clause(clause);
    clause_count += 1;
}

void model_t::add_clause(int var_1, int var_2) {
    clause.clear();
    clause.push_back(to_lit(var_1));
    clause.push_back(to_lit(var_2));
    solver->add_clause(clause);
    clause_count += 1;
}

void model_t::add_clause(int var_1, int var_2, int var_3) {
    clause.clear();
    clause.push_back(to_lit(var_1));
    clause.push_back(to_lit(var_2));
    clause.push_back(to_lit(var_3));
    solver->add_clause(clause);
    clause_count += 1;
}

void model_t::add_reachable(int constraint_from) {
    declare_visited;
    set<int> queue;
    vector<constraint_t *> to_add;

    queue.insert(abs(constraint_from));

    while (!queue.empty()) {
        int var = queue.extract(queue.begin()).value();
        if (is_visited(var)) {
            continue;
        }
        visit(var);

        if (value_constraint_map.contains(var)) {
            constraint_t *con = value_constraint_map[var];
            if (!con->assigned()) {
                con->assign_vars(this);
                to_add.push_back(con);
            }

            if (!is_visited(abs(con->left))) {
                queue.insert(abs(con->left));
            }
            if (!is_visited(abs(con->right))) {
                queue.insert(abs(con->right));
            }
        }
    }

    update_max_vars();

    for (constraint_t *con : to_add) {
        con->add(this);
    }
}

void model_t::extend_solution() {
    const vector<lbool>& cnf_solution = solver->get_model();
    declare_visited;
    unordered_set<int> queue;

    solution = unordered_map<int, bool>();

    assert(cnf_solution.size() == (size_t)cnf_var);

    for (int c_var = 1; c_var < cnf_var; c_var++) {
        assert(cnf_constraint_map.contains(c_var));

        int var = cnf_constraint_map[c_var];
        if (!solution.contains(var)) {
            solution[var] = to_bool(cnf_solution[c_var]);
        }

        if (operand_constraint_map.contains(var) && !operand_constraint_map[var].empty()) {
            queue.insert(var);
        }
    }

    while (!queue.empty()) {
        int var = queue.extract(queue.begin()).value();
        if (is_visited(var)) {
            continue;
        }
        visit(var);

        bool var_value = solution[var];

        for (constraint_t *con : operand_constraint_map[var]) {
            if (solution.contains(con->value)) {
                continue;
            }

            if (abs(con->left) == var) {
                if (!solution.contains(abs(con->right))) {
                    continue;
                }

                bool right_value = solution[abs(con->right)];
                bool con_value = con->eval(ubv(var_value, con->left < 0), ubv(right_value, con->right < 0));
                solution[con->value] = con_value;

                if (!is_visited(con->value)) {
                    queue.insert(con->value);
                }
            } else {
                if (!solution.contains(abs(con->left))) {
                    continue;
                }

                bool left_value = solution[abs(con->left)];
                bool con_value = con->eval(ubv(left_value, con->left < 0), ubv(var_value, con->right < 0));
                solution[con->value] = con_value;

                if (!is_visited(con->value)) {
                    queue.insert(con->value);
                }
            }
        }
    }
}

lbool model_t::solve(bool only_indep_solution) {
    // Add all asserts.
    for (int cnf_assert : asserts) {
        add_clause(cnf_assert);
    }

    // Build assumptions.
    vector<Lit> lit_assumptions;
    for (int cnf_assume : assumptions) {
        lit_assumptions.push_back(to_lit(cnf_assume));

        int constraint_var = cnf_constraint_map[abs(cnf_assume)];
        add_reachable(constraint_var);
    }

    // Solve the model.
    solved = solver->solve(&lit_assumptions, only_indep_solution);

    if (solved == l_True) {
        // Calculate values for all values determined by the model when the
        // solution has been found.
        extend_solution();
    }

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
        if (constraint_var > 0) {
            if (!solution.contains(constraint_var)) {
                extend_solution();
                assert(solution.contains(constraint_var));
            }

            return solution[constraint_var];
        }


        if (!solution.contains(abs(constraint_var))) {
            extend_solution();
            assert(solution.contains(abs(constraint_var)));
        }
        return !solution[abs(constraint_var)];
    }
    assert(false);
    return false;
}

int model_t::num_constraint_vars() {
    return constraint_var;
}

int model_t::num_constraints() {
    return constraints.size();
}

int model_t::num_cnf_vars() {
    return cnf_var;
}

int model_t::num_cnf_clauses() {
    return clause_count;
}
