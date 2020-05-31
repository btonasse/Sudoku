from random import randint, choice
from copy import deepcopy


class SudokuGrid():
	'''
	Sudoku board.
	Attributes:
	width = size of the board - defaults to 3.
	emptycells = With how many empty cells the program should try to generate the puzzle.
	rows = List of 9 lists of 9 values. The root from which the grid is built.
	cols = List of 9 lists of 9 values. Derived from rows.
	regions = List of 9 lists of 9 values. Derived from rows.
	coordregs = Same as above but stores the coordinates of each cell in tuple form.
	coord_dict = Dictionary of coordinates (keys) and values.
	result = the final resolved board
	Standalone methods:
	print_grid(): Prints the grid to the console, taking the rows attribute as argument.
	printable_coords(): Returns a list of rows where the values have been replaced by their coordinates
		in symmetric fashion. Pass it to the method above to have a pretty grid of coordinates printed.
	populate_grid(): Populates a grid with the argument passed- usually a character - and prints it. Returns a list of rows of identical contents.
		Optionally accepts 'rand' to randomize the board (ignoring sudoku rules) or 'clear' to clear it.
	'''

	def __init__(self, width=3, clues=35):
		self.width = width
		self.clues = clues
		self.rows = self.build_rows()
		self.cols = self.build_cols(self.rows)
		self.regions = self.build_regions(self.rows)
		self.coordregs = self.build_coords(self.rows)
		self.coord_dict = self.build_coord_dict(self.coordregs, self.regions)
		self.pop_valid_board()
		self.result = self.rows

		self.puzzle = self.propose_puzzle(self.result, self.clues)
		self.solvestate, self.attempts, self.puzzlestate, self.printable = self.constraint_solve(self.puzzle)

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

	def printable_possibles(self, possibles): 
		'''
		blbalba
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
		if first_time:
			print(f'Generating a valid board...', end='')
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
		print('DONE.')
	
	def propose_puzzle(self, prows, clues = 17): #the minimum squares necessary for a unique solution
		print(f'Proposing a puzzle with {clues} clues...', end='')
		puzzle = self.populate_grid()
		while sum(x.count(' ') for x in puzzle) > (81-clues): 
			r = randint(0,8)
			c = randint(0,8)
			puzzle[r][c] = prows[r][c]
		print('DONE.')
		return puzzle

	def constraint_solve(self, puzzle, times=0, oldprows=[[]]):
		prows = deepcopy(puzzle)
		pcols = self.build_cols(prows)
		pregions = self.build_regions(prows)
		
		pcoordregs = self.build_coords(prows)
		pcoord_dict = self.build_coord_dict(pcoordregs, pregions)
		regpossibles = deepcopy(pcoord_dict)

		#print(f'times: {times}')

		for i, dic in enumerate(regpossibles):
			for r, c in dic.keys():
				if isinstance(dic[r,c], int):
					continue 
				dic[r,c] = [number for number in range(1,self.width*3+1) if number not in (prows[r]+pcols[c]+pregions[i]) and number not in dic]

		for dic in regpossibles:
			l = [item for sublist in dic.values() if isinstance(sublist, list) for item in sublist]
			for r, c in dic.keys():
				if isinstance(dic[r,c], int):
					continue
				if len(dic[r,c]) == 1:
					dic[r,c] = dic[r,c][0]
					prows[r][c] = dic[r,c]
				if isinstance(dic[r,c], list):
					for number in dic[r,c]:
						if l.count(number) == 1:
							dic[r,c] = number
							prows[r][c] = number
		
		printable = [[str(value) for value in dic.values()] for dic in regpossibles]
		for sublist in printable:
			for i, item in enumerate(sublist):
				sublist[i] = item.replace(', ','').strip('[]')
		printable = self.printable_possibles(printable)	

		while True:
			if prows == oldprows:
				#print('Cannot solve further')
				return 'INCOMPLETE', times, prows, printable
			for dic in regpossibles:
				if any(cell == [] for cell in dic.values()):
					#print('Contradiction found.')
					return False, times, puzzle, False
			for i, row in enumerate(prows):
				if not all(type(cell) is int for cell in row):
					break
				else:
					if i < 8:
						continue
					else:
						pass
				#print('Puzzle solved')
				return 'SOLVED', times, prows, False
			break
		
		oldprows = prows
		return self.constraint_solve(prows, times=times+1, oldprows=prows)
		

	#attempts will be used to determine level of the puzzle			
	
	#Now implement the next step: trying one possibility and see if it works.	

	#Do a version of printable_coords for regpossibles so the return 'incomplete' returns it and can be used by next function	

			

t = SudokuGrid(clues=35)

print('')
print('------Final result------')
t.print_grid(t.result)
print('')
print('-----Proposed puzzle----')
t.print_grid(t.puzzle)
print('')
print('------Puzzle state------', f'Constraint propagation attempts: {t.attempts}', f'Solve state: {t.solvestate}', sep='\n')
t.print_grid(t.puzzlestate)
print('')
if t.printable:
	print('-----Possible numbers----')
	t.print_grid(t.printable)
print('')











	











