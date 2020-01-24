from typing import List, Dict, Tuple, Optional
from itertools import product, chain
from collections import Counter
from random import choice
from copy import deepcopy

import numpy as np

from sudoku import Sudoku, SudokuElement


class SudokuSolver:
    def __init__(self, sudoku: Sudoku):
        self.s: Sudoku = sudoku
        self.counter: int = 0

    def main_sequence(self) -> None:
        if not self.is_already_completed():
            self.pre_solving_check()
            self.solve()
            self.try_random_insert()

    def validate_sudoku(self) -> int:
        if self.s.elements_count[0] == 81:
            return 0
        if not self.check_occurences():
            return -1
        return 1

    def check_occurences(self) -> bool:
        if self.check_if_one_occurence_of_digit(self.s.rows):
            if self.check_if_one_occurence_of_digit(self.s.columns):
                if self.check_if_one_occurence_of_digit(self.s.squares):
                    return True
        return False

    def check_if_one_occurence_of_digit(self, elements_list: List[SudokuElement]) -> bool:
        for element in elements_list:
            array = self.s.array[element.row_start:element.row_stop, element.column_start:element.column_stop]
            digits = [i for i in np.unique(array) if i > 0]
            for digit in digits:
                if np.count_nonzero(array == digit) > 1:
                    return False
        return True

    def is_already_completed(self) -> bool:
        if self.is_sudoku_completed():
            # print('This sudoku is already completed.')
            return True
        return False

    def pre_solving_check(self) -> None:
        self.check_elements(self.s.rows)
        self.check_elements(self.s.columns)
        self.check_elements(self.s.squares)

    def check_elements(self, elements_list: List[SudokuElement]) -> None:
        for element in elements_list:
            self.fill_element(element)
        self.check_stock()

    def fill_element(self, element: SudokuElement) -> None:
        if element.completed:
            return None
        if element.digits == 8:
            array = self.s.array[element.row_start:element.row_stop, element.column_start:element.column_stop]
            row_index, column_index = self.get_zero_coordinate(array, element.row_start, element.column_start)
            digit = self.find_last_digit(array)
            self.insert_digit(digit, row_index, column_index)

    @staticmethod
    def get_zero_coordinate(square_array: np.ndarray, row_start: int, column_start: int) -> Tuple[int, int]:
        coord = np.where(square_array == 0)
        return coord[0][0] + row_start, coord[1][0] + column_start

    def find_last_digit(self, array: np.ndarray) -> int:
        for digit in self.s.available_digits:
            if digit not in array:
                return digit

    def insert_digit(self, digit, row_index, column_index) -> None:
        if digit is None:
            return None
        self.s.array[row_index, column_index] = digit
        self.s.zero_positions.remove((row_index, column_index))
        self.update_available_elements(digit)
        self.update_elements_statistics(row_index, column_index)

    def update_available_elements(self, digit: int) -> None:
        self.s.elements_count[digit] += 1
        if self.s.elements_count[digit] == 9:
            self.s.available_digits.remove(digit)
            # sort available digits???

    def update_elements_statistics(self, row_index: int, column_index: int) -> None:
        self.increment_digit_and_add_to_stock(self.s.rows, row_index)
        self.increment_digit_and_add_to_stock(self.s.columns, column_index)
        square_index = self.find_square(row_index, column_index)
        self.increment_digit_and_add_to_stock(self.s.squares, square_index)

    def increment_digit_and_add_to_stock(self, elements_list: List[SudokuElement], index: int) -> None:
        elements_list[index].increment_digits()
        self.s.unchecked_stack.append(elements_list[index])

    def find_square(self, row_index: int, column_index: int) -> int:
        sq_number = 0
        while not (
                self.s.square_coordinates[sq_number][0] <= row_index < self.s.square_coordinates[sq_number][1]
                and
                self.s.square_coordinates[sq_number][2] <= column_index < self.s.square_coordinates[sq_number][3]
        ):
            sq_number += 1
        return sq_number

    def check_stock(self) -> None:
        self.s.unchecked_stack = list(set(self.s.unchecked_stack))
        while len(self.s.unchecked_stack):
            self.fill_element(self.s.unchecked_stack[-1])
            self.s.unchecked_stack.pop()

    def solve(self) -> None:
        self.counter = 0
        self.s.possible_digits_in_cells = {coordinate: [] for coordinate in self.s.zero_positions}
        while self.counter < len(self.s.available_digits):
            self.check_available_digits()
        self.check_blank_cells()

    def check_available_digits(self):
        digit = self.s.available_digits[self.counter]
        self.s.changed = False
        positions_in_squares = self.get_positions_in_squares(digit)
        self.insert_digit_if_only_one_possible_position_in_square(digit, positions_in_squares)
        if self.s.changed:
            self.after_change_procedure()
        else:
            potential_positions, solutions = self.positions_in_one_row_or_column(positions_in_squares)
            self.apply_solutions(digit, solutions)
            if self.s.changed:
                self.after_change_procedure()
            else:
                self.add_digit_to_blank_cells(digit, potential_positions)

    def get_positions_in_squares(self, digit: int) -> Dict[int, List[Tuple[int, int]]]:
        available_positions = self.search_for_available_positions(digit)
        positions_in_squares = self.divide_positions_by_squares(available_positions, digit)
        for i in range(2):
            positions_in_squares = self.update_positions_if_one_dimensional_positions_in_squares(positions_in_squares,
                                                                                                 i)
        return positions_in_squares

    def search_for_available_positions(self, digit: int) -> List[Tuple[int, int]]:
        positions = np.where(self.s.array == digit)
        available_rows = set(i[0] for i in self.s.zero_positions).difference(set(positions[0]))
        available_cols = set(i[1] for i in self.s.zero_positions).difference(set(positions[1]))
        return [i for i in product(available_rows, available_cols) if self.s.array[i[0], i[1]] == 0]

    def divide_positions_by_squares(self, available_positions, digit):
        positions_in_squares = {}
        for element in available_positions:
            square_number = self.find_square(element[0], element[1])
            if self.digit_in_square(digit, square_number):
                continue
            if square_number not in positions_in_squares:
                positions_in_squares[square_number] = []
            positions_in_squares[square_number].append(element)
        return positions_in_squares

    def update_positions_if_one_dimensional_positions_in_squares(self,
                                                                 positions_in_squares: Dict[int, List[Tuple[int, int]]],
                                                                 flag: int) -> Dict[int, List[Tuple[int, int]]]:
        for square in positions_in_squares:
            element = self.positions_in_one_dimention(positions_in_squares[square], flag)
            self.delete_unavailable_coordinates(element, flag, positions_in_squares, square)
        return positions_in_squares

    @staticmethod
    def delete_unavailable_coordinates(element, flag, positions_in_squares, square) -> None:
        if element:
            for square_number in positions_in_squares:
                if square_number == square:
                    continue
                positions_in_squares[square_number] = [
                    coordinate for coordinate in positions_in_squares[square_number] if coordinate[flag] != element]

    def insert_digit_if_only_one_possible_position_in_square(self, digit, positions_in_squares) -> None:
        for square in positions_in_squares:
            if len(positions_in_squares[square]) == 1:
                row_index, column_index = positions_in_squares[square][0][0], positions_in_squares[square][0][1]
                self.insert_and_set_changed(digit, row_index, column_index)

    def insert_and_set_changed(self, digit: int, row_index: int, column_index: int) -> None:
        self.insert_digit(digit, row_index, column_index)
        self.s.changed = True

    @staticmethod
    def positions_in_one_row_or_column(positions_in_squares) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        potential_positions = list(chain.from_iterable(positions_in_squares.values()))
        rows_count = Counter([p[0] for p in potential_positions])
        columns_count = Counter([p[1] for p in potential_positions])
        solutions = [p for p in potential_positions if rows_count[p[0]] == 1 or columns_count[p[1]] == 1]
        return potential_positions, solutions

    def after_change_procedure(self) -> None:
        self.check_stock()
        self.clear_possible_coordinates()
        self.counter = 0

    def apply_solutions(self, digit, solutions) -> None:
        if len(solutions):
            for coordinate in solutions:
                self.insert_and_set_changed(digit, coordinate[0], coordinate[1])

    def digit_in_square(self, digit: int, square_number: int) -> bool:
        return digit in self.s.array[
                        self.s.squares[square_number].row_start: self.s.squares[square_number].row_stop,
                        self.s.squares[square_number].column_start: self.s.squares[square_number].column_stop,
                        ]

    def add_digit_to_blank_cells(self, digit, potential_positions) -> None:
        for position in potential_positions:
            self.s.possible_digits_in_cells[position].append(digit)
        self.counter += 1

    def check_blank_cells(self) -> None:
        self.s.changed = False
        if len(self.s.zero_positions):
            for coordinate in self.s.possible_digits_in_cells:
                if len(self.s.possible_digits_in_cells[coordinate]) == 1:
                    self.insert_and_set_changed(self.s.possible_digits_in_cells[coordinate][0], coordinate[0],
                                                coordinate[1])
        if self.s.changed:
            self.check_stock_and_solve_again()

    def try_random_insert(self, max_tries: int = 10):
        number_of_tries = 0
        while len(self.s.zero_positions) and number_of_tries <= max_tries:
            self.random_check()
            number_of_tries += 1

    def random_check(self) -> None:
        backup_sudoku = deepcopy(self.s)
        minimum_number_of_digits = min(
            len(digits_list) for digits_list in self.s.possible_digits_in_cells.values() if len(digits_list) > 0)
        considered_position = choice([coordinate for coordinate in self.s.possible_digits_in_cells.keys()
                                      if len(self.s.possible_digits_in_cells[coordinate]) == minimum_number_of_digits])
        considered_digit = choice(self.s.possible_digits_in_cells[considered_position])
        self.insert_digit(considered_digit, considered_position[0], considered_position[1])
        self.check_stock_and_solve_again()
        if not self.is_sudoku_completed():
            self.s = backup_sudoku

    def check_stock_and_solve_again(self):
        self.check_stock()
        self.solve()

    def is_sudoku_completed(self) -> bool:
        if len(self.s.zero_positions) == 0:
            if self.assert_sum_digits_in_element(self.s.rows):
                if self.assert_sum_digits_in_element(self.s.columns):
                    if self.assert_sum_digits_in_element(self.s.squares):
                        return True
        return False

    def assert_sum_digits_in_element(self, elements_list: List[SudokuElement], result: int = 45) -> bool:
        for element in elements_list:
            if np.sum(self.s.array[element.row_start:element.row_stop,
                      element.column_start:element.column_stop]) != result:
                return False
        return True

    def clear_possible_coordinates(self) -> None:
        for coordinate in self.s.possible_digits_in_cells:
            self.s.possible_digits_in_cells[coordinate] = []

    @staticmethod
    def positions_in_one_dimention(square_positions: List[Tuple[int, int]], flag: int) -> Optional[int]:
        """
        If all possible coordinates (for particular digit) in square are located in one row or one column,
        that row/column can be deleted from the rest possible coordinates.
        :param square_positions: all possible coordinates in square
        :param flag: 0 for row, 1 for column
        :return: the number of row or column
        """
        if len(square_positions) == 1:
            return None
        elements = set([coordinate[flag] for coordinate in square_positions])
        if len(elements) == 1:
            return list(elements)[0]
        else:
            return None
