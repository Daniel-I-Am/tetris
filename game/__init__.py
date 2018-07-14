#imports
from random import randrange
from graphics import *
from keyboard import is_pressed

# variables
fieldSize = [10, 20] #0,0 top left x,y bottom right
field = [None] * fieldSize[1]
for i in range(0, fieldSize[1]):
	field[i] = [None] * fieldSize[0]
points = 0
pointsPerLine = 100
scale = 32
targetFPS = 30
frame = 0
maxFrame = 19
rotateButtonPressed = False

defaultColor = 'white' #background color of empty cells

startingLocation = [int((fieldSize[0]-1)/2), 4] #center 5 down from top
win = GraphWin(title="Tetris", width=fieldSize[0]*scale, height=fieldSize[1]*scale)

# classes
class GameOverError(Exception):
    pass

class shape:
	global field
	global fieldSize
	global win
	tiles = [
		#[color, [location relative to origin], [loc], [loc], ...],
		['red',[0,0],[1,0],[0,1],[1,1]], #square
		['blue',[0,0],[1,0],[0,1],[0,2]], #l right
		['blue',[1,0],[0,0],[1,1],[1,2]], #l left
		['yellow',[-1,0],[0,0],[1,0],[0,1]], #t
		['green',[0,-1],[0,0],[0,1],[0,2]], #line
		['orange', [0,0],[0,1],[1,0],[1,-1]], #s
		['orange', [0,0],[0,-1],[1,0],[1,1]] #s-inv
	]
	def __init__(self, type, location):
		self.type = list(map(lambda type : type if type >= 0 else randrange(0, len(shape.tiles)), [type]))[0]
		self.location = location
		self.tiles = shape.tiles[self.type][1:]
		self.color = shape.tiles[self.type][0]
		if self.canMove('none'):
			self.draw()
		else:
			raise GameOverError
		
	def move(self, direction):
		dx, dy = directionTranslate(direction)
		self.undraw()
		canMove = self.canMove(direction)
		if canMove:
			if direction == 'rotate_left':
				for i in range(0, len(self.tiles)):
					self.tiles[i] = [self.tiles[i][1], -self.tiles[i][0]]
			if direction == 'rotate_right':
				for i in range(0, len(self.tiles)):
					self.tiles[i] = [-self.tiles[i][1], self.tiles[i][0]]
			else:
				self.location = [self.location[0] + dx, self.location[1] + dy]
		self.draw()
		return canMove
			
	def canMove(self, direction):
		if direction == 'rotate_right' or direction == 'rotate_left':
			for i in range(0, len(self.tiles)):
				if direction == 'rotate_left':
					loc = [self.location[0] + self.tiles[i][1], self.location[1] - self.tiles[i][0]]
				else:
					loc = [self.location[0] - self.tiles[i][1], self.location[1] + self.tiles[i][0]]
				if loc[0] < 0 or loc[0] > fieldSize[0]-1 or loc[1] < 0 or loc[1] > fieldSize[1]-1:
					return False
				if field[loc[1]][loc[0]]['color'] != defaultColor:
					return False
			return True
		else:
			dx, dy = directionTranslate(direction)
			for sq in self.tiles:
				loc = [self.location[0] + sq[0] + dx, self.location[1] + sq[1] + dy]
				if loc[0] < 0 or loc[0] > fieldSize[0]-1 or loc[1] < 0 or loc[1] > fieldSize[1]-1:
					return False
				if field[loc[1]][loc[0]]['color'] != defaultColor:
					return False
			return True
		return False
	
	def draw(self):
		for sq in self.tiles:
			field[self.location[1]+sq[1]][self.location[0]+sq[0]]['color'] = self.color
			field[self.location[1]+sq[1]][self.location[0]+sq[0]]['object'].undraw()
			field[self.location[1]+sq[1]][self.location[0]+sq[0]]['object'].setFill(self.color)
			field[self.location[1]+sq[1]][self.location[0]+sq[0]]['object'].draw(win)
	
	def undraw(self):
		for sq in self.tiles:
			field[self.location[1]+sq[1]][self.location[0]+sq[0]]['color'] = defaultColor
			field[self.location[1]+sq[1]][self.location[0]+sq[0]]['object'].undraw()
			field[self.location[1]+sq[1]][self.location[0]+sq[0]]['object'].setFill(defaultColor)
			field[self.location[1]+sq[1]][self.location[0]+sq[0]]['object'].draw(win)

# global methods
def directionTranslate(direction):
    dx = 0; dy = 0
    if direction == 'up':
        dy = -1
    elif direction == 'down':
        dy = 1
    elif direction == 'left':
        dx = -1
    elif direction == 'right':
        dx = 1
    return dx, dy

def makeField():
	global field
	global fieldSize
	global defaultColor
	for y in range(0, fieldSize[1]):
		for x in range(0, fieldSize[0]):
			field[y][x] = {'color': defaultColor, 'object': Rectangle(Point(x*scale,y*scale), Point((x+1)*scale-1,(y+1)*scale-1))}
			field[y][x]['object'].setOutline('black')
			field[y][x]['object'].setFill(defaultColor)
			field[y][x]['object'].draw(win)

def score(amount):
	if amount == 0:
		return
	global points
	scored = pointsPerLine * pow(2, amount-1)
	points += scored
	print('scored {} points, total: {}'.format(scored, points))

# main code
try:
	makeField()
	s = shape(-1, startingLocation)
	while True:
		frame = frame % maxFrame
		if frame == 0: #run once every `maxFrame` frames
			if s.move('down') != True: #tick down and check if should stop
				linesCleared = 0
				#done moving, so check for lines that are done
				for y in range(0, fieldSize[1]):
					isLine = True
					for x in range(0, fieldSize[0]):
						if field[y][x]['color'] == defaultColor:
							isLine = False
					if isLine:
						linesCleared += 1
						print('found a line')
						#all lines above this point need to be copied down one
						for _y in range(y, 1, -1):
							print('moving line {} down'.format(_y))
							for x in range(0, fieldSize[0]):
								field[_y][x]['object'].undraw()
								field[_y][x]['object'].setFill(field[_y-1][x]['color'])
								field[_y][x]['color'] = field[_y-1][x]['color']
								field[_y][x]['object'].draw(win)
						for x in range(0, fieldSize[0]):
							field[0][x]['object'].undraw()
							field[_y][x]['object'].setFill(defaultColor)
							field[0][x]['color'] = defaultColor
							field[0][x]['object'].draw(win)
				score(linesCleared)
				s = shape(-1, startingLocation) #remove control and spawn a new piece
				
		#user input
		if is_pressed('q') and not rotateButtonPressed:
			s.move('rotate_left')
			rotateButtonPressed = True
		if is_pressed('e') and not rotateButtonPressed:
			s.move('rotate_right')
			rotateButtonPressed = True
		if is_pressed('s'):
			s.move('down')
		if is_pressed('a'):
			s.move('left')
		if is_pressed('d'):
			s.move('right')
		if is_pressed('p') and not pausedButtonPressed:
			pausedButtonPressed = True
			while is_pressed('p'): #loop until you un-press
				update(targetFPS)
			while not is_pressed('p'): #loop until you re-press
				update(targetFPS)
		
		if not is_pressed('q') and not is_pressed('e'):
			rotateButtonPressed = False
		if not is_pressed('p'):
			pausedButtonPressed = False
		
		frame += 1
		update(targetFPS)
except GraphicsError:
	print('Window closed. Goodbye')
except GameOverError:
	print('Game Over')
	win.close() #close window
sys.exit(0) #properly exit program
