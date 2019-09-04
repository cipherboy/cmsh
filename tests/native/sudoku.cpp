#include "cmsh.h"
#include <iostream>

using namespace cmsh;
using namespace std;

#define GSQRT (3)
#define GMAX (GSQRT*GSQRT)

int to_num(model_t *m, int square[GMAX]) {
    for (int i = 0; i < GMAX; i++) {
        if (m->val(square[i])) {
            for (int j = i+1; j < GMAX; j++) {
                assert(!m->val(square[j]));
            }
            return i+1;
        }
    }
    assert(false);
    return -1;
}

int ***build_grid(model_t *m) {
    int ***grid = new int**[GMAX];

    for (int i = 0; i < GMAX; i++) {
        grid[i] = new int*[GMAX];
        for (int j = 0; j < GMAX; j++) {
            grid[i][j] = new int[GMAX];
            for (int k = 0; k < GMAX; k++) {
                grid[i][j][k] = m->var();
            }
        }
    }

    return grid;
}

void free_grid(int ***grid) {
    for (int i = 0; i < GMAX; i++) {
        for (int j = 0; j < GMAX; j++) {
            delete [] grid[i][j];
        }
        delete [] grid[i];
    }
    delete [] grid;
}

void one_of(model_t *m, int *choices) {
    int result = 0;
    for (int i = 0; i < GMAX; i++) {
        int base = choices[i];
        for (int j = 0; j < GMAX; j++) {
            if (j == i) {
                continue;
            }
            base = m->v_and(base, -choices[j]);
        }

        if (result == 0) {
            result = base;
        } else {
            result = m->v_or(result, base);
        }
    }

    m->v_assert(result);
}

void add_constraints(model_t *m, int ***grid) {
    for (int x = 0; x < GMAX; x++) {
        for (int y = 0; y < GMAX; y++) {
            int *row = new int[GMAX];
            int *col = new int[GMAX];
            one_of(m, grid[x][y]);
            for (int z = 0; z < GMAX; z++) {
                row[z] = grid[z][x][y];
            }
            one_of(m, row);
            for (int z = 0; z < GMAX; z++) {
                col[z] = grid[x][z][y];
            }
            one_of(m, col);
            delete [] row;
            delete [] col;
        }
    }

    for (int x = 0; x < GSQRT; x++) {
        for (int y = 0; y < GSQRT; y++) {
            for (int z = 0; z < GMAX; z++) {
                int *square = new int[GMAX];
                size_t s_i = 0;
                for (int dx = 0; dx < GSQRT; dx++) {
                    int ax = GSQRT*x + dx;
                    for (int dy = 0; dy < GSQRT; dy++) {
                        int ay = GSQRT*y + dy;
                        square[s_i] = grid[ax][ay][z];
                        s_i += 1;
                    }
                }
                assert(s_i == GMAX);
                one_of(m, square);
                delete [] square;
            }
        }
    }
}

void overlap_grid(model_t *m, int ***grid_1, int x1, int y1, int ***grid_2, int x2, int y2) {
    for (int dx = 0; dx < GSQRT; dx++) {
        for (int dy = 0; dy < GSQRT; dy++) {
            int gx1 = x1 + dx;
            int gy1 = y1 + dy;
            int gx2 = x2 + dx;
            int gy2 = y2 + dy;
            for (int z = 0; z < GMAX; z++) {
                int equals = -(m->v_xor(grid_1[gx1][gy1][z], grid_2[gx2][gy2][z]));
                m->v_assert(equals);
            }
        }
    }
}

void print_solution(model_t *m, int ***grid) {
    for (int x = 0; x < GMAX; x++) {
        for (int y = 0; y < GMAX; y++) {
            int value = to_num(m, grid[x][y]);
            std::cout << value << " ";
        }
        std::cout << std::endl;
    }
}

int main() {
    model_t m;

    int ***grid_tl = build_grid(&m);
    int ***grid_tr = build_grid(&m);
    int ***grid_c = build_grid(&m);
    int ***grid_bl = build_grid(&m);
    int ***grid_br = build_grid(&m);

    add_constraints(&m, grid_tl);
    add_constraints(&m, grid_tr);
    add_constraints(&m, grid_c);
    add_constraints(&m, grid_bl);
    add_constraints(&m, grid_br);

    int end = GMAX - GSQRT;
    overlap_grid(&m, grid_tl, end, end, grid_c, 0, 0);
    overlap_grid(&m, grid_tr, end, 0, grid_c, 0,  end);
    overlap_grid(&m, grid_bl, 0, end, grid_c, end, 0);
    overlap_grid(&m, grid_tl, 0, 0, grid_c, end, end);

    cout << "Starting solving..." << endl;
    assert(m.solve() == l_True);
    cout << "    ...done solving model with circuit size ("
         << m.num_constraint_vars() << ", " << m.num_constraints()
         << ") and CNF size (" << m.num_cnf_vars() << ", "
         << m.num_cnf_clauses() << ")." << endl;

    cout << "top_left" << endl;
    print_solution(&m, grid_tl);
    cout << endl;

    cout << "top_right" << endl;
    print_solution(&m, grid_tr);
    cout << endl;

    cout << "center" << endl;
    print_solution(&m, grid_c);
    cout << endl;

    cout << "bottom_left" << endl;
    print_solution(&m, grid_bl);
    cout << endl;

    cout << "bottom_right" << endl;
    print_solution(&m, grid_br);
    cout << endl;

    free_grid(grid_tl);
    free_grid(grid_tr);
    free_grid(grid_c);
    free_grid(grid_bl);
    free_grid(grid_br);
    return 0;
}
