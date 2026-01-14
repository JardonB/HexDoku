import math, random
from solver import solve, check_num_is_valid

class Board:
    def __init__(self, size):
        self.size = size
        self.grid = [[None for row in range(size)] for col in range(size)]
        self.rows = [set() for _ in range(size)]
        self.cols = [set() for _ in range(size)]
        self.boxes = [set() for _ in range(size)]
        self.valid_nums = [i for i in range(size)]
        self.valid_chars = [format(i, 'X') for i in range(size)]
        self.num_solutions = None

        # Store the solution board after generation
        self.solution_board = None

        # Bitmask representations for fast candidate computation
        self.box_width = int(math.sqrt(size))
        self.full_mask = (1 << size) - 1
        self.rows_mask = [0 for _ in range(size)]
        self.cols_mask = [0 for _ in range(size)]
        self.boxes_mask = [0 for _ in range(size)]

    def display(self): # Displays the board in a readable format
        for row in self.grid:
            print(" ".join("_" if num == None else format(num, 'X') for num in row))

    def set_value(self, row, col, num): # Sets a value in the board, updating tracking sets, no validation
        old = self.grid[row][col]
        if old is not None:
            self.rows[row].remove(old)
            self.cols[col].remove(old)
            box_index = (row // self.box_width) * self.box_width + (col // self.box_width)
            self.boxes[box_index].remove(old)
            bit = 1 << old
            self.rows_mask[row] &= ~bit
            self.cols_mask[col] &= ~bit
            self.boxes_mask[box_index] &= ~bit
        self.grid[row][col] = num

        if num is not None:
            self.rows[row].add(num)
            self.cols[col].add(num)
            box_index = (row // self.box_width) * self.box_width + (col // self.box_width)
            self.boxes[box_index].add(num)
            bit = 1 << num
            self.rows_mask[row] |= bit
            self.cols_mask[col] |= bit
            self.boxes_mask[box_index] |= bit

    def set_value_validated(self, row, col, value): # Sets a value in the board if valid, updating tracking sets
        if check_num_is_valid(self, row, col, value) or value is None:
            self.set_value(row, col, value)
        else:
            raise ValueError(f"Invalid value {value} for cell ({row}, {col})")
        
    def generate_random(self): # Generates a random solved board
        while not self.is_solved():
            self.set_all(None)
            solve(self, randomized=True)
        self.solution_board = self.board_copy()

    def unfill_cells(self, percent_unfill): # Unfills a percentage of cells to create a puzzle
        total_cells = self.size * self.size
        cells_to_unfill = int(total_cells * percent_unfill / 100)
        all_positions = [(r, c) for r in range(self.size) for c in range(self.size)]
        random_positions = random.sample(all_positions, cells_to_unfill)
        for r, c in random_positions:
            # use set_value to update masks and sets properly
            self.set_value(r, c, None)

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
        n = self.size
        # Build the grid and reset tracking sets and masks
        self.grid = [[value for _ in range(n)] for _ in range(n)]
        self.rows = [set() for _ in range(n)]
        self.cols = [set() for _ in range(n)]
        self.boxes = [set() for _ in range(n)]
        self.rows_mask = [0 for _ in range(n)]
        self.cols_mask = [0 for _ in range(n)]
        self.boxes_mask = [0 for _ in range(n)]

        # Populate tracking sets and masks if value is not None
        if value is not None:
            bit = 1 << value
            for r in range(n):
                for c in range(n):
                    self.rows[r].add(value)
                    self.cols[c].add(value)
                    box = (r // self.box_width) * self.box_width + (c // self.box_width)
                    self.boxes[box].add(value)
                    self.rows_mask[r] |= bit
                    self.cols_mask[c] |= bit
                    self.boxes_mask[box] |= bit

    def board_copy(self): # Returns a copy of the board with all attributes
        # Create an instance without running __init__ to avoid allocating
        # temporary structures twice. Copy only the necessary attributes.
        new = object.__new__(Board)
        new.size = self.size
        new.box_width = self.box_width
        new.grid = [row.copy() for row in self.grid]
        new.rows = [s.copy() for s in self.rows]
        new.cols = [s.copy() for s in self.cols]
        new.boxes = [s.copy() for s in self.boxes]
        new.valid_nums = self.valid_nums[:] if hasattr(self, 'valid_nums') else [i for i in range(new.size)]
        new.valid_chars = self.valid_chars[:] if hasattr(self, 'valid_chars') else [format(i, 'X') for i in range(new.size)]
        new.num_solutions = self.num_solutions
        new.solution_board = self.solution_board.board_copy() if self.solution_board else None
        new.full_mask = self.full_mask
        new.rows_mask = self.rows_mask[:]
        new.cols_mask = self.cols_mask[:]
        new.boxes_mask = self.boxes_mask[:]
        return new
    