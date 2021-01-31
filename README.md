## SUDOKU SOLVER
<br>

**Backtracking algoritm** for solving sudoku with GUI made in **Tkinter** and ready-to-use sudoku examples.

![GUI EXAMPLE](/ReadMe/gui.JPG)
<br>
<br>

### LIST OF CONTENT
1. [Sudoku Rules](#sudoku-rules)
2. [Backtracking](#backtracking)
3. [Setup](#setup--requirements)
<br>
<br>

### Sudoku Rules
Sudoku is a number puzzle in the shape of 9 x 9 grid.
Grid can be divided into *9 rows*, *9 columns* and *9 boxes* (3 x 3 subgrids, also called "blocks" or "regions").
<br>
**Main rule:** Each row, columns and box has to contain 9 digits (from 1 to 9, without duplicates).
<br>
**Objective:** With partially filled grid one's objective is to complete the rest of digits.

######*More information about sudoku can be found on Wikipedia: [history and variants](https://en.wikipedia.org/wiki/Sudoku), [solving algoritms](https://en.wikipedia.org/wiki/Sudoku_solving_algorithms).*

### Backtracking
Before we start, program validates sudoku grid. If any row, column or box already contains more than 1 occurrence of digit, sudoku is unsolvable.
<br><br>
**Solving procedure (metacode)**

* Create *list of empty cells*.
  

* Assign *test number* to every empty cell (we will start with the lowest number: 1).
  

* Create *cell index*. It will point empty cell, we're currently working with (starting with 0).
  

* LOOP: While *cell index* is lower than length of *empty cells' list*: 

    <br>1. Get current empty cell (cell index points it).
  
    <br>2. Get current *test number* of selected cell.
  
    <br>3. if *test number* is out of range (greater than 9):
    * reset *test number* (set value to 1),
    * reset cell value (cell is empty again),
    * move to previous cell (decrement *cell index*),
    * **continue** loop.
    
    <br>4. If *test number* is valid in empty cell:
    * insert *test number*,
    * increment *cell index* (move to next empty cell in next iteration).
    
    <br>5. Increment *test number* (if we come back to that cell, we will start testing from next number).

### Setup / Requirements
* **Python**, version **3.7**.
* Additional packages required: **Numpy 1.20.0** (allows easy slicing of 2 dimensional array).
* Essential files:
    * *sudokusolver.py* - solving procedure and validation methods
    * *gui.py* - graphical interface based on **Tkinter** (run program from that file)
    * *examples.py* - ready-to-solve sudoku examples (including **[the hardest sudoku ever](https://www.conceptispuzzles.com/index.aspx?uri=info/article/424)**)
    * *sudoku.ico* - icon file (required only on Windows)

Program has been tested on Windows 10 and linux (Debian 10 Buster).
