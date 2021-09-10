'''
Unit tests for sudoku solver/creator
Usage:
python -m unittest discover -s tests -v
'''
import unittest
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
    def test_a_puzzle_parsing(self) -> None:
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

    def test_transposition(self) -> None:
        expected_cols = [(0, 9, 0, 0, 7, 0, 0, 8, 0), (0, 0, 0, 0, 0, 0, 0, 0, 0), (3, 0, 1, 8, 0, 6, 2, 0, 5), (0, 3, 8, 1, 0, 7, 6, 2, 0), (2, 0, 0, 0, 0, 0, 0, 0, 1), (0, 5, 6, 2, 0, 8, 9, 3, 0), (6, 0, 4, 9, 0, 2, 5, 0, 3), (0, 0, 0, 0, 0, 0, 0, 0, 0), (0, 1, 0, 0, 8, 0, 0, 9, 0)]
        expected_regions = [[0, 0, 3, 9, 0, 0, 0, 0, 1], [0, 2, 0, 3, 0, 5, 8, 0, 6], [6, 0, 0, 0, 0, 1, 4, 0, 0], [0, 0, 8, 7, 0, 0, 0, 0, 6], [1, 0, 2, 0, 0, 0, 7, 0, 8], [9, 0, 0, 0, 0, 8, 2, 0, 0], [0, 0, 2, 8, 0, 0, 0, 0, 5], [6, 0, 9, 2, 0, 3, 0, 1, 0], [5, 0, 0, 0, 0, 9, 3, 0, 0]]
        cols = self.sud.rows_to_cols(self.puzzle)
        regions = self.sud.rows_to_regions(self.puzzle)
        self.assertEqual(cols, expected_cols)
        self.assertEqual(regions, expected_regions)

    def test_is_possible_on_empty_space(self) -> None:
        expected_results_at_00 = [False,False,False,True,True,False,False,False,False]
        for number in range(1,10):
            with self.subTest(i=number):
                self.assertEqual(self.sud.is_possible(self.puzzle, 0, 0, number), expected_results_at_00[number-1])

    def test_is_possible_on_non_empty_space(self) -> None:
        possibilities = [self.sud.is_possible(self.puzzle, 1, 0, number) for number in range(1,10)]
        self.assertTrue(not any(possibilities))
    
    def test_region_index(self) -> None:
        coords = [(4,3), (7,0), (2,8)]
        expected_indexes = [4, 6, 2]
        for i in range(3):
            with self.subTest(i=i):
                self.assertEqual(self.sud.get_region_index(coords[i][0], coords[i][1]), expected_indexes[i])

    def test_possible_numbers_for_space(self) -> None:
        coords = [(4,5), (1,0), (0,0)]
        expected = [[4], [9], [4,5]]
        for i in range(3):
            with self.subTest(i=i):
                self.assertEqual(self.sud.get_possible_numbers_for_space(self.puzzle, coords[i][0], coords[i][1]), expected[i])

    def test_is_only_possible_space_for_number(self) -> None:
        coords = [(0,5), (1,2), (1,1)]
        numbers = [1, 4, 6]
        expected = [True, False, True]
        for i in range(len(coords)):
            with self.subTest(i=i):
                self.assertEqual(self.sud.is_only_possible_space_for_number(self.puzzle, coords[i][0], coords[i][1], numbers[i]), expected[i])
    
    def test_full_solution_with_constraint_propagation(self) -> None:
        self.assertEqual(self.sud.constraint_propagation(self.puzzle), self.solution)

    def test_is_solved(self) -> None:
        self.assertFalse(self.sud.is_puzzle_solved(self.puzzle))
        self.assertTrue(self.sud.is_puzzle_solved(self.solution))

