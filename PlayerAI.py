# created by:		Brad Arrowood
# created on:		2019.12.04
# last updated:		2020.04.21
# python version:	3.7.6
# run format:		python3 GameManager.py
# file:			PlayerAI.py
# addendums:		BaseAI.py
#			BaseDisplayer.py
#			ComputerAI.py
#			Displayer.py
#			GameManager.py
#			Grid.py
# notes:		made for edX ColumbiaX: CSMM.101x - Artificial Intelligence (AI) - week 4, project 2
#			This should inherit from BaseAI. The getMove() function, which you will need to implement, returns a number that indicates the player’s action.
#			In particular, 0 stands for "Up", 1 stands for "Down", 2 stands for "Left", and 3 stands for "Right". You need to create this file and make it as intelligent as possible.
#			You may include other files in your submission, but they will have to be included through this file.

# 1) Employ the minimax algorithm. This is a requirement. There are many viable strategies to beat the 2048-puzzle game, but in this assignment we will be practicing with the minimax algorithm.
# 2) Implement alpha-beta pruning. This is a requirement. This should speed up the search process by eliminating irrelevant branches. In this case, is there anything we can do about move ordering?
# 3) Use heuristic functions. What is the maximum height of the game tree? Unlike elementary games like tic-tac-toe, in this game it is highly impracticable to search the entire depth of the theoretical game tree.
#    To be able to cut off your search at any point, you must employ heuristic functions to allow you to assign approximate values to nodes in the tree. Remember, the time limit allowed for each move is 0.2 seconds, so you must implement a systematic way to cut off your search before time runs out.
# 4) Assign heuristic weights. You will likely want to include more than one heuristic function. In that case, you will need to assign weights associated with each individual heuristic. Deciding on an appropriate set of weights will take careful reasoning, along with careful experimentation. If you feel adventurous, you can also simply write an optimization meta-algorithm to iterate over the space of weight vectors, until you arrive at results that you are happy enough with.

# import some basics and the class BaseAI from the BaseAI.py script
from random import randint
from BaseAI import BaseAI
import math
import time

