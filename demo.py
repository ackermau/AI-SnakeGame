import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = "hide"
import copy
import itertools
import math
import numpy as np
import random
import pygame
import argparse
import ast
import multiprocessing as mp
from neato import Ecosystem
from neato import Genome

import gui_game_demo as gui_game

def fit_func(individual):
    game1 = gui_game.SnakeGame(20, individual, pygame)
    game1.runGame()

parser = argparse.ArgumentParser()
parser.add_argument('--start_file', nargs='?', default='',
                    help='specify the file to get the starting population from (defualt generate random new pop)')
args = parser.parse_args()

inputs = 0
outputs = 0
conn = 0
nodes = []
connections = []
with open(args.start_file, 'r') as f:
    data = f.read()
    data = data.replace('\t', '')
    data = data.replace(' ', '')
    data = data.split("\n")
    pop_size = int(data[0])
    input_genome = data[1:len(data) - 1]
    input_fit = data[len(data) - 1]
    for line in input_genome:
        if "input" in line:
            inputs += 1
        if "output" in line:
            outputs += 1
        if "[O]" in line or "[X]" in line:
            connections.append(line.split(":")[1])

if __name__ == '__main__':
    ecosystem = Ecosystem()
    parent = Genome(inputs, outputs)
    parent.add_connection(int(4), int(12), float(-0.9481904157219666))
    parent.add_node(parent.get_innovation_number(4, 12))
    parent.add_connection(int(1), int(11), float(-0.770409606691889))
    parent.add_node(parent.get_innovation_number(1, 11))
    parent.add_connection(int(15), int(11), float(0.40285651666288835))
    parent.add_node(parent.get_innovation_number(15, 11))
    parent.add_connection(int(2), int(15), float(1.1))
    parent.add_connection(int(15), int(13), float(-0.20801854622992433))
    parent.add_connection(int(3), int(15), float(0.7748068261421966))
    parent.add_connection(int(7), int(10), float(-0.22229622024753973))
    parent.add_connection(int(2), int(11), float(0.9929764458813932))
    parent.add_connection(int(8), int(11), float(0.6574363503380212))
    parent.add_connection(int(6), int(12), float(0.3199641253471479))
    parent.add_connection(int(14), int(15), float(1.0))
    parent.add_connection(int(2), int(14), float(1.1))
    parent.add_connection(int(16), int(12), float(-0.8874908567562353))
    parent.add_connection(int(16), int(13), float(0.8572114631347103))
    parent.add_connection(int(4), int(16), float(-0.8819611323164496))
    parent.add_connection(int(6), int(15), float(0.6000846932898511))
    parent.add_connection(int(6), int(16), float(0.9))
    parent.add_connection(int(17), int(16), float(-0.7819611323164496))
    parent.add_connection(int(2), int(17), float(-0.6467833656842207))
    parent.add_connection(int(16), int(10), float(0.24427220435499808))
    parent.add_connection(int(4), int(17), float(1.1))
    
    ecosystem.create_initial_population(1, parent_genome=parent)
    
    # test genomes and score fitness
    index = 0
    pool_args = [[genome] for genome in ecosystem.get_population()]
    pool = mp.Pool()
    fitnesses = pool.starmap(fit_func, pool_args)
    pool.close()
    for genome in ecosystem.get_population():
        genome.fitness = fitnesses[index]
        index += 1