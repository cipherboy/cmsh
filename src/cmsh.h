/*
 * Core header file for cmsh's native interface.
 *
 * Copyright (C) 2019 Alexander Scheel <alexander.m.scheel@gmail.com>
 *
 * See LICENSE in the root of the repository for license information.
 *
 * https://github.com/cipherboy/cmsh
 * High level bindings for Mate Soos's CryptoMiniSat.
 */

#include <unordered_map>
#include <unordered_set>
#include <vector>
#include <cryptominisat5/cryptominisat.h>

using std::unordered_map;
using std::unordered_set;
using std::vector;

using CMSat::SATSolver;
using CMSat::Lit;
using CMSat::lbool;

#pragma once

namespace cmsh {
    /*
     * Internal detail: what operator is used in a constraint / circuit gate.
     */
    enum op_t {
        AND,
        NAND,
        OR,
        NOR,
        XOR
    };

    /*
     * Forward declarations of the classes we create. A constraint is a single
     * circuit gate (between two operands and having a single result) which
     * translates to multiple CNF clauses. model_t stores state about the full
     * circuit and wraps the SATSolver class from CryptoMiniSat.
     */
    class constraint_t;
    class model_t;

    /*
     * There are two types of variables: constraint variables and cnf
     * variables. The former are assigned by the model_t whenever they
     * are requested. The latter are assigned when the CNF is created and
     * given to the solver.
     *
     * Unlike CryptoMiniSat, both sets of variables are assigned beginning
     * at 1. This allows variable negations to be expressed as a negative for
     * all values. CryptoMiniSat begins at zero, at the cost of having a
     * separate literal class.
     */

    class constraint_t {
        friend model_t;

        /*
         * This class is largely internal implementation detail of model_t and
         * isn't exposed to the library user in most instances.
         */

        protected:
            // The variables representing the left operand, operator, right
            // operand, and the result of the computation.
            int left;
            op_t op;
            int right;
            int value = 0;

            // When assigned, these are the variables in the CNF for this
            // constraint. These correspond to the values of left, right,
            // and value above.
            int cnf_left = 0;
            int cnf_right = 0;
            int cnf_value = 0;

        public:
            // Operator for checking whether or not two 'constraint_t's are
            // equal. This is done on the basis of left, op, and right
            // variables. value is ignored.
            bool operator==(const constraint_t& other);

            // A hash function for this class. Allows us to implement a
            // hashable interface and put constraint_t directly into a
            // hashtable, though we don't currently.
            size_t hash() const;

        protected:
            // Constructor: private since constraint_t should only be
            // available as an internal detail of model_t and should be
            // created from there.
            constraint_t(model_t *m, int l, op_t o, int r);

            // Add this constraint to the specified model. Assumes that *m
            // is equal to the value in the constructor call.
            void add(model_t *m);

            // Returns true <=> all constraint variables have been assigned
            // values in the cnf. (i.e., cnf_* are non-zero).
            bool assigned();

            // Assigns values to the CNF variables based on whether or not
            // they've been previously assigned values in the model or not.
            // Note that this allocates new values for unseen variables.
            void assign_vars(model_t *m);

            // Evaluate the value of a circuit under the specified inputs.
            // This is used for
            bool eval(bool left, bool right) const;

        private:
            // Internal functions for normalizing a circuit gate into the
            // CNF. This is the basic Tseitin transform described in his
            // paper, "On the complexity of derivation in propositional
            // calculus". This leaves open other, more complicated
            // transformations as a future improvement.
            void tseitin(model_t *m);
            void tseitin_and(model_t *m);
            void tseitin_nand(model_t *m);
            void tseitin_or(model_t *m);
            void tseitin_nor(model_t *m);
            void tseitin_xor(model_t *m);
    };

    class model_t {
        friend constraint_t;

        /*
         * This class is the public interface of cmsh's native interface and
         * allows callers to interact with CryptoMiniSat via a circuit-like
         * interface instead of constructing a CNF themselves. For most users
         * this will be more intuitive.
         *
         * Additional functionality and convenience functions are provided by
         * the Python cmsh library which utilizes these methods.
         */

        private:
            // == Variables == //
            // Variables begin at one. These are counters for the number of
            // each. To query statistics, use the num_* functions in the
            // public section.
            int constraint_var = 1;
            int cnf_var = 1;
            int clause_count = 0;

            // Map from constraint variable number to CNF variable number,
            // if present and assigned.
            unordered_map<int, int> constraint_cnf_map;

            // Reverse of the above map. The internal function
            // cnf_from_constraint(int constraint_var) assigns both at the
            // same time.
            unordered_map<int, int> cnf_constraint_map;


            // == Constraints == //
            // A container of all our constraints (gates) in the model. These
            // have to be explicitly freed as items will be allocated with new.
            vector<constraint_t *> constraints;

            // A map between the output of the constraint (as a variable) and
            // the constraint itself.
            unordered_map<int, constraint_t*> value_constraint_map;

            // A map for looking up all constraints a variable appears in as
            // an operand (i.e., as either constraint_t->left or
            // constraint_t->right).
            unordered_map<int, unordered_set<constraint_t *>> operand_constraint_map;


            // == CNF Solving == //
            // The base assertions in our circuit constraint system.
            unordered_set<int> asserts;

            // Assumptions to solve the model under, if any.
            unordered_set<int> assumptions;

