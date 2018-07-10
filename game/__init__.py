from graphics import *
import time
import keyboard
import random
from sys import exit

scale = 32
targetFPS = 30
playingFieldOffsetTiles = 6

speed = 19 #0-indexed #speed of 20 (19) seems good
speedMultiplier = 0.9 #delay multiplied by this every time a line is collected

tilesHor = 10
tilesVer = 25

piecePreviewX = 2
piecePreviewY = -4

pieceStartingX = int((tilesHor-1)/2)
pieceStartingY = tilesVer - 5

playingFieldOffset = playingFieldOffsetTiles * scale

screenWidth = scale * tilesHor
screenHeight = scale * tilesVer + playingFieldOffset

w_pressed, a_pressed, s_pressed, d_pressed = False, False, False, False
frame = 0

allSquares = []

playingField = [0] * tilesVer
for i in range(tilesVer):
    playingField[i] = [0] * tilesHor

print('Playing field size: {},{}'.format(len(playingField), len(playingField[0])))

win = GraphWin(title='TETRIS', width=screenWidth, height=screenHeight)

def directionTranslate(direction):
    dx = 0; dy = 0
    if direction == 'up':
        dy = 1
    elif direction == 'left':
        dx = -1
    elif direction == 'down':
        dy = -1
    elif direction == 'right':
        dx = 1
    return dx, dy

def row(number):
    toPop = []
    for i in range(0, len(allSquares)):
        sq = allSquares[i]
        if sq.y == number:
            sq.object.undraw()
            toPop.append(i)
    for i in range(0, len(toPop)):
        allSquares.pop(toPop[i]-i)
    playingField[number] = [0] * tilesHor #reset the hit box
    for sq in allSquares:
        if sq.y > number:
            sq.move('down') #move tiles down

def gameOver():
    print('Game Over')
    win.close()
    sys.exit(0)

def drawGUI():
    gui = Rectangle(Point(0, tilesVer*scale), Point(tilesHor*scale, (tilesVer+playingFieldOffset)*scale))
    gui.setFill('black')
    gui.setOutline('black')
    gui.draw(win)

class square:
    width = scale
    height = scale
    def __init__(self, color, type, x, y, rotateAxis):
        self.x = x
        self.y = y
        if playingField[self.y][self.x] == 1 and type >= 0:
            gameOver()
        self.color = color
        self.rotateAxis = rotateAxis
        playingField[self.y][self.x] = 1
        self.generateObject(self.color)
        self.object.draw(win)
        allSquares.append(self)

    def generateObject(self, color):
        self.object = Rectangle(Point(self.x*square.width, screenHeight - self.y*square.height - playingFieldOffset), Point((self.x+1)*square.width, screenHeight - (self.y+1)*square.height - playingFieldOffset))
        self.object.setFill(color)
    
    def move(self, direction):
        if direction == 'rotate':
            self.setField(0)
            rotateAxis = self.rotateAxis
            dx = rotateAxis[0]; dy = rotateAxis[1]
            self.x += -dx + dy
            self.y += -dx - dy
            self.rotateAxis = [dy, -dx]
            self.setField(1)
        else:
            self.object.undraw()
            playingField[self.y][self.x] = 0
            if direction == 'up':
                self.y += 1
            elif direction == 'left':
                self.x -= 1
            elif direction == 'down':
                self.y -= 1
            elif direction == 'right':
                self.x += 1
            playingField[self.y][self.x] = 1
            self.generateObject(self.color)
            self.object.draw(win)

    def setField(self, state=1):
        playingField[self.y][self.x] = state

    def canMove(self, direction, others):
        if direction == 'rotate':
            rotateAxis = self.rotateAxis
            dx = rotateAxis[0]; dy = rotateAxis[1]
            toCheck = [self.y -dy - dx, self.x -dx + dy]
            if toCheck[0]<0 or toCheck[0] >= tilesVer or toCheck[1]<0 or toCheck[1] >=tilesHor:
                return False
            else:
                if playingField[toCheck[0]][toCheck[1]] == 1:
                    canMove = False
                    for sq in others:
                        if toCheck == [sq.y, sq.x]:
                            canMove = True
                    return canMove
                return True
        else:
            if direction == 'left' and self.x < 1 or direction == 'right' and self.x >= tilesHor - 1: #horizontal
                return False
            if direction == 'up' and self.y >= tilesVer - 1 or direction == 'down' and self.y < 1: #vertical
                return False
            dx, dy = directionTranslate(direction)
            toCheck = [self.y+dy, self.x+dx]
            if playingField[toCheck[0]][toCheck[1]] == 1:
                canMove = False
                for sq in others:
                    if toCheck == [sq.y, sq.x]:
                        canMove = True
                return canMove
            return True

