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
#define cleanup_visited free(visited)
/*#define declare_visited unordered_set<int> visited
#define is_visited(pos) (visited.contains(pos))
#define visit(pos) visited.insert(pos)*/

model_t::model_t(int threads, bool gauss) {
    // Create a new SATSolver (the CryptoMiniSat interface) with the
    // specified configuration. Note that all other members are allocated
    // as needed.
    solver = new SATSolver();
    assert(solver != NULL);

    solver->set_num_threads(threads);
    if (gauss) {
        solver->set_allow_otf_gauss();
    }
}

model_t::~model_t() {
    // Free all constraints in this model. We allocate them in v_op and place
    // the primary pointer to them in vector<constraint_t *> constraints. All
    // other references can be ignored.
    for (constraint_t *con : constraints) {
        delete con;
    }

    delete solver;
}

void model_t::config_timeout(double max_time) {
    if (max_time >= 0) {
        solver->set_max_time(max_time);
    } else {
        solver->set_max_time(std::numeric_limits<double>::max());
    }
}

void model_t::config_conflicts(int64_t max_conflicts) {
    if (max_conflicts > 0) {
        solver->set_max_confl(max_conflicts);
    } else {
        solver->set_max_confl(std::numeric_limits<int64_t>::max());
    }
}

int model_t::var() {
    return next_constraint();
}

int model_t::cnf(int var) {
    // Map a constraint variable to its CNF equivalent. Returns 0 if the
    // variable is not found.
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

    int a_constraint_var = abs(constraint_var);
    constraint_cnf_map[a_constraint_var] = cnf_var;
    cnf_constraint_map[cnf_var] = a_constraint_var;

    if (constraint_var < 0) {
        return -cnf_var;
    }

    return cnf_var;
}

int model_t::find_constraint(int left, op_t op, int right) {
    constraint_t us(NULL, left, op, right);

    int a_left = abs(left);
    int a_right = abs(right);

    // Check the smaller of the two operand listings for this constraint.
    // Compare not the pointer value, but the object under the pointer.
    if (operand_constraint_map[a_left].size() < operand_constraint_map[a_right].size()) {
        for (constraint_t *candidate : operand_constraint_map[a_left]) {
            if (*candidate == us) {
                assert(candidate->value != 0);
                return candidate->value;
            }
        }
    } else {
        for (constraint_t *candidate : operand_constraint_map[a_right]) {
            if (*candidate == us) {
                assert(candidate->value != 0);
                return candidate->value;
            }
        }
    }

    return 0;
}

void model_t::update_solution(constraint_t *con) {
    // If we're not solved, return.
    if (solved != CMSat::l_True) {
        return;
    }

    int a_left = abs(con->left);
    int a_right = abs(con->right);

    // If either of our parameters is not solved for, return.
    if (!solution.contains(a_left) || !solution.contains(a_right)) {
        return;
    }

    // Evaluate the value of the constraint and store it back in the solution
    // cache.
    bool left_value = solution[a_left];
    bool right_value = solution[a_right];
    bool con_value = con->eval(ubv(left_value, con->left < 0),
                               ubv(right_value, con->right < 0));
    solution[con->value] = con_value;
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

    // To add a constraint (value = left <op> right) we:
    //
    //  1. Initialize a new dynamic instance,
    //  2. Store it in the global list of instances to free,
    //  3. Store it in the global map of id->instance,
    //  4. Store it in the operand map for left->instance and right->instance,
    //  5. Update any existing solution.
    constraint_t *con = new constraint_t(this, left, op, right);
    constraints.push_back(con);

    value_constraint_map[abs(con->value)] = con;

    operand_constraint_map[abs(left)].insert(con);
    operand_constraint_map[abs(right)].insert(con);

    // Updating the solution here lets us handle post-solve computations on
    // available data. If we've solved for both of the operands, we can more
    // easily compute the value of the entire constraint than our caller can.
    update_solution(con);

    // Return the id of our new constraint.
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
    assert(var != 0);

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
    // add_reachable(...) lets us add only constraints that are reachable
    // from the base model assertions to the underlying CNF. This saves us
    // from solving for clauses we don't directly depend on.

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

    cleanup_visited;
}

void model_t::extend_solution() {
    // extend_solution() is called by solve(...) to compute values for
    // variables not part of the CNF but are fully determined by them. For
    // instance, in the following example:
    //      c1 = (v1 & v2)
    //      model.assert(c1 == True)
    //      c2 = (c1 | v2)
    // c2 won't get added to the underlying CNF as it isn't reachable from
    // the assert. However, after solving the model, c2's value is know: c1 has
    // been solved for, and in solving for c2, v2 also has gotten a value.
    //
    // We extend the solution by traversing the list of CNF variables, marking
    // them as solved, and on the edge of newly-solved variables, checking if
    // all reachable constraints have two solved-for variables. Any such
    // constraint is thus fully determined and can have its solution computed.
    // The result variable is then added to the edge.

    const vector<lbool>& cnf_solution = solver->get_model();
    declare_visited;
    unordered_set<int> queue;

    solution = unordered_map<int, bool>();

    assert(cnf_solution.size() == (size_t)cnf_var);

    // Walk all CNF variables: these correspond to constraint variables
    // with a known solution. Add them to a queue of solved variables to
    // process.
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

    // Processing a solved variable involves finding all constraints where it
    // is an operand and, when both constraints have been solved for,
    // computing the new value.
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

            // We need to know what side this var is on; otherwise we end up
            // with duplicate lookups for var_value.
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

    cleanup_visited;
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

    if (solved == CMSat::l_True) {
        // Calculate values for all values determined by the model when the
        // solution has been found.
        extend_solution();
    }

    return solved;
}

inline lbool model_t::to_lbool(bool var) {
    if (var) {
        return CMSat::l_True;
    }

    return CMSat::l_False;
}

inline bool model_t::to_bool(lbool var, bool negate) {
    if (var == CMSat::l_True) {
        if (negate) {
            return false;
        }
        return true;
    } else if (var == CMSat::l_False) {
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
    lbool result = lval(constraint_var);
    if (result == CMSat::l_True) {
        return true;
    } else if (result == CMSat::l_False) {
        return false;
    } else {
        assert(false);
        return false;
    }
}

lbool model_t::lval(int constraint_var) {
    // This version avoids the assert that val(...) has. This lets callers in
    // higher-level language bindings such as Python detect the error and
    // throw an exception rather than asserting.
    if (solved == CMSat::l_True) {
        if (constraint_var > 0) {
            if (!solution.contains(constraint_var)) {
                return CMSat::l_Undef;
            }

            return to_lbool(solution[constraint_var]);
        }

        if (!solution.contains(-constraint_var)) {
            return CMSat::l_Undef;
        }

        return to_lbool(!solution[-constraint_var]);
    }

    return CMSat::l_Undef;
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
