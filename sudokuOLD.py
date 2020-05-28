from random import randint
from copy import deepcopy

#only thing missing: implement check for unique cols
#actually now that checks are being made, the checks only work in a 3x3 grid, which is ok, honestly.

class SudokuGrid():
	def __init__(self, width, **kwargs):
		self.width = width
		self.regno = width*width
		#self.rows = self.build_rows(self.width) #use this attribute to access specific coordinates
		#self.cols = self.build_cols(self.rows)
		self.rows = self.one_by_one(width)
		#self.coords = self.build_coords(self.rows)
		self.print_grid(self.rows)
		#self.print_grid(self.coords)
		#self.coord_dict = self.build_coord_dict(self.rows,self.coords)

	def start_new_row(self, cols, rows, roffset=0, coffset=0): #
		r = rows
		c = cols
		success = 0
		while success < 3: 
			success = 0
			nextreg = self.build_reg()
			for i, row in enumerate(nextreg):
				if row[0] in c[0]:
					break
				elif row[1] in c[1]:
					break
				elif row[2] in c[2]:
					break
				else:
					success += 1
		return nextreg

	
	def new_reg_two_neighbors(self, cols, rows, roffset=0, coffset=0):
		r = rows
		c = cols
		success = 0
		while success < 3: 
			success = 0
			nextreg = self.build_reg()
			for i, row in enumerate(nextreg):
				if row[0] in c[3+(roffset*3)]:
					break
				elif row[1] in c[4+(roffset*3)]:
					break
				elif row[2] in c[5+(roffset*3)]:
					break
				if any(item in r[3+i+(coffset*3)] for item in row):
					break
				else:
					success += 1
		return nextreg			
				

	def one_by_one(self, width):
		firstregs = self.build_rows(width, once=True)
		rows = [[item for item in row] for row in firstregs]
		cols = [[row[i] for row in rows[:3]] for i in range(9)]
		added_regs = 0
		
		
		nextreg = self.start_new_row(cols,rows) #LEFT
		added_regs += 1
		
		for r in range(3): #LEFT
			rows[r+3].extend(nextreg[r])
			for c in nextreg:
				cols[r].append(c[r])

		nextreg = self.new_reg_two_neighbors(cols,rows) #MIDDLE
		added_regs += 1

		for r in range(3): #MIDDLE
			rows[r+3].extend(nextreg[r])
			for c in nextreg:
				cols[r+3].append(c[r])

		nextreg = self.new_reg_two_neighbors(cols,rows, roffset=1) #RIGHT
		added_regs += 1

		for r in range(3): #RIGHT
			rows[r+3].extend(nextreg[r])
			for c in nextreg:
				cols[r+6].append(c[r])

		nextreg = self.start_new_row(cols,rows) #BOTLEFT
		added_regs += 1

		for r in range(3): #BOTLEFT
			rows[r+6].extend(nextreg[r])
			for c in nextreg:
				cols[r].append(c[r])

		nextreg = self.new_reg_two_neighbors(cols,rows, coffset=1) #BOTTOM
		added_regs += 1

		for r in range(3): #BOTTOM
			rows[r+6].extend(nextreg[r])
			for c in nextreg:
				cols[r+3].append(c[r])	

		#nextreg = self.new_reg_two_neighbors(cols,rows, roffset=1, coffset=1) #BOTRIGHT
		#added_regs += 1

		#for r in range(3): #BOTRIGHT
		#	rows[r+6].extend(nextreg[r])
		#	for c in nextreg:
		#		cols[r+6].append(c[r])	


		#print(rows,'\n')
		#print(cols,'\n')

		#for i in range(3):
		#	print(nextreg[i])

		return rows


		

	
	def build_reg(self): 
		'''
		Builds each region of sudoku as a list of 3 rows. Each region has unique numbers.
		'''
		check = set()
		region = []
		for r in range(3): 
			row = []
			for c in range(3): 
				chklen = len(check)
				while chklen == len(check):
					#n = randint(1,self.width*3)
					n = randint(1,9) #extending the range (in case of larger grid) takes too long to compute (too many useless loops). Better to take each region and only insert the next if it fits.
					check.add(n)
				row.append(n) 
			region.append(row)
		return region

	
	def build_outrow(self,width):
		outrow = []
		for c in range(width):
			outrow.append(self.build_reg())
		return outrow
	

	
	def build_rows(self, width, once=False):
		if once:
			itme = 1
		else:
			itme = width

		rowsets = [set() for times in range(width*3)] 
		colsets = [set() for times in range(width*3)]

		finalrowlist = []
		for row in range(width*3):
			finalrowlist.append([])

		Y = 0
		for x in range(itme):
			print(f'Loading row of regions from index Y = {Y} to {Y+2}...')
			while len(rowsets[Y]) < width*3 or len(rowsets[Y+1]) < width*3 or len(rowsets[Y+2]) < width*3: 
				rowsets = [set() for times in range(width*3)]
				rowlist = []
				for row in range(width*3):
					rowlist.append([])

				outrow = self.build_outrow(width)
				for tc, mc, bc in outrow:
					rowsets[Y] |= set(tc)
					rowlist[Y].extend(tc)
					rowsets[Y+1] |= set(mc)
					rowlist[Y+1].extend(mc)
					rowsets[Y+2] |= set(bc)
					rowlist[Y+2].extend(bc)
			finalrowlist[Y] = deepcopy(rowlist[Y])
			finalrowlist[Y+1] = deepcopy(rowlist[Y+1])
			finalrowlist[Y+2] = deepcopy(rowlist[Y+2])
			print(f'The three rows of Y index {Y} to {Y+2} are:')
			for index in range(Y,Y+3):
				print(finalrowlist[index])
			print('')
			Y += 3
		return finalrowlist
	
	'''
	def build_cols(self, rows):
		
		Builds a list of x columns (x=width*3) from the rows generated by the above method. Used when building the grid coordinates.
		
		colslist = []
		for col in range(self.width*3): #initializes list of cols
			colslist.append([])
		for row in rows:
			colindex = 0
			for col in row:
				colslist[colindex].append(col)
				colindex += 1
		return colslist
	'''

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

	def build_coords(self, rows): 
		'''
		Replaces the values populated on the grid by their coordinates. Returns a list of rows - much like build_rows().
		For widths or heights larger than 3, zeroes are inserted before the relevant coordinates to ensure symmetry.
		'''
		rowscopy = deepcopy(rows)
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

	def build_coord_dict(self,rows,coords):
		'''
		Builds a dictionary, where keys are the coordinates built by build_coords(), and values are the actual values originally populated on the grid.
		'''
		coord_dict = {}
		for row in range(self.width*3):
			for col in range(self.width*3):
				coord_dict[coords[row][col]] = rows[row][col]
		return coord_dict

			

test = SudokuGrid(3)
#test.print_grid(test.rows)
#test.print_grid(test.coords)
#print(test.coord_dict)


	











