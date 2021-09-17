import multiprocessing as mp
from Sudoku import Sudoku

puzzle = '4.....8.5.3..........7......2.....6.....8.4......1.......6.3.7.5..2.....1.4......'

if __name__ == '__main__':
    interrupt = mp.Event()
    solved = mp.Event()
    iter_methods = ['sequential', 'reversed']
    for i in range(mp.cpu_count()):
        try:
            method = iter_methods[i]
        except IndexError:
            method = 'random'
        
        sud = Sudoku(puzzle)
        sud.interrupt = interrupt
        sud.solved = solved
        
        p = mp.Process(target=sud.solve, args=(method,))
        p.start()
    solved.wait()
    interrupt.set()

