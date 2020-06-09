from random import randint, choice
from copy import deepcopy


class SudokuGrid():
	'''
	Sudoku board.
	Attributes:
	width = size of the board - defaults to 3.
	clues = how many clues should a proposed puzzle have
	rows = List of 9 lists of 9 values. The root from which the grid is built.
	cols = List of 9 lists of 9 values. Derived from rows.
	regions = List of 9 lists of 9 values. Derived from rows.
	coordregs = Same as above but stores the coordinates of each cell in tuple form.
	coord_dict = Dictionary of coordinates (keys) and values.
	result = the final resolved board
	puzzle = a proposed puzzle
	printable = list of possible numbers for each square in printable format
	solvestate = current state of the solve attempt (SOLVED, INCOMPLETE or None)
	prrop_attempts = current number of iterations the solver took so far. Helps determining level of puzzle.
	puzzlestate = current state of the proposed puzzle during solving
	possibles = dictionary of possible numbers for each square;
	
	Standalone methods:
	print_grid(): Prints the grid to the console, taking the rows attribute as argument.
	printable_coords(): Returns a list of rows where the values have been replaced by their coordinates
		in symmetric fashion. Pass it to the method above to have a pretty grid of coordinates printed.
	populate_grid(): Populates a grid with the argument passed- usually a character - and prints it. Returns a list of rows of identical contents.
		Optionally accepts 'rand' to randomize the board (ignoring sudoku rules) or 'clear' to clear it.
	#put the rest here
	'''

	def __init__(self, width=3, clues=35):
		self.width = width
		self.clues = clues
		self.puzzle = None
		self.solvedpuzzle = None
	
		

	def build_rows(self, defval=' ', args=[], kwargs={}):
		'''
		Builds a list of x rows (x=width*3). Populates cells with empty string by default,
		but function can be called with a different function, such as randint(1,9).
		In this case, the function has to be called like this: self.build_rows(defval=randint,args=[1,9])
		'''	
		w = self.width*3
		rowlist = [[list() for i in range(w)] for i in range(w)]
		for r in range(w):
			for c in range(w):
				try:
					rowlist[r][c] = defval(*args, **kwargs)
				except:
					rowlist[r][c] = defval
		return rowlist

	def build_cols(self, rows):
		'''
		Builds a list of x columns (x=width*3) from the rows generated by the above method. Used when building the grid coordinates.
		'''		
		colslist = []
		for col in range(self.width*3): #initializes list of cols
			colslist.append([])
		for row in rows:
			colindex = 0
			for col in row:
				colslist[colindex].append(col)
				colindex += 1
		return colslist

	def build_regions(self, rows):
		reglist = [list() for _ in range(len(rows))] 
		for i in range(0,9,3):
			for row in rows[i:i+3]:
				x = 0
				for I in range(3):
					reglist[I+i].extend(row[x:x+3])
					x += 3
		return reglist

	def build_coords(self, rows): 
		'''
		Replaces the values populated on the grid by their coordinates. Returns a list of rows containing tuple pairs..
		'''
		rowscopy = deepcopy(rows)
		colscopy = self.build_cols(rowscopy)
		

		for row in rowscopy:
			for item in row:
				newtuple = tuple()
				icol = row.index(rowscopy[rowscopy.index(row)][row.index(item)])
				irow = rowscopy.index(row)
				newtuple = irow, icol
				rowscopy[rowscopy.index(row)][row.index(item)] = newtuple
		
		
		coordregs = self.build_regions(rowscopy)
		
		return coordregs

	def OLD_printable_possibles(self, possibles): 
		'''
		Formats the dictionary of possible numbers in a printable form
		to be displayed with self.print_grid()
		'''
		max_len = 1
		poscopy = deepcopy(possibles)
		
		for row in poscopy:
			for cell in row:
				max_len = max(max_len, len(cell))
		for I, row in enumerate(poscopy):
			for i, cell in enumerate(row):
				while len(cell) < max_len:
					cell = ' ' + cell
					poscopy[I][i] = cell
		return poscopy

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

	def printable_coords(self): 
		'''
		Replaces the values populated on the grid by their coordinates. Returns a list of rows - much like build_rows().
		For widths or heights larger than 3, zeroes are inserted before the relevant coordinates to ensure symmetry.
		'''
		rowscopy = deepcopy(self.rows)
		colscopy = self.build_cols(rowscopy)
		max_irow_len = len(str(self.width*3))
		max_icol_len = len(str(self.width*3))
		for row in rowscopy:
			for item in row:
				icol = str(row.index(rowscopy[rowscopy.index(row)][row.index(item)]))
				while len(icol) < max_icol_len:
					icol = '0' + icol
				irow = str(rowscopy.index(row))
				while len(irow) < max_irow_len:
					irow = '0' + irow
				rowscopy[rowscopy.index(row)][row.index(item)] = irow + icol

		return rowscopy

	def build_coord_dict(self, coordregs, regions):
		'''
		Builds a list of dictionaries where keys are the coordinates built by build_coords(),
		and values are the actual values originally populated on the grid. Each dictionary corresponds to one region.
		'''
		w = self.width*3
		coord_dict_reglist = []
		for i in range(w):
			d = dict(zip(coordregs[i], regions[i]))
			coord_dict_reglist.append(d)
		return coord_dict_reglist

	def print_grid(self, rows):
		'''
		Pretty prints the grid using a list of rows.
		'''
		rowstr = ''.join(map(str, rows[0]))
		cellen = len(rowstr)//(self.width*3)
		regsep = ('+' + ('-'*(cellen*3)) + ('----'))*self.width + '+'

		print(regsep)
		for y in range(0,self.width*3,3):
			for row in rows[y:y+3]:
				print('| ', end='')
				for x in range(0,self.width*3,3):
					print(*row[x:x+3], '| ', end='')
				print('')
			print(regsep)

	def populate_grid(self, val=' '):
		'''Populates a grid with a default value.
		Accepts keywords 'rand' (randomizes grid) and 'clear' (clears grid - the default).
		'''
		if val == 'rand':
			rows = self.build_rows(defval=randint,args=[1,9])
			#self.print_grid(rows)
		elif val == 'clear' or not val:
			rows = self.build_rows(defval=' ')
			#self.print_grid(rows)
		else:
			rows = self.build_rows(defval=val)
			#self.print_grid(rows)
		return rows

	def pop_valid_board(self, first_time=True, last_valid_region=0):
		'''
		Populates a valid Sudoku board. The final result is stored in self.result.
		'''
		if first_time:
			print(f'Generating a valid board...', end='')
			self.rows = self.build_rows()
			self.cols = self.build_cols(self.rows)
			self.regions = self.build_regions(self.rows)
			self.coordregs = self.build_coords(self.rows)
			self.coord_dict = self.build_coord_dict(self.coordregs, self.regions)
		for i, dic in enumerate(self.coord_dict):
			if i < last_valid_region:
				continue
			if i == last_valid_region:
				for times in range(3):
					for r, c in self.coord_dict[i+times].keys():
						self.rows[r][c] = ' '
						self.cols = self.build_cols(self.rows)
						self.regions = self.build_regions(self.rows)
						self.coordregs = self.build_coords(self.rows)
						self.coord_dict = self.build_coord_dict(self.coordregs, self.regions)
				
			for r, c in dic.keys():
				valids = [number for number in range(1,self.width*3+1) if number not in (self.rows[r]+self.cols[c]+self.regions[i])]
				while True:
					try:
						n = choice(valids)
					except IndexError:
						self.pop_valid_board(first_time=False, last_valid_region=max(i-2,0))
						return
					if n in (self.rows[r]+self.cols[c]+self.regions[i]):
						valids.remove(n)
						continue
					else:
						self.rows[r][c] = n
						self.cols = self.build_cols(self.rows)
						self.regions = self.build_regions(self.rows)
						self.coordregs = self.build_coords(self.rows)
						self.coord_dict = self.build_coord_dict(self.coordregs, self.regions)
						break
		self.result = self.rows
		print('DONE.')
	
	def propose_puzzle(self): 
		'''
		Creates an empty board and populates it with x (x=self.clues) random values from the generated board.
		17 is the minimum squares necessary for a puzzle to havea chance to be unique solution.
		'''
		print(f'Proposing a puzzle with {self.clues} clues...', end='')
		puzzle = self.populate_grid()
		while sum(x.count(' ') for x in puzzle) > (81-self.clues): 
			r = randint(0,8)
			c = randint(0,8)
			puzzle[r][c] = self.result[r][c]
		print('DONE.')
		self.puzzle = puzzle
		return puzzle

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
		return self.constraint_prop(puzzle, oldrows=deepcopy(puzzle))

	def experiment_new(self, puzzle):
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
		for n in rp[r][c]:
			oldpuzzle = deepcopy(puzzle)
			puzzle[r][c] = n
			solvestate, puzzle = self.constraint_prop(puzzle)
			if self.experiment_new(puzzle):
				return self.solvedpuzzle
			puzzle = deepcopy(oldpuzzle)
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
		state, result = self.constraint_prop(self.puzzle)
		if state == 'SOLVED':
			self.print_grid(self.solvedpuzzle)
			input('Solved with no need for guessing! Hit Enter to close.')
		else:
			afterexp = self.experiment_new(result)
			if not afterexp:
				input('Puzzle has no solution. Hit Enter to close.')
			else:
				self.print_grid(self.solvedpuzzle)
				input('Solved with guessing! Hit Enter to close.')





t = SudokuGrid(clues=35)

'''
t.pop_valid_board()
t.print_grid(t.result)
t.propose_puzzle()
t.print_grid(t.puzzle)
input('Enter to close')
'''


t.solve_puzzle()
input('Close?')






	











