from board import Board
from solver import solve, first_empty_cell

def main():
    size = 16
    solution = Board(size)
    puzzle = Board(size)

    solution.generate_random()
    puzzle.grid = solution.grid.copy()

    solution.display()
    print(solution.is_solved())
    puzzle.display()
    print(puzzle.is_solved())

if __name__ == "__main__":
    main()