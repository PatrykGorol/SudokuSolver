import tkinter as tk


class Window:

    def __init__(self, master: tk.Tk) -> None:
        master.title('SudokuSolver')
        master.iconbitmap(r'sudoku.ico')
        self.instruction = tk.Label(master, text='Insert sudoku below.')
        self.instruction.grid(columnspan=9)
        pass


if __name__ == '__main__':
    root = tk.Tk()
    Window(root)
    root.mainloop()
