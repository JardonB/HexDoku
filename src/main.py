from board import Board
from solver import get_unique_solution
from display import HexDokuDisplay

def main():
    size = 16
    solution = Board(size)
    solution.generate_random()
    solution.display()

    puzzle = get_unique_solution(solution, percent_unfill=1)

    gui = HexDokuDisplay(puzzle)
    gui.run()

if __name__ == "__main__":
    main()