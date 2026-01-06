import copy
from board import Board
from solver import solve, first_empty_cell, solution_is_unique, get_unique_solution

def main():
    size = 16
    solution = Board(size)
    solution.generate_random()

    puzzle = get_unique_solution(solution, percent_unfill=20)

    puzzle.display()

if __name__ == "__main__":
    main()