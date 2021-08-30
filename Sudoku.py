from random import shuffle, randint
class Sudoku:
    '''
    Sudoku solver/generator. Uses a mixture of constraint propagation/backtracking to solve puzzles.
    # Todo usage
    '''
    def __init__(self) -> None:
        self.puzzle = None
        self.solution = None

    def _parse_puzzle(self, puzzle_string: str) -> list:
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
        self.puzzle = puzzle
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
            


