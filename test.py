from copy import deepcopy
from Sudoku import Sudoku, NoValidNumbers, AlreadySolved
import typing
import logging

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
                elif col == target_c and number in self.possibles[row][col]:
                    in_col += 1
                elif row//3 == target_r//3 and col//3 == target_c//3 and number in self.possibles[row][col]:
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






if __name__ == '__main__':
    puz = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'
    sud = test(puz, logging.DEBUG)
    #for row in sud.possibles:
    #    print(row)
    #sud.update_possibles(9, (0,1))
    #print('')
    #for row in sud.possibles:
    #    print(row)
    #print('')
    #print(sud.is_only_possible_space_for_number(4, (5,1)))
    #print('')
    sud.constraint_propagation()
    partial = sud.puzzle_to_string(sud.solution)