from settings import *
from display import HexDokuDisplay

HexDokuVersion = "1.1a"

def main():
    print(f"HexDoku Version: {HexDokuVersion}")
    gui = HexDokuDisplay()
    gui.run()

if __name__ == "__main__":
    main()