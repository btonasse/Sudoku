import unittest
from Sudoku import Sudoku

class TestSudoku(unittest.TestCase):

    def setUp(self) -> None:
        self.sud = Sudoku()
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
    
    def test_puzzle_parsing(self) -> None:
        puzzle_string = '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
        puzzle = self.sud.parse_puzzle(puzzle_string)
        self.assertEqual(puzzle, self.puzzle)

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