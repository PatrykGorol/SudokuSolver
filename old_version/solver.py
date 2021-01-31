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
        """
        General flow of procedures. Starts with basic checks for blank cell that can be already completed.
        Then the main solving methods are used.
        If sudoku is still incomplete after previous procedures, program tries random insertions.
        :return: None
        """
        if not self.is_sudoku_completed():
            self.pre_solving_check()
            self.solve()
            # self.try_random_insert()
            self.backtracking()
        return None

    def validate_sudoku(self) -> int:
        """
        Checks if sudoku array is valid, i.e. if rows, columns or squares don't contain duplicated digits.
        :return: 0 if array is empty, 1 if is valid, -1 if invalid
        """
        if self.s.elements_count[0] == 81:
            return 0
        if not self.check_occurences():
            return -1
        return 1

    def check_occurences(self) -> bool:
        """
        Checks if every row, column and square contains only one occurrence of digit.
        :return: True if sudoku is valid, otherwise False
        """
        if self.check_if_one_occurence_of_digit(self.s.rows):
            if self.check_if_one_occurence_of_digit(self.s.columns):
                if self.check_if_one_occurence_of_digit(self.s.squares):
                    return True
        return False

    def check_if_one_occurence_of_digit(self, elements_list: List[SudokuElement]) -> bool:
        """
        Checks if row, column or square contains only one of non-zero digits.
        :param elements_list: list of rows, columns or squares
        :return: bool
        """
        for element in elements_list:
            array = self.s.array[element.row_start:element.row_stop, element.column_start:element.column_stop]
            digits = [i for i in np.unique(array) if i > 0]
            for digit in digits:
                if np.count_nonzero(array == digit) > 1:
                    return False
        return True

    def pre_solving_check(self) -> None:
        """
        Checks if there are rows, columns or squares ready to fill.
        :return: None
        """
        self.check_elements(self.s.rows)
        self.check_elements(self.s.columns)
        self.check_elements(self.s.squares)
        return None

    def check_elements(self, elements_list: List[SudokuElement]) -> None:
        """
        Checks if element can be completed immediately.
        :param elements_list: list of sudoku rows, columns, or squares
        :return: None
        """
        for element in elements_list:
            self.fill_element(element)
        self.check_stack()
        return None

    def fill_element(self, element: SudokuElement) -> None:
        """
        For element with 8 digits already in place, find last digit and insert into blank cell.
        Also upadte statistics of row, column and square containing filled cell.
        :param element: row, column or square
        :return: None
        """
        if element.completed:
            return None
        if element.digits == 8:
            array = self.s.array[element.row_start:element.row_stop, element.column_start:element.column_stop]
            row_index, column_index = self.get_zero_coordinate(array, element.row_start, element.column_start)
            digit = self.find_last_digit(array)
            self.insert_digit(digit, row_index, column_index)
        return None

    @staticmethod
    def get_zero_coordinate(element_array: np.ndarray, row_start: int, column_start: int) -> Tuple[int, int]:
        """
        Generates coordinates of blank cell in given array.
        :param element_array: sudoku element as list of digits
        :param row_start: no. of sudoku row element starts with
        :param column_start: no. of sudoku column element starts with
        :return: tuple of coordinates (row, column)
        """
        coord = np.where(element_array == 0)
        return coord[0][0] + row_start, coord[1][0] + column_start

    def find_last_digit(self, array: np.ndarray) -> int:
        """
        Get digit an array is lacking. Searches only in available digits' list.
        :param array: sudoku element as an array of digits
        :return: digit not present in an array; digit to insert
        """
        for digit in self.s.available_digits:
            if digit not in array:
                return digit

    def insert_digit(self, digit, row_index, column_index) -> None:
        """
        Insert digit into cell of provided coordinates, delete cell from list of zeros' coordinates.
        Upadtes available digits and statistics of row, column and square.
        :param digit: digit to insert
        :param row_index: row coordinate of cell to fill
        :param column_index: column coordinate of cell to fill
        :return: None
        """
        if digit is None:
            return None
        self.s.array[row_index, column_index] = digit
        self.s.zero_positions.remove((row_index, column_index))
        self.update_available_elements(digit)
        self.update_elements_statistics(row_index, column_index)
        return None

    def update_available_elements(self, digit: int) -> None:
        """
        Adds digit to the sudoku's digit counter and upadates available digits.
        I inserted digit is a 9th occurrence, digit is removed from available digits' list.
        :param digit: inserted digit
        :return: None
        """
        self.s.elements_count[digit] += 1
        self.s.set_available_digits()
        return None

    def update_elements_statistics(self, row_index: int, column_index: int) -> None:
        """
        Increment number of digits in row, column and square containing recently filled cell.
        Also adds those elements to stack in order to check if (after insertion) elements are easy solvable.
        :param row_index: row coordinate of recently filled cell
        :param column_index: column coordinate of recently filled cell
        :return: None
        """
        self.increment_digit_and_add_to_stack(self.s.rows[row_index])
        self.increment_digit_and_add_to_stack(self.s.columns[column_index])
        square_index = self.find_square(row_index, column_index)
        self.increment_digit_and_add_to_stack(self.s.squares[square_index])
        return None

    def increment_digit_and_add_to_stack(self, element: SudokuElement) -> None:
        """
        Increments digit in element's counter and adds element into stack (queue of recently updates elements,
        which enable to check if elements are not easy solvable).
        :param element: sudoku element
        :return: None
        """
        element.increment_digits()
        self.s.unchecked_stack.append(element)
        return None

    def find_square(self, row_index: int, column_index: int) -> int:
        """
        Check which sudoku square contains a cell of provided coordinates
        :param row_index: row coordinate of recently filled cell
        :param column_index: column coordinate of recently filled cell
        :return: number of square which contains cell of provided coordinates
        """
        sq_number = 0
        while not (
                self.s.square_coordinates[sq_number][0] <= row_index < self.s.square_coordinates[sq_number][1]
                and
                self.s.square_coordinates[sq_number][2] <= column_index < self.s.square_coordinates[sq_number][3]
        ):
            sq_number += 1
        return sq_number

    def check_stack(self) -> None:
        """
        For all elements in stack function checks if element can be easly solve and solves that element.
        Stack can be incremented during a process, so function runs as long as there are no more elements to check.
        :return: None
        """
        self.s.unchecked_stack = list(set(self.s.unchecked_stack))
        while len(self.s.unchecked_stack):
            self.fill_element(self.s.unchecked_stack[0])
            self.s.unchecked_stack.pop(0)
            self.s.unchecked_stack = list(set(self.s.unchecked_stack))
        return None

    def solve(self) -> None:
        """
        Main solving sequence.
        Checks if there are blank cells where only one digit can be inserted.
        :return: None
        """
        self.counter = 0
        self.s.possible_digits_in_cells = {coordinate: [] for coordinate in self.s.zero_positions}
        while self.counter < len(self.s.available_digits):
            self.check_available_digits()
        self.check_blank_cells()
        return None

    def check_available_digits(self) -> None:
        """
        For given digit function generates all permissible blank cells.
        Checks in squares, rows and columns if there is only one possible cell to insert the digit.
        If all checks don't cause digit insertion, function updates dictionary with all blank cells
        and their corresponding permissible digits.
        :return: None
        """
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
        return None

    def get_positions_in_squares(self, digit: int) -> Dict[int, List[Tuple[int, int]]]:
        """
        Creates a dictionary with blank cells' coordinates divided by square numbers.
        :param digit: evaluating digit
        :return: dictionary with blank cells' coordinates divided by square numbers
        """
        available_positions = self.search_for_available_positions(digit)
        positions_in_squares = self.divide_positions_by_squares(available_positions, digit)
        for i in range(2):
            positions_in_squares = self.update_positions_if_one_dimensional_positions_in_squares(positions_in_squares,
                                                                                                 i)
        return positions_in_squares

    def search_for_available_positions(self, digit: int) -> List[Tuple[int, int]]:
        """
        Searches for blank cells where there are no interferences (same digit in a row, column or square)
        :param digit: digit we are evaluating
        :return: list of blank cells' coordinates where digit can be inserted
        """
        positions = np.where(self.s.array == digit)
        available_rows = set(i[0] for i in self.s.zero_positions).difference(set(positions[0]))
        available_cols = set(i[1] for i in self.s.zero_positions).difference(set(positions[1]))
        return [i for i in product(available_rows, available_cols) if self.s.array[i[0], i[1]] == 0]

    def divide_positions_by_squares(self, available_positions: List[Tuple[int, int]], digit: int) -> Dict[
        int, List[int]]:
        """
        Creates a dictionary with square numbers as keys and list of black cells' coordinates,
         where digit can be inserted.
        :param available_positions:
        :param digit: digit we are evaluating
        :return: dictionary with blank cells' coordinates divided by square numbers
        """
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
        """
        Checks if there are rows or columns inside squares where digit must be inserted.
        Deletes the same rows/columns' coordinates in another squares (inside list od available coordinates).
        :param positions_in_squares: list of available blank cells' coordinates divided by squares
        :param flag: 0 for row, 1 for column
        :return: updated list of available blank cells' coordinates divided by squares
        """
        for square in positions_in_squares:
            element = self.positions_in_one_dimention(positions_in_squares[square], flag)
            self.delete_unavailable_coordinates(element, flag, positions_in_squares, square)
        return positions_in_squares

    @staticmethod
    def delete_unavailable_coordinates(element: int, flag: int, positions_in_squares: Dict[int, List[Tuple[int, int]]],
                                       square: int) -> None:
        """
        Get all potential (for insertion) blank cells' coordinates and deletes non-valid coordinates.
        Non-valid coordinates are ones that digit MUST be inserted in the same row/column but in another square.
        :param element: number of row or column
        :param flag: 0 for row, 1 for column
        :param positions_in_squares: list of available blank cells' coordinates divided by squares
        :param square: number of square where digit must be inserted
        :return: updated list of available blank cells' coordinates divided by squares
        """
        if element:
            for square_number in positions_in_squares:
                if square_number == square:
                    continue
                positions_in_squares[square_number] = [
                    coordinate for coordinate in positions_in_squares[square_number] if coordinate[flag] != element]
        return None

    def insert_digit_if_only_one_possible_position_in_square(self, digit: int, positions_in_squares: Dict[
        int, List[Tuple[int, int]]]) -> None:
        """
        If there is only one available (for aur digit) blank cell inside a square, it can be filled.
        Function inserts a digit and sets sudoku array status on "changed".
        :param digit: evaluating digit
        :param positions_in_squares: list of available blank cells' coordinates divided by squares
        :return: None
        """
        for square in positions_in_squares:
            if len(positions_in_squares[square]) == 1:
                row_index, column_index = positions_in_squares[square][0][0], positions_in_squares[square][0][1]
                self.insert_and_set_changed(digit, row_index, column_index)
        return None

    def insert_and_set_changed(self, digit: int, row_index: int, column_index: int) -> None:
        """
        Inserts digit and sets sudoku array status on "changed".
        :param digit: evaluating digit
        :param row_index: row coordinate of cell to fill
        :param column_index: column coordinate of cell to fill
        :return: None
        """
        self.insert_digit(digit, row_index, column_index)
        self.s.changed = True
        return None

    @staticmethod
    def positions_in_one_row_or_column(positions_in_squares) -> Tuple[List[Tuple[int, int]], List[Tuple[int, int]]]:
        """
        Checks how many available blank cells is in each row and collumn.
        If row/column has only one available cell, it can be filled with digit.
        :param positions_in_squares:
        :return: list of available blank cells' coordinates, list of black cells' coordinates which can be filled
        """
        potential_positions = list(chain.from_iterable(positions_in_squares.values()))
        rows_count = Counter([p[0] for p in potential_positions])
        columns_count = Counter([p[1] for p in potential_positions])
        solutions = [p for p in potential_positions if rows_count[p[0]] == 1 or columns_count[p[1]] == 1]
        return potential_positions, solutions

    def after_change_procedure(self) -> None:
        """
        After inserted a digit, stack has elements to check for easy solving.
        Also lists of possible digits for all blank cells need to be clared.
        Program's counter resets.
        :return: None
        """
        self.check_stack()
        self.clear_possible_coordinates()
        self.counter = 0
        return None

    def apply_solutions(self, digit, solutions) -> None:
        """
        Insert digit into all available cells.
        :param digit: digit to insert in available cells
        :param solutions: list of coordinates digit can be inserted
        :return: None
        """
        if len(solutions):
            for coordinate in solutions:
                self.insert_and_set_changed(digit, coordinate[0], coordinate[1])
        return None

    def digit_in_square(self, digit: int, square_number: int) -> bool:
        """
        Checks if digit is already in square.
        :param digit: digit we are evaluating
        :param square_number: index of square in list of sqares' coordinates
        :return: bool
        """
        return digit in self.s.array[
                        self.s.squares[square_number].row_start: self.s.squares[square_number].row_stop,
                        self.s.squares[square_number].column_start: self.s.squares[square_number].column_stop,
                        ]

    def add_digit_to_blank_cells(self, digit: int, potential_positions: List[Tuple[int, int]]) -> None:
        """
        Fills dictionary of blank cells.
        For every blank cell, if digit is permissible in that cell, digit is added to the list of digits.
        :param digit: evaluating digit
        :param potential_positions: list of available blank cells' coordinates
        :return: None
        """
        for position in potential_positions:
            self.s.possible_digits_in_cells[position].append(digit)
        self.counter += 1
        return None

    def check_blank_cells(self) -> None:
        """
        Checks if there are coordinates, which have only one permissible digit.
        If so, digit can be inserted.
        :return: None
        """
        self.s.changed = False
        if len(self.s.zero_positions):
            for coordinate in self.s.possible_digits_in_cells:
                if len(self.s.possible_digits_in_cells[coordinate]) == 1:
                    self.insert_and_set_changed(self.s.possible_digits_in_cells[coordinate][0], coordinate[0],
                                                coordinate[1])
        if self.s.changed:
            self.check_stack_and_solve_again()
        return None

    def try_random_insert(self, max_tries: int = 10) -> None:
        """
        If Sudoku is still incomplete after previous solving procedure, program tries to use random insertions.
        It will insert digits chosen randomly from list of available digits.
        Insertion will occur on blank cell with minimum number of possible digits,
        so the probability for accurate choice is utmost.
        :param max_tries: maximum number of tries (random insertions)
        :return: None
        """
        number_of_tries = 0
        while len(self.s.zero_positions) and number_of_tries <= max_tries:
            self.random_check()
            number_of_tries += 1
        return None

    def random_check(self) -> None:
        """
        At first function makes a deepcopy of sudoku array as an backup.
        Then it gets a blank cell with minimum number or permissible digits.
        Than gets one of the coordinates with that minimum.
        For chosen coordinates (blank cell) inserts randomly one of the available digits.
        After insertion function starts solving procedure again.
        If sudoku is not completed after solving procedure, original sudoku array is restored from backup.
        :return: None
        """
        backup_sudoku = deepcopy(self.s)
        minimum_number_of_digits = min(
            len(digits_list) for digits_list in self.s.possible_digits_in_cells.values() if len(digits_list) > 0)
        considered_position = choice([coordinate for coordinate in self.s.possible_digits_in_cells.keys()
                                      if len(self.s.possible_digits_in_cells[coordinate]) == minimum_number_of_digits])
        considered_digit = choice(self.s.possible_digits_in_cells[considered_position])
        self.insert_digit(considered_digit, considered_position[0], considered_position[1])
        self.check_stack_and_solve_again()
        if not self.is_sudoku_completed():
            self.s = backup_sudoku
        return None

    def check_stack_and_solve_again(self) -> None:
        """
        Stack is not empty, so it needs to be checked.
        Digit has been inserted, so we can try solve sudoku again.
        :return: None
        """
        self.check_stack()
        self.solve()
        return None

    def is_sudoku_completed(self) -> bool:
        """
        Checks if there are no blank cells and all elements are correctly filled.
        :return: bool
        """
        # if len(self.s.zero_positions) == 0:
        if np.count_nonzero(self.s.array) == 81:
            if self.assert_sum_digits_in_element(self.s.rows):
                if self.assert_sum_digits_in_element(self.s.columns):
                    if self.assert_sum_digits_in_element(self.s.squares):
                        return True
        return False

    def assert_sum_digits_in_element(self, elements_list: List[SudokuElement], result: int = 45) -> bool:
        """
        Check if sum of digits in sudoku element equals given result.
        :param elements_list: list of sudoku elements (rows, columns or squares)
        :param result: For element fully filled with unique digits result equals sum of digits from 1 to 9, which is 45.
        :return: bool
        """
        for element in elements_list:
            if np.sum(self.s.array[element.row_start:element.row_stop,
                      element.column_start:element.column_stop]) != result:
                return False
        return True

    def clear_possible_coordinates(self) -> None:
        """
        Clears lists of possible digits for all blank cells' coordinates.
        :return: None
        """
        for coordinate in self.s.possible_digits_in_cells:
            self.s.possible_digits_in_cells[coordinate] = []
        return None

    @staticmethod
    def positions_in_one_dimention(square_positions: List[Tuple[int, int]], flag: int) -> Optional[int]:
        """
        If all possible coordinates (for particular digit) in square are located in one row or one column,
        that row/column can be deleted from the rest possible coordinates.
        :param square_positions: all possible coordinates in square
        :param flag: 0 for row, 1 for column
        :return: the number of row or column or None
        """
        if len(square_positions) == 1:
            return None
        elements = set([coordinate[flag] for coordinate in square_positions])
        if len(elements) == 1:
            return list(elements)[0]
        else:
            return None

    def backtracking(self) -> None:
        counter = 0
        if len(self.s.zero_positions) == 0:
            return None
        self.s.zero_positions.sort(key=lambda x: len(self.s.possible_digits_in_cells[x]), reverse=False)
        # print(self.s.zero_positions)
        print(self.s.possible_digits_in_cells)
        print()

        # x = 1
        # for coord in self.s.possible_digits_in_cells:
        #     x *= len(self.s.possible_digits_in_cells[coord])
        # print('ilość wariantów: {:e}'.format(x))
        # print()

        # print(len(self.s.zero_positions))
        # print()
        digits_counter = {coordinate: 0 for coordinate in self.s.zero_positions}
        cell_index = 0
        insertion_list = []
        while cell_index < len(self.s.zero_positions):
            counter += 1
            print(counter)
            coordinate = self.s.zero_positions[cell_index]
            insertion_list = [i for i in insertion_list if i[0] != coordinate]
            # print(f'Coordinate: {coordinate}')
            # print(f'digits_counter: {digits_counter[coordinate]}')
            digit_index = digits_counter[coordinate]
            # print(f'digits: {self.s.possible_digits_in_cells[coordinate]}')
            # print(f'digit_index: {digit_index}')
            # print(f'cell_index: {cell_index}')

            if digit_index < len(self.s.possible_digits_in_cells[coordinate]):
                digit = self.s.possible_digits_in_cells[coordinate][digit_index]
                # self.s.array[coordinate[0], coordinate[1]] = digit
                insertion_list.append((coordinate, digit))
            else:
                digits_counter[coordinate] = 0
                # self.s.array[coordinate[0], coordinate[1]] = 0
                cell_index -= 1
                # insertion_list = [i for i in insertion_list if i[0] != coordinate]
                # print('previous_cell')
                # print()
                if cell_index < 0:
                    break
                continue

            if self.check_occurences_in_potential_array(insertion_list):
                # print(insertion_list)
                if self.try_insert(insertion_list):
                    return None
                digits_counter[coordinate] += 1
                cell_index += 1
                # print(f'Digit: {digit}')
                # print('next cell')
                # print()
                continue
            else:
                digits_counter[coordinate] += 1
                # insertion_list.pop()

        print(self.s.array)
        return None

    def check_occurences_in_potential_array(self, insertion_list: List[Tuple[Tuple[int, int], int]]) -> bool:
        backup_sudoku = deepcopy(self.s)
        for item in insertion_list:
            self.s.array[item[0][0], item[0][1]] = item[1]
        if self.check_occurences():
            self.s = backup_sudoku
            return True
        else:
            self.s = backup_sudoku
            return False

    def try_insert(self, insertion_list: List[Tuple[Tuple[int, int], int]]) -> bool:
        backup_sudoku = deepcopy(self.s)
        for item in insertion_list:
            self.insert_digit(item[1], item[0][0], item[0][1])
        self.check_stack_and_solve_again()
        if not self.is_sudoku_completed():
            self.s = backup_sudoku
            return False
        return True

