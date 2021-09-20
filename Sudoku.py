import random
from copy import deepcopy
import logging
from typing import TextIO
import time
import argparse
import multiprocessing as mp

from utils.logger import create_logger
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
    # Set up logger
    logger = create_logger('Sudoku', 'debug_logs/lastrun.log')
    def __init__(self, puzzle_string: str = None) -> None:
        if puzzle_string:
            self.puzzle = self.parse_puzzle(puzzle_string)
            self.logger.info(f'Loaded puzzle:\n{self.puzzle_to_string(self.puzzle)}')
        else:
            self.puzzle = [[0 for _ in range(9)] for _ in range(9)]
        self.solution = deepcopy(self.puzzle)
        self.possibles = self.get_list_of_possible_numbers()
        self.solution_count = 0

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

                
    def is_possible(self, row: int, col: int, number: int) -> bool:
        '''
        Check if a number can be entered in a given space.
            Args:
                row/col -> the space coordinates
                number -> the number being tested
        '''
        # Check if space already has a number
        if self.solution[row][col]:
            return False
        for i in range(9):
            if self.solution[row][i] == number:
                return False
            if self.solution[i][col] == number:
                return False
            # Check in region
            root_row = (row//3)*3
            root_col = (col//3)*3
            if number in self.solution[root_row+i//3][root_col:root_col+3]:
                return False
        return True

    def get_list_of_possible_numbers(self) -> list:
        '''
        Generates a nested list of possible numbers for each square.
        '''
        possibles = [[[] for _ in range(9)] for _ in range(9)]
        for rowno, row in enumerate(self.puzzle):
            for colno, value in enumerate(row):
                if not value:
                    for number in range(1,10):
                        if self.is_possible(rowno, colno, number):
                            possibles[rowno][colno].append(number)
                else:
                    possibles[rowno][colno] = [value]
        return possibles

    def update_possibles(self, number: int, space: tuple) -> list:
        '''
        Update self.possibles after a number is added to a space.
        '''
        target_r, target_c = space
        for row in range(9):
            for col in range(9):
                if row == target_r and col == target_c:
                    self.possibles[row][col] = [number]
                elif row == target_r or col == target_c or (row//3 == target_r//3 and col//3 == target_c//3):
                    try:
                        self.possibles[row][col].remove(number)
                    except ValueError:
                        pass
        return self.possibles

    def is_only_possible_space_for_number(self, number: int, space: tuple) -> bool:
        '''
        Constraing propagation strategy 2:
        Check if a number cannot fit anywhere else in the row, col or region of a given coordinate.
        '''
        target_r, target_c = space
        in_row = in_col = in_reg = 0
        for row, row_possibles in enumerate(self.possibles):
            for col, possibles in enumerate(row_possibles):
                if row == target_r and number in possibles:
                    in_row += 1
                if col == target_c and number in possibles:
                    in_col += 1
                if row//3 == target_r//3 and col//3 == target_c//3 and number in possibles:
                    in_reg += 1
                if in_row > 1 and in_col > 1 and in_reg > 1:
                    return False
        return True

    def constraint_propagation(self) -> list:
        '''
        Recursive method to populate spaces using the following constraint propagation strategies:
            1) If a given space only has one possible number, populate that number
            2) If a given row/column/region only has one possible space for a number, populate it there.
        '''
        has_changed = False
        for row in range(9):
            for col in range(9):
                need_update = False
                if self.solution[row][col]:
                    continue

                if not self.possibles[row][col]:
                    self.logger.debug(f'No valid numbers in row {row}, col {col}.')
                    raise NoValidNumbers(f'No valid numbers in row {row}, col {col}.')

                # If a given space only has one possible number, populate that number
                if len(self.possibles[row][col]) == 1:
                    selected_number = self.possibles[row][col][0]
                    self.logger.debug(f'Coordinate ({row},{col}) only has one possible: {selected_number}')
                    need_update = True
                # If a number cannot fit anywhere else in same row/column/region only has one possible space for a number, populate it here
                else:
                    for possible in self.possibles[row][col]:
                        if self.is_only_possible_space_for_number(possible, (row, col)):
                            selected_number = possible
                            self.logger.debug(f'Coordinate ({row},{col}) is only possibility for number: {selected_number}')
                            need_update = True
                # Update self.possibles if a space has been populated
                if need_update:
                    self.solution[row][col] = selected_number
                    self.update_possibles(selected_number, (row, col))
                    has_changed = True
        # Check if new_puzzle is the same as original one (no more propagation is possible)
        # If it is not, try to keep propagating recursively
        if not has_changed:
            self.logger.debug('No more propagation possible.')
            return self.solution
        else:
            self.logger.debug(
                f'New state after propagation:\n'
                f'{self.puzzle_to_string(self.solution)}'
            )
            return self.constraint_propagation()
 
    def get_next_space_with_least_candidates(self) -> tuple:
        '''
        Instead of just getting next empty space, get next empty space with least number of candidates.
        '''
        possibles_by_length = {n: None for n in range(2,10)}
        for row, row_possibles in enumerate(self.possibles):
            for col, possibles in enumerate(row_possibles):
                if len(possibles) == 1:
                    continue
                # If the number of candidates is two (the minimum), there's no point in looping further
                if len(possibles) == 2:
                    return (row, col)
                # Store just the first coordinate that has a given number of possibles
                if not possibles_by_length[len(possibles)]:
                    possibles_by_length[len(possibles)] = (row, col)
        # Return first coord with lowest number of possibles 
        for coord in possibles_by_length.values():
            if coord:
                return coord 
        raise AlreadySolved(f'Puzzle is already solved!')

    def solve(self, itertype: str = 'sequential') -> list:
        '''
        Solve the loaded puzzle by first applying constraint propagation techniques.
        If puzzle cannot be solved like this, brute force the remaining spaces using a backtracking algorithm.
        To speed up this process, after each 'guess' the constraint propagation algorithm is applied again.
            Args:
                itertype: the type of iteration when guessing possible numbers: 'sequential' (default), 'random' or 'reversed'.
        Solution is stored in self.solution and also returned as a list
        '''
        try:
            self.constraint_propagation()
        except NoValidNumbers:
            return False
        try:
            row, col = self.get_next_space_with_least_candidates()
            possibles = self.possibles[row][col]
        except AlreadySolved:
            self.logger.debug(f'No more empty spaces. Puzzle solved!')
            self.logger.info(f'Puzzle solved by {mp.current_process().name}')
            self.logger.info(f'Solution:\n{self.puzzle_to_string(self.solution)}')
            return self.solution
        
        if itertype == 'random':
            random.shuffle(possibles)
        elif itertype == 'reversed':
            possibles.reverse()
        
        for number in possibles:
            self.logger.debug(f'Trying {number} in ({row},{col})...')
            backup_solution = deepcopy(self.solution)
            backup_possibles = deepcopy(self.possibles)
            self.solution[row][col] = number
            self.update_possibles(number, (row, col))
            if self.solve(itertype):
                return self.solution
            self.solution = deepcopy(backup_solution)
            self.possibles = deepcopy(backup_possibles)

    def get_solution_count(self) -> int:
        '''
        Modified version of self.solve. Instead of returning when a solution is found,
        keep looking for solutions until more than one solution is found or no more solutions can be found.

        Example with multiple solutions: '....19......74.51.75....6...1..3.....6.12.9.5.92..4.31475..13.6.3...51.718....45.'
        '''
        try:
            self.constraint_propagation()
        except NoValidNumbers:
            return False
        try:
            row, col = self.get_next_space_with_least_candidates()
            possibles = self.possibles[row][col]
        except AlreadySolved:
            self.solution_count += 1
            self.logger.debug(f'No more empty spaces. Puzzle solved. Solutions so far: {self.get_solution_count}')
            return self.solution_count

        for number in possibles:
            backup_solution = deepcopy(self.solution)
            backup_possibles = deepcopy(self.possibles)
            self.solution[row][col] = number
            self.update_possibles(number, (row, col))
            # Recurse but do not return (keep solving even if solution is found)
            self.get_solution_count()
            self.solution = deepcopy(backup_solution)
            self.possibles = deepcopy(backup_possibles)
        return self.solution_count


    def build_puzzle_output_string(self, timetaken: float, no_solution: float) -> str:
        '''
        Take self.puzzle (and potentially self.solution) and return them as a string.
            Args:
                timetaken: time in seconds that the puzzle took to solve.
                no_solution: if set, only the puzzle will be output and the time it took to generate 
        '''
        output = []
        puzzle_notation = self.puzzle_to_notation(self.puzzle)
        output.append(f'Puzzle: {puzzle_notation}')
        puzzle_as_string = self.puzzle_to_string(self.puzzle)
        output.append(puzzle_as_string)
        solution_notation = self.puzzle_to_notation(self.solution)
        if no_solution:
            output.insert(-1, f'Generated in {timetaken:.6f}s by {mp.current_process().name}')
        else:
            output.append(f'Solution: {solution_notation}')
            output.append(f'Solved in {timetaken:.6f}s by {mp.current_process().name}')
            solution_as_string = self.puzzle_to_string(self.solution)
            output.append(solution_as_string)
        return '\n'.join(output)
    
    def remove_space(self, puzzle: list) -> list: 
        '''
        Removes a random number from a board and then return the new board state.
        '''
        while True:
            row = random.randint(0,8)
            col = random.randint(0,8)
            if not puzzle[row][col]:
                continue
            puzzle[row][col] = 0
            return puzzle

    def propose_puzzle(self, clues: int = 35) -> list:
        '''
        Looks for a valid unique puzzle with the specified number of clues.
        This is a recursive function that follows the following workflow:
        1) Generate a full random board via self.experiment
        2) Remove random space
        3) Get number of solutions. If more than one solution found, go back to step 2 and try again until a threshold is met.
           If the threshold is reached, go back to step 1.
        '''
        if clues < 17:
            raise ValueError('Cannot generate a unique puzzle with less than 17 clues.')
        toremove = 81-clues
        puzzle = self.solve(itertype='random')

        loops = 0
        while toremove > 0:
            backup = deepcopy(puzzle)
            puzzle = self.remove_space(puzzle)
            if self.has_unique_solution(puzzle):
                toremove -= 1
                continue
            else:
                puzzle = deepcopy(backup)
            if loops == 100:
                self.logger.info('No unique puzzle found after 100 attempts. Trying a new board...')
                return self.propose_puzzle(clues)
            loops += 1
        self.puzzle = puzzle
        return puzzle
    
    def has_unique_solution(self, puzzle: list) -> bool:
        '''
        Checks if a given puzzle has a unique solution.
        Create a new Sudoku instance so the solution of the proposed puzzle doesn't interfere with the current instance's attributes.
        '''
        puzzle_str = self.puzzle_to_notation(puzzle)
        sud = Sudoku(puzzle_str)
        solutions = sud.get_solution_count()
        return solutions == 1

    def generate(self, clues: int = 35) -> list:
        '''
        Master method to generate a valid and unique puzzle.
        '''
        self.logger.info(f'Looking for a unique puzzle with {clues} clues...')
        start = time.perf_counter()
        puzzle = self.propose_puzzle(clues)
        end = time.perf_counter()
        self.logger.info(f'Generated puzzle in {end-start:.6f}s:')
        self.logger.info(self.puzzle_to_string(self.puzzle))
        self.logger.info(self.puzzle_to_notation(self.puzzle))
        self.logger.info('Solution:')
        self.logger.info(self.puzzle_to_string(self.solution))
        self.logger.info(self.puzzle_to_notation(self.solution))
        return puzzle

def solve_puzzle(puzzle_index: int, puzzle: str) -> str:
    '''
    Wrapper for the Sudoku.solve method that return the final string representation of the puzzle and its solution,
    including the time it took to solve.
        Args:
            puzzle_index: used only for the output to console. Useful when solving multiple puzzles at once.
            puzzle: string representation of the puzzle to solve (in Sudoku notation)
    '''
    start = time.perf_counter()
    print(f'Solving puzzle {puzzle_index}: {puzzle}')
    sud = Sudoku(puzzle)
    result = sud.solve()
    end = time.perf_counter()
    runtime = end-start
    if not result:
        sud.logger.warning(f'Puzzle {puzzle_index} invalid: {puzzle}')
        return f'\n\nPuzzle {puzzle_index} invalid: {puzzle}\nElapsed time: {runtime:.6f}s.'
    sud.logger.info(f'Elapsed time: {runtime:.6f}s')
    output = '\n\n' + sud.build_puzzle_output_string(runtime, False)
    print(f'Puzzle {puzzle_index} done ({runtime:.6f}s)')
    return output

def solve_file(file: TextIO) -> None:
    '''
    Solve all puzzles in the given file using a multiprocessing pool. Results are saved to /solved_puzzles subfolder.
    '''
    print(f'Solving puzzles from file {file.name}...')
    start = time.perf_counter()
    with file as source:
        puzzles = source.read().split('\n')
    tasks = [(i+1, puzzle) for i, puzzle in enumerate(puzzles)]
    workers = mp.cpu_count()

    with mp.Pool(workers) as pool:
        result = pool.starmap_async(solve_puzzle, tasks)
    
        output_file_path = time.strftime('solved_puzzles/puzzles%Y%m%d-%H%M.txt', time.localtime(time.time()))
        with open(output_file_path, 'w') as outfile:
            outfile.write(f'Solved puzzles from file {file.name}:')
            for puz in result.get():
                if puz:
                    outfile.write(puz)
            end = time.perf_counter()
            total_runtime = end-start
            outfile.write(f'\n\n{workers} processes solved {len(tasks)} puzzles in {total_runtime:.6f}s.')
        print(f'{workers} processes solved {len(tasks)} puzzles in {total_runtime:.6f}s. Output file: {output_file_path}')

def generate_puzzle(puzzle_index: str, clues: int) -> str:
    '''
    Wrapper for the Sudoku.generate method.
    Return a string representation of the generated puzzle, including the time it took to generate.
        Args:
            puzzle_index: used only for the output to console. Useful when generating multiple puzzles.
            clues: the number of clues the puzzle should have
    '''
    start = time.perf_counter()
    print(f'Generating puzzle {puzzle_index}...')
    sud = Sudoku()
    sud.generate(clues)
    end = time.perf_counter()
    runtime = end-start
    output = '\n\n' + sud.build_puzzle_output_string(runtime, True)
    print(f'Puzzle {puzzle_index} done ({runtime:.6f}s)')
    return output

def generate_many_puzzles(clues: int, number_of_puzzles: int) -> None:
    '''
    Wrapper for the Sudoku.generate method. Uses a multiprocessing pool to generate multiple puzzles concurrently.
    Results are saved in the /generated_puzzles subdir.
        Args:
            clues: how many clues to give to each puzzle
            number_of_puzzles: how many puzzles to generate
    '''
    print(f'Generating {number_of_puzzles} puzzles with {clues} clues...')
    start = time.perf_counter()
    output_file_path = time.strftime('generated_puzzles/puzzles%Y%m%d-%H%M.txt', time.localtime(time.time()))
    tasks = [(i+1, clues) for i in range(number_of_puzzles)]
    workers = mp.cpu_count()
    with mp.Pool(workers) as pool:
        result = pool.starmap_async(generate_puzzle, tasks)

        with open(output_file_path, 'w') as outfile:
            outfile.write(f'Generated puzzles with {clues} clues:')
            for puz in result.get():
                outfile.write(puz)
            end = time.perf_counter()
            total_runtime = end-start
            outfile.write(f'\n\n{workers} processes generated {len(tasks)} puzzles in {total_runtime:.6f}s.')
        print(f'{workers} processes generated {len(tasks)} puzzles in {total_runtime:.6f}s. Output file: {output_file_path}')

    
def main(args: argparse.Namespace) -> None:
    '''
    Function that translates main arguments (usually provided by the command-line) into concrete actions for the program,
    such as solving or generating a puzzle.
        Args:
            args.puzzle: a 81-long string of characters in Sudoku notation. If not provided, a puzzle will be generated.
            args.file: if set, solve puzzles from given file and output solutions to a timestamped file in the solved_puzzles subdir.
                Does nothing when generating (puzzles are output to file by default).
            args.debug: If set, loglevel = DEBUG. Does nothing when generating puzzles or solving multiple puzzles (log level will always be WARNING).
            args.generate: if generating a puzzle, this is a list containning clues and number of puzzles to generate.
                Puzzles are saved in a timestamped file in generated_puzzles subdir
    '''
    if args.puzzle:
        if args.debug:
            Sudoku.logger.setLevel(logging.DEBUG)
            Sudoku.logger.handlers[0].setLevel(logging.DEBUG)
        
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

        result = solve_puzzle(1, puzzle)
        if result:
            print(result)
    
    elif args.file:
        solve_file(args.file)

    else:
        clues, number_of_puzzles = args.generate
        generate_many_puzzles(clues, number_of_puzzles)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    mex = parser.add_mutually_exclusive_group(required=True)
    mex.add_argument('-p', '--puzzle', action='store', help="Run the solver for a given puzzle. For solving a demo puzzle, pass the value 'easy'|'medium'|'hard'|'hardest' instead of a puzzle.")
    mex.add_argument('-g', '--generate', action='store', type=int, nargs=2, metavar=('CLUES', 'HOWMANY'), help='Generate a puzzle with a given number of clues.')
    mex.add_argument('-f', '--file', action='store', type=argparse.FileType('r'), nargs='?', const='puzzles.txt', help='Solve puzzles from given file. Output also goes to a file.')
    parser.add_argument('-d', '--debug', action='store_true', help='Set logger level to debug. Has no effect when generating a puzzle or solving multiple puzzles.')
    args = parser.parse_args()

    main(args)


