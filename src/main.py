import copy
from board import Board
from solver import solve, first_empty_cell, solution_is_unique

def main():
    size = 16
    solution = Board(size)
    puzzle = Board(size)

    solution.generate_random()
    puzzle.grid = copy.deepcopy(solution.grid)
    puzzle.unfill_cells(50)  # Unfill 25% of the cells  

    solution.display()
    print(f"solution grid is solved: {solution.is_solved()}")
    puzzle.display()
    print(f"puzzle grid is solved: {puzzle.is_solved()}")
    print(f"puzzle grid has unique solution: {solution_is_unique(puzzle)}")
    puzzle.display()

if __name__ == "__main__":
    main()