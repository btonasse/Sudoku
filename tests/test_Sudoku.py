'''
Unit tests for sudoku solver/creator
Usage:
python -m unittest discover -s tests -v -b
'''
import unittest
import random
from Sudoku import Sudoku

class TestSudokuSimple(unittest.TestCase):
    '''
    Test case with a simple puzzle where the full solution can be obtained via constraint propagation.
    '''
    def setUp(self) -> None:
        self.sud = Sudoku('003020600900305001001806400008102900700000008006708200002609500800203009005010300')
        self.puzzle = [
            [0, 0, 3, 0, 2, 0, 6, 0, 0],
            [9, 0, 0, 3, 0, 5, 0, 0, 1],
            [0, 0, 1, 8, 0, 6, 4, 0, 0],
            [0, 0, 8, 1, 0, 2, 9, 0, 0],
            [7, 0, 0, 0, 0, 0, 0, 0, 8],
            [0, 0, 6, 7, 0, 8, 2, 0, 0],
            [0, 0, 2, 6, 0, 9, 5, 0, 0],
            [8, 0, 0, 2, 0, 3, 0, 0, 9],
            [0, 0, 5, 0, 1, 0, 3, 0, 0]
        ]
        self.solution = [
            [4, 8, 3, 9, 2, 1, 6, 5, 7],
            [9, 6, 7, 3, 4, 5, 8, 2, 1],
            [2, 5, 1, 8, 7, 6, 4, 9, 3],
            [5, 4, 8, 1, 3, 2, 9, 7, 6],
            [7, 2, 9, 5, 6, 4, 1, 3, 8],
            [1, 3, 6, 7, 9, 8, 2, 4, 5],
            [3, 7, 2, 6, 8, 9, 5, 1, 4],
            [8, 1, 4, 2, 5, 3, 7, 6, 9],
            [6, 9, 5, 4, 1, 7, 3, 8, 2]
        ]
        self.possibles = [
            [[4, 5], [4, 5, 7, 8], [3], [4, 9], [2], [1, 4, 7], [6], [5, 7, 8, 9], [5, 7]],
            [[9], [2, 4, 6, 7, 8], [4, 7], [3], [4, 7], [5], [7, 8], [2, 7, 8], [1]],
            [[2, 5], [2, 5, 7], [1], [8], [7, 9], [6], [4], [2, 3, 5, 7, 9], [2, 3, 5, 7]],
            [[3, 4, 5], [3, 4, 5], [8], [1], [3, 4, 5, 6], [2], [9], [3, 4, 5, 6, 7], [3, 4, 5, 6, 7]],
            [[7], [1, 2, 3, 4, 5, 9], [4, 9], [4, 5, 9], [3, 4, 5, 6, 9], [4], [1], [1, 3, 4, 5, 6], [8]],
            [[1, 3, 4, 5], [1, 3, 4, 5, 9], [6], [7], [3, 4, 5, 9], [8], [2], [1, 3, 4, 5], [3, 4, 5]],
            [[1, 3, 4], [1, 3, 4, 7], [2], [6], [4, 7, 8], [9], [5], [1, 4, 7, 8], [4, 7]],
            [[8], [1, 4, 6, 7], [4, 7], [2], [4, 5, 7], [3], [1, 7], [1, 4, 6, 7], [9]],
            [[4, 6], [4, 6, 7, 9], [5], [4], [1], [4, 7], [3], [2, 4, 6, 7, 8], [2, 4, 6, 7]]
        ]
    
    def test_puzzle_parsing(self) -> None:
        puzzle_string = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
        sudoku = Sudoku(puzzle_string)
        self.assertEqual(sudoku.puzzle, self.puzzle)

    def test_printable_string(self) -> None:
        expected = '+-------+-------+-------+\n|     3 |   2   | 6     | \n| 9     | 3   5 |     1 | \n|     1 | 8   6 | 4     | \n+-------+-------+-------+\n|     8 | 1   2 | 9     | \n| 7     |       |     8 | \n|     6 | 7   8 | 2     | \n+-------+-------+-------+\n|     2 | 6   9 | 5     | \n| 8     | 2   3 |     9 | \n|     5 |   1   | 3     | \n+-------+-------+-------+'
        puzzle_as_string = self.sud.puzzle_to_string(self.puzzle)
        self.assertEqual(puzzle_as_string, expected)
    
    def test_puzzle_to_notation(self) -> None:
        expected = '..3.2.6..9..3.5..1..18.64....81.29..7.......8..67.82....26.95..8..2.3..9..5.1.3..'
        notation = self.sud.puzzle_to_notation(self.puzzle)
        self.assertEqual(notation, expected)

    def test_is_possible_on_empty_space(self) -> None:
        expected_results_at_00 = [False,False,False,True,True,False,False,False,False]
        for number in range(1,10):
            with self.subTest(i=number):
                self.assertEqual(self.sud.is_possible(0, 0, number), expected_results_at_00[number-1])

    def test_is_possible_on_non_empty_space(self) -> None:
        possibilities = [self.sud.is_possible(1, 0, number) for number in range(1,10)]
        self.assertTrue(not any(possibilities))
    
    def test_list_of_possibles(self) -> None:
        possibles = self.sud.get_list_of_possible_numbers()
        self.assertEqual(possibles, self.possibles)

    def test_is_only_possible_space_for_number(self) -> None:
        coords = [(0,5), (1,2), (1,1)]
        numbers = [1, 4, 6]
        expected = [True, False, True]
        for i in range(len(coords)):
            with self.subTest(i=i):
                self.assertEqual(self.sud.is_only_possible_space_for_number(numbers[i], coords[i]), expected[i])
    
    def test_full_solution_with_constraint_propagation(self) -> None:
        self.assertEqual(self.sud.constraint_propagation(), self.solution)