class minmax:
    infinite = float('inf')
    def __init__(self, grid):
        # setting up self with some class level variables... the grid, the options for random tiles generated, alphs beta pruning, and the depths
        self.root = grid
        self.newTileOptions = [2, 4]
        self.alpha = -minmax.infinite
        self.beta = minmax.infinite
        self.deep = 0
        self.maxDeep = 6

    def workflow(self):
        maxValue = -minmax.infinite
        bestMove = None
        for move in self.root.getAvailableMoves():
            newGrid = self.root.clone()
            newGrid.move(move)
            value = self.get_min(newGrid)
            if maxValue < value:
                maxValue, bestMove = value, move
        return bestMove

    def get_max(self, grid):
        self.deep += 1
        moves = grid.getAvailableMoves()
        if moves == [] or self.deep > self.maxDeep:
            self.deep -= 1
            return self.grid_asses(grid)
        combinedValues = -minmax.infinite
        for move in moves:
            newGrid = grid.clone()
            newGrid.move(move)
            combinedValues = max(combinedValues, self.get_min(newGrid))
            if combinedValues >= self.beta:
                self.deep -= 1
                return combinedValues
            self.alpha = max(self.alpha, combinedValues)
        self.deep -= 1
        return combinedValues

    def get_min(self, grid):
        # this func is more for getting the average of the max than searching for a min value
        self.deep += 1
        cells = grid.getAvailableCells()
        if cells == [] or self.deep > self.maxDeep:
            self.deep -= 1
            return self.grid_asses(grid)

        combinedValues = minmax.infinite
        for cell in cells:
            for cell_value in self.newTileOptions:
                newGrid = grid.clone()
                newGrid.setCellValue(cell, cell_value)
                nextValue = self.get_max(newGrid)
                combinedValues = min(combinedValues, nextValue)
                if combinedValues <= nextValue:
                    self.deep -= 1
                    return combinedValues
        self.deep -= 1
        return combinedValues

    def grid_asses(self, grid):
        # picking the upper-right corner as highest weighted value; avoid middle 2 col on top row as they can get game values stuck/unplayable; best to use 1,2,4,8,16,32,... double-values for greater weight differences
        # setup 4?: highest weighted value in upper-right with cascading down in weighted values [[2,4,8,16],[2,4,8,8],[1,4,4,4],[1,1,2,2]] [HIGHEST(3): 512,256,...]
        # setup 5: highest weighted value in upper-right with cascading out in weighted values [[4,8,8,16],[2,4,4,8],[1,2,4,8],[1,1,2,4]] [HIGHEST(3): 512,256,...]
        # setup 6: highest in upper-right, top 2 rows staggard snake values, bottom 2 rows stagged lowest values [[8,16,16,32],[8,4,4,4],[1,2,2,4],[1,1,2,4]] [HIGHEST(3): 256,...]
        # setup 7: highest in upper-right, snake values more across top, row 2 then right wall, with lowest values in bottom-left corner [[16,16,16,32],[8,8,8,4],[1,2,2,4],[1,1,2,4]] [HIGHEST(3): 1024,512,256,...]
        # setup 8: highest upper-right, snake left, down next row and back right, down and back left, down and back right in values [[16,32,32,64],[16,8,8,8],[2,2,4,4],[2,1,1,1]] [HIGHEST(3): 512,256,...]
        # setup 9: highest upper-right doing broader cascade left, out, then down, with lower-left corner lowest value [[32,64,64,128],[32,16,16,8],[2,4,8,8],[1,2,4,8]][HIGHEST(5): 512,512,512,1024,512]
        #*setup 10: going back to a more cascade from the upper-right after raising the highest values again [[64,128,128,256],[64,32,32,16],[2,4,8,16],[1,2,4,16]] [HIGHEST(5): 1024,512,1024,1024,512]
        # setup 11: attempting to expand the snake high-low value with some lower low-inner values to prevent choke in the lower-middle of the game [[128,256,512,1024],[64,32,32,16],[4,8,8,16],[4,1,2,16]] [HIGHEST(3): 256...]
        # setup 12: going full snake high-low double-stagged values until lowest and doing individual lowest values [[256,512,512,1024],[256,128,128,64],[16,32,32,64],[8,4,2,1]] [HIGHEST(5): 512,1024,512,512,...]
        #*setup 13: inverting the snake setup to having the top 3 rows have individual how-low values instead of lower rows [[1024,2048,4096,8192],[512,256,128,64],[4,8,16,32],[4,2,2,1]] [HIGHEST(10): 512,512,2048,2048,2048,1024,512,...]
        # setup 14: trying a complete snake layout but with each row up from the bottom i times the lower value by 4 instead of 2 for greater seperation between weighted values [[32768,65536,131072,262144],[8192,4096,2048,1024],[32,64,128,256],[8,4,2,1]] [HIGHEST(5): 512,512,512,...]
        # setup 15: trying out flipping the snake layout from setup 14 to see if it makes any difference which corner has highest priority [[262144,131072,65536,32768],[1024,2048,4096,8192],[256,128,64,32],[1,2,4,8]] [HIGHEST(10): 4096,2048,512,2048,4096,4096,1024,2048,4096,4096]
        # WTF?!...well that answers my question on if a particular corner actually matters; taking the exact same values and inverting them can greatly affect the results. running scipt 10 times using setup 15 to see outputs but first time i've seen a 4096 from all my other attempts
        weighted_values =  [[262144,131072,65536,32768],
                         [1024,2048,4096,8192],
                         [256,128,64,32],
                         [1,2,4,8]]
        deepValue = self.deep + 1
        sepValues = 0
        mergeValues = 0
        total = 0
        sortedValues = 0
        
        for x in range(0, 4):
            for y in range(0, 4):
                total += grid.map[x][y]
                if grid.map[x][y] == 0:
                    pass
                sortedValues += weighted_values[x][y] * grid.map[x][y]
                if x > 0:
                    sepValues += abs(grid.map[x][y] - grid.map[x - 1][y])
                    if grid.map[x][y] == grid.map[x - 1][y]:
                        mergeValues += grid.map[x][y]
                if y > 0:
                    sepValues += abs(grid.map[x][y] - grid.map[x][y - 1])
                    if grid.map[x][y] == grid.map[x][y - 1]:
                        mergeValues += grid.map[x][y]
                if x < 3:
                    sepValues += abs(grid.map[x][y] - grid.map[x + 1][y])
                    if grid.map[x][y] == grid.map[x + 1][y]:
                        mergeValues += grid.map[x][y]
                if y < 3:
                    sepValues += abs(grid.map[x][y] - grid.map[x][y + 1])
                    if grid.map[x][y] == grid.map[x][y + 1]:
                        mergeValues += grid.map[x][y]
        return deepValue * (total + sepValues + mergeValues + 2 * sortedValues)

class PlayerAI(BaseAI):
    def getMove(self, grid):
        alg = minmax(grid)
        return alg.workflow()
