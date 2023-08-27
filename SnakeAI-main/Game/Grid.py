from Game.Point import Point,PointType
import random
import time
from enum import Enum
import numpy as np

class Direction(Enum):
    UP = 1
    RIGHT = 2
    DOWN = 3
    LEFT = 4

    #Returns the direction opposite the input
    @classmethod
    def reverse(self, direction):
        match direction:
            case Direction.UP:
                return Direction.DOWN
            case Direction.RIGHT:
                return Direction.LEFT
            case Direction.DOWN:
                return Direction.UP
            case Direction.LEFT:
                return Direction.RIGHT
            case _:
                print("Some unforseen cataclysm has occured.")
                raise RuntimeError
    
    #Returns the direction clockwise from the input
    @classmethod
    def rotateCW(self, direction):
        match direction:
            case Direction.UP:
                return Direction.RIGHT
            case Direction.RIGHT:
                return Direction.DOWN
            case Direction.DOWN:
                return Direction.LEFT
            case Direction.LEFT:
                return Direction.UP
            case _:
                print("Some unforseen cataclysm has occured.")
                raise RuntimeError

    #Returns the direction counterclockwise from the input
    @classmethod
    def rotateCCW(self, direction):
        match direction:
            case Direction.UP:
                return Direction.LEFT
            case Direction.LEFT:
                return Direction.DOWN
            case Direction.DOWN:
                return Direction.RIGHT
            case Direction.RIGHT:
                return Direction.UP
            case _:
                print("Some unforseen cataclysm has occured.")
                raise RuntimeError

    #Returns an offset for points on a grid. ex: the point 'up' is 1 above, and 0 to the sides
    @classmethod
    def getOffset(self, direction):
        match direction:
            case Direction.UP:
                return [1, 0]
            case Direction.RIGHT:
                return [0, 1]
            case Direction.DOWN:
                return [-1, 0]
            case Direction.LEFT:
                return [0, -1]
            case _:
                print("Some unforseen cataclysm has occured.")
                raise RuntimeError


class Grid:
    def __init__(self, cols, rows, agent):
        self.colNum = cols
        self.rowNum = rows
        self.numPoints = self.colNum * self.rowNum
        self.points = [[Point(PointType.EMPTY, x, y) for x in range(0, cols)] for y in range(0, rows)] #Initialize all points as empty
        self.snake = None
        self.food = None
        self.agent = agent
        self.gameRunning = False
    

    def Setup(self):
        #Setting up point types
        for x in range(0, self.colNum):
            for y in range(0, self.rowNum):
                if(x == 0 or x == self.colNum-1)or(y == 0 or y == self.rowNum-1):
                    self.points[y][x].SetType(PointType.WALL) #Set border points as walls
                else:
                    self.points[y][x].SetType(PointType.EMPTY) #Set other points as empty

        #Placing snake in center of board, and then placing food
        headX = self.colNum//2
        headY = self.rowNum//2
        self.PlaceSnake(4, [headX, headY], Direction.UP)
        self.placeRandomFood()

    #Starts the game loop, which lasts until the snake dies.
    def startLoopNoGUI(self):
        self.gameRunning = True
        while(self.gameRunning):
            self.gameLoop()
    
    #Returns the integer value of a point
    def getPointType(self, point):
        return point.GetType().value
    
    #Returns a 1d array of all points on the grid, represented as their integer values
    #Could be used as NN input, currently unused as it needs a very large input layer.
    def flattenGrid(self):
        flat = np.array(self.points)
        flat = flat.flatten()
        out = np.vectorize(self.getPointType)(flat)
        return out

    #Resets the board to be ready for antoher without needing the slow Setup()
    def reset(self):
        #Clears the snake and remaining food
        if(self.snake != None):
            while(self.snake.body):
                point = self.snake.body.pop()
                point.SetType(PointType.EMPTY)
        if(self.food != None):
            self.food.SetType(PointType.EMPTY)
        self.snake = None
        self.food = None
        
        #Placeing new snake and food
        headX = self.colNum//2
        headY = self.rowNum//2
        self.PlaceSnake(4, [headX, headY], Direction.UP)
        self.placeRandomFood()

    #Called whenever a snake dies, currently just stops the gameLoop
    def GameOver(self):
        self.gameRunning = False
        #Potentially do other stuff

    #Calls the agent to choose and make a move, updating the state of the grid.
    #If GUI is used, will be updated to reflect change.
    def gameLoop(self):
        self.agent.MakeMove(self)

    #Creates and tracks a snake object, placing it on the board
    def PlaceSnake(self, size, position, heading):
        from Game.Snake import Snake
        self.snake = Snake(self, size, heading)
        self.snake.BuildBody(position, heading)

    #Returns the point at the given coordinates
    def getPoint(self, x, y):
        return self.points[y][x]

    #Returns the point adjacent to the given point, in the given direction
    def getAdjPoint(self, point, direction):
        x, y = point.GetPosition()
        offset = Direction.getOffset(direction)
        return self.points[y+offset[0]][x+offset[1]]
    
    #Returns a list of empty points
    #NOTE: Could be optimized, rather than building the list, start a list in Setup()
    #Add and remove points from the empty list as the snake moves and food is eaten/placed
    #Simply get that list when needed
    def getEmptyPoints(self):
        freePoints = []
        for x in range(0, self.colNum):
            for y in range(0, self.rowNum):
                point = self.points[y][x]
                if(point.GetType() == PointType.EMPTY):
                    freePoints.append(point)
        return freePoints
    
    #Returns an array of information about the game to be fed into AIAgent models
    #Currently includes: Position of head, current direction, distance and type of points forward, to the left, and right, the size of the snake, food position, manhattan distance from head to food 
    def getState(self):
        snake = self.snake
        food = self.food
        heading = snake.heading
        headPos = snake.head.GetPosition()
        
        foodPos = food.GetPosition()

        lookLeft = snake.Look(Direction.rotateCCW(heading))
        lookForward = snake.Look(heading)
        lookRight = snake.Look(Direction.rotateCW(heading))

        state = np.asarray([headPos[0],
                            headPos[1],
                            heading.value,

                            lookLeft[0],
                            lookLeft[1],
                            lookForward[0],
                            lookForward[1],
                            lookRight[0],
                            lookRight[1],

                            snake.bodySize,
                            foodPos[0],
                            foodPos[1],
                            self.GetDistance(snake.head, food)
                            ])

        return state

    #Returns the manhattan distance between 2 points
    def GetDistance(self, point1, point2):
        x1 = point1.x
        y1 = point1.y

        x2 = point2.x
        y2 = point2.y

        distance = abs(x1-x2) + abs(y1-y2)
        return distance


    #Places food in a random empty space
    def placeRandomFood(self):
        freePoints = self.getEmptyPoints()
        if(freePoints):
            point = random.choice(freePoints)
            point.SetType(PointType.FOOD)
            self.food = point
        else:
            #A perfect game has somehow been played
            #TODO: What to do here?
            pass

    #Places food at a given coordinate, if it is empty
    #Returns true or false depending on if food was successfully placed or not
    def placeFoodAt(self, position):
        point = self.points[position[0]][position[1]]
        if(point.GetType() != PointType.EMPTY):
            return False
        point.SetType(PointType.FOOD)
        self.food = point
        return True

    
