import math, random


def candidate_mask(board, row, col):
    box = (row // board.box_width) * board.box_width + (col // board.box_width)
    return board.full_mask & ~(board.rows_mask[row] | board.cols_mask[col] | board.boxes_mask[box])


def propagate(board):
    """Apply naked-single propagation repeatedly. Returns False on contradiction."""
    n = board.size
    made_progress = True
    while made_progress:
        made_progress = False
        for r in range(n):
            for c in range(n):
                if board.grid[r][c] is None:
                    mask = candidate_mask(board, r, c)
                    if mask == 0:
                        return False
                    # single candidate
                    if mask & (mask - 1) == 0:
                        num = mask.bit_length() - 1
                        board.set_value(r, c, num)
                        made_progress = True
    return True


def solve(board, randomized=False):
    """Backtracking solver with propagation and MRV heuristic.
    Returns True if solved, False otherwise."""
    # First apply deterministic propagation
    if not propagate(board):
        return False

    # If solved
    row, col = first_empty_cell(board)
    if (row, col) == (-1, -1):
        return True # No empty cells left, board is solved

    # Choose MRV cell
    row, col = best_empty_cell(board)
    mask = candidate_mask(board, row, col)
    # Build candidate list; shuffle if randomized
    candidates = []
    while mask:
        lowbit = mask & -mask
        num = lowbit.bit_length() - 1
        candidates.append(num)
        mask &= mask - 1
    if randomized:
        random.shuffle(candidates)

    for num in candidates:
        board.set_value(row, col, num)
        if solve(board, randomized=randomized):
            return True
        board.set_value(row, col, None)
    return False

def solution_is_unique(board): # Counts the number of solutions for the current board
    board.num_solutions = 0

    def backtrack():
        if board.num_solutions > 1:
            return False  # Early exit if more than one solution found

        row, col = best_empty_cell(board)
        if (row, col) == (-1, -1):
            board.num_solutions += 1
            return board.num_solutions <= 1  # Continue only if max solutions not exceeded
        # iterate candidate bits using board masks for speed
        box = (row // board.box_width) * board.box_width + (col // board.box_width)
        candidate_mask = board.full_mask & ~(board.rows_mask[row] | board.cols_mask[col] | board.boxes_mask[box])
        while candidate_mask:
            lowbit = candidate_mask & -candidate_mask
            num = lowbit.bit_length() - 1
            board.set_value(row, col, num)
            continue_search = backtrack()
            board.set_value(row, col, None)
            if not continue_search:
                return False
            candidate_mask &= candidate_mask - 1
        return True

    backtrack()
    return board.num_solutions == 1

def get_unique_solution(board, percent_unfill): # Returns the unique solution if it exists
    unique_solution_board = board.board_copy()
    unique_solution_board.unfill_cells(percent_unfill)

    while not solution_is_unique(unique_solution_board):
        unique_solution_board = board.board_copy()
        unique_solution_board.unfill_cells(percent_unfill)
        percent_unfill = max(percent_unfill - 1, 1)  # Decrease unfill percentage to try again

    return unique_solution_board

def first_empty_cell(board): # Finds the first empty cell in the board and returns its coordinates
    for row in range(len(board.grid)):
        for col in range(len(board.grid[row])):
            if board.grid[row][col] is None:
                return (row, col)
    return (-1, -1)

def best_empty_cell(board): # Finds the empty cell with the fewest valid candidates
    min_candidates = float('inf')
    best_cell = (-1, -1)
    for row in range(len(board.grid)):
        for col in range(len(board.grid[row])):
            if board.grid[row][col] is None:
                box = (row // board.box_width) * board.box_width + (col // board.box_width)
                candidate_mask = board.full_mask & ~(board.rows_mask[row] | board.cols_mask[col] | board.boxes_mask[box])
                count = candidate_mask.bit_count()
                if count < min_candidates:
                    min_candidates = count
                    best_cell = (row, col)
                    if min_candidates == 1:
                        return best_cell  # Early exit if only one candidate, already optimal
    return best_cell

def check_num_is_valid(self, row, col, num): # Checks if a number can be placed in a cell
    box = (row // self.box_width) * self.box_width + (col // self.box_width)
    bit = 1 << num
    return not (self.rows_mask[row] & bit or self.cols_mask[col] & bit or self.boxes_mask[box] & bit)

def check_box_is_valid(board, row, col, num): # Checks the sub-grid
    box_width = math.sqrt(board.size)
    box_start_row = row - (row % box_width)
    box_start_col = col - (col % box_width)
    for r in range(int(box_start_row), int(box_start_row + box_width)):
        for c in range(int(box_start_col), int(box_start_col + box_width)):
            if board.grid[r][c] == num:
                return False
    return True

def check_row_is_valid(board, row, col, num): # Checks the row
    for cell in board.grid[row]:
        if cell == num:
            return False
    return True

def check_col_is_valid(board, row, col, num): # Checks the column
    for r in board.grid:
        if r[col] == num:
            return False
    return True

