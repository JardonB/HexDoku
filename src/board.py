import math, random
from solver import solve, check_num_is_valid

class Board:
    def __init__(self, size):
        self.size = size
        self.grid = [[None for row in range(size)] for col in range(size)]
        self.valid_nums = [i for i in range(size)]
        self.valid_chars = [format(i, 'X') for i in range(size)]
        self.num_solutions = None

    def display(self): # Displays the board in a readable format
        for row in self.grid:
            print(" ".join("_" if num == None else format(num, 'X') for num in row))

    def set_value(self, row, col, value): # Sets a value in the board if valid
        if check_num_is_valid(self, row, col, value) or value is None:
            self.grid[row][col] = value
        else:
            raise ValueError(f"Invalid value {value} for cell ({row}, {col})")
        
    def user_set_value(self, row, col, value): # Sets a value in the board without validation
        self.grid[row][col] = value
        
    def generate_random(self): # Generates a random solved board
        self.set_all(None)
        solve(self)

    def unfill_cells(self, percent_unfill): # Unfills a percentage of cells to create a puzzle
        total_cells = self.size * self.size
        cells_to_unfill = int(total_cells * percent_unfill / 100)
        all_positions = [(r, c) for r in range(self.size) for c in range(self.size)]
        random_positions = random.sample(all_positions, cells_to_unfill)
        for r, c in random_positions:
            self.grid[r][c] = None

    def is_solved(self): # Checks if the board is completely and correctly filled
        n = self.size
        allowed = set(self.valid_nums)

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

    def set_all(self, value): # Sets all cells to a specific value
        for r in self.grid:
            for c in r:
                self.grid[self.grid.index(r)][r.index(c)] = value
    