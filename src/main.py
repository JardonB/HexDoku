from board import Board
from solver import get_unique_solution

def main():
    size = 16
    solution = Board(size)
    solution.generate_random()
    solution.display()

    puzzle = get_unique_solution(solution, percent_unfill=50)

    print("\nGenerated Puzzle:")
    puzzle.display()

if __name__ == "__main__":
    main()