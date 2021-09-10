from random import shuffle, randint
from copy import deepcopy
from typing import List

class NoValidNumbers(ValueError):
    '''
    Error for when there are no valid numbers for a space
    '''
class Sudoku:
    '''
    Sudoku solver/generator. Uses a mixture of constraint propagation/backtracking to solve puzzles.
    # Todo usage
    '''
    def __init__(self, puzzle_string) -> None:
        self.puzzle = self.parse_puzzle(puzzle_string)
        self.solution = None

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
    
    def puzzle_to_notation(self) -> str:
        '''
        Transforms the puzzle into a string (with dots representing empty spaces)
        '''
        string = ''
        for row in self.puzzle:
            for cell in row:
                string += str(cell)
        string = string.replace('0','.')
        return string

    def puzzle_to_string(self) -> str:
        '''
        Builds a string representation of the Sudoku grid for pretty printing.
        Replace 0's with whitespace.
        '''
        separator = '+-------+-------+-------+'
        output = [separator]
        # Iterate three rows/cols at a time so separators can be inserted
        for y in range(0,9,3):
            for row in self.puzzle[y:y+3]:
                new_line = '| '
                for x in range(0,9,3):
                    for cell in row[x:x+3]:
                        new_line += str(cell)+' '
                    new_line += '| '
                output.append(new_line.replace('0',' '))
            output.append(separator)
        output_string = '\n'.join(output)
        return output_string

    def rows_to_cols(self) -> list:
        '''
        Transpose the puzzle from a list of rows to a list of columns
        '''
        return list(zip(*self.puzzle))
    def rows_to_regions(self) -> list:
        '''
        Transpose the puzzle from a list of rows to a list of regions
        '''
        regions = []
        for row in range(0,9,3):
            for col in range(0,9,3):
                new_region = []
                for i in range(3):
                    new_region.extend(self.puzzle[row+i][col:col+3])
                regions.append(new_region)
        return regions
                
    def is_possible(self, row: int, col: int, number: int) -> bool:
        '''
        Check if a number can be entered in a given space.
            Args:
                row/col -> the space coordinates
                number -> the number being tested
        '''
        # Check if space already has a number
        if self.puzzle[row][col]:
            return False
        # Check if number exists in row
        if number in self.puzzle[row]:
            return False
        # Check if number exists in column
        columns = self.rows_to_cols()
        if number in columns[col]:
            return False
        # Check if number exists in region by:
        # 1) Transposing the puzzle to a list of regions
        # 2) Determine target space's coordinates in the 3x3 grid of regions
        # 3) Determine to which index of the new list these coordinates correspond
        regions = self.rows_to_regions()
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

    def get_possible_numbers_for_space(self, row: int, col: int) -> list:
        '''
        Get a list of possible numbers for a given space.
        Iterate through all 9 numbers and append them to the return list
        if not already present in the same row/column/region
            Args:
                puzzle -> the whole grid
                row/col -> the space coordinates
        '''
        # If there's already a number, return a list with that as the single element
        if self.puzzle[row][col]:
            return [self.puzzle[row][col]]
        
        possible_numbers = []
        for number in range(1,10):
            if self.is_possible(row, col, number):
                possible_numbers.append(number)
        
        if not possible_numbers:
            raise NoValidNumbers(f'No valid numbers in coordinate ({row},{col})')

        return possible_numbers

    def get_possible_spaces_for_number(self, row: int, col: int, number: int) -> List[tuple]:
        '''
        Get all possible spaces (represented as tuples of row/col coordinates),
        where a number can be placed in a given row, column and region.
            Args:
                row/col -> reference coordinate from which to derive the row, column and region to be analyzed
                number -> number to analyze
            Returns:
                Three lists of tuple coordinates (row, column and region),
                representing all spaces where the specified number could be placed.
        '''
        row_possibles = [(row, cell) for cell in range(9) if self.is_possible(row, cell, number)]
        col_possibles = [(cell, col) for cell in range(9) if self.is_possible(cell, col, number)]

        region_root_x = (row//3)*3
        region_root_y = (col//3)*3
        region_possibles = [
            (x,y)
            for x in range(region_root_x, region_root_x+3)
            for y in range(region_root_y, region_root_y+3)
            if self.is_possible(x, y, number)
        ]
        
        return row_possibles, col_possibles, region_possibles


    def constraint_propagation(self, puzzle: list) -> list:
        '''
        Recursive method to populate spaces using the following constraint propagation strategies:
            1) If a given space only has one possible number, populate that number
            2) If a given row/column/region only has one possible space for a number, populate it there.
        '''
        new_puzzle = deepcopy(puzzle)
        for row in range(9):
            for col in range(9):
                if not puzzle[row][col]:
                    possibles = self.get_possible_numbers_for_space(new_puzzle, row, col)
                    if not possibles:
                        raise NoValidNumbers(f'No valid numbers in row {row}, col {col}.')
                    
                    # If a given space only has one possible number, populate that number
                    if len(possibles) == 1:
                        new_puzzle[row][col] = possibles[0]
                  
                    else:
                        # If a number cannot fit anywhere else in same row/column/region only has one possible space for a number, populate it here
                        for number in possibles:
                            in_row, in_col, in_reg = self.get_possible_spaces_for_number(new_puzzle, row, col, number)
                            if len(in_row) == 1 or len(in_col) == 1 or len(in_reg) == 1:
                                new_puzzle[row][col] = number
        
        # Check if new_puzzle is the same as original one (no more propagation is possible)
        # If it is not, try to keep propagating recursively
        if new_puzzle == puzzle:
            return new_puzzle
        else:
            return self.constraint_propagation(new_puzzle)










            


