# Sudoku solver and creator
This is a Sudoku solver that combines simple constraint propagation techniques with a brute force backtracking algorithm for when the propagation is not enough to solve the puzzles. This allows it to quickly solve puzzles that would take ages to solve by simple backtracking.

Some examples of hard puzzles (solved in an average of 0.05s):
`85...24..72......9..4.........1.7..23.5...9...4...........8..7..17..........36.4.`
`..53.....8......2..7..1.5..4....53...1..7...6..32...8..6.5....9..4....3......97..`

![Sudoku solver](https://github.com/btonasse/Sudoku/blob/master/demo/demo.gif)