            // Solution to our model, representing a mapping between a
            // constraint variable and its boolean value. Note that this won't
            // necessarily include all variables.
            unordered_map<int, bool> solution;

            // Whether or not our model has been solved yet.
            lbool solved = l_False;

            // Pointer to our SAT solver instance.
            SATSolver *solver;

            // Helper variable for adding clauses to the solver.
            vector<Lit> clause;

        private:
            // Helper to find an existing constraint_t if it already exists.
            int find_constraint(int left, op_t op, int right);

            // Helper to create a new constraint_t; not exposed to callers.
            int v_op(int left, op_t op, int right);

            // Update number of CNF variables in the SATSolver object. The
            // pycryptosat Python bindings will automatically detect what
            // the largest variable is and set it in the solver. The C++
            // SATSolver interface does not, and requires an explicit call
            // informing the solver of the number of variables.
            //
            // We call this after calling assign_vars() on all constraints
            // added to the solver.
            void update_max_vars();

            // Convert the boolean-like lbool to a real bool, optionally
            // negating it. This assumes lbool is either l_True or l_False,
            // asserting on anything else (l_Undef for instance).
            static inline bool to_bool(lbool var, bool negate=false);

            // ubv is an internal function which stands for "update boolean
            // value" and is used to update a boolean value to match the sign
            // of a variable. In particular, solution only stores the positive
            // variables and their values; however, constraints may have the
            // negations of variables as inputs, which means the value from
            // solution needs to be conditionally negated based on the sign of
            // the variable's int identifier. This is used for that.
            static inline bool ubv(bool var, bool negate=false);

            // A helper method of solve(): add all reachable constraints
            // reachable from the assumptions or assertions to the SATSolver
            // model.
            void add_reachable();

            // Extend the solution from the SATSolver to include constraints
            // which are fully determined by the solution but not added to the
            // constraint because they aren't necessary in reaching an
            // asserted variable. The user still expects a value for them
            // (when calling val(int var)) because they don't know that the
            // constraint wasn't given to the SATSolver.
            void extend_solution();

        protected:
            // Get the identifier of the next constraint variable and
            // increment the internal counter of the number of constraint
            // variables.
            int next_constraint();

            // Get the identifier of the next CNF variable and increment the
            // internal counter of the number of CNF variables.
            int next_cnf();

            // Convert a constraint variable to a CNF variable at assignment
            // time, allocating a new CNF variable if one doesn't already
            // exist for this variable.
            int cnf_from_constraint(int constraint_var);

            // Add a 1-, 2-, or 3-variable clause to the CNF model.
            void add_clause(int var_1);
            void add_clause(int var_1, int var_2);
            void add_clause(int var_1, int var_2, int var_3);

            // Convert an integer CNF variable to a SATSolver Lit class,
            // optionally negating it.
            inline Lit to_lit(int var, bool neg=false) const;

        public:
            /*
             * Public interface to cmsh's C++ bindings.
             */

            // The constructor takes two CryptoMiniSat configuration values
            // which must be specified before adding any clauses:
            //
            //  - the number of threads to use for solving
            //  - whether or not to use Gaussian elimnation.
            //
            // Note that the latter requires CryptoMiniSat to be compiled with
            // support for Gaussian elimination.
            model_t(int threads=1, bool gauss=true);

            // Our deconstructor calls SATSolver's and frees all internally
            // allocated data. This can be intentionally omitted when you're
            // only intending to solve one model and exit, letting the OS
            // clean up after you.
            ~model_t();

            // Configure the max time the solver should run for, for any
            // given call to SATSolver->solve(). Note that you can call
            // SATSolver->solve() multiple times with different assumptions
            // and different timeouts / conflict counts if you desire.
            void config_timeout(double max_time);

            // Configure the maxinimum number of conflicts until the solver
            // should exit on any given call to SATSolver->solve(). See note
            // on config_timeout above.
            void config_conflicts(int64_t max_conflicts);

            // Create a new constraint variable, returning its value. This
            // should be used with all calls below; the value from cnf(...)
            // should never be used unless parsing the generated CNF and
            // correlating the variables there with constraint variables.
            int var();

            // Inquire as to the value of the cnf variable for the associated
            // constraint variable. Returns 0 when the constraint variable
            // hasn't yet been assigned a CNF counterpart.
            int cnf(int var);

            // These functions create a new gate and add it to the model. The
            // parameters to these functions are values returned by var() or
            // the gate functions below. Each function returns the identifier
            // of the variable representing the value of the evaluated gate.
            int v_and(int left, int right);
            int v_nand(int left, int right);
            int v_or(int left, int right);
            int v_nor(int left, int right);
            int v_xor(int left, int right);

            // Assert that a single variable is true. A negative variable
            // identifier can be passed here, in which case the negation
            // of the variable is asserted to be true, i.e., the variable
            // is asserted to be false.
            void v_assert(int var);

            // Same as v_assert(int var) except that it takes a series of
            // variables to assert instead of a single variable.
            void v_assert(const vector<int> vars);

            // Solve the model under the specified set of assumptions.
            lbool solve(const vector<Lit>* assumptions=0, bool only_indep_solution=false);

            // Get the value of a constraint variable after solve returns
            // l_True. If solve returns anything other than l_True, and
            // val(...) is called, it will assert.
            bool val(int var);

            // Functions to get statistics about the size of the constraint
            // model and the underlying CNF.
            int num_constraint_vars();
            int num_constraints();
            int num_cnf_vars();
            int num_cnf_clauses();
    };
}
