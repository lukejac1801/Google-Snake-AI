from Game.Point import Point, PointType
from Game.Grid import Grid, Direction
from collections import deque
class Snake:
    
    def __init__(self, grid, startSize, heading):
        self.heading = heading
        self.bodySize = startSize
        self.grid = grid
        self.body = deque()
        self.heading = None
        self.head = None
    
    #Checks each point in a line from the snake head in a given direction.
    #When a non-empty point is encountered, the distance to that point and'
    #the type of point are returned as (Type, Dist). Type is an int corresponding
    #to the PointType enum.
    def Look(self, direction):
        lookedAt = self.grid.getAdjPoint(self.head, direction)
        dist = 1
        while(lookedAt.GetType() == PointType.EMPTY):
            lookedAt = self.grid.getAdjPoint(lookedAt, direction)
            dist += 1
        return (lookedAt.GetType().value, dist)

    #Builds the snake on the grid, with the head placed at the specified position
    #and facing in the direction. The rest of the body will be placed opposite the 
    #direction the head is facing. If a wall is encountered, the snake will curve to
    #compensate.
    def BuildBody(self, position, heading):
        
        #Placing the head
        curSegment = self.grid.getPoint(*position) 
        curSegment.SetType(PointType.HEAD)
        self.body.append(curSegment)
        self.head = curSegment
        self.heading = heading

        #Adding remainder of body off of head
        buildDir = Direction.reverse(heading)
        while(len(self.body) < self.bodySize):
            nextSegment = self.grid.getAdjPoint(curSegment, buildDir)
            
            #Turn if obstacle in way of body
            if(nextSegment.GetType() != PointType.EMPTY):
                buildDir = Direction.rotateCW(buildDir)
            else:
                curSegment = nextSegment
                curSegment.SetType(PointType.BODY)
                self.body.append(curSegment)
            
    
    #Moves in the direction the snake is currently facing, and detects if food 
    #was eaten or a wall was hit. The snake body will update accordingly For scoring
    #purposes, eating food, hitting a wall and simply moving will return 
    #a 1, -1, and 0, respectively.
    def MoveForward(self):
        #Get head and spot snake is about to move into
        head = self.body[0]
        newPos = self.grid.getAdjPoint(head, self.heading)

        #Snake has eaten food, same as normal movement, just doesn't delete tail
        if newPos.GetType() == PointType.FOOD:
            head.SetType(PointType.BODY)
            newPos.SetType(PointType.HEAD)
            self.body.appendleft(newPos)
            self.grid.placeRandomFood()
            self.head = newPos
            return 1

        #Snake has hit itself or a wall
        elif newPos.GetType()!=PointType.EMPTY:
            self.grid.GameOver()
            return -1
        
        #Snake has moved into empty space
        else:
            #Remove end of tail
            tail = self.body.pop()
            tail.SetType(PointType.EMPTY)

            #Move head into space
            head.SetType(PointType.BODY)
            newPos.SetType(PointType.HEAD)
            self.body.appendleft(newPos)
            self.head = newPos
            return 0
            
        

    #Turns the head of the snake, and moves in that direction
    def TurnRight(self):
        self.heading = Direction.rotateCW(self.heading)
        return self.MoveForward()
    def TurnLeft(self):
        self.heading = Direction.rotateCCW(self.heading)
        return self.MoveForward()

    #Takes input from agent, and makes the corresponding movement
    def MakeMove(self, choice):
        if(choice == 0):
            #print("LEFT")
            return self.TurnLeft()
        elif(choice==1):
            #print("FORWARD")
            return self.MoveForward()
        elif(choice == 2):
            #print("RIGHT")
            return self.TurnRight()
        else:
            print("INVALID MOVE")
            raise RuntimeError