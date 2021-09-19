from copy import deepcopy
from Sudoku import Sudoku, NoValidNumbers, AlreadySolved
import typing
import logging
import random
import time

class test(Sudoku):
    def __init__(self, puzzle_string: str = None, loglevel: int = logging.WARNING) -> None:
        super().__init__(puzzle_string=puzzle_string, loglevel=loglevel)
        self.possibles = self.get_list_of_possible_numbers()
        self.solution = deepcopy(self.puzzle)
    
    def get_list_of_possible_numbers(self) -> list:
        '''
        test
        '''
        possibles = [[[] for _ in range(9)] for _ in range(9)]
        for rowno, row in enumerate(self.puzzle):
            for colno, value in enumerate(row):
                if not value:
                    for number in range(1,10):
                        if self.is_possible(self.puzzle, rowno, colno, number):
                            possibles[rowno][colno].append(number)
                else:
                    possibles[rowno][colno] = [value]
        return possibles

    def update_possibles(self, number: int, space: tuple) -> list:
        '''
        test
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
        test
        '''
        target_r, target_c = space
        in_row = in_col = in_reg = 0
        for row in range(9):
            for col in range(9):
                if row == target_r and number in self.possibles[row][col]:
                    in_row += 1
                if col == target_c and number in self.possibles[row][col]:
                    in_col += 1
                if row//3 == target_r//3 and col//3 == target_c//3 and number in self.possibles[row][col]:
                    in_reg += 1
                if in_row > 1 and in_col > 1 and in_reg > 1:
                    return False
        return True

    def constraint_propagation(self) -> list:
        '''
        test
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

                if len(self.possibles[row][col]) == 1:
                    selected_number = self.possibles[row][col][0]
                    self.logger.debug(f'Coordinate ({row},{col}) only has one possible: {selected_number}')
                    need_update = True

                else:
                    for possible in self.possibles[row][col]:
                        if self.is_only_possible_space_for_number(possible, (row, col)):
                            selected_number = possible
                            self.logger.debug(f'Coordinate ({row},{col}) is only possibility for number: {selected_number}')
                            need_update = True

                if need_update:
                    self.solution[row][col] = selected_number
                    self.update_possibles(selected_number, (row, col))
                    has_changed = True
        
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
        possibles_by_length = {n: None for n in range(2,10)}
        for row in range(9):
            for col in range(9):
                possibles = self.possibles[row][col]
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
        test
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
                return True
            self.solution = deepcopy(backup_solution)
            self.possibles = deepcopy(backup_possibles)








if __name__ == '__main__':
    puz = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    sud = test(puz, logging.DEBUG)
    print(sud.puzzle_to_string(sud.solution))
    #sud.constraint_propagation()
    #print(sud.puzzle_to_string(sud.solution))
    s = time.perf_counter()
    sud.solve()
    e = time.perf_counter()
    print(sud.puzzle_to_string(sud.solution))
    print(f'{e-s:.6f}s')
