from random import shuffle
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

    def rows_to_cols(self, puzzle: list) -> list:
        '''
        Transpose the puzzle from a list of rows to a list of columns
        '''
        return list(zip(*puzzle))
    def rows_to_regions(self, puzzle: list) -> list:
        '''
        Transpose the puzzle from a list of rows to a list of regions
        '''
        regions = []
        for row in range(0,9,3):
            for col in range(0,9,3):
                new_region = []
                for i in range(3):
                    new_region.extend(puzzle[row+i][col:col+3])
                regions.append(new_region)
        return regions
                
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
        # Check if number exists in row
        if number in puzzle[row]:
            return False
        # Check if number exists in column
        columns = self.rows_to_cols(puzzle)
        if number in columns[col]:
            return False
        # Check if number exists in region by:
        # 1) Transposing the puzzle to a list of regions
        # 2) Determine target space's coordinates in the 3x3 grid of regions
        # 3) Determine to which index of the new list these coordinates correspond
        regions = self.rows_to_regions(puzzle)
        target_region = self.get_region_index(row, col)
        if number in regions[target_region]:
            return False
        return True

    def get_region_index(self, row: int, col: int) -> int:
        '''
        Given row and column, return the index corresponding to the region a given space is in.
        Regions are arbitrarily ordered from left to right and top to bottom
            Args:
                row/col -> the space coordinates
        '''
        region_row = row//3
        region_col = col//3
        region_index = region_row*3 + region_col
        return region_index

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

    def is_only_possible_space_for_number(self, all_possibles: list, row: int, col: int, number: int) -> bool:
        '''
        Check if a number can only be placed on the specified space by checking
        if the number can be placed anywhere else on same row, column or region.
            Args:
                all_possibles -> a nested list of all possible numbers for each space
                row/col -> reference coordinate from which to derive the row, column and region to be analyzed
                number -> number to analyze. Is assumed to be possible number on the specified coordinate.
        '''
        flattened_row_possibles = [possible for cell in all_possibles[row] for possible in cell]
        if flattened_row_possibles.count(number) == 1:
            return True
        
        all_possibles_cols = self.rows_to_cols(all_possibles)
        flattened_col_possibles = [possible for cell in all_possibles_cols[col] for possible in cell]
        if flattened_col_possibles.count(number) == 1:
            return True

        all_possibles_regs = self.rows_to_regions(all_possibles)
        target_region = self.get_region_index(row, col)
        flattened_reg_possibles = [possible for cell in all_possibles_regs[target_region] for possible in cell]
        if flattened_reg_possibles.count(number) == 1:
            return True
        
        return False

    def constraint_propagation(self, puzzle: list) -> list:
        '''
        Recursive method to populate spaces using the following constraint propagation strategies:
            1) If a given space only has one possible number, populate that number
            2) If a given row/column/region only has one possible space for a number, populate it there.
        '''
        has_changed = False
        all_possibles = self.get_full_list_of_possible_numbers(puzzle)
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
                        if self.is_only_possible_space_for_number(all_possibles, row, col, number) and self.is_possible(puzzle, row, col, number):
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
    
    def get_full_list_of_possible_numbers(self, puzzle: list) -> list:
        '''
        Returns a list of possible numbers for each space in the puzzle grid
        '''
        possibles = []
        for row in range(9):
            possibles.append([])
            for col in range(9):
                possibles_in_space = self.get_possible_numbers_for_space(puzzle, row, col)
                if not possibles_in_space:
                    raise NoValidNumbers(f'No valid numbers in row {row}, col {col}.')
                possibles[row].append(possibles_in_space)
        return possibles

    def is_puzzle_solved(self, puzzle: list) -> bool:
        '''
        Check if all spaces have been filled
        '''
        flattened_puzzle = [y for row in puzzle for y in row]
        return all(flattened_puzzle)

    def get_next_empty_space(self, puzzle: list) -> Tuple[int]:
        '''
        Iterate through the puzzle and return the coordinates of the first empty space
        '''
        for row in range(9):
            for col in range(9):
                if not puzzle[row][col]:
                    return row, col
        raise AlreadySolved(f'Puzzle is already solved!')
       
    def experiment(self, puzzle: list, randomize: bool = False) -> list:
        '''
        Get all possibilities for each space and experiment one at a time.
        If the experiment results in an invalid grid state, backtrack and try next number.
            Args:
                puzzle -> the grid to solve
                randomize -> if this is True, when trying possible numbers, a random one will be selected.
        '''
        try:
            row, col = self.get_next_empty_space(puzzle)
        except AlreadySolved:
            self.logger.debug(f'No more empty spaces. Puzzle solved!')
            return puzzle
        possibles = self.get_possible_numbers_for_space(puzzle, row, col)
        if randomize:
            shuffle(possibles)
        for number in possibles:
            self.logger.debug(f'Trying {number} in ({row},{col})...')
            puzzle[row][col] = number
            try:
                puzzle_after_constraint_prop = self.constraint_propagation(deepcopy(puzzle))
                puzzle_after_constraint_prop = self.experiment(puzzle_after_constraint_prop, randomize=randomize)
                if puzzle_after_constraint_prop:
                    return puzzle_after_constraint_prop
            except NoValidNumbers:
                puzzle[row][col] = 0
    
    def solve(self) -> list:
        '''
        Solve the loaded puzzle by first applying constraint propagation techniques.
        If puzzle cannot be solved like this, brute force the remaining spaces using a backtracking algorithm.
        To speed up this process, after each 'guess' the constraint propagation algorithm is applied again.
        '''
        print('Trying to solving puzzle using constraint propagation...')
        start_time = time.perf_counter()
        prop_result = self.constraint_propagation(deepcopy(self.puzzle))
        if self.is_puzzle_solved(prop_result):
            solution = prop_result
        else:
            print('This is a tough one. Let me try guessing some numbers...')
            solution = self.experiment(prop_result)

        end_time = time.perf_counter()
        total_time = end_time - start_time
        print(f'Success! Puzzle solved in {total_time:.6f}s.')
        print(f'Solution:\n{self.puzzle_to_string(solution)}')
        self.solution = solution
        return self.solution


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('puzzle', action='store', help="Run the solver for a given puzzle. For solving a demo puzzle, pass the value 'easy'|'hard'|'hardest' instead of a puzzle.")
    parser.add_argument('-d', '--debug', action='store_true', help='Set logger level to debug.')
    args = parser.parse_args()

    if args.puzzle == 'easy':
        puzzle = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
    elif args.puzzle == 'hard':
        puzzle = '85...24..72......9..4.........1.7..23.5...9...4...........8..7..17..........36.4.'
    elif args.puzzle == 'hardest':
        puzzle = '..53.....8......2..7..1.5..4....53...1..7...6..32...8..6.5....9..4....3......97..'
    else:
        puzzle = args.puzzle
    
    if args.debug:
        loglevel = logging.DEBUG
    else:
        loglevel = logging.WARNING
    
    sud = Sudoku(puzzle, loglevel)
    sud.solve()


