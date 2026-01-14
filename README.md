# HexDoku
A sudoku puzzle using hexadecimal 0-F instead of 1-9

## How to play
This plays just like sudoku, but with a larger board.
Set your difficulty, click "Start Game", and fill in the grid!
Progress is saved when the game board is left via the menu options, allowing you to work on the puzzle across multiple sessions

### Rules
Each row must contain 0-F
Each column must contain 0-F
Each 4x4 box must contain 0-F
Numbers may not be repeated within a row, column, or box

### Tools
The "Hint" button will highlight the best empty box (the box with the minimum remaining values)
The "Fill One" button fills in the best empty box

### Difficulty
Difficulty is set by the percentage of cells that are empty. This is limited to 60% due to the time required to find a unique solution scaling exponentially as cells are removed.
Hardcore mode removes all hints, including indication of an incorrect entry.

### Requirements
The graphical interface for this program utilizes tkinter, so please ensure that it is installed prior to running this program.