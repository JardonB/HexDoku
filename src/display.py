import tkinter as tk
from solver import check_num_is_valid, char_to_num, num_to_char

class HexDokuDisplay:
    def __init__(self, board):
        self.board = board
        self.root = tk.Tk()
        self.root.title("HexDoku")

        self.cells = [[None for _ in range(board.size)] for _ in range(board.size)]
        self._build_grid()
        self._render_board()

    def _build_grid(self):
        for r in range(self.board.size):
            for c in range(self.board.size):
                # Decide if this cell is on a 4x4 box boundary
                top_border    = (r % self.board.box_width == 0)
                left_border   = (c % self.board.box_width == 0)
                bottom_border = (r == self.board.size - 1)
                right_border  = (c == self.board.size - 1)

                # Create a frame to hold the entry and draw borders with it
                frame = tk.Frame(self.root, highlightthickness=0, bd=0, bg="black")
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

                # Bind with row/col via lambda
                entry.bind("<FocusOut>", lambda e, row=r, col=c: self._on_cell_change(e, row, col))
                self.cells[r][c] = entry

    def _render_board(self):
        for r in range(self.board.size):
            for c in range(self.board.size):
                val = self.board.grid[r][c]
                widget = self.cells[r][c]
                widget.delete(0, tk.END)
                if val is not None:
                    widget.insert(0, num_to_char(val))
                
                if self._is_fixed_cell(r, c):
                    widget.config(state='readonly', readonlybackground='black', fg='white')
                else:
                    widget.config(state='normal')

    def _is_fixed_cell(self, row, col):
        # Fixed cells are those that are not None in the original puzzle board
        return self.board.grid[row][col] is not None
    
    def _on_cell_change(self, event):
        widget = event.widget
        r, c = widget.row, widget.col
        text = widget.get().strip().upper()

        # Handle empty input
        if text == "":
            self.board.grid[r][c] = None
            widget.config(bg="white")
            return
        
        # Validate input
        allowed = set(self.board.valid_chars)
        if len(text) != 1 or text not in allowed:
            widget.delete(0, tk.END)
            widget.config(bg="red")
            return
        
        value = char_to_num(text) # Convert character to number

        if not self._is_fixed_cell(r, c):
            if check_num_is_valid(self.board, r, c, value):
                self.board.set_value(r, c, value)
                widget.config(bg="white", fg="black")
            else:
                widget.config(bg="red", fg="white")

    def run(self):
        self.root.mainloop()
