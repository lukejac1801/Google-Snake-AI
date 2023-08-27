import random
import tensorflow
import numpy as np
#import keyboard    used for human player, unused in final setup


class Agent():
    def __init__(self) -> None:
        self.steps = 0
        self.movement = 0.0
        self.foodEaten = 0
        self.died = False
    
    #Resets this agent
    def reset(self):
        self.steps = 0
        self.movement = 0.0
        self.foodEaten = 0
        self.died = False
    
    #Chooses a move, makes that move, updates personal stats accordingly.
    def MakeMove(self, g):
        distToFood = g.GetDistance(g.snake.head, g.food)        
        move = self.ChooseMove()
        state = g.snake.MakeMove(move)

        newDistToFood = g.GetDistance(g.snake.head, g.food)

        change = distToFood-newDistToFood
        
        #Points for eating food
        if(state==1):
            self.foodEaten += 1
        #Moved towards or away from food
        elif(change>0):
            self.movement += 1.0
        else:
            self.movement += -1.5

        if(state==-1):
            self.died = True
        self.steps += 1



    def ChooseMove(self):
        #Implemented by specific agent
        raise NotImplementedError

class RandomAgent(Agent):
    def ChooseMove(self):
        picked = random.randint(0,2)
        return picked 

# Used to play manually, not used in final setup. requires keyboard module
#class HumanPlayer(Agent): 
#    def ChooseMove(self):
#        if keyboard.is_pressed("left"):
#           return 2
#        elif keyboard.is_pressed("right"):
#            return 0
#        else:
#            return 1
        

class AIAgent(Agent):
        def __init__(self, model):
            super().__init__()
            self.model = model
            self.energyMax = 300 #How long can go without food before dying, prevents infinite loops or extremely slow paths
            self.energy = self.energyMax


        def reset(self):
            self.steps = 0
            self.movement = 0.0
            self.foodEaten = 0
            self.died = False
            self.energy = self.energyMax
            
        def MakeMove(self, g):
            distToFood = g.GetDistance(g.snake.head, g.food)

            #Gets input from grid state, and passes it to the model
            input = g.getState()
            move = self.ChooseMove(input)
            state = g.snake.MakeMove(move)

            newDistToFood = g.GetDistance(g.snake.head, g.food)

            change = distToFood-newDistToFood
            self.energy -= 1
            #Points for eating food
            if(state==1):
                self.foodEaten += 1
                self.energy = self.energyMax
            #Moved towards or away from food
            elif(change>0):
                self.movement += 1.0
            else:
                self.movement -= 1.5

            if(state==-1):
                self.died = True
            self.steps += 1
            if(self.energy <= 0):
                g.GameOver()
                self.movement -= 50
                self.died = True


        #Model uses input to choose 3 moves, left forward or right.
        def ChooseMove(self, input):
            #input = tensorflow.cast(input, float)
            input = tensorflow.expand_dims(input, axis=0)
            choices = self.model(input)
            bestChoice = np.argmax(choices)
            return bestChoice

            