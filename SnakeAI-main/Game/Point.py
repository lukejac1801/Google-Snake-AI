from enum import IntEnum
class PointType(IntEnum):
    EMPTY = 1
    FOOD = 2
    
    WALL =  -1
    HEAD = -2
    BODY = -3

class Point:
    def __init__(self, type, x, y):
        self.type = type
        self.x = x
        self.y = y

    def SetType(self, type):
        self.type = type
        
    def GetType(self):
        return self.type


    def UpdatePosition(self, x, y):
        self.x = x
        self.y = y

    def GetPosition(self):
        return [self.x, self.y]