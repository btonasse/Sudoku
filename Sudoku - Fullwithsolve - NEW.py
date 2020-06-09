from random import shuffle
from copy import deepcopy


class SudokuGrid():
	'''
	Sudoku board.
	Attributes:
	clues = how many clues should a proposed puzzle have
	result = the final resolved board
	puzzle = a proposed puzzle
	solvedpuzzle = solved puzzle
	prop_steps, exp_steps = current number of iterations the solver took to solve a puzzle with constraint propagation/guessing
		
	Standalone methods:
	print_grid(): Prints the grid to the console, taking the rows attribute as argument.
	#put the rest here
	'''

	def __init__(self, clues=35):
		self.clues = clues
		self.puzzle = None
		self.solvedpuzzle = None
		self.prop_steps = 0
		self.exp_steps = 0

	def printable_possibles(self, possibles):
		'''
		Formats the list of possible numbers in a printable form
		to be displayed with print_grid()
		'''
		poscopy = [[str(value) for value in row] for row in possibles]
		for sublist in poscopy:
			for i, item in enumerate(sublist):
				sublist[i] = item.replace(', ','').strip('[]')
		
		max_len = 1
		for row in poscopy:
			for cell in row:
				max_len = max(max_len, len(cell))
		for I, row in enumerate(poscopy):
			for i, cell in enumerate(row):
				while len(cell) < max_len:
					cell = ' ' + cell
					poscopy[I][i] = cell
		return poscopy	

	def print_grid(self, rows):
		'''
		Pretty prints the grid using a list of rows.
		'''
		rowstr = ''.join(map(str, rows[0]))
		cellen = len(rowstr)//(9)
		regsep = ('+' + ('-'*(cellen*3)) + ('----'))*3 + '+'

		print(regsep)
		for y in range(0,9,3):
			for row in rows[y:y+3]:
				print('| ', end='')
				for x in range(0,9,3):
					print(*row[x:x+3], '| ', end='')
				print('')
			print(regsep)
	
	
	def propose_puzzle(self): 
		pass

	def parse_puzzle(self, puzzlestring):
		'''
		Parses sudoku notation into a processable puzzle format
		Easy puzzle: '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
		Hard: '85...24..72......9..4.........1.7..23.5...9...4...........8..7..17..........36.4.'
		Another hard: '..53.....8......2..7..1.5..4....53...1..7...6..32...8..6.5....9..4....3......97..'
		'''
		puzzle = []
		puzzlestring = puzzlestring.replace('.',' ')
		puzzlestring = puzzlestring.replace('0',' ')
		for i in range(0,81,9):
			puzzle.append([char for char in puzzlestring[i:i+9]])
		for row in puzzle:
			for i, cell in enumerate(row):
				try:
					row[i] = int(cell)
				except:
					pass
		self.puzzle = puzzle
		return puzzle	

	def is_possible(self, puzzle, r, c, n):
		'''
		Quality of life helper function stolen from the Youtube guy. Checks if a number can be entered on a specific space.
		'''
		for i in range(0,9):
			if puzzle[r][i] == n:
				return False
		for i in range(0,9):
			if puzzle[i][c] == n:
				return False
		r1 = (r//3)*3
		c1 = (c//3)*3
		for i in range(0,3):
			for j in range(0,3):
				if puzzle[r1+i][c1+j] == n:
					return False
		return True

	def gen_possibles(self, puzzle):
		'''
		Generates a list of possible numbers for each square. rpf/cpf/regpf are flattened versions of this list organized by columns/regions, to be used with constraint propagation strategy 2.
		'''
		rp = [[[] for i in range(9)] for i in range(9)]
		for r, row in enumerate(puzzle):
			for c, col in enumerate(row):
				if col == ' ':
					for n in range(1,10):
						if self.is_possible(puzzle, r, c, n):
							rp[r][c].append(n)
				else:
					rp[r][c] = puzzle[r][c]
		
		rpf= [[] for _ in range(9)] 
		cpf= [[] for _ in range(9)]
		regpf= [[] for _ in range(9)]
		for i, row in enumerate(rp):
			for I, col in enumerate(row):
				if type(col) == list:
					for el in col:
						rpf[i].append(el)
						cpf[I].append(el)
						regpf[I//3+3*(i//3)].append(el)

		return rp, rpf, cpf, regpf

	def constraint_prop(self, puzzle, oldrows=[[]]):
		rp, rpf, cpf, regpf = self.gen_possibles(puzzle)
		for i, r in enumerate(rp):   #Strategy 1
			for I, c in enumerate(r):
				if c == []:
					#print(f"No solution possible! No valid numbers for square {i}{I}.")
					#self.print_grid(puzzle)
					#self.print_grid(self.printable_possibles(rp))
					#input('Hit Enter to close')
					return False, puzzle
				if type(c) is list and len(c) == 1 and self.is_possible(puzzle, i, I, c[0]):
					puzzle[i][I] = c[0]
					rp[i][I] = c[0]
					continue
		
		rp, rpf, cpf, regpf = self.gen_possibles(puzzle)
		for i, r in enumerate(rp):  #Strategy 2
			for I, c in enumerate(r):
				if type(c) is list:
					for n in c:
						if rpf[i].count(n) == 1 or cpf[I].count(n) == 1 or regpf[I//3+3*(i//3)].count(n) == 1 and self.is_possible(puzzle, i, I, n):
							puzzle[i][I] = n
							rp[i][I] = n
							break
		
		if not any([any([cell == ' ' for cell in row]) for row in puzzle]): #Checking if puzzle solved
			#print('SOLVED!')
			self.solvedpuzzle = puzzle
			#self.print_grid(puzzle)
			#print('*')
			#input('Hit Enter to close')
			return 'SOLVED', puzzle
		elif puzzle == oldrows:  #No more propagation possible
			#print('Partial solution')
			#self.print_grid(puzzle)
			#self.print_grid(self.printable_possibles(rp))
			#print('*')
			return 'INCOMPLETE', puzzle
		#else:
			#print('Puzzle still incomplete:')
			#self.print_grid(puzzle)
			#self.print_grid(self.printable_possibles(rp))
			#print('Trying one more propagation step...', end='\n\n')
			#input('More?')
		self.prop_steps += 1
		return self.constraint_prop(puzzle, oldrows=deepcopy(puzzle))

	def experiment(self, puzzle, shuff=False):
		emptysq = None
		for i, row in enumerate(puzzle):
			if emptysq:
				break
			for I, col in enumerate(row):
				if col == ' ':
					emptysq = (i, I)
					break
		if not emptysq:
			return True
		else:
			r, c = emptysq
					
		rp, rpf, cpf, regpf = self.gen_possibles(puzzle)						
		if shuff:
			shuffle(rp[r][c])
		for n in rp[r][c]:
			oldpuzzle = deepcopy(puzzle)
			puzzle[r][c] = n
			solvestate, puzzle = self.constraint_prop(puzzle)
			if self.experiment(puzzle, shuff=shuff):
				return self.solvedpuzzle
			puzzle = deepcopy(oldpuzzle)
		self.exp_steps += 1
		return False

	def solve_puzzle(self):
		while True:
			puzzlestring = input('Enter a Sudoku puzzle.\nDefault: 85...24..72......9..4.........1.7..23.5...9...4...........8..7..17..........36.4.\n')
			if not puzzlestring:
				puzzlestring = '85...24..72......9..4.........1.7..23.5...9...4...........8..7..17..........36.4.'
			if len(puzzlestring) == 81 and all(char in '0123456789.' for char in puzzlestring):
				self.parse_puzzle(puzzlestring)
				break
			else:
				print('Please enter a valid puzzle in Sudoku notation (dots or zeros for empty squares)')		
		print('Puzzle:')
		self.print_grid(self.puzzle)
		print('')
		state, result = self.constraint_prop(deepcopy(self.puzzle))
		if state == 'SOLVED':
			self.print_grid(self.solvedpuzzle)
			input(f'Solved with no need for guessing after {self.prop_steps} steps! Hit Enter to close.')
		else:
			afterexp = self.experiment(result, shuff=False)
			if not afterexp:
				input('Puzzle has no solution. Hit Enter to close.')
			else:
				self.print_grid(self.solvedpuzzle)
				input(f'Solved with guessing after {self.exp_steps} steps! Hit Enter to close.')

	def gen_valid_puzzle(self):
		print('Generating a valid Sudoku grid...')
		board = [[' ' for i in range(9)] for i in range(9)]
		result = self.experiment(board, shuff=True)
		print('DONE')
		self.result = result
		return result





t = SudokuGrid(clues=35)

'''
t.gen_valid_puzzle()
t.print_grid(t.result)
input('Enter to close')
'''


t.solve_puzzle()
input('Close?')






	










