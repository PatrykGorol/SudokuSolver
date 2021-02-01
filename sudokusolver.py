import numpy as np

from typing import List


class SudokuSolver:

    def __init__(self, array: List[List[int]]):
        self.sudoku = np.array(array)
        self.empty_cells = list(zip(np.where(self.sudoku == 0)[0], np.where(self.sudoku == 0)[1]))
        self.test_numbers = {coord: 1 for coord in self.empty_cells}

    def solve(self) -> None:
        '''
        Backtracking method of solving sudoku.
        For consecutive empty cells method checks subsequent numbers (from 1 to 9).
        If number is permissible, program inserts number and moves to next empty cell.
        If number in impermissible, program checks next number.
        If all 9 numbers were already checked and none of them was permissible,
        program returns to the previous empty cell and tries next number.
        :return: None
        '''
        cell_index = 0
        while cell_index < len(self.empty_cells):
            coordinates = self.empty_cells[cell_index]
            row, column = coordinates
            number = self.test_numbers[coordinates]

            if number == 10:
                self.insert_number(row, column)
                self.test_numbers[coordinates] = 1
                cell_index -= 1
                continue

            if self.validate_number(row, column, number):
                self.insert_number(row, column, number)
                cell_index += 1
            self.test_numbers[coordinates] += 1

        return None

    def validate_number(self, row: int, column: int, number: int) -> bool:
        '''
        Checks if number is available in place indicated by coordinates.
        If such number is already present in row, column or box, method returns False.
        :param row: row coordinate of cell
        :param column: column coordinate of cell
        :param number: number for checking
        :return: True if number is valid in this place, False otherwise
        '''
        if number in self.sudoku[row, :]:
            return False
        if number in self.sudoku[:, column]:
            return False
        box_row, box_column = row // 3 * 3, column // 3 * 3
        if number in self.sudoku[box_row:box_row + 3, box_column:box_column + 3]:
            return False
        return True

    def insert_number(self, row: int, column: int, number: int = 0) -> None:
        '''
        Insert number into cell of provided coordinates.
        :param row: row coordinate of cell to fill
        :param column: column coordinate of cell to fill
        :param number: number to insert
        :return: None
        '''
        self.sudoku[row, column] = number
        return None

    def validate_sudoku(self) -> int:
        """
        Checks if sudoku array is valid, i.e. if rows, columns or boxes don't contain duplicated numbers.
        :return: 0 if array is empty, 1 if is valid, -1 if invalid
        """
        if np.count_nonzero(self.sudoku) == 0:
            return 0
        if not self.check_occurences():
            return -1
        return 1

    def check_occurences(self) -> bool:
        '''
        Checks if every row, column and box contains only one occurrence of number.
        :return: True if sudoku is valid, otherwise False
        '''
        for e in range(0, 9):
            for number in range(1, 10):
                if np.count_nonzero(self.sudoku[e, :] == number) > 1:
                    return False
                if np.count_nonzero(self.sudoku[:, e] == number) > 1:
                    return False
                box_row = e // 3 * 3
                box_column = 3 * (e - box_row)
                if np.count_nonzero(self.sudoku[box_row:box_row + 3, box_column:box_column + 3] == number) > 1:
                    return False
        return True

    def is_sudoku_completed(self) -> bool:
        """
        Checks if there are no blank cells and all elements are correctly filled.
        :return: bool
        """
        if np.count_nonzero(self.sudoku) == 81:
            if self.check_occurences():
                return True
        return False