class shape:
    pieces = [
        ['red',[0,0],[1,0],[0,1],[1,1]], #square
        ['blue',[0,0],[1,0],[0,1],[0,2]], #l right
        ['blue',[1,0],[0,0],[1,1],[1,2]], #l left
        ['yellow',[-1,0],[0,0],[1,0],[0,1]], #t
        ['green',[0,0],[0,1],[0,2],[0,3]], #line
        ['orange', [0,0],[0,1],[1,0],[1,-1]], #s
        ['orange', [0,0],[0,-1],[1,0],[1,1]] #s-inv
        ]
    
    def __init__(self, type):
        self.isControlling = True
        self.type = type
        rnd = random.randrange(0, len(shape.pieces))
        if self.type < 0:
            self.piece = shape.pieces[rnd]
            self.type = rnd
        else:
            self.piece = shape.pieces[self.type]
        self.squares = []
        for i in range(1,len(self.piece)):
            if type < 0:
                self.squares.append(square(self.piece[0], type, self.piece[i][0] + piecePreviewX, self.piece[i][1] + piecePreviewY, self.piece[i]))
            else:
                self.squares.append(square(self.piece[0], type, self.piece[i][0] + pieceStartingX, self.piece[i][1] + pieceStartingY, self.piece[i]))
        
    def move(self, direction):
        if direction == 'rotate':
            if self.canRotate():
                for i in range(0,len(self.squares)):
                    sq = self.squares[i]
                    sq.move('rotate')#, self.piece[i+1])
                for sq in self.squares:
                    sq.setField()
                return True
            else:
                return False
        else:
            if self.canMove(direction):
                for sq in self.squares:
                    sq.move(direction)
                for sq in self.squares:
                    sq.setField()
                return True
            else:
                return False
    
    def canMove(self, direction):
        dx, dy = directionTranslate(direction)
        canMove = True
        for sq in self.squares:
            canMove = sq.canMove(direction, self.squares)
            if not canMove:
                return False
        return True

    def canRotate(self):
        canMove = True
        for i in range(0,len(self.squares)):
            sq = self.squares[i]
            canMove = sq.canMove('rotate', self.squares)
            if not canMove:
                return False
        return True

    def remove(self):
        for sq in self.squares:
            sq.object.undraw()
            #playingField[sq.y][sq.x] = 0

drawGUI()
s = shape(random.randrange(0, len(shape.pieces)))
p = shape(-1)
while True:
    frame = (frame+1)%int(speed+1)
    if frame == 0:
        hasMoved = s.move('down')
        if not hasMoved:
            #piece has landed, you lose control
            s.isControlling = False
            found = 0
            for i in range(0, len(playingField)):
                if playingField[i-found].count(1) == tilesHor:
                    row(i-found)
                    speed *= speedMultiplier
                    found += 1
    
    if not s.isControlling:
        p.remove()
        s = shape(p.type)
        p = shape(-1)
    if keyboard.is_pressed('w') and not w_pressed:
        s.move('rotate')
        w_pressed = True
    if not keyboard.is_pressed('w'):
        w_pressed = False
    if keyboard.is_pressed('a') and not a_pressed:
        s.move('left')
        a_pressed = True
    else:
        a_pressed = False
    if keyboard.is_pressed('s') and not s_pressed:
        hasMoved = s.move('down')
        if not hasMoved:
            #piece has landed, you lose control
            s.isControlling = False
            found = 0
            for i in range(0, len(playingField)):
                if playingField[i-found].count(1) == tilesHor:
                    row(i-found)
                    speed *= speedMultiplier
                    found += 1
        s_pressed = True
    else:
        s_pressed = False
    if keyboard.is_pressed('d') and not d_pressed:
        s.move('right')
        d_pressed = True
    else:
        d_pressed = False
        
    update(targetFPS) #update from the graphics api
