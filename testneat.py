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

import nogui_game2 as nogui_game


def fit_func(individual):
    game1 = nogui_game.SnakeGame(200, individual, pygame)
    game1.runGame()
    game2 = nogui_game.SnakeGame(200, individual, pygame)
    game2.runGame()
    game3 = nogui_game.SnakeGame(200, individual, pygame)
    game3.runGame()

    """ Calculate the fitness of an individual. """

    food_score1 = math.sqrt(math.pow(game1.score, 3)) * 3000  # weigh picking up more food heavily
    time_score1 = (game1.total_ticks / 10)  # use time in seconds as survival
    food_score2 = math.sqrt(math.pow(game2.score, 3)) * 3000  # weigh picking up more food heavily
    time_score2 = (game2.total_ticks / 10)  # use time in seconds as survival
    food_score3 = math.sqrt(math.pow(game3.score, 3)) * 3000  # weigh picking up more food heavily
    time_score3 = (game3.total_ticks / 10)  # use time in seconds as survival
    dist_to_food1 = math.sqrt(
        math.pow((game1.snake_pos[0] - game1.food_pos[0]), 2) + math.pow((game1.snake_pos[1] - game1.food_pos[1]), 2))
    death_score1 = (1 / dist_to_food1) * 80000
    dist_to_food2 = math.sqrt(
        math.pow((game2.snake_pos[0] - game2.food_pos[0]), 2) + math.pow((game2.snake_pos[1] - game2.food_pos[1]), 2))
    death_score2 = (1 / dist_to_food2) * 80000
    dist_to_food3 = math.sqrt(
        math.pow((game3.snake_pos[0] - game3.food_pos[0]), 2) + math.pow((game3.snake_pos[1] - game3.food_pos[1]), 2))
    death_score3 = (1 / dist_to_food3) * 80000
    avg_death_score = (death_score1 + death_score2 + death_score3) / 3.0

    avg_food_score = (food_score1 + food_score2 + food_score3) / 3.0
    if (avg_food_score) <= 2000.0:
        avg_food_score = avg_death_score
    avg_time_score = (time_score1 + time_score2 + time_score3) / 3.0
    print('Foodscore: ' + str((game1.score + game2.score + game3.score)) + ' Fitness: ' + str(
        avg_food_score + avg_time_score))  # + avg_death_score
    return avg_food_score + avg_time_score  # + avg_death_score


# note: can't specify number of inputs (not input nodes) because NN constructor uses inputs as args
parser = argparse.ArgumentParser()
parser.add_argument('--pop', nargs='?', type=int, default=25,
                    help='Specify the number of individuals in the population (default 25)')
parser.add_argument('--eliteism', action='store_true', help='Enables Eliteism')
parser.add_argument('--gens', nargs='?', type=int, default=100,
                    help='Specify the number of generations to train the population')
parser.add_argument('--mut_rate', nargs='?', type=float, default=0.5,
                    help='Specify how frequently a gene should randomly mutate')
parser.add_argument('--big_mut_rate', nargs='?', type=float, default=0.05,
                    help='Specify how frequently a gene should randomly mutate')
parser.add_argument('--cx_rate', nargs='?', type=float, default=0.1,
                    help='Specify how frequently a child should cross over')
parser.add_argument('--hidden_nodes', nargs='?', type=int, default=5, help='Specify how many hidden nodes to use')
parser.add_argument('--input_nodes', nargs='?', type=int, default=3, help='Specify how many input nodes')
parser.add_argument('--inputs', nargs='?', type=int, default=3,
                    help='Specify how many inputs will be fed to the input nodes')
parser.add_argument('--output_nodes', nargs='?', type=int, default=4, help='Specify how many output nodes')
parser.add_argument('--start_file', nargs='?', default='',
                    help='specify the file to get the starting population from (defualt generate random new pop)')
parser.add_argument('--disable_rate', nargs='?', type=float, default=0.001,
                    help='Specify how frequently a gene should be turned off')
parser.add_argument('--save_rate', nargs='?', type=int, default=5,
                    help='Specify how frequently to save the current generation to a file')

args = parser.parse_args()

input_count = args.inputs
output_node_count = args.output_nodes
input_node_count = args.input_nodes
hidden_node_count = args.hidden_nodes

pop_size = args.pop
genome_size = input_count * args.input_nodes + args.input_nodes * args.hidden_nodes + args.hidden_nodes * output_node_count
num_gens = args.gens

elitism = args.eliteism
mut_rate = args.mut_rate  # 2 / genome_size
big_mut_rate = args.big_mut_rate
cx_rate = args.cx_rate  # 1/2
disable_rate = args.disable_rate

save_rate = args.save_rate

if args.start_file == '':
    pass
else:
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

# print(population)
if __name__ == '__main__':
    ecosystem = Ecosystem()
    if args.start_file == '':
        ecosystem.create_initial_population(pop_size, input_size=input_count, output_size=output_node_count)
    else:
        parent = Genome(inputs, outputs)
        for connec in connections:
            nid1 = connec.split("-")[0]
            nid2 = connec.split("-")[1].split("[")[0]
            weight = connec.split("]")[1]
            parent.add_connection(int(nid1), int(nid2), float(weight))
        ecosystem.create_initial_population(pop_size, parent_genome=parent)
    for generation in range(0, num_gens):
        print("\nGeneration: {}".format(generation), end=" ")
        print("-" * 80 + " ")
        print(str(len(ecosystem.get_population())))

        # test genomes and score fitness
        index = 0
        pool_args = [[genome] for genome in ecosystem.get_population()]
        pool = mp.Pool()
        fitnesses = pool.starmap(fit_func, pool_args)
        pool.close()
        for genome in ecosystem.get_population():
            genome.fitness = fitnesses[index]
            index += 1

        best_genome = ecosystem.get_best_genome()
        print(str(best_genome))
        print('best_fitness: ' + str(best_genome.fitness))

        # save genomes to file
        if generation % save_rate == 0:
            with open('generations\\gen' + str(generation) + '.txt', 'w') as f:
                f.write(str(pop_size))
                f.write(str(best_genome))
                f.write(str(fitnesses))
            f.close()
            
        ecosystem.next_generation(kill_percentage=40, parent_genome=best_genome)
