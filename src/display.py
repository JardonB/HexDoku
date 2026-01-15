import tkinter as tk
import tkinter.messagebox as mb
from board import Board
from solver import check_num_is_valid, char_to_num, num_to_char, get_unique_solution, best_empty_cell
from save import save_state, load_state, SAVE_PATH

MAX_DIFFICULTY, MIN_DIFFICULTY = 60, 1

class HexDokuDisplay:
    board: "Board | None"
    cells: "list[list[tk.Entry | None]] | None"

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HexDoku")
        self.root.protocol("WM_DELETE_WINDOW", self._on_quit) # Handle window close event by calling _on_quit

        self.start_frame = tk.Frame(self.root)
        self.game_frame = tk.Frame(self.root)

        self.board = None # Board object to be set later after difficulty selection
        self.fixed = None # Track fixed cells after puzzle generation
        self.cells = None # To be initialized after board is set

        self.hardcore_mode = tk.BooleanVar(value=False) # Variable for hardcore mode, which will disable hints, fills, and incorrect input indication
        
        self._build_start_screen()
        self.start_frame.pack(fill='both', expand=True)

    def _build_start_screen(self):
        # Kill the old start frame if it exists
        if hasattr(self, 'start_frame'):
            self.start_frame.destroy()
        
        self.start_frame = tk.Frame(self.root)
        label = tk.Label(self.start_frame, text="HexDoku", font=("Arial", 24))
        label.pack(pady=20)

        tk.Label(self.start_frame, text=f"Select Difficulty ({MIN_DIFFICULTY}-{MAX_DIFFICULTY}):", font=("Arial", 14)).pack(pady=10)

        # Difficulty slider, controls percent of cells to unfill
        self.difficulty_var = tk.IntVar(value=int(MAX_DIFFICULTY - MIN_DIFFICULTY) // 2 + MIN_DIFFICULTY)
        slider = tk.Scale(
            self.start_frame, 
            from_=MIN_DIFFICULTY, 
            to=MAX_DIFFICULTY, 
            orient="horizontal",
            variable=self.difficulty_var,
            showvalue=True,
            length=300,)
        slider.pack(pady=10)

        # Hardcore mode checkbox
        hardcore_check = tk.Checkbutton(
            self.start_frame,
            text="Hardcore Mode (No Hints or Fills)",
            variable=self.hardcore_mode
        )
        hardcore_check.pack(pady=10)

        start_button = tk.Button(self.start_frame, text="Start Game", command=self._start_game, bg="green")
        start_button.pack(pady=10)

        if SAVE_PATH.exists():
            continue_button = tk.Button(self.start_frame, text="Continue Saved Game", command=self._continue_game)
            continue_button.pack(pady=5)

        quit_button = tk.Button(self.start_frame, text="Quit", command=self._on_quit, bg="red", fg="white")
        quit_button.pack(pady=5)

    def _start_game(self):
        # Kill the old frames
        if hasattr(self, 'game_frame'):
            self.game_frame.destroy()

        # Get the selected difficulty
        percent_unfill = self.difficulty_var.get()
        hardcore = self.hardcore_mode.get()

        # Generate puzzle board based on difficulty
        puzzle = Board(16)
        puzzle.generate_random()
        puzzle = get_unique_solution(puzzle, percent_unfill)
        self.board = puzzle
        self.fixed = [[self.board.grid[r][c] for c in range(self.board.size)] for r in range(self.board.size)]
        self.cells = [[None for _ in range(self.board.size)] for _ in range(self.board.size)]
        self.hardcore = hardcore

        # Setup game frames
        self._setup_game_frames()

    def _setup_game_frames(self):
        # Kill the old frames
        if hasattr(self, 'game_frame'):
            self.game_frame.destroy()

        # Hide start frame and show game frame
        self.start_frame.pack_forget()
        self.game_frame = tk.Frame(self.root)
        self.game_frame.pack(fill='both', expand=True)

        # Start control frame
        self.control_frame = tk.Frame(self.game_frame)
        self.control_frame.pack(side="top", fill="x")

        # Build control buttons
        state = "disabled" if self.hardcore else "normal"
        hint_btn = tk.Button(self.control_frame, text="Hint", command=self._show_hint, bg="yellow", state=state)
        hint_btn.pack(side="left", padx=10)
        fill_one_btn = tk.Button(self.control_frame, text="Fill One", command=self._fill_one_space, bg="lightblue", state=state)
        fill_one_btn.pack(side="left", padx=10)
        quit_btn = tk.Button(self.control_frame, text="Quit", command=self._on_quit, bg="red", fg="white")
        quit_btn.pack(side="right", padx=10)
        restart_btn = tk.Button(self.control_frame, text="Restart", command=self._restart_game, bg="orange")
        restart_btn.pack(side="right", padx=10)
        back_btn = tk.Button(self.control_frame, text="Back to Menu", command=self._back_to_start)
        back_btn.pack(side="right", padx=10)

        # Start and build grid frame
        self.grid_frame = tk.Frame(self.game_frame)
        self.grid_frame.pack(side="top")
        self._build_grid()
        self._render_board()

    def _on_quit(self):
        if self.board is not None:
            save_state(self.board, self.fixed, self.difficulty_var.get(), self.hardcore)
        self.root.quit()

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
                frame = tk.Frame(self.grid_frame, highlightthickness=0, bd=0, bg="black")
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
                    widget.config(state='normal', bg='white', fg='black')

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
        if self.board is not None:
            save_state(self.board, self.fixed, self.difficulty_var.get(), self.hardcore)
        self.game_frame.pack_forget()
        self._build_start_screen()
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
            if not self.hardcore: # Only indicate incorrect input if not in hardcore mode
                widget.config(bg="red", fg="white")

    def _show_hint(self):
        if self.board is None or self.cells is None:
            raise ValueError("Board and cells must be initialized before showing hints.")
        
        row, col = best_empty_cell(self.board)
        if row == -1 and col == -1:
            mb.showinfo("No Hints", "The puzzle is already complete!")
            return
        cell = self.cells[row][col]
        if cell is None:
            return
        cell.config(bg="yellow")

    def _fill_one_space(self):
        if self.board is None or self.cells is None or self.board.solution_grid is None:
            raise ValueError("Board and cells must be initialized before filling spaces.")
        
        row, col = best_empty_cell(self.board)
        if row == -1 and col == -1:
            mb.showinfo("No Spaces", "The puzzle is already complete!")
            return
        
        # Fill the cell with the correct solution value
        correct_value = self.board.solution_grid[row][col]
        self.board.set_value(row, col, correct_value)
        cell = self.cells[row][col]
        if cell is None:
            return
        cell.delete(0, tk.END)
        cell.insert(0, num_to_char(correct_value))
        cell.config(bg="lightblue", fg="black")

        # Check for puzzle completion
        if self.board.is_solved():
            self._show_puzzle_complete()

    def _restart_game(self):
        if self.board is None or self.fixed is None:
            raise ValueError("Board and fixed cells must be initialized before restarting the game.")
        
        # Reset board to original puzzle state
        for r in range(self.board.size):
            for c in range(self.board.size):
                val = self.fixed[r][c]
                self.board.set_value(r, c, val)
        self._render_board()

    def _continue_game(self):
        data = load_state()
        if data is None:
            return  # no save, or handle gracefully

        size = data["size"]
        grid = data["grid"]
        fixed = data["fixed"]
        solution = data["solution"]
        difficulty = data.get("difficulty", 3)
        hardcore = data.get("hardcore_mode", False)

        board = Board(size)
        board.grid = grid
        self.fixed = fixed
        board.solution_grid = solution
        self.hardcore = hardcore

        # Rebuild masks/sets from grid (so check_num_is_valid works)
        board.rebuild_masks_from_grid()

        self.board = board
        self.difficulty_var.set(difficulty)
        self.cells = [[None for _ in range(size)] for _ in range(size)]

        self.start_frame.pack_forget()
        self.game_frame.pack(fill="both", expand=True)

        # Set up game frames
        self._setup_game_frames()

    def run(self):
        self.root.mainloop()