class TestSudokuMedium(unittest.TestCase):
    '''
    Test case for harder puzzles that require backtracking to solve
    '''
    def setUp(self) -> None:
        self.sud = Sudoku('85...24..72......9..4.........1.7..23.5...9...4...........8..7..17..........36.4.')
        self.puzzle = [
            [8, 5, 0, 0, 0, 2, 4, 0, 0],
            [7, 2, 0, 0, 0, 0, 0, 0, 9],
            [0, 0, 4, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 1, 0, 7, 0, 0, 2],
            [3, 0, 5, 0, 0, 0, 9, 0, 0],
            [0, 4, 0, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 8, 0, 0, 7, 0],
            [0, 1, 7, 0, 0, 0, 0, 0, 0],
            [0, 0, 0, 0, 3, 6, 0, 4, 0]
        ]
        self.solution = [
            [8, 5, 9, 6, 1, 2, 4, 3, 7],
            [7, 2, 3, 8, 5, 4, 1, 6, 9],
            [1, 6, 4, 3, 7, 9, 5, 2, 8],
            [9, 8, 6, 1, 4, 7, 3, 5, 2],
            [3, 7, 5, 2, 6, 8, 9, 1, 4],
            [2, 4, 1, 5, 9, 3, 7, 8, 6],
            [4, 3, 2, 9, 8, 1, 6, 7, 5],
            [6, 1, 7, 4, 2, 5, 8, 9, 3],
            [5, 9, 8, 7, 3, 6, 2, 4, 1]
        ]
        self.partial_solution = [
            [8, 5, 0, 0, 0, 2, 4, 0, 0],
            [7, 2, 0, 0, 0, 0, 0, 0, 9],
            [0, 0, 4, 0, 0, 0, 0, 2, 0],
            [0, 0, 0, 1, 4, 7, 0, 0, 2],
            [3, 7, 5, 0, 0, 8, 9, 1, 4],
            [0, 4, 0, 0, 0, 0, 0, 0, 0],
            [4, 0, 0, 9, 8, 1, 0, 7, 0],
            [0, 1, 7, 0, 0, 0, 0, 9, 0],
            [0, 0, 0, 7, 3, 6, 0, 4, 0]
        ]
    
    def test_partial_solution_after_constraint_propagation(self) -> None:
        partial_solution = self.sud.constraint_propagation()
        self.assertEqual(partial_solution, self.partial_solution)

    def test_get_next_empty_space(self) -> None:
        expected = (0,3)
        expected_possibles = [3,6]
        self.sud.constraint_propagation()
        space = self.sud.get_next_space_with_least_candidates()
        self.assertEqual(space, expected)
        self.assertEqual(self.sud.possibles[0][3], expected_possibles)

    def test_full_solve(self) -> None:
        solution = self.sud.solve()
        self.assertEqual(solution, self.solution)

class TestRandomExperiment(unittest.TestCase):
    '''
    Tests using the 'random' iteration method for the backtracking algorithm.
    '''
    def setUp(self) -> None:
        random.seed(627834523645)
        #Todo

    def not_impl(self):
        raise NotImplementedError

class TestGenPuzzle(unittest.TestCase):
    '''
    Tests for the puzzle generating functionality
    '''
    def setUp(self) -> None:
        random.seed(627834523645)
        self.sud = Sudoku()
        self.generated_puzzle = [
            [0, 0, 0, 3, 7, 1, 0, 0, 2],
            [0, 2, 0, 0, 6, 5, 0, 0, 3],
            [1, 0, 0, 0, 9, 2, 8, 0, 0],
            [0, 0, 0, 5, 0, 0, 0, 7, 0],
            [0, 1, 4, 0, 0, 6, 3, 0, 0],
            [3, 9, 5, 0, 0, 0, 0, 8, 4],
            [0, 0, 0, 1, 0, 8, 4, 0, 0],
            [9, 8, 7, 0, 0, 0, 2, 3, 0],
            [2, 0, 0, 7, 3, 0, 0, 6, 0]
        ]

    def test_generate_valid_board(self) -> None:
        expected = [
            [6, 5, 8, 3, 7, 1, 9, 4, 2],
            [4, 2, 9, 8, 6, 5, 7, 1, 3],
            [1, 7, 3, 4, 9, 2, 8, 5, 6],
            [8, 6, 2, 5, 4, 3, 1, 7, 9],
            [7, 1, 4, 9, 8, 6, 3, 2, 5],
            [3, 9, 5, 2, 1, 7, 6, 8, 4],
            [5, 3, 6, 1, 2, 8, 4, 9, 7],
            [9, 8, 7, 6, 5, 4, 2, 3, 1],
            [2, 4, 1, 7, 3, 9, 5, 6, 8]
        ]
        self.sud.solve(itertype='random')
        self.assertEqual(self.sud.solution, expected)
    
    def test_has_unique_solution(self) -> None:
        self.assertTrue(self.sud.has_unique_solution(self.generated_puzzle))

    def test_propose_puzzle(self) -> None:
        proposed = self.sud.propose_puzzle(35)
        self.assertEqual(proposed, self.generated_puzzle)

