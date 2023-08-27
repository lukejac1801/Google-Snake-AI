from Agent.Agents import AIAgent
from Game.Grid import Grid
from Game.GUI import GUI
import tensorflow
import pygad.kerasga
import numpy as np
import os

class Population():
    def __init__(self, config, modelName=None):
        tensorflow.compat.v1.logging.set_verbosity(tensorflow.compat.v1.logging.ERROR)
        self.config = config        
        self.modelName = modelName
            

    def run(self, populationSize, generations, parents, modelName):
        self.grids = []
        self.agents = []
        self.models = []
        self.avgFit = []
        self.peakFit = []

        print("Setting up...")
        for i in range(0, populationSize+1):
            model = tensorflow.keras.models.load_model("Agent/Models/"+modelName)
                
            agent = AIAgent(model)
            grid = Grid(self.config["gridHeight"],self.config["gridWidth"], agent)
            grid.Setup()
            self.grids.append(grid)
            self.agents.append(agent)
            self.models.append(model)
        print("Done.")
        print("Starting.\n")
        self.gencount = 0
        self.gentarget = generations
        self.modelName = modelName
        modelGA = pygad.kerasga.KerasGA(model=self.models[0], num_solutions=populationSize)
        initialPopulation = modelGA.population_weights

        GA = pygad.GA(num_generations=generations,
                      num_parents_mating=parents,
                      initial_population=initialPopulation,
                      fitness_func=self.fitness,
                      on_generation=self.genCallback,
                      parallel_processing=12,
                      parent_selection_type="rws",
                      keep_elitism=populationSize//2
                      )
        GA.run()


        #saving stats
        path = 'statbackup/'+self.modelName
        if not os.path.exists(path):
            os.makedirs(path)
        np.savetxt(path + "/avg.csv", self.avgFit, delimiter=", ")
        np.savetxt(path + "/peak.csv", self.peakFit, delimiter=", ")

        solution = GA.best_solution()[0]
        solIdx = GA.best_solution()[2]
        bestModel = self.models[solIdx]
        bestWeights = pygad.kerasga.model_weights_as_matrix(model=bestModel, weights_vector=solution)
        bestModel.set_weights(bestWeights)

        bestModel.save("Agent/Models/"+modelName)
        print("Best Model: Model", solIdx, "Fitness:", GA.best_solution()[1]-250)
   
    def fitness(self, inst, solution, sol_idx):
        agent = self.agents[sol_idx]
        grid = self.grids[sol_idx]
        model = agent.model

        modelWeights = pygad.kerasga.model_weights_as_matrix(model=model, weights_vector=solution)
        model.set_weights(weights=modelWeights)
        

        grid.reset()
        agent.reset()
        
        #self.agent.setModel(self.model)
        #self.agent.reset()
        #self.grid.reset()

        #gui = GUI(self.config, self.grid)
        #gui.startGameLoop()

        grid.startLoopNoGUI()

        score = 50*agent.foodEaten + agent.movement + agent.died*-50
        score += 250 #offset from negative values

        #print("Model", sol_idx, "Done. Fitness:",score-250)
        return score

    def genCallback(self, ga):
        self.gencount += 1
        fit = ga.last_generation_fitness
        avg = np.average(fit)-250
        peak = np.max(fit)-250
        
        self.peakFit.append(peak)
        self.avgFit.append(avg)

        print("Generation", self.gencount, "of", self.gentarget, "finished!")
        print("Average Fitness: ", avg)
        print("Peak Fitness:", peak, "\n")
        if(self.gencount%50==0):
            print("Saving progress...")
            path = 'statbackup/'+self.modelName
            if not os.path.exists(path):
                os.makedirs(path)
            np.savetxt(path + "/avg.csv", self.avgFit, delimiter=", ")
            np.savetxt(path + "/peak.csv", self.peakFit, delimiter=", ")
            
            model = self.models[np.argmax(fit)]
            model.save("Agent/Models/"+self.modelName)

    
        

    #-------------------Model Functions------------------
     #layers is a list of tuples, with an integer count and a string activation function
    #It does NOT include the input or output layers
    
    def buildModel(self, layers, modelName):
        self.modelName = modelName
        model = tensorflow.keras.Sequential()
        #15
        model.add(tensorflow.keras.layers.Dense(layers[0], activation=tensorflow.keras.activations.relu, input_shape=[13,]))
        for size in layers[1:]:
            model.add(tensorflow.keras.layers.Dense(size, activation=tensorflow.keras.activations.relu))
        
        model.add(tensorflow.keras.layers.Dense(3, activation=tensorflow.keras.activations.softmax))
        
        #adam = tensorflow.keras.optimizers.Adam()
        #model.compile(loss='mse', optimizer=adam)
        #if(weights):
        #    model.load_weights(weights)
        model.save("Agent/Models/"+self.modelName)
        return model
    
    def saveModel(self, path):
        self.model.save(path)

    def setModel(self, model):
        self.model = model
    
    def getModel(self):
        return self.model