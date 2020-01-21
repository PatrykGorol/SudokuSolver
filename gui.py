from random import choice

from solver import SudokuSolver
from examples import *

import tkinter as tk
from re import fullmatch
from typing import List


class EntryCell:

    def __init__(self, cell: tk.Frame):
        self._text = tk.StringVar()
        self.entry = tk.Entry(cell, borderwidth=0, justify='center', font=1, textvariable=self._text)
        self.entry.place(width=33, heigh=33)
        self._text.trace("w", lambda *args: self.character_limit())

    @property
    def text(self) -> str:
        return self._text.get()

    @text.setter
    def text(self, value: str) -> None:
        self._text.set(value)

    def character_limit(self) -> None:
        if len(self.text) > 0:
            if len(self.text) == 1 and not self.input_validation(self.text[0]):
                self.text = ''
            else:
                if self.input_validation(self.text[-1]):
                    self.text = self.text[-1]
                else:
                    self.text = self.text[-2]

    @staticmethod
    def input_validation(input_: str) -> bool:
        return fullmatch('[1-9]', input_) is not None


class Window:

    def __init__(self, master: tk.Tk) -> None:
        master.title('SudokuSolver')
        master.iconbitmap(r'sudoku.ico')
        self.instruction = tk.Label(master, text='Insert Sudoku below.', font=20)
        self.instruction.grid(row=0, column=0, columnspan=9, pady=10)
        self.frame = tk.LabelFrame(master, padx=10, pady=10)
        self.frame.grid(row=1, column=0, columnspan=9)
        # self.squares = {}
        # self.cells = {}
        self.entries: List[List[EntryCell]] = [[], [], [], [], [], [], [], [], []]
        self.create_grid(self.frame)
        self.solve_button = tk.Button(self.frame, text='Solve Sudoku', font=10, command=self.solve)
        self.solve_button.grid(row=9, column=0, pady=(10, 0))
        self.examples_button = tk.Button(self.frame, text='Get example', font=1, command=self.example)
        self.examples_button.grid(row=9, column=1, pady=(10, 0))
        self.clear_button = tk.Button(self.frame, text='Clear Sudoku', font=10, command=self.clear)
        self.clear_button.grid(row=9, column=2, pady=(10, 0))
        self.status_bar = tk.Label(master, text='Ready', anchor='e')
        self.status_bar.grid(row=2, column=0, columnspan=9, sticky='we')

    def create_grid(self, main_frame: tk.LabelFrame) -> None:
        for square_row in range(3):
            for square_column in range(3):
                frame = tk.Frame(main_frame, highlightbackground='black', highlightcolor='red',
                                 highlightthickness=1, width=120, heigh=120, padx=0)
                frame.grid(row=square_row, column=square_column)
                self.create_cells_and_entries(frame, square_column, square_row)
                # self.squares[(square_row, square_column)] = frame

    def create_cells_and_entries(self, frame: tk.Frame, square_column: int, square_row: int) -> None:
        for row in range(3):
            for column in range(3):
                cell = tk.Frame(frame, bg='white', highlightbackground='black',
                                highlightcolor='black', highlightthickness=0.5,
                                width=40, heigh=40, padx=3, pady=3)
                cell.grid(row=row, column=column)
                row_index = square_row * 3 + row
                # column_index = square_column * 3 + column
                entry_cell = EntryCell(cell)
                # self.cells[(row_index, column_index)] = cell
                self.entries[row_index].append(entry_cell)

    def get_data(self):
        sudoku_array = []
        for row in self.entries:
            sudoku_array.append([0 if entry.text == '' else int(entry.text) for entry in row])
        return sudoku_array

    def solve(self) -> None:
        sudoku = Sudoku(self.get_data())
        solver = SudokuSolver(sudoku)
        solver.main_sequence()

    def clear(self):
        for row in self.entries:
            for entry in row:
                entry.text = ''

    def example(self):
        random_sudoku = choice(sudoku_examples)
        for row in range(9):
            for column in range(9):
                self.entries[row][column].text = str(random_sudoku.array[row, column])


if __name__ == '__main__':
    root = tk.Tk()
    Window(root)
    root.mainloop()
