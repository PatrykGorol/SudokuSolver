import numpy as np
import tkinter as tk

from re import fullmatch
from typing import List
from random import choice
from platform import system

from sudokusolver import SudokuSolver
from examples import sudoku_examples


class EntryCell:

    def __init__(self, cell: tk.Frame):
        self._text = tk.StringVar()
        self.entry = tk.Entry(cell, borderwidth=0, justify='center', font='Helvetica 16 bold', textvariable=self._text)
        self.entry.place(relwidth=1.0, relheigh=1.0)
        self._text.trace("w", lambda *args: self.character_limit())

    @property
    def text(self) -> str:
        return self._text.get()

    @text.setter
    def text(self, value: str):
        self._text.set(value)

    def character_limit(self) -> None:
        """
        Checks if user's input is valid and changes invalid characters for blank string or previous valid character.
        :return: None
        """
        if len(self.text) > 0:
            if len(self.text) == 1 and not self.input_validation(self.text[0]):
                self.text = ''
            else:
                if self.input_validation(self.text[-1]):
                    self.text = self.text[-1]
                else:
                    self.text = self.text[-2]
        return None

    @staticmethod
    def input_validation(input_: str) -> bool:
        """
        Checks if user input is valid, i.e. if it's digit in range <1;9>
        :param input_: user input
        :return: bool
        """
        return fullmatch('[1-9]', input_) is not None


class Window:

    def __init__(self, master: tk.Tk):
        self.set_general_properties(master)
        frame = tk.LabelFrame(master, padx=10, pady=10)
        frame.grid(row=1, column=0, columnspan=9)
        self.entries: List[List[EntryCell]] = [[], [], [], [], [], [], [], [], []]
        self.create_grid(frame)
        self.create_buttons(frame)
        self.status_bar = tk.Label(master, text='Ready', anchor='e')
        self.status_bar.grid(row=2, column=0, columnspan=9, sticky='we')

    def set_general_properties(self, master) -> None:
        """
        Sets properties of tkinter window: title, icon and upper grid with label.
        :param master: thinter object
        :return: None
        """
        master.title('SudokuSolver')
        if system() == 'Windows':
            master.iconbitmap(r'sudoku.ico')    # doesn't work on linux
        instruction = tk.Label(master, text='Insert Sudoku below.', font=20)
        instruction.grid(row=0, column=0, columnspan=9, pady=10)
        return None

    def create_buttons(self, frame: tk.LabelFrame) -> None:
        """
        Creates 3 buttons on the bottom af window.
        :param frame: tkinter master element (window's grid)
        :return: None
        """
        solve_button = tk.Button(frame, text='Solve Sudoku', font=10, command=self.solve)
        solve_button.grid(row=9, column=0, pady=(10, 0))
        examples_button = tk.Button(frame, text='Get Example', font=1, command=self.example)
        examples_button.grid(row=9, column=1, pady=(10, 0))
        clear_button = tk.Button(frame, text='Clear Sudoku', font=10, command=self.clear)
        clear_button.grid(row=9, column=2, pady=(10, 0))
        return None

    def create_grid(self, main_frame: tk.LabelFrame) -> None:
        """
        Creates grid of sudoku boxes.
        :param main_frame: tkinter master element for a boxes' grid
        :return: None
        """
        for box_row in range(3):
            for box_column in range(3):
                box = tk.Frame(main_frame, highlightbackground='black', highlightcolor='red', highlightthickness=1,
                               width=150, heigh=150, padx=0)
                box.grid(row=box_row, column=box_column)
                self.create_cells_and_entries(box, box_row)
        return None

    def create_cells_and_entries(self, frame: tk.Frame, box_row: int) -> None:
        """
        Creates  9 cells inside a box.
        :param frame: tkinter maser element (box) for a cell
        :param box_row: number of box's index
        :return: None
        """
        for row in range(3):
            for column in range(3):
                cell = tk.Frame(frame, bg='white', highlightbackground='black', highlightcolor='black',
                                highlightthickness=0.5, width=50, heigh=50)
                cell.grid(row=row, column=column)
                row_index = box_row * 3 + row
                entry_cell = EntryCell(cell)
                self.entries[row_index].append(entry_cell)
        return None

    def solve(self) -> None:
        """
        Checks if sudoku array is valid and runs solving procedures.
        :return: None
        """
        solver = SudokuSolver(self.get_data())
        validation = solver.validate_sudoku()
        if validation == 1:
            solver.solve()
            self.get_result(solver)
        elif validation == -1:
            self.status_bar.config(text='This sudoku array contains invalid digits.', fg='red')
        return None

    def get_data(self) -> List[List[int]]:
        """
        Maps entered sudoku data as nested array of digits.
        :return: sudoku array
        """
        sudoku_array = []
        for row in self.entries:
            sudoku_array.append([0 if entry.text == '' else int(entry.text) for entry in row])
        return sudoku_array

    def get_result(self, solver: SudokuSolver) -> None:
        """
        If sudoku has been solved, function prints result into grid in window.
        Otherwise changes status bar and communicates that sudoku is unsolvable.
        :param solver: solver object containing processed sudoku array
        :return: None
        """
        if solver.is_sudoku_completed():
            self.insert_digits(solver)
        else:
            self.status_bar.config(text='This sudoku is unsolvable.', fg='red')
        return None

    def insert_digits(self, solver) -> None:
        """
        Inserts solving results into sudoku grid in window.
        :param solver: solver object containing completed array
        :return: None
        """
        for row in range(9):
            for column in range(9):
                if self.entries[row][column].text == '':
                    self.entries[row][column].text = solver.sudoku[row, column]
                    self.entries[row][column].entry.config(fg='blue')
        return None

    def clear(self) -> None:
        """
        Clears grid in window.
        :return: None
        """
        for row in self.entries:
            for entry in row:
                entry.text = ''
                entry.entry.config(fg='black')
        self.status_bar.config(text='Ready', fg='black')
        return None

    def example(self) -> None:
        """
        Randomly chooses sudoku from saved examples and prints it into grid.
        :return: None
        """
        random_sudoku = np.array(choice(sudoku_examples))
        for row in range(9):
            for column in range(9):
                self.entries[row][column].text = str(random_sudoku[row, column])
                self.entries[row][column].entry.config(fg='black')
        self.status_bar.config(text='Ready', fg='black')
        return None


if __name__ == '__main__':
    root = tk.Tk()
    Window(root)
    root.mainloop()
