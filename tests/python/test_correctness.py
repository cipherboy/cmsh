import math
import pytest

import cmsh


def test_bc2cnf_examples():
    mod = cmsh.Model()

    c, d, e = mod.var(), mod.var(), mod.var()
    bit_sum = mod.to_vec([c, d, e]).bit_sum()
    b = (1 <= bit_sum) & (bit_sum <= 2)
    a = b & c
    mod.add_assert(a)

    known_solutions = [
        (True, False, False),
        (True, True,  False),
        (True, False, True)
    ]

    while mod.solve():
        sol = (bool(c), bool(d), bool(e))

        assert sol in known_solutions
        known_solutions.remove(sol)

        negated = mod.negate_solution((c, d, e))
        mod.add_assert(negated)

    assert len(known_solutions) == 0


def sudoku_build_grid(model, width=9):
    pos_grid = {}
    box_grid = {}
    row_grid = {}
    column_grid = {}
    all_squares = []

    bits = math.ceil(math.log(width, 2))
    boxes = math.sqrt(width)
    if math.ceil(boxes) != math.floor(boxes):
        raise ValueError("Width must be a square: %d" % width)
    boxes = int(boxes)

    for row in range(0, width):
        if row not in row_grid:
            row_grid[row] = [None]*width
        r_box = row//boxes

        for column in range(0, width):
            if column not in column_grid:
                column_grid[column] = [None]*width
            c_box = column//boxes
            if (r_box, c_box) not in box_grid:
                box_grid[(r_box, c_box)] = [None]*width

            i_box = (boxes * (row % boxes)) + (column % boxes)

            square = model.vector(bits)
            pos_grid[(row, column)] = square
            box_grid[(r_box, c_box)][i_box] = square
            row_grid[row][column] = square
            column_grid[column][row] = square
            all_squares.append(square)

    grid = {}
    grid['pos'] = pos_grid
    grid['box'] = box_grid
    grid['row'] = row_grid
    grid['col'] = column_grid
    grid['all'] = all_squares

    return grid


def sudoku_build_constraints(model, grid, width=9):
    constraints = True

    for key in grid['pos']:
        item = grid['pos'][key]
        item_range = (1 <= item) & (item <= width)
        constraints = constraints & item_range

    for grid_key in ['box', 'row', 'col']:
        for key in grid[grid_key]:
            items = grid[grid_key][key]
            for value in range(1, width+1):
                one_value = []
                for item in items:
                    one_value.append(item == value)

                vec_one_value = model.to_vector(one_value)
                constraints = constraints & (vec_one_value.bit_sum() == 1)

    return constraints


def sudoku_solve(known, solution):
    width = len(known)

    model = cmsh.Model()
    grid = sudoku_build_grid(model, width)
    consts = sudoku_build_constraints(model, grid, width)

    for i, row in enumerate(known):
        for j, value in enumerate(row):
            if not value:
                continue
            consts = consts & (grid['pos'][(i, j)] == value)

    model.add_assert(consts)
    assert model.solve()

    left = grid['pos'][(0, 0)]
    right = grid['pos'][(0, 0)]
    value = left | right

    output = int(value)

    negated = False
    for x in range(0, width):
        row = []
        for y in range(0, width):
            value = int(grid['pos'][(x, y)])
            assert value == solution[x][y]

            negation = grid['pos'][(x, y)] != value
            negated = negated | negation

    model.add_assert(negated)
    assert not model.solve()


def sudoku_conv(grid, width):
    results = []
    row = []

    for char in grid:
        if char == ' ':
            row.append(None)
        else:
            row.append(int(char))

        if len(row) == width:
            results.append(row)
            row = []

    assert len(row) == 0
    assert len(results) == width
    return results


def test_sudokus():
    grids = [
        ("     92753 5 2   1 2 1      62 4   7  3   5  5   6 89      3 4 6   8 7 37386     ",
         "146839275375426981829175436962548317483917562517362894251793648694281753738654129"),
        ("7238      59 2     1  7      7  5 341 5   7 929 7  5      5  9     4 16      1375",
         "723894651659123847418576923867915234135462789294738516381657492572349168946281375"),
        ("     1 28 3  5 7     8    31  2 936 6 3   1 2 271 6  44    5     6 9  4 27 4     ",
         "754361928832954716961827453148279365693548172527136894419685237386792541275413689"),
        ("     9 47  9  78  43 852   9      51  4   7  61      4   924 78  25  1  79 1     ",
         "586319247129467835437852916973248651254631789618795324361924578842576193795183462")
    ]

    for grid in grids:
        known = sudoku_conv(grid[0], 9)
        solution = sudoku_conv(grid[1], 9)
        sudoku_solve(known, solution)


if __name__ == "__main__":
    test_sudokus()
