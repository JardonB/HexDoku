import math
from solver import solve, check_num_is_valid

class Board:
    def __init__(self, size):
        self.size = size
        self.grid = [[None for _ in range(size)] for _ in range(size)]
        self.valid_nums = set([i for i in range(size)])

    def display(self):
        for row in self.grid:
            print(" ".join(str(num) if num == None else format(num, 'X') for num in row))

    def set_value(self, row, col, value):
        if check_num_is_valid(self, row, col, value) or value is None:
            self.grid[row][col] = value
        else:
            raise ValueError(f"Invalid value {value} for cell ({row}, {col})")
        
    def generate_random(self):
        self.set_all(None)
        solve(self)

    def is_solved(self):
        n = self.size
        allowed = self.valid_nums

        # rows
        for r in range(n):
            if set(self.grid[r]) != allowed:
                return False

        # columns
        for c in range(n):
            col = [self.grid[r][c] for r in range(n)]
            if set(col) != allowed:
                return False

        # boxes
        box_width = int(math.sqrt(n))
        for br in range(0, n, box_width):
            for bc in range(0, n, box_width):
                box_cells = []
                for r in range(br, br + box_width):
                    for c in range(bc, bc + box_width):
                        box_cells.append(self.grid[r][c])
                if set(box_cells) != allowed:
                    return False

        return True

    def __repr__(self):
        return f"Board(size={self.size})"

    def set_all(self, value):
        for r in self.grid:
            for c in r:
                self.grid[self.grid.index(r)][r.index(c)] = value
    