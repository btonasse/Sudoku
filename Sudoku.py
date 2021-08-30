from random import shuffle, randint
class Sudoku:
    '''
    Sudoku solver/generator. Uses a mixture of constraint propagation/backtracking to solve puzzles.
    # Todo usage
    '''
    def __init__(self) -> None:
        self.puzzle = None
        self.solution = None

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
        # Check if number exists in row
        if number in puzzle[row]:
            return False
        # Check if number exists in column
        columns = self.rows_to_cols(puzzle)
        if number in columns[col]:
            return False
        # Check if number exists in region by:
        # 1) Transposing the puzzle to a list of regions
        # 2) Determine where target space's coordinates in the 3x3 grid of regions
        # 3) Determine to which index of the new list these coordinates correspond to
        regions = self.rows_to_regions(puzzle)
        reg_row = (row//3)*3
        reg_col = (col//3)*3
        target_region = reg_row*3 + reg_col
        if number in regions[target_region]:
            return False
        return True



            


