import pygame, sys, time, random
import neuralnet as nn
import numpy as np
import snakegame_class

genome = []
for i in range(0, 44):
    genome.append(1)

game1 = snakegame_class.SnakeGame(10, genome, pygame)
game2 = snakegame_class.SnakeGame(10, genome, pygame)
game3 = snakegame_class.SnakeGame(10, genome, pygame)
game1.runGame()
game2.runGame()
game3.runGame()