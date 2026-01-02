from board import Board
from solver import solve, first_empty_cell

def main():
    size = 16
    board = Board(size)
    board.set_value(0, 0, 1)
    board.display()
    print(board)
    print("First empty cell:", first_empty_cell(board))
    if solve(board):
        print("Solved Board:")
        board.display()
        print(board.is_solved())
    else:
        print("No solution exists.")
    print(board.grid)

if __name__ == "__main__":
    main()