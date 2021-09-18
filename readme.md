# Sudoku solver and creator
This is a Sudoku solver that combines simple constraint propagation techniques with a brute force backtracking algorithm for when the propagation is not enough to solve the puzzles. This allows it to quickly solve puzzles that would take ages to solve by simple backtracking.

The same algorithm can also be used to generate puzzles with unique solutions (see usage notes below)

Some examples of hard puzzles (solved in an average of 0.05s):
`85...24..72......9..4.........1.7..23.5...9...4...........8..7..17..........36.4.`
`..53.....8......2..7..1.5..4....53...1..7...6..32...8..6.5....9..4....3......97..`

This especially tough one is solved in 0.2s:

`4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......`

## Command line usage

```
Sudoku.py [-h] (-p PUZZLE | -g CLUES HOWMANY | -f [FILE]) [-d]

optional arguments:
  -h, --help            show this help message and exit
  -p PUZZLE, --puzzle PUZZLE
                        Run the solver for a given puzzle. For solving a demo puzzle, pass the value 'easy'|'medium'|'hard'|'hardest' instead of a puzzle.
  -g CLUES HOWMANY, --generate CLUES HOWMANY
                        Generate a puzzle with a given number of clues.
  -f [FILE], --file [FILE]
                        Solve puzzles from given file. Output also goes to a file.
  -d, --debug           Set logger level to debug. Has no effect when generating a puzzle.
```

![Sudoku solver](https://github.com/btonasse/Sudoku/blob/master/demo/demo.gif)
