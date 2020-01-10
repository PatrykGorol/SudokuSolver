import tkinter as tk


class Window:

    def __init__(self, master: tk.Tk) -> None:
        master.title('SudokuSolver')
        master.iconbitmap(r'sudoku.ico')
        self.instruction = tk.Label(master, text='Insert Sudoku below.', font=20)
        self.instruction.grid(row=0, column=0, columnspan=9, pady=10)
        self.frame = tk.LabelFrame(master, padx=10, pady=10)
        self.frame.grid(row=1, column=0, columnspan=9)
        self.cells = {}
        self.create_grid(self.frame)
        self.button = tk.Button(self.frame, text='Solve Sudoku', font=10)
        self.button.grid(row=9, column=0, columnspan=9, pady=(10, 0))

    def create_grid(self, frame: tk.LabelFrame):
        for row in range(9):
            for column in range(9):
                cell = tk.Frame(frame, bg='white', highlightbackground='black',
                                highlightcolor='black', highlightthickness=0.5,
                                width=40, heigh=40, padx=3, pady=3)
                cell.grid(row=row, column=column)
                self.cells[(row, column)] = cell


if __name__ == '__main__':
    root = tk.Tk()
    Window(root)
    root.mainloop()
