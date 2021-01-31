import numpy as np

from typing import List


class SudokuSolver:

    def __init__(self, array: List[List[int]]):
        self.sudoku = np.array(array)
        self.zero_positions = list(zip(np.where(self.sudoku == 0)[0], np.where(self.sudoku == 0)[1]))
        self.digits = {coord: 1 for coord in self.zero_positions}

    def solve(self) -> None:
        '''
        Backtracking method of solving sudoku.
        For consecutive empty cells method checks subsequent digits (from 1 to 9).
        If digit is permissible, program inserts digit and moves to next empty cell.
        If digit in impermissible, program checks next digit.
        If all 9 digits were already checked and none of them was permissible,
        program returns to the previous empty cell and tries next digit.
        :return: None
        '''
        i = 0
        while i < len(self.zero_positions):
            coords = self.zero_positions[i]
            row, column = coords
            digit = self.digits[coords]

            if digit == 10:
                self.insert_digit(row, column)
                self.digits[coords] = 1
                i -= 1
                continue

            if self.validate_digit(row, column, digit):
                self.insert_digit(row, column, digit)
                i += 1
            self.digits[coords] += 1
        return None

    def validate_digit(self, row: int, column: int, digit: int) -> bool:
        '''
        Checks if digit is available in place indicated by coordinates.
        If such number is already present in row, column or square, method returns False.
        :param row: row coordinate of cell
        :param column: column coordinate of cell
        :param digit: digit for checking
        :return: True if digit is valid in this place, False otherwise
        '''
        if digit in self.sudoku[row, :]:
            return False
        if digit in self.sudoku[:, column]:
            return False
        row_square, column_square = row // 3 * 3, column // 3 * 3
        if digit in self.sudoku[row_square:row_square + 3, column_square:column_square + 3]:
            return False
        return True

    def insert_digit(self, row: int, column: int, digit: int = 0) -> None:
        '''
        Insert digit into cell of provided coordinates.
        :param row: row coordinate of cell to fill
        :param column: column coordinate of cell to fill
        :param digit: digit to insert
        :return: None
        '''
        self.sudoku[row, column] = digit
        return None

    def validate_sudoku(self) -> int:
        """
        Checks if sudoku array is valid, i.e. if rows, columns or squares don't contain duplicated digits.
        :return: 0 if array is empty, 1 if is valid, -1 if invalid
        """
        if np.count_nonzero(self.sudoku) == 0:
            return 0
        if not self.check_occurences():
            return -1
        return 1

    def check_occurences(self) -> bool:
        '''
        Checks if every row, column and square contains only one occurrence of digit.
        :return: True if sudoku is valid, otherwise False
        '''
        for i in range(0, 9):
            for digit in range(1, 10):
                if np.count_nonzero(self.sudoku[i, :] == digit) > 1:
                    return False
                if np.count_nonzero(self.sudoku[:, i] == digit) > 1:
                    return False
                row_square = i // 3 * 3
                column_square = i * 3 - 3 * row_square
                if np.count_nonzero(
                        self.sudoku[row_square:row_square + 3, column_square:column_square + 3] == digit) > 1:
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
