from random import shuffle, randint
from copy import deepcopy

class NoValidNumbers(ValueError):
    '''
    Error for when there are no valid numbers for a space
    '''
class Sudoku:
    '''
    Sudoku solver/generator. Uses a mixture of constraint propagation/backtracking to solve puzzles.
    # Todo usage
    '''
    def __init__(self) -> None:
        self.puzzles = None
        self.solutions = None

    def parse_puzzle(self, puzzle_string: str) -> list:
        '''
        Parses sudoku notation into a processable puzzle format.
        Accepted representations of empty squares is the number 0 or a dot.
        Returns a list of 9 rows of numbers (with 0 for empty spaces)
        '''
        if len(puzzle_string) != 81:
            raise ValueError(f'Puzzle string must have 81 characters, and not {len(puzzle_string)}.')
        puzzle = []
        puzzle_string = puzzle_string.replace('.', '0')
        for i in range(0,81,9):
            puzzle.append([int(char) for char in puzzle_string[i:i+9]])
        return puzzle
    
    def puzzle_to_notation(self, puzzle: list) -> str:
        '''
        Transforms a puzzle into a string (with dots representing empty spaces)
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
        reg_row = (row//3)*3
        reg_col = (col//3)*3
        target_region = reg_row + reg_col
        if number in regions[target_region]:
            return False
        return True

    def get_possible_numbers(self, puzzle: list, row: int, col: int) -> list:
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
        
        if not possible_numbers:
            raise NoValidNumbers(f'No valid numbers in coordinate ({row},{col})')

        return possible_numbers

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
                    possibles = self.get_possible_numbers(new_puzzle, row, col)

                    # If a given space only has one possible number, populate that number
                    if len(possibles) == 1:
                        new_puzzle[row][col] = possibles[0]
                    else:
                        # If a number cannot fit anywhere else in same row/column/region only has one possible space for a number, populate it here
                        for number in possibles:
                            times_possible_in_row = sum([self.is_possible(new_puzzle, row, cell, number) for cell in range(9)])
                            times_possible_in_col = sum([self.is_possible(new_puzzle, cell, col, number) for cell in range(9)])
                            # region
                            if times_possible_in_row == 1:
                                new_puzzle[row][col] = number
                            









            


