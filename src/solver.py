import math, random, copy

def solve(board): # Solves the board using backtracking
    row, col = first_empty_cell(board)
    if (row, col) == (-1, -1):
        return True  # No empty cells left, solved
    
    candidate_nums = list(board.valid_nums)
    random.shuffle(candidate_nums)  # Shuffle to generate random solutions

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

        row, col = first_empty_cell(board)
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
    unique_solution_board = copy.deepcopy(board)
    unique_solution_board.unfill_cells(percent_unfill)

    while not solution_is_unique(unique_solution_board):
        unique_solution_board = copy.deepcopy(board)
        unique_solution_board.unfill_cells(percent_unfill)
        percent_unfill = max(percent_unfill - 1, 1)  # Decrease unfill percentage to try again

    return unique_solution_board

def first_empty_cell(board):
    for row in board.grid:
        for cell in row:
            if cell is None:
                return (board.grid.index(row), row.index(cell))
    return (-1, -1)
            
def check_num_is_valid(board, row, col, num): # Checks if a number can be placed in a cell
    if check_box_is_valid(board, row, col, num) and \
       check_row_is_valid(board, row, col, num) and \
       check_col_is_valid(board, row, col, num):
        return True
    return False

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

