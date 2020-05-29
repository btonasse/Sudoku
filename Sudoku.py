from random import randint, choice
from copy import deepcopy


class SudokuGrid():
	'''
	Sudoku board.
	Attributes:
	width = size of the board - defaults to 3.
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

	def __init__(self, width=3, **kwargs):
		self.width = width
		self.rows = self.build_rows()
		self.cols = self.build_cols(self.rows)
		self.regions = self.build_regions(self.rows)
		self.coordregs = self.build_coords(self.rows)
		self.coord_dict = self.build_coord_dict(self.coordregs, self.regions)
		self.pop_valid_board()
		self.result = self.rows
		self.build_puzzle(self.result)

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
			self.print_grid(rows)
		elif val == 'clear' or not val:
			rows = self.build_rows(defval=' ')
			self.print_grid(rows)
		else:
			rows = self.build_rows(defval=val)
			self.print_grid(rows)
		return rows

	def pop_valid_board(self, first_time=True, last_valid_region=0):
		if first_time:
			print('Generating a valid board...')
			#self.populate_grid('')
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
				valids = [number for number in range(1,self.width*3+1)]
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

	def remove_randcell(self, rows, howmany=1): 
		newrows = deepcopy(rows)
		for i in range(howmany):
			while True:
				r = randint(0,8)
				c = randint(0,8)
				if newrows[r][c] == ' ':
					continue
				else:
					newrows[r][c] = ' '
					break
		return newrows

	def solve(self, rows, solutions=[], tries=0):
		rowscopy = deepcopy(rows)
		colscopy = self.build_cols(rows)
		regionscopy = self.build_regions(rows)
		coordregscopy = self.build_coords(rows)
		coord_dictcopy = self.build_coord_dict(coordregscopy, regionscopy)
		solutions.append({}) # list of solutions.
		correct_cells = solutions

		for i, dic in enumerate(coord_dictcopy):
			for r, c in dic.keys():
				if dic[r,c] != ' ':
					continue
				valids = [number for number in range(1,self.width*3+1)]
				while True:
					try:
						n = choice(valids)
					except IndexError:
						self.solve(rows)
						return
					if n in (rowscopy[r]+colscopy[c]+regionscopy[i]):
						valids.remove(n)
						continue
					else:
						rowscopy[r][c] = n
						correct_cells[tries][r,c] = n
						colscopy = self.build_cols(rowscopy)
						regionscopy = self.build_regions(rowscopy)
						coordregscopy = self.build_coords(rowscopy)
						coord_dictcopy = self.build_coord_dict(coordregscopy, regionscopy)
						break
		if tries > 0:
			if correct_cells[tries] == correct_cells[tries-1]:
				correct_cells.pop()
				return
			else:
				self.build_puzzle(rows, correct_cells, tries+1, first_time=False)
		self.solve(rows, solutions=correct_cells, tries=tries+1)
		return 

	def build_puzzle(self, rows, solutions=[], tries=0, first_time=True):
		if first_time:
			newrows = self.remove_randcell(rows, howmany=1)
		elif tries == 0:
			newrows = self.remove_randcell(rows)
		self.solve(newrows, solutions, tries)
		no_of_solutions = len(solutions)
		if no_of_solutions > 1:
			return
		else:
			self.puzzle = newrows
			self.build_puzzle(newrows, solutions=[], tries=0, first_time=False)














			

t = SudokuGrid()

t.print_grid(t.puzzle)
t.print_grid(t.result)












	











