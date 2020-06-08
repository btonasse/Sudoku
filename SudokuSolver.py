from copy import deepcopy

def parse_puzzle(puzzlestring):
	'''
	Parses sudoku notation into a processable puzzle format
	Easy puzzle: '003020600900305001001806400008102900700000008006708200002609500800203009005010300'
	Hard: '85...24..72......9..4.........1.7..23.5...9...4...........8..7..17..........36.4.'
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
	return puzzle

def print_grid(puzzle):
	'''
	Pretty prints the grid using a list of puzzle.
	'''
	rowstr = ''.join(map(str, puzzle[0]))
	cellen = len(rowstr)//(9)
	regsep = ('+' + ('-'*(cellen*3)) + ('----'))*3 + '+'

	print(regsep)
	for y in range(0,9,3):
		for row in puzzle[y:y+3]:
			print('| ', end='')
			for x in range(0,9,3):
				print(*row[x:x+3], '| ', end='')
			print('')
		print(regsep)

def printable_possibles(possibles): 
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

def is_possible(puzzle, r, c, n):
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

def gen_possibles(puzzle):
	'''
	Generates a list of possible numbers for each square. rpf/cpf/regpf are flattened versions of this list organized by columns/regions, to be used with constraint propagation strategy 2.
	'''
	rp = [[[] for i in range(9)] for i in range(9)]
	for r, row in enumerate(puzzle):
		for c, col in enumerate(row):
			if col == ' ':
				for n in range(1,10):
					if is_possible(puzzle, r, c, n):
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

def constraint_prop(puzzle, oldrows=[[]]):
	rp, rpf, cpf, regpf = gen_possibles(puzzle)
	for i, r in enumerate(rp):   #Strategy 1
		for I, c in enumerate(r):
			if c == []:
				print(f"No solution possible! No valid numbers for square {i}{I}.")
				print_grid(puzzle)
				print_grid(printable_possibles(rp))
				#input('Hit Enter to close')
				return False, puzzle
			if type(c) is list and len(c) == 1 and is_possible(puzzle, i, I, c[0]):
				puzzle[i][I] = c[0]
				rp[i][I] = c[0]
				continue
	
	rp, rpf, cpf, regpf = gen_possibles(puzzle)
	for i, r in enumerate(rp):  #Strategy 2
		for I, c in enumerate(r):
			if type(c) is list:
				for n in c:
					if rpf[i].count(n) == 1 or cpf[I].count(n) == 1 or regpf[I//3+3*(i//3)].count(n) == 1 and is_possible(puzzle, i, I, n):
						puzzle[i][I] = n
						rp[i][I] = n
						break
	
	rp, rpf, cpf, regpf = gen_possibles(puzzle)						
	if not any([any([cell == ' ' for cell in row]) for row in puzzle]): #Checking if puzzle solved
		print('SOLVED!')
		print_grid(puzzle)
		print('*')
		#input('Hit Enter to close')
		return 'SOLVED', puzzle
	elif puzzle == oldrows:  #No more propagation possible
		print('Partial solution')
		print_grid(puzzle)
		print_grid(printable_possibles(rp))
		print('*')
		return 'INCOMPLETE', puzzle
	else:
		print('Puzzle still incomplete:')
		print_grid(puzzle)
		print_grid(printable_possibles(rp))
		print('Trying one more propagation step...', end='\n\n')
		#input('More?')
		return constraint_prop(puzzle, oldrows=puzzle)

def experiment(puzzle):
	global x  #temporary solution for my inability of returning the damn complete puzzle.
	rp, rpf, cpf, regpf = gen_possibles(puzzle)
	for i, row in enumerate(puzzle):
		for I, col in enumerate(row):
			if col == ' ':
				for n in rp[i][I]:
					oldpuzzle = deepcopy(puzzle)
					puzzle[i][I] = n
					solvestate, puzzle = constraint_prop(puzzle)
					if solvestate == 'INCOMPLETE':
						experiment(puzzle)
					elif solvestate == 'SOLVED':
						x = puzzle
						print_grid(puzzle)
						input('Puzzle solved! Hit Enter to close')
						return puzzle
					puzzle = deepcopy(oldpuzzle)
				return puzzle
	#return oldpuzzle








puzzle = parse_puzzle('85...24..72......9..4.........1.7..23.5...9...4...........8..7..17..........36.4.')
print('Puzzle:')
print_grid(puzzle)
print('')
state, result = constraint_prop(puzzle)
if state == 'INCOMPLETE':
	y = experiment(result)
print(x)
print(y)
input('Exiting...')
