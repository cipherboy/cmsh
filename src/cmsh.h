#include <cmath>
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

namespace cmsh {
    enum op_t {
        AND,
        NAND,
        OR,
        NOR,
        XOR
    };

    class constraint_t;
    class model_t;

    class constraint_t {
        friend model_t;

        protected:
            int left;
            op_t op;
            int right;
            int value;

            int cnf_left;
            int cnf_right;
            int cnf_value;

        public:
            bool operator==(const constraint_t& other);
            bool eval(bool left, bool right) const;

            size_t hash() const;

        protected:
            constraint_t(model_t *m, int l, op_t o, int r);
            void add(model_t *m);

            bool assigned();
            void assign_vars(model_t *m);

            static void add_clause(SATSolver *s, vector<Lit>& c, int var_1);
            static void add_clause(SATSolver *s, vector<Lit>& c, int var_1, int var_2);
            static void add_clause(SATSolver *s, vector<Lit>& c, int var_1, int var_2, int var_3);

        private:
            void tseitin(SATSolver *s, vector<Lit>& c);
            void tseitin_and(SATSolver *s, vector<Lit>& c);
            void tseitin_nand(SATSolver *s, vector<Lit>& c);
            void tseitin_or(SATSolver *s, vector<Lit>& c);
            void tseitin_nor(SATSolver *s, vector<Lit>& c);
            void tseitin_xor(SATSolver *s, vector<Lit>& c);
            static Lit to_lit(int var, bool neg=false);
    };

    class model_t {
        friend constraint_t;

        private:
            int constraint_var = 1;
            int cnf_var = 1;

            unordered_map<int, int> constraint_cnf_map;
            unordered_map<int, int> cnf_constraint_map;

            vector<constraint_t *> constraints;
            unordered_map<int, constraint_t*> value_constraint_map;
            unordered_map<int, unordered_set<constraint_t *>> operand_constraint_map;

            unordered_set<int> asserts;
            unordered_set<int> assumptions;

            unordered_map<int, bool> solution;

            lbool solved = l_False;

        protected:
            SATSolver *solver;
            vector<Lit> clause;

        private:
            int v_op(int left, op_t op, int right);
            void update_max_vars();

            static inline bool to_bool(lbool var, bool negate=false);
            static inline bool ubv(bool var, bool negate=false);

            void add_reachable();
            void extend_solution();

        protected:
            int next_constraint();
            int next_cnf();
            int cnf_from_constraint(int constraint_var);

        public:
            model_t(int threads=1, bool gauss=true);
            ~model_t();

            void config_timeout(double max_time);
            void config_conflicts(int64_t max_conflicts);

            int var();
            int cnf(int var);

            int v_and(int left, int right);
            int v_nand(int left, int right);
            int v_or(int left, int right);
            int v_nor(int left, int right);
            int v_xor(int left, int right);

            void v_assert(int var);
            void v_assert(const vector<int> vars);

            lbool solve(const vector<Lit>* assumptions=0, bool only_indep_solution=false);
            bool val(int constraint_var);
    };
}
