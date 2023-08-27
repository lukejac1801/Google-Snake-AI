from Game.Grid import Grid
from Game.GUI import GUI
from Game.Point import PointType
from Agent.Agents import *
from Agent.Training import Population
import tensorflow
import matplotlib.pyplot as plt
import argparse




tensorflow.compat.v1.logging.set_verbosity(tensorflow.compat.v1.logging.ERROR)

conf = {
    "gridHeight": 30,
    "gridWidth": 30,
    "canvasSize": 800,
    "updateRate": 100,
    "colorPalette": {
        PointType.EMPTY: '#2a2a2b',
        PointType.WALL: '#141414',
        PointType.FOOD: '#8bf739',
        PointType.HEAD: '#2450f0',
        PointType.BODY: '#18328f'},
}


#Sets up a grid instance, with a specified agent player
def setupGrid(agent):
    cols = conf["gridHeight"]
    rows = conf["gridWidth"]
    grid = Grid(cols, rows, agent)
    grid.Setup()
    return grid

#Creates an runs a game with the given agent, displays game on screen
def runGameGUI(agent):
    grid = setupGrid(agent)
    gui = GUI(conf, grid)
    gui.startGameLoop()

#Creates and runs a game without displaying on screen, runs much faster
def runGameNoGUI(agent):
    grid = setupGrid(agent)
    grid.startLoopNoGUI(throttle=0)


#Loads a model by name, and runs a game on screen using that model
def RunAI(args):
    modelName = args.name
    model = tensorflow.keras.models.load_model("Agent\\Models\\"+modelName)
    #print(model.layers)
    agent = AIAgent(model)
    runGameGUI(agent)

#Creates a new model of a given name, with the given architecture
#Trains the model according to the given parameters, saves it under given name
def createModel(args):
    pop = Population(conf)
    pop.buildModel(args.layers, args.name)
    print(args.name+" successfully created.")

#Trains an existing model by creating a 1 parent population based on it,
#and running the GA according to the given parameters. New resulting model
#will overwrite previous model.
def trainModel(args):
    pop = Population(conf, modelName=args.name)
    pop.run(args.population, args.generations, args.parents, args.name)

#Displays a plot of the average and peak fitness of the most recent GA run.
def plotStats(args):
    model = args.name
    with open(("statbackup/" + model + "/avg.csv"), 'r') as file:
        avg = [round(float(line.strip()), 3) for line in file.readlines()]
        
    with open(("statbackup/" + model + "/peak.csv"), 'r') as file:
        peak = [round(float(line.strip()), 3) for line in file.readlines()]
    fig, axs = plt.subplots(1,2, figsize=(10,5))

    axs[0].plot(avg)
    axs[0].set_title("Average Fitness")
    axs[0].set_xlabel("Generations")
    axs[0].set_ylabel("Fitness")
    
    axs[1].plot(peak)
    axs[1].set_title("Peak Fitness")
    axs[1].set_xlabel("Generations")
    axs[1].set_ylabel("Fitness")

    plt.show()

#Plots fitness of multiple models on one graph
def compareStats(args):
    models = args.names
    avgs = []
    peaks = []
    for model in models:
        with open(("statbackup/" + model + "/avg.csv"), 'r') as file:
            avg = [round(float(line.strip()), 3) for line in file.readlines()]
            avgs.append(avg)
        
        with open(("statbackup/" + model + "/peak.csv"), 'r') as file:
            peak = [round(float(line.strip()), 3) for line in file.readlines()]
            peaks.append(peak)

    fig, axs = plt.subplots(1,2, figsize=(10,5))

    axs[0].set_title("Average Fitness")
    axs[0].set_xlabel("Generations")
    axs[0].set_ylabel("Fitness")

    axs[1].set_title("Peak Fitness")
    axs[1].set_xlabel("Generations")
    axs[1].set_ylabel("Fitness")

    for i in range(0, len(models)):
        axs[0].plot(avgs[i], label=models[i])
        axs[1].plot(peaks[i], label=models[i])

    plt.legend()
    plt.show()


#Argument parser setup ------------------------------------------------------------------------------------------------------------------------------------------------------
parser = argparse.ArgumentParser(description="Create, train, or view statistics on neural networks trained with a genetic algorithm on the game Snake.")

subparsers = parser.add_subparsers(title="Commands", dest="subcommand")

createParse = subparsers.add_parser("create", help="Create a new model.", description="Create a new model.")
createParse.add_argument("-n", "--name", type=str, required=True, help="Model name.")
createParse.add_argument("-l", "--layers", nargs="+", type=int, required=True, help="List of ints corresponding to nodes in each layer.")


trainParse = subparsers.add_parser("train", help="Train an existing model.", description="Train an existing model.")
trainParse.add_argument("-n", "--name", type=str, required=True, help="Name of model to train.")
trainParse.add_argument("-g", "--generations", type=int, required=True, help="Number of generations to run.")
trainParse.add_argument("-pop", "--population", type=int, required=True, help="Number of models in population.")
trainParse.add_argument("-par", "--parents", type=int, required=True, help="Number of parents to be selected.")

runParse = subparsers.add_parser("run", help="Run a game with a model.", description="Run a game with a model.")
runParse.add_argument("-n", "--name", type=str, required=True, help="Name of model to run game.")

plotParse = subparsers.add_parser("plot", help="Plot the fitness of a model.", description="Plot the fitness of a model.")
plotParse.add_argument("-n", "--name", type=str, required=True, help="Name of model to plot.")

compareParse = subparsers.add_parser("compare", help="Plot the fitness of multiple models on a graph.", description="Plot the fitness of multiple models on a graph.")
compareParse.add_argument("-N", "--names", nargs="+", type=str, required=True, help="Names of models to plot.")
#----------------------------------------------------------------------------------------------------------------------------------------------------------------------------



args = parser.parse_args()
match args.subcommand:
        case "create":
            createModel(args)
        case "train":
            trainModel(args)
        case "plot":
            plotStats(args)
        case "compare":
            compareStats(args)
        case "run":
            RunAI(args)
        case _:
            print("Invalid command.")