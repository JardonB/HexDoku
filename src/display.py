import tkinter as tk
import tkinter.messagebox as mb
from board import Board
from solver import check_num_is_valid, char_to_num, num_to_char, get_unique_solution

class HexDokuDisplay:
    board: "Board | None"
    cells: "list[list[tk.Entry | None]] | None"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HexDoku")

        self.start_frame = tk.Frame(self.root)
        self.game_frame = tk.Frame(self.root)

        self.board = None # Board object to be set later after difficulty selection
        self.fixed = None # Track fixed cells after puzzle generation
        self.cells = None # To be initialized after board is set
        
        self._build_start_screen()
        self.start_frame.pack(fill='both', expand=True)

    def _build_start_screen(self):
        label = tk.Label(self.start_frame, text="HexDoku", font=("Arial", 24))
        label.pack(pady=20)

        tk.Label(self.start_frame, text="Select Difficulty:", font=("Arial", 14)).pack(pady=10)

        # Difficulty slider, 1-75% unfilled
        self.difficulty_var = tk.IntVar(value=38)
        slider = tk.Scale(
            self.start_frame, 
            from_=1, 
            to=75, 
            orient="horizontal",
            variable=self.difficulty_var,
            showvalue=True,)
        slider.pack(pady=10)

        start_button = tk.Button(self.start_frame, text="Start Game", command=self._start_game)
        start_button.pack(pady=10)

        quit_button = tk.Button(self.start_frame, text="Quit", command=self.root.quit)
        quit_button.pack(pady=5)

    def _start_game(self):
        # Get the selected difficulty
        percent_unfill = self.difficulty_var.get()

        # Generate puzzle board based on difficulty
        puzzle = Board(16)
        puzzle.generate_random()
        puzzle = get_unique_solution(puzzle, percent_unfill)
        self.board = puzzle
        self.fixed = [[self.board.grid[r][c] for c in range(self.board.size)] for r in range(self.board.size)]
        self.cells = [[None for _ in range(self.board.size)] for _ in range(self.board.size)]

        # Hide start frame and show game frame
        self.start_frame.pack_forget()
        self.game_frame.pack(fill='both', expand=True)

        # Build the game grid inside game frame
        self._build_grid()
        self._render_board()

    def _build_grid(self):
        if self.board is None or self.cells is None:
            raise ValueError("Board and cells must be initialized before building the grid.")
        
        for r in range(self.board.size):
            for c in range(self.board.size):
                # Decide if this cell is on a 4x4 box boundary
                top_border    = (r % self.board.box_width == 0)
                left_border   = (c % self.board.box_width == 0)
                bottom_border = (r == self.board.size - 1)
                right_border  = (c == self.board.size - 1)

                # Create a frame to hold the entry and draw borders with it
                frame = tk.Frame(self.game_frame, highlightthickness=0, bd=0, bg="black")
                frame.grid(row=r, column=c, padx=0, pady=0, sticky="nsew")

                # Use internal padding of the frame to simulate borders
                ipadx_left = 1 + (2 if left_border else 0)
                ipady_top  = 1 + (2 if top_border else 0)
                ipady_bot  = 1 + (2 if bottom_border else 0)
                ipadx_right= 1 + (2 if right_border else 0)

                inner = tk.Frame(frame, bg="black")
                inner.pack(
                    padx=(ipadx_left, ipadx_right),
                    pady=(ipady_top, ipady_bot)
                )

                entry = tk.Entry(inner, width=2, font=("Arial", 16), justify="center")
                entry.pack()

                # Bind events
                entry.bind("<FocusOut>", lambda e, row=r, col=c: self._on_cell_change(e, row, col))
                self.cells[r][c] = entry

    def _render_board(self):
        if self.board is None or self.cells is None:
            raise ValueError("Board and cells must be initialized before rendering the grid.")
        
        for r in range(self.board.size):
            for c in range(self.board.size):
                val = self.board.grid[r][c]
                widget = self.cells[r][c]
                if widget is None:
                    continue
                widget.delete(0, tk.END)
                if val is not None:
                    widget.insert(0, num_to_char(val))
                
                if self._is_fixed_cell(r, c):
                    widget.config(state='readonly', readonlybackground='lightgray', fg='black')
                else:
                    widget.config(state='normal')

    def _is_fixed_cell(self, row, col):
        # Fixed cells are those that are not None in the original puzzle board
        return False if self.fixed is None else self.fixed[row][col] is not None
    
    def _show_puzzle_complete(self): # Highlight all cells to indicate completion
        if self.board is None or self.cells is None:
            raise ValueError("Board and cells must be initialized before showing completion.")
        
        for r in range(self.board.size):
            for c in range(self.board.size):
                cell = self.cells[r][c]
                if cell is None:
                    continue
                cell.config(state='readonly', readonlybackground='lightgreen', fg='black')
        mb.showinfo("Congratulations!", "Puzzle Completed Successfully! Click OK to return to start screen.")
        self._back_to_start()

    def _back_to_start(self):
        self.game_frame.pack_forget()
        self.start_frame.pack(fill='both', expand=True)

    def _on_cell_change(self, event, r: int, c: int):
        if self.board is None or self.cells is None:
            raise ValueError("Board and cells must be initialized before handling cell changes.")
        
        widget = event.widget
        text = widget.get().strip().upper()

        # If fixed cell, revert any changes
        if self._is_fixed_cell(r, c) and self.fixed is not None:
            original_val = self.fixed[r][c]
            widget.delete(0, tk.END)
            if original_val is not None:
                widget.insert(0, num_to_char(original_val))
            widget.config(bg="lightgray", fg="black", state='readonly')
            return
        
        # If cell is not fixed and text is empty, clear the cell
        if text == "":
            self.board.set_value(r, c, None)
            widget.config(bg="white", fg="black")
            return
        
        # Validate that input is a single allowed character
        allowed = set(self.board.valid_chars)
        if len(text) != 1 or text not in allowed:
            widget.config(bg="red", fg="white")
            return
        
        # Convert char to number
        num = char_to_num(text)
        if check_num_is_valid(self.board, r, c, num):
            self.board.set_value(r, c, num)
            widget.config(bg="white", fg="black")

            # Check for puzzle completion
            if self.board.is_solved():
                self._show_puzzle_complete()
        else:
            # Clear the cell from the board state when validation fails
            self.board.set_value(r, c, None)
            widget.config(bg="red", fg="white")

    def run(self):
        self.root.mainloop()
