import math, random

def solve(board, randomized=False): # Solves the board using backtracking
    row, col = first_empty_cell(board)
    if (row, col) == (-1, -1):
        return True  # No empty cells left, solved
    
    if randomized:
        candidate_nums = list(board.valid_nums)
        random.shuffle(candidate_nums)
    else:
        candidate_nums = board.valid_nums

    for num in candidate_nums:
        if check_num_is_valid(board, row, col, num):
            board.set_value(row, col, num)
            if solve(board):
                return True
            board.set_value(row, col, None)  # Backtrack
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

        for num in board.valid_nums:
            if check_num_is_valid(board, row, col, num):
                board.set_value(row, col, num)
                continue_search = backtrack()
                board.set_value(row, col, None)

                if not continue_search:
                    return False
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
                candidates = [num for num in board.valid_nums if check_num_is_valid(board, row, col, num)]
                if len(candidates) < min_candidates:
                    min_candidates = len(candidates)
                    best_cell = (row, col)
                    if min_candidates == 1:
                        return best_cell  # Early exit if only one candidate, already optimal
    return best_cell

def check_num_is_valid(self, row, col, num): # Checks if a number can be placed in a cell
    box = (row // 4) * 4 + (col // 4)
    return (
        num not in self.rows[row] and
        num not in self.cols[col] and
        num not in self.boxes[box]
    )

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

