from typing import List, Dict, Tuple

import numpy as np


class SudokuElement:

    def __init__(self, row_start: int, row_stop: int, column_start: int, column_stop: int):
        self.row_start: int = row_start
        self.row_stop: int = row_stop
        self.column_start: int = column_start
        self.column_stop: int = column_stop
        self.completed: bool = False
        self.digits: int = 0

    def increment_digits(self) -> None:
        """
        Each time digit is inserted into sudoku element, increment counter.
        If all 9 digits have been inserted, mark element as completed.
        :return: None
        """
        if not self.completed:
            self.digits += 1
            if self.digits == 9:
                self.completed = True
        return None


class SudokuRow(SudokuElement):

    def __init__(self, row_index: int):
        super().__init__(row_index, row_index + 1, 0, 10)


class SudokuColumn(SudokuElement):

    def __init__(self, column_index: int):
        super().__init__(0, 10, column_index, column_index + 1)


class Sudoku:
    square_coordinates = [(0, 3, 0, 3), (0, 3, 3, 6), (0, 3, 6, 9),
                          (3, 6, 0, 3), (3, 6, 3, 6), (3, 6, 6, 9),
                          (6, 9, 0, 3), (6, 9, 3, 6), (6, 9, 6, 9)]

    def __init__(self, array: List[List[int]]):
        self.array: np.ndarray((9, 9)) = np.array(array)
        self.rows: List[SudokuElement] = [SudokuRow(i) for i in range(9)]
        self.columns: List[SudokuElement] = [SudokuColumn(j) for j in range(9)]
        self.squares: List[SudokuElement] = [SudokuElement(*k) for k in self.square_coordinates]
        self.elements_count: Dict[int: int] = {0: 0, 1: 0, 2: 0, 3: 0, 4: 0, 5: 0, 6: 0, 7: 0, 8: 0, 9: 0}
        self.available_digits: List[int] = []
        self.unchecked_stack: List[SudokuElement] = []
        self.zero_positions: List[Tuple[int, int]] = []
        self.possible_digits_in_cells: Dict[Tuple[int, int]: List[int]] = {}
        self.changed: bool = False
        self.set_zero_positions()
        self.set_statistics()

    def set_zero_positions(self) -> None:
        """
        Creates list with coordinates of zeros (blank sudoku cells).
        :return: None
        """
        zero_positions = np.where(self.array == 0)
        self.zero_positions = list(zip(zero_positions[0], zero_positions[1]))
        return None

    def set_statistics(self) -> None:
        """
        Creates basic parameters of sudoku array:
        - counts occurrences of all digits <0,9>,
        - creates list of available digits,
        - for each sudoku element count already filled cells.
        :return: None
        """
        for digit in self.elements_count:
            self.elements_count[digit] = np.count_nonzero(self.array == digit)
        self.set_available_digits()
        self.set_elements_statistics(self.rows)
        self.set_elements_statistics(self.columns)
        self.set_elements_statistics(self.squares)
        return None

    def set_available_digits(self) -> None:
        """
        Creates list of digits available for inserting into sudoku array. Digits already used 9 times are omitted.
        :return: None
        """
        self.elements_count = dict(sorted(self.elements_count.items(), key=lambda x: x[1], reverse=True))
        self.available_digits = [k for k, v in self.elements_count.items() if k > 0 and v < 9]
        return None

    def set_elements_statistics(self, elements_list: List[SudokuElement]) -> None:
        """
        For each sudoku element function counts number of cells already filled.
        :param elements_list: list of sudoku elements (rows, columns or squares)
        :return: None
        """
        for element in elements_list:
            element.digits = np.count_nonzero(
                self.array[element.row_start:element.row_stop, element.column_start:element.column_stop])
        return None

    def __str__(self) -> str:
        return str(self.array)
