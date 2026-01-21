from typing import TypedDict
from save import load_settings

# Game Settings
GRID_SIZE = 16
MAX_DIFFICULTY = 60 # Percentage of empty cells. Practical limit is around 55-60, higher difficulty will result in excessive generation times.
MIN_DIFFICULTY = 1

# Colors
BACKGROUND_COLOR = "lightgray"
LABEL_COLOR = "darkgray"
EMPTY_CELL_COLOR = "white"
FIXED_CELL_COLOR = "lightgray"
HIGHLIGHT_COLOR = "yellow"
FILL_CELL_COLOR = "lightblue"
ERROR_COLOR = "red"
BORDER_COLOR = "black"
START_BUTTON_COLOR = "green"
QUIT_BUTTON_COLOR = "red"
FILL_BUTTON_COLOR = "lightblue"
HINT_BUTTON_COLOR = "yellow"
RESTART_BUTTON_COLOR = "orange"
TEXT_COLOR_1 = "black"
TEXT_COLOR_2 = "white"

# Fonts
FONT = "Arial"
CELL_FONT_SIZE = 16   # Not implemented yet
BUTTON_FONT_SIZE = 14 # Not implemented yet
TITLE_FONT_SIZE = 24  # Not implemented yet

FONT_OPTIONS = ["Arial", "Courier", "Helvetica", "Times New Roman", "Verdana"]

class SettingsDict(TypedDict):
    grid_size: int
    max_difficulty: int
    min_difficulty: int
    background_color: str
    label_color: str
    empty_cell_color: str
    fixed_cell_color: str
    highlight_color: str
    fill_cell_color: str
    error_color: str
    border_color: str
    start_button_color: str
    quit_button_color: str
    fill_button_color: str
    hint_button_color: str
    restart_button_color: str
    text_color_1: str
    text_color_2: str
    font: str
    cell_font_size: int
    button_font_size: int
    title_font_size: int
    font_options: list[str]

def get_settings() -> SettingsDict:
    loaded = load_settings()
    if loaded is not None:
        return loaded  # type: ignore
    else:
        settings: SettingsDict = {
            "grid_size": GRID_SIZE,
            "max_difficulty": MAX_DIFFICULTY,
            "min_difficulty": MIN_DIFFICULTY,
            "background_color": BACKGROUND_COLOR,
            "label_color": LABEL_COLOR,
            "empty_cell_color": EMPTY_CELL_COLOR,
            "fixed_cell_color": FIXED_CELL_COLOR,
            "highlight_color": HIGHLIGHT_COLOR,
            "fill_cell_color": FILL_CELL_COLOR,
            "error_color": ERROR_COLOR,
            "border_color": BORDER_COLOR,
            "start_button_color": START_BUTTON_COLOR,
            "quit_button_color": QUIT_BUTTON_COLOR,
            "fill_button_color": FILL_BUTTON_COLOR,
            "hint_button_color": HINT_BUTTON_COLOR,
            "restart_button_color": RESTART_BUTTON_COLOR,
            "text_color_1": TEXT_COLOR_1,
            "text_color_2": TEXT_COLOR_2,
            "font": FONT,
            "cell_font_size": CELL_FONT_SIZE,
            "button_font_size": BUTTON_FONT_SIZE,
            "title_font_size": TITLE_FONT_SIZE,
            "font_options": FONT_OPTIONS
        }
        return settings
    
def set_default_settings() -> SettingsDict:
    settings: SettingsDict = {
        "grid_size": GRID_SIZE,
        "max_difficulty": MAX_DIFFICULTY,
        "min_difficulty": MIN_DIFFICULTY,
        "background_color": BACKGROUND_COLOR,
        "label_color": LABEL_COLOR,
        "empty_cell_color": EMPTY_CELL_COLOR,
        "fixed_cell_color": FIXED_CELL_COLOR,
        "highlight_color": HIGHLIGHT_COLOR,
        "fill_cell_color": FILL_CELL_COLOR,
        "error_color": ERROR_COLOR,
        "border_color": BORDER_COLOR,
        "start_button_color": START_BUTTON_COLOR,
        "quit_button_color": QUIT_BUTTON_COLOR,
        "fill_button_color": FILL_BUTTON_COLOR,
        "hint_button_color": HINT_BUTTON_COLOR,
        "restart_button_color": RESTART_BUTTON_COLOR,
        "text_color_1": TEXT_COLOR_1,
        "text_color_2": TEXT_COLOR_2,
        "font": FONT,
        "cell_font_size": CELL_FONT_SIZE,
        "button_font_size": BUTTON_FONT_SIZE,
        "title_font_size": TITLE_FONT_SIZE,
        "font_options": FONT_OPTIONS
    }
    return settings

def set_dark_mode(settings: SettingsDict) -> SettingsDict:
    settings["background_color"] = "black"
    settings["label_color"] = "dimgray"
    settings["empty_cell_color"] = "dimgray"
    settings["fixed_cell_color"] = "gray"
    settings["text_color_1"] = "white"
    settings["text_color_2"] = "lightgray"
    return settings