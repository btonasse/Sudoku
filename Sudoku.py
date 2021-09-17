import random
from copy import deepcopy
import logging
from typing import Tuple
import time
import argparse

class NoValidNumbers(ValueError):
    '''
    Error for when there are no valid numbers for a space
    '''
class AlreadySolved(Exception):
    '''
    Error for when trying to solve an already solved puzzle
    '''
class Sudoku:
    '''
    Sudoku solver/generator. Uses a mixture of constraint propagation/backtracking to solve puzzles.
    # Todo usage
    '''
    def __init__(self, puzzle_string, loglevel=logging.WARNING) -> None:
        self.puzzle = self.parse_puzzle(puzzle_string)
        self.solution = None
        
        # Set up logger
        logging.basicConfig(level=loglevel)
        self.logger = logging.getLogger('Sudoku')
        print(f'Loaded puzzle:\n{self.puzzle_to_string(self.puzzle)}')

    def parse_puzzle(self, puzzle_string: str) -> list:
        '''
        Parses sudoku notation into a processable puzzle format.
        Accepted representations of empty squares is the number 0 or a dot.
        Returns a list of 9 rows of numbers (with 0 for empty spaces)
        '''
        if len(puzzle_string) != 81:
            raise ValueError(f'Puzzle string must have 81 characters, and not {len(puzzle_string)}.')
        if not all([char in '0123456789.' for char in puzzle_string]):
            raise ValueError(f'Puzzle string only accepts digits. Use 0 or . for empty spaces.')
        puzzle_string = puzzle_string.replace('.', '0')
        puzzle = []
        for i in range(0,81,9):
            puzzle.append([int(char) for char in puzzle_string[i:i+9]])
        return puzzle
    
    def puzzle_to_notation(self, puzzle: list) -> str:
        '''
        Transforms the puzzle into a string (with dots representing empty spaces)
        '''
        string = ''
        for row in puzzle:
            for cell in row:
                string += str(cell)
        string = string.replace('0','.')
        return string

    def puzzle_to_string(self, puzzle: list) -> str:
        '''
        Builds a string representation of the Sudoku grid for pretty printing.
        Replace 0's with whitespace.
        '''
        separator = '+-------+-------+-------+'
        output = [separator]
        # Iterate three rows/cols at a time so separators can be inserted
        for y in range(0,9,3):
            for row in puzzle[y:y+3]:
                new_line = '| '
                for x in range(0,9,3):
                    for cell in row[x:x+3]:
                        new_line += str(cell)+' '
                    new_line += '| '
                output.append(new_line.replace('0',' '))
            output.append(separator)
        output_string = '\n'.join(output)
        return output_string

                
    def is_possible(self, puzzle: list, row: int, col: int, number: int) -> bool:
        '''
        Check if a number can be entered in a given space.
            Args:
                puzzle -> the whole grid
                row/col -> the space coordinates
                number -> the number being tested
        '''
        # Check if space already has a number
        if puzzle[row][col]:
            return False
        for i in range(9):
            if puzzle[row][i] == number:
                return False
            if puzzle[i][col] == number:
                return False
            # Check in region
            root_row = (row//3)*3
            root_col = (col//3)*3
            if number in puzzle[root_row+i//3][root_col:root_col+3]:
                return False
        return True


    def get_possible_numbers_for_space(self, puzzle: list, row: int, col: int) -> list:
        '''
        Get a list of possible numbers for a given space.
        Iterate through all 9 numbers and append them to the return list
        if not already present in the same row/column/region
            Args:
                puzzle -> the whole grid
                row/col -> the space coordinates
        '''
        # If there's already a number, return a list with that as the single element
        if puzzle[row][col]:
            return [puzzle[row][col]]        
        possible_numbers = []
        for number in range(1,10):
            if self.is_possible(puzzle, row, col, number):
                possible_numbers.append(number)
        return possible_numbers

    def get_list_of_possible_numbers(self, puzzle: list) -> Tuple[list]:
        '''
        Generates a nested list of possible numbers for each square.
        Then takes the full list of possible numbers and transforms it into three lists
        containing all possible numbers for each row, col and region, respectively.
        '''
        possibles = [[[] for _ in range(9)] for _ in range(9)]
        for rowno, row in enumerate(puzzle):
            for colno, value in enumerate(row):
                if not value:
                    for number in range(1,10):
                        if self.is_possible(puzzle, rowno, colno, number):
                            possibles[rowno][colno].append(number)
                else:
                    possibles[rowno][colno] = [value]
        
        by_rows = [[] for _ in range(9)] 
        by_cols = [[] for _ in range(9)]
        by_regs = [[] for _ in range(9)]
        for row, row_possibles in enumerate(possibles):
            for col, space in enumerate(row_possibles):
                for number in space:
                    by_rows[row].append(number)
                    by_cols[col].append(number)
                    by_regs[col//3+3*(row//3)].append(number)
        return possibles, by_rows, by_cols, by_regs

    def is_only_possible_space_for_number(self, in_rows: list, in_cols: list, in_regs: list, row: int, col: int, number: int) -> bool:
        '''
        Constraing propagation strategy 2:
        Check if a number cannot fit anywhere else in the row, col or region of a given coordinate.
        '''
        if in_rows[row].count(number) == 1:
            return True
        if in_cols[col].count(number) == 1:
            return True
        if in_regs[col//3+3*(row//3)].count(number) == 1:
            return True
        return False

    def constraint_propagation(self, puzzle: list) -> list:
        '''
        Recursive method to populate spaces using the following constraint propagation strategies:
            1) If a given space only has one possible number, populate that number
            2) If a given row/column/region only has one possible space for a number, populate it there.
        To avoid the overhead of generating the list of possible numbers every time a new space is filled,
        self.is_possible() is called instead right before insertion to make sure it's a valid number.
        '''
        has_changed = False
        all_possibles, by_rows, by_cols, by_regs = self.get_list_of_possible_numbers(puzzle)
        for row, possibles_row in enumerate(all_possibles):
            for col, possibles_in_space in enumerate(possibles_row):
                if puzzle[row][col]:
                    continue
                if not possibles_in_space:
                    self.logger.debug(f'No valid numbers in row {row}, col {col}.')
                    raise NoValidNumbers(f'No valid numbers in row {row}, col {col}.')
                
                # If a given space only has one possible number, populate that number
                if len(possibles_in_space) == 1 and self.is_possible(puzzle, row, col, possibles_in_space[0]):
                    self.logger.debug(f'Coordinate ({row},{col}) only has one possible: {possibles_in_space[0]}')
                    puzzle[row][col] = possibles_in_space[0]
                    has_changed = True
                # If a number cannot fit anywhere else in same row/column/region only has one possible space for a number, populate it here
                else:
                    for number in possibles_in_space:
                        if self.is_only_possible_space_for_number(by_rows, by_cols, by_regs, row, col, number) and self.is_possible(puzzle, row, col, number):
                            self.logger.debug(f'Coordinate ({row},{col}) is only possibility for number: {number}')
                            puzzle[row][col] = number
                            has_changed = True
                            break
        # Check if new_puzzle is the same as original one (no more propagation is possible)
        # If it is not, try to keep propagating recursively
        if not has_changed:
            self.logger.debug('No more propagation possible.')
            return puzzle
        else:
            self.logger.debug(
                f'New state after propagation:\n'
                f'{self.puzzle_to_string(puzzle)}'
            )
            return self.constraint_propagation(puzzle)
    
    def is_puzzle_solved(self, puzzle: list) -> bool:
        '''
        Check if all spaces have been filled
        '''
        flattened_puzzle = [y for row in puzzle for y in row]
        return all(flattened_puzzle)
 
    def get_next_space_with_least_candidates(self, puzzle: list) -> Tuple[tuple, list]:
        '''
        Instead of just getting next empty space, get next empty space with least number of candidates.
        '''
        sorted_possibles = [{} for _ in range(8)]
        for rowno, row in enumerate(puzzle):
            for colno, value in enumerate(row):
                if not value:
                    possibles_for_coord = self.get_possible_numbers_for_space(puzzle, rowno, colno)
                    sorted_possibles[len(possibles_for_coord)-2][(rowno,colno)] = possibles_for_coord
                    
        for dic in sorted_possibles:
            for coord, possibles in dic.items():
                return coord, possibles
        raise AlreadySolved(f'Puzzle is already solved!')

    def experiment(self, puzzle: list, itertype: str = 'sequential') -> list:
        '''
        Get all possibilities for each space and experiment one at a time.
        If the experiment results in an invalid grid state, backtrack and try next number.
            Args:
                puzzle -> the grid to solve
                randomize -> if this is True, when trying possible numbers, a random one will be selected.
        '''
        if self.interrupt.is_set():
            raise AlreadySolved('Another process already solved it.')
        try:
            coord, possibles = self.get_next_space_with_least_candidates(puzzle)
            row, col = coord
        except AlreadySolved:
            self.logger.debug(f'No more empty spaces. Puzzle solved!')
            self.solved.set()
            return puzzle
        if itertype == 'random':
            random.shuffle(possibles)
        elif itertype == 'reversed':
            possibles.reverse()
        for number in possibles:
            self.logger.debug(f'Trying {number} in ({row},{col})...')
            puzzle[row][col] = number
            try:
                puzzle_after_constraint_prop = self.constraint_propagation(deepcopy(puzzle))
                puzzle_after_constraint_prop = self.experiment(puzzle_after_constraint_prop, itertype)
                if puzzle_after_constraint_prop:
                    return puzzle_after_constraint_prop
            except NoValidNumbers:
                puzzle[row][col] = 0
    
    def solve(self, itertype: str = 'sequential') -> list:
        '''
        Solve the loaded puzzle by first applying constraint propagation techniques.
        If puzzle cannot be solved like this, brute force the remaining spaces using a backtracking algorithm.
        To speed up this process, after each 'guess' the constraint propagation algorithm is applied again.
            Args:
                itertype: the type of iteration when guessing possible numbers: 'sequential' (default), 'random' or 'reversed'.
        '''
        print('Trying to solving puzzle using constraint propagation...')
        start_time = time.perf_counter()
        prop_result = self.constraint_propagation(deepcopy(self.puzzle))
        if self.is_puzzle_solved(prop_result):
            solution = prop_result
        else:
            print('This is a tough one. Let me try guessing some numbers...')
            solution = self.experiment(prop_result, itertype)

        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Success! Puzzle solved in {total_time:.6f}s.')
        print(f'Solution:\n{self.puzzle_to_string(solution)}')
        self.solution = solution
        return self.solution


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('puzzle', action='store', help="Run the solver for a given puzzle. For solving a demo puzzle, pass the value 'easy'|'medium'|'hard'|'hardest' instead of a puzzle.")
    parser.add_argument('-d', '--debug', action='store_true', help='Set logger level to debug.')
    args = parser.parse_args()

    if args.puzzle == 'easy':
        puzzle = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
    elif args.puzzle == 'medium':
        puzzle = '85...24..72......9..4.........1.7..23.5...9...4...........8..7..17..........36.4.'
    elif args.puzzle == 'hard':
        puzzle = '..53.....8......2..7..1.5..4....53...1..7...6..32...8..6.5....9..4....3......97..'
    elif args.puzzle == 'hardest':
        puzzle = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    else:
        puzzle = args.puzzle
    
    if args.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.WARNING
    
    sud = Sudoku(puzzle, loglevel)
    sud.solve()


