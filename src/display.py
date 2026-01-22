import tkinter as tk
from tkinter import ttk
import tkinter.messagebox as mb
from settings import get_settings, SettingsDict, set_default_settings, set_dark_mode
from board import Board
from solver import check_num_is_valid, char_to_num, num_to_char, get_unique_solution, best_empty_cell
from save import save_state, load_state, SAVE_PATH

class HexDokuDisplay:
    board: "Board | None"
    cells: "list[list[tk.Entry | None]] | None"
    settings: SettingsDict
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("HexDoku")
        
        self.settings = get_settings()
        
        # Set window close protocol
        self.root.protocol("WM_DELETE_WINDOW", self._on_quit)
        
        # Create main container with border (entire window with small border)
        self.main_container = tk.Frame(self.root, bg=self.settings["border_color"])
        self.main_container.pack(fill='both', expand=True, padx=1, pady=1)
        
        # Create inner frame for content
        self.content_frame = tk.Frame(self.main_container, bg=self.settings["background_color"])
        self.content_frame.pack(fill='both', expand=True)

        self.start_frame = tk.Frame(self.content_frame, bg=self.settings["background_color"])
        self.game_frame = tk.Frame(self.content_frame, bg=self.settings["background_color"])

        self.board = None # Board object to be set later after difficulty selection
        self.fixed = None # Track fixed cells after puzzle generation
        self.cells = None # To be initialized after board is set

        self.hardcore_mode = tk.BooleanVar(value=False) # Variable for hardcore mode, which will disable hints, fills, and incorrect input indication
        
        self._build_start_screen()
        self.start_frame.pack(fill='both', expand=True)
        
        # Center window on screen after rendering
        self.root.after(100, self._center_window)
    
    def _center_window(self):
        """Center the window on the screen"""
        self.root.update_idletasks()
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        window_width = self.root.winfo_width()
        window_height = self.root.winfo_height()
        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2
        self.root.geometry(f"+{x}+{y}")
    
    def _build_start_screen(self):
        # Kill the old start frame if it exists
        if hasattr(self, 'start_frame'):
            self.start_frame.destroy()
        
        self.start_frame = tk.Frame(self.content_frame, bg=self.settings["background_color"])
        label = tk.Label(self.start_frame, text="HexDoku", font=(self.settings["font"], self.settings["title_font_size"]), bg=self.settings["background_color"], fg=self.settings["text_color_1"])
        label.pack(pady=20)

        tk.Label(self.start_frame, text=f"Select Difficulty ({self.settings['min_difficulty']}-{self.settings['max_difficulty']}):", font=(self.settings["font"], self.settings["button_font_size"]), bg=self.settings["background_color"], fg=self.settings["text_color_1"]).pack(pady=10)

        # Difficulty slider, controls percent of cells to unfill
        self.difficulty_var = tk.IntVar(value=int(self.settings["max_difficulty"] - self.settings["min_difficulty"]) // 2 + self.settings["min_difficulty"])
        slider = tk.Scale(
            self.start_frame, 
            from_=self.settings["min_difficulty"], 
            to=self.settings["max_difficulty"], 
            orient="horizontal",
            variable=self.difficulty_var,
            showvalue=True,
            length=300,
            bg=self.settings["background_color"],
            fg=self.settings["text_color_1"],
            troughcolor=self.settings["empty_cell_color"]
        )
        slider.pack(pady=10)

        # Hardcore mode checkbox
        hardcore_check = tk.Checkbutton(
            self.start_frame,
            text="Hardcore Mode (No Hints or Fills)",
            variable=self.hardcore_mode,
            bg=self.settings["background_color"],
            fg=self.settings["text_color_1"],
            activebackground=self.settings["background_color"],
            activeforeground=self.settings["text_color_1"],
            selectcolor=self.settings["background_color"]
        )
        hardcore_check.pack(pady=10)

        start_button = tk.Button(self.start_frame, text="Start Game", command=self._start_game, bg=self.settings["start_button_color"], fg=self.settings["text_color_1"])
        start_button.pack(pady=10)

        if SAVE_PATH.exists():
            continue_button = tk.Button(self.start_frame, text="Continue Saved Game", command=self._continue_game, bg=self.settings["fill_button_color"], fg=self.settings["text_color_1"])
            continue_button.pack(pady=5)

        quit_button = tk.Button(self.start_frame, text="Quit", command=self._on_quit, bg=self.settings["quit_button_color"], fg=self.settings["text_color_2"])
        quit_button.pack(pady=5)

        settings_button = tk.Button(self.start_frame, text=f"\u2699", command=self._settings_menu, bg=self.settings["background_color"], fg=self.settings["text_color_1"])
        settings_button.pack(side="right")

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
        self.game_frame = tk.Frame(self.content_frame, bg=self.settings["background_color"])
        self.game_frame.pack(fill='both', expand=True)

        # Start control frame
        self.control_frame = tk.Frame(self.game_frame, bg=self.settings["background_color"])
        self.control_frame.pack(side="top", fill="x")

        # Build control buttons
        state = "disabled" if self.hardcore else "normal"
        hint_btn = tk.Button(self.control_frame, text="Hint", command=self._show_hint, bg=self.settings["hint_button_color"], state=state)
        hint_btn.pack(side="left", padx=10)
        fill_one_btn = tk.Button(self.control_frame, text="Fill One", command=self._fill_one_space, bg=self.settings["fill_button_color"], state=state)
        fill_one_btn.pack(side="left", padx=10)
        quit_btn = tk.Button(self.control_frame, text="Quit", command=self._on_quit, bg=self.settings["quit_button_color"], fg=self.settings["text_color_2"])
        quit_btn.pack(side="right", padx=10)
        restart_btn = tk.Button(self.control_frame, text="Restart", command=self._restart_game, bg=self.settings["restart_button_color"])
        restart_btn.pack(side="right", padx=10)
        back_btn = tk.Button(self.control_frame, text="Back to Menu", command=self._back_to_start)
        back_btn.pack(side="right", padx=10)

        # Start and build grid frame
        self.grid_frame = tk.Frame(self.game_frame, bg=self.settings["background_color"])
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
                frame = tk.Frame(self.grid_frame, highlightthickness=0, bd=0, bg=self.settings["border_color"])
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

                entry = tk.Entry(inner, width=2, font=(self.settings["font"], self.settings["cell_font_size"]), 
                               justify="center", state='normal')
                entry.pack()
                
                # Store reference before binding
                self.cells[r][c] = entry

                # Bind events
                entry.bind("<FocusOut>", lambda e, row=r, col=c: self._on_cell_change(e, row, col))
                entry.bind("<Return>", lambda e, row=r, col=c: self._on_cell_change(e, row, col))

    def _render_board(self):
        if self.board is None or self.cells is None:
            raise ValueError("Board and cells must be initialized before rendering the grid.")
        
        first_empty = None
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
                    widget.config(state='readonly', readonlybackground=self.settings["fixed_cell_color"], fg=self.settings["text_color_1"], relief='sunken')
                else:
                    widget.config(state='normal', bg=self.settings["empty_cell_color"], fg=self.settings["text_color_1"], relief='sunken')
                    if first_empty is None:
                        first_empty = widget
        
        # Give focus to the first empty cell if one exists
        if first_empty:
            first_empty.focus_set()

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
        mb.showinfo("Congratulations!", "Puzzle Completed Successfully!")
        self._back_to_start()

    def _back_to_start(self):
        if self.board is not None:
            save_state(self.board, self.fixed, self.difficulty_var.get(), self.hardcore)
        if hasattr(self, 'game_frame') and self.game_frame.winfo_exists():
            self.game_frame.destroy()
        if hasattr(self, 'settings_frame') and self.settings_frame.winfo_exists():
            self.settings_frame.destroy()
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
            widget.config(bg=self.settings["fixed_cell_color"], fg=self.settings["text_color_1"], state='readonly')
            return
        
        # If cell is not fixed and text is empty, clear the cell
        if text == "":
            self.board.set_value(r, c, None)
            widget.config(state='normal', bg=self.settings["empty_cell_color"], fg=self.settings["text_color_1"])
            return
        
        # Validate that input is a single allowed character
        allowed = set(self.board.valid_chars)
        if len(text) != 1 or text not in allowed:
            widget.config(state='normal', bg=self.settings["error_color"], fg=self.settings["text_color_2"])
            return
        
        # Convert char to number
        num = char_to_num(text)
        
        if check_num_is_valid(self.board, r, c, num):
            self.board.set_value(r, c, num)
            widget.config(state='normal', bg=self.settings["empty_cell_color"], fg=self.settings["text_color_1"])

            # Check for puzzle completion
            if self.board.is_solved():
                self._show_puzzle_complete()
        else:
            # Clear the cell from the board state when validation fails
            self.board.set_value(r, c, None)
            if not self.hardcore: # Only indicate incorrect input if not in hardcore mode
                widget.config(state='normal', bg=self.settings["error_color"], fg=self.settings["text_color_2"])

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
        cell.config(bg=self.settings["highlight_color"])

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
        cell.config(bg=self.settings["fill_cell_color"], fg=self.settings["text_color_1"])

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
        
        # Set up game frames (this will create and pack the game_frame)
        self._setup_game_frames()

    def _settings_menu(self):
        # Hide start frame and build settings frame
        self.start_frame.pack_forget()
        if hasattr(self, 'settings_frame'):
            self.settings_frame.destroy() # Remove old settings frame if it exists
        self.settings_frame = tk.Frame(self.content_frame, bg=self.settings["background_color"])

        # Title
        label = tk.Label(self.settings_frame, text="HexDoku Settings", font=(self.settings["font"], self.settings["title_font_size"]), bg=self.settings["background_color"], fg=self.settings["text_color_1"])
        label.pack(pady=10)

        # Font Selection (full width)
        font_frame = tk.Frame(self.settings_frame, bg=self.settings["background_color"])
        font_frame.pack(pady=5, fill='x', padx=20)
        tk.Label(font_frame, text="Font:", bg=self.settings["background_color"], fg=self.settings["text_color_1"], width=15, anchor='e').pack(side="left", padx=5)
        font_selection = ttk.Combobox(
            font_frame,
            values=self.settings["font_options"],
            state="readonly",
            width=20
        )
        font_selection.set(self.settings["font"])
        font_selection.pack(side="left", padx=5, fill='x', expand=True)
        font_selection.bind("<<ComboboxSelected>>", lambda e: self._on_setting_change("font", font_selection.get()))

        # Two-column container
        columns_frame = tk.Frame(self.settings_frame, bg=self.settings["background_color"])
        columns_frame.pack(fill='both', expand=True, padx=10, pady=10)

        # Left Column - Colors
        left_column = tk.Frame(columns_frame, bg=self.settings["background_color"])
        left_column.pack(side='left', fill='both', expand=True, padx=5)

        tk.Label(left_column, text="Colors", font=(self.settings["font"], self.settings["button_font_size"]), bg=self.settings["background_color"], fg=self.settings["text_color_1"]).pack(pady=10)

        # Background Color
        bg_frame = tk.Frame(left_column, bg=self.settings["background_color"])
        bg_frame.pack(pady=5, fill='x')
        tk.Label(bg_frame, text="Background:", bg=self.settings["background_color"], fg=self.settings["text_color_1"], width=15, anchor='e').pack(side="left", padx=5)
        bg_color_var = tk.StringVar(value=self.settings["background_color"])
        bg_color_btn = tk.Button(bg_frame, bg=self.settings["background_color"], width=15)
        bg_color_btn.config(command=lambda: self._change_color("background", bg_color_var, bg_color_btn))
        bg_color_btn.pack(side="left", padx=5)

        # Empty Cell Color
        empty_frame = tk.Frame(left_column, bg=self.settings["background_color"])
        empty_frame.pack(pady=5, fill='x')
        tk.Label(empty_frame, text="Empty Cell:", bg=self.settings["background_color"], fg=self.settings["text_color_1"], width=15, anchor='e').pack(side="left", padx=5)
        empty_color_var = tk.StringVar(value=self.settings["empty_cell_color"])
        empty_color_btn = tk.Button(empty_frame, bg=self.settings["empty_cell_color"], width=15)
        empty_color_btn.config(command=lambda: self._change_color("empty_cell", empty_color_var, empty_color_btn))
        empty_color_btn.pack(side="left", padx=5)

        # Fixed Cell Color
        fixed_frame = tk.Frame(left_column, bg=self.settings["background_color"])
        fixed_frame.pack(pady=5, fill='x')
        tk.Label(fixed_frame, text="Fixed Cell:", bg=self.settings["background_color"], fg=self.settings["text_color_1"], width=15, anchor='e').pack(side="left", padx=5)
        fixed_color_var = tk.StringVar(value=self.settings["fixed_cell_color"])
        fixed_color_btn = tk.Button(fixed_frame, bg=self.settings["fixed_cell_color"], width=15)
        fixed_color_btn.config(command=lambda: self._change_color("fixed_cell", fixed_color_var, fixed_color_btn))
        fixed_color_btn.pack(side="left", padx=5)

        # Error Color
        error_frame = tk.Frame(left_column, bg=self.settings["background_color"])
        error_frame.pack(pady=5, fill='x')
        tk.Label(error_frame, text="Error Color:", bg=self.settings["background_color"], fg=self.settings["text_color_1"], width=15, anchor='e').pack(side="left", padx=5)
        error_color_var = tk.StringVar(value=self.settings["error_color"])
        error_color_btn = tk.Button(error_frame, bg=self.settings["error_color"], width=15)
        error_color_btn.config(command=lambda: self._change_color("error", error_color_var, error_color_btn))
        error_color_btn.pack(side="left", padx=5)

        # Highlight Color
        highlight_frame = tk.Frame(left_column, bg=self.settings["background_color"])
        highlight_frame.pack(pady=5, fill='x')
        tk.Label(highlight_frame, text="Highlight Color:", bg=self.settings["background_color"], fg=self.settings["text_color_1"], width=15, anchor='e').pack(side="left", padx=5)
        highlight_color_var = tk.StringVar(value=self.settings["highlight_color"])
        highlight_color_btn = tk.Button(highlight_frame, bg=self.settings["highlight_color"], width=15)
        highlight_color_btn.config(command=lambda: self._change_color("highlight", highlight_color_var, highlight_color_btn))
        highlight_color_btn.pack(side="left", padx=5)

        # Label Color
        label_frame = tk.Frame(left_column, bg=self.settings["background_color"])
        label_frame.pack(pady=5, fill='x')
        tk.Label(label_frame, text="Label Color:", bg=self.settings["background_color"], fg=self.settings["text_color_1"], width=15, anchor='e').pack(side="left", padx=5)
        label_color_var = tk.StringVar(value=self.settings["label_color"])
        label_color_btn = tk.Button(label_frame, bg=self.settings["label_color"], width=15)
        label_color_btn.config(command=lambda: self._change_color("label", label_color_var, label_color_btn))
        label_color_btn.pack(side="left", padx=5)

        # Border Color
        border_frame = tk.Frame(left_column, bg=self.settings["background_color"])
        border_frame.pack(pady=5, fill='x')
        tk.Label(border_frame, text="Border Color:", bg=self.settings["background_color"], fg=self.settings["text_color_1"], width=15, anchor='e').pack(side="left", padx=5)
        border_color_var = tk.StringVar(value=self.settings["border_color"])
        border_color_btn = tk.Button(border_frame, bg=self.settings["border_color"], width=15)
        border_color_btn.config(command=lambda: self._change_color("border", border_color_var, border_color_btn))
        border_color_btn.pack(side="left", padx=5)

        # Right Column - Button Colors
        right_column = tk.Frame(columns_frame, bg=self.settings["background_color"])
        right_column.pack(side='right', fill='both', expand=True, padx=5)

        tk.Label(right_column, text="Button Colors", font=(self.settings["font"], self.settings["button_font_size"]), bg=self.settings["background_color"], fg=self.settings["text_color_1"]).pack(pady=10)

        # Start Button Color
        start_btn_frame = tk.Frame(right_column, bg=self.settings["background_color"])
        start_btn_frame.pack(pady=5, fill='x')
        tk.Label(start_btn_frame, text="Start Button:", bg=self.settings["background_color"], fg=self.settings["text_color_1"], width=15, anchor='e').pack(side="left", padx=5)
        start_btn_color_var = tk.StringVar(value=self.settings["start_button_color"])
        start_btn_color_btn = tk.Button(start_btn_frame, bg=self.settings["start_button_color"], width=15)
        start_btn_color_btn.config(command=lambda: self._change_color("start_button", start_btn_color_var, start_btn_color_btn))
        start_btn_color_btn.pack(side="left", padx=5)

        # Quit Button Color
        quit_btn_frame = tk.Frame(right_column, bg=self.settings["background_color"])
        quit_btn_frame.pack(pady=5, fill='x')
        tk.Label(quit_btn_frame, text="Quit Button:", bg=self.settings["background_color"], fg=self.settings["text_color_1"], width=15, anchor='e').pack(side="left", padx=5)
        quit_btn_color_var = tk.StringVar(value=self.settings["quit_button_color"])
        quit_btn_color_btn = tk.Button(quit_btn_frame, bg=self.settings["quit_button_color"], width=15)
        quit_btn_color_btn.config(command=lambda: self._change_color("quit_button", quit_btn_color_var, quit_btn_color_btn))
        quit_btn_color_btn.pack(side="left", padx=5)

        # Hint Button Color
        hint_btn_frame = tk.Frame(right_column, bg=self.settings["background_color"])
        hint_btn_frame.pack(pady=5, fill='x')
        tk.Label(hint_btn_frame, text="Hint Button:", bg=self.settings["background_color"], fg=self.settings["text_color_1"], width=15, anchor='e').pack(side="left", padx=5)
        hint_btn_color_var = tk.StringVar(value=self.settings["hint_button_color"])
        hint_btn_color_btn = tk.Button(hint_btn_frame, bg=self.settings["hint_button_color"], width=15)
        hint_btn_color_btn.config(command=lambda: self._change_color("hint_button", hint_btn_color_var, hint_btn_color_btn))
        hint_btn_color_btn.pack(side="left", padx=5)

        # Fill Button Color
        fill_btn_frame = tk.Frame(right_column, bg=self.settings["background_color"])
        fill_btn_frame.pack(pady=5, fill='x')
        tk.Label(fill_btn_frame, text="Fill Button:", bg=self.settings["background_color"], fg=self.settings["text_color_1"], width=15, anchor='e').pack(side="left", padx=5)
        fill_btn_color_var = tk.StringVar(value=self.settings["fill_button_color"])
        fill_btn_color_btn = tk.Button(fill_btn_frame, bg=self.settings["fill_button_color"], width=15)
        fill_btn_color_btn.config(command=lambda: self._change_color("fill_button", fill_btn_color_var, fill_btn_color_btn))
        fill_btn_color_btn.pack(side="left", padx=5)

        # Restart Button Color
        restart_btn_frame = tk.Frame(right_column, bg=self.settings["background_color"])
        restart_btn_frame.pack(pady=5, fill='x')
        tk.Label(restart_btn_frame, text="Restart Button:", bg=self.settings["background_color"], fg=self.settings["text_color_1"], width=15, anchor='e').pack(side="left", padx=5)
        restart_btn_color_var = tk.StringVar(value=self.settings["restart_button_color"])
        restart_btn_color_btn = tk.Button(restart_btn_frame, bg=self.settings["restart_button_color"], width=15)
        restart_btn_color_btn.config(command=lambda: self._change_color("restart_button", restart_btn_color_var, restart_btn_color_btn))
        restart_btn_color_btn.pack(side="left", padx=5)

        # Theme and Reset Section
        theme_frame = tk.Frame(self.settings_frame, bg=self.settings["background_color"])
        theme_frame.pack(pady=20)
        
        dark_mode_btn = tk.Button(theme_frame, text="Dark Mode", command=self._apply_dark_mode)
        dark_mode_btn.pack(side="left", padx=5)
        
        restore_btn = tk.Button(theme_frame, text="Restore Defaults", command=self._restore_defaults)
        restore_btn.pack(side="left", padx=5)

        # Back Button
        back_button = tk.Button(self.settings_frame, text="Back to Start", command=self._back_to_start)
        back_button.pack(pady=20)

        self.settings_frame.pack(fill='both', expand=True)

    def _change_color(self, color_type, color_var, button=None):
        """Change a color setting via color picker"""
        from tkinter.colorchooser import askcolor
        color = askcolor(title=f"Choose {color_type} color")
        if color[1]:  # If a color was selected
            color_var.set(color[1])
            self._on_setting_change(color_type, color[1], button)

    def _on_setting_change(self, setting_key: str, value, widget=None):
        #Handle a setting change - update settings dict, save to file, and refresh UI
        from save import save_settings
        
        # Map setting key to settings dict key
        setting_map = {
            "background": "background_color",
            "empty_cell": "empty_cell_color",
            "fixed_cell": "fixed_cell_color",
            "error": "error_color",
            "highlight": "highlight_color",
            "label": "label_color",
            "border": "border_color",
            "start_button": "start_button_color",
            "quit_button": "quit_button_color",
            "hint_button": "hint_button_color",
            "fill_button": "fill_button_color",
            "restart_button": "restart_button_color",
            "font": "font"
        }
        
        dict_key = setting_map.get(setting_key, setting_key)
        self.settings[dict_key] = value  # type: ignore
        
        # Save to file
        save_settings(self.settings)
        
        # Update the button/widget visual if provided
        if widget and isinstance(widget, tk.Button):
            widget.config(bg=value)
        
        # Refresh affected UI elements
        self._refresh_ui_for_setting(dict_key)
    
    def _refresh_ui_for_setting(self, setting_key: str):
        #Refresh UI elements affected by a setting change
        if setting_key == "background_color":
            # Update root window background
            self.root.config(bg=self.settings["background_color"])
            if hasattr(self, 'settings_frame'):
                self.settings_frame.config(bg=self.settings["background_color"])
            # Update all child widgets with new background
            self._update_widget_colors(self.settings_frame if hasattr(self, 'settings_frame') else self.root)
        elif setting_key == "font":
            # Font changes would require rebuilding the settings frame
            if hasattr(self, 'settings_frame'):
                self._settings_menu()
    
    def _update_widget_colors(self, parent):
        #Recursively update background colors and styles for all widgets
        try:
            parent.config(bg=self.settings["background_color"])
        except tk.TclError:
            pass
        for child in parent.winfo_children():
            try:
                if isinstance(child, tk.Frame):
                    child.config(bg=self.settings["background_color"])
                elif isinstance(child, tk.Label):
                    child.config(bg=self.settings["background_color"], fg=self.settings["text_color_1"])
                elif isinstance(child, tk.Button):
                    # Try to determine button type and apply appropriate color
                    child.config(bg=self.settings["background_color"], fg=self.settings["text_color_1"])
                elif isinstance(child, tk.Checkbutton):
                    child.config(bg=self.settings["background_color"], fg=self.settings["text_color_1"], activebackground=self.settings["background_color"], selectcolor=self.settings["background_color"])
                elif isinstance(child, tk.Scale):
                    child.config(bg=self.settings["background_color"], fg=self.settings["text_color_1"], troughcolor=self.settings["empty_cell_color"])
            except tk.TclError:
                pass
            self._update_widget_colors(child)
    
    def _apply_dark_mode(self):
        #Apply dark mode theme to all settings
        from save import save_settings
        
        # Apply dark mode to settings
        dark_settings = set_dark_mode(self.settings)
        
        # Update each setting individually to trigger UI refresh
        for key, value in dark_settings.items():
            if key != self.settings.get(key):
                self.settings[key] = value  # type: ignore
        
        # Save all settings
        save_settings(self.settings)
        
        # Rebuild visible screens
        if self.start_frame.winfo_exists() and self.start_frame.winfo_viewable():
            self._build_start_screen()
        elif self.game_frame.winfo_exists() and self.game_frame.winfo_viewable():
            self._refresh_ui_for_setting("background_color")
        
        # Refresh the entire settings menu
        self._settings_menu()
    
    def _restore_defaults(self):
        """Restore all settings to default values"""
        from save import save_settings
        
        # Confirm action
        result = mb.askyesno("Confirm", "Restore all settings to defaults?")
        if not result:
            return
        
        # Get default settings
        default_settings = set_default_settings()
        
        # Update settings
        for key, value in default_settings.items():
            self.settings[key] = value  # type: ignore
        
        # Save settings
        save_settings(self.settings)
        
        # Rebuild visible screens
        if self.start_frame.winfo_exists() and self.start_frame.winfo_viewable():
            self._build_start_screen()
        elif self.game_frame.winfo_exists() and self.game_frame.winfo_viewable():
            self._refresh_ui_for_setting("background_color")
        
        # Refresh the entire settings menu
        self._settings_menu()

    def run(self):
        self.root.mainloop()
