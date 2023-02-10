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

import nogui_game


def fit_func(individual, num_inputs, input_node_count, hidden_node_count, num_output_nodes):
    game1 = nogui_game.SnakeGame(200, individual, num_inputs, input_node_count, hidden_node_count, num_output_nodes, pygame)
    game1.runGame()
    game2 = nogui_game.SnakeGame(200, individual, num_inputs, input_node_count, hidden_node_count, num_output_nodes, pygame)
    game2.runGame()
    game3 = nogui_game.SnakeGame(200, individual, num_inputs, input_node_count, hidden_node_count, num_output_nodes, pygame)
    game3.runGame()

    """ Calculate the fitness of an individual. """

    #food_score = game1.score * 1000  # weigh picking up more food heavily
    #time_score = game1.total_ticks  # use time in seconds as survival
    food_score1 = math.sqrt(math.pow(game1.score, 3)) * 3000  # weigh picking up more food heavily
    time_score1 = (game1.total_ticks/10)  # use time in seconds as survival
    food_score2 = math.sqrt(math.pow(game2.score, 3)) * 3000  # weigh picking up more food heavily
    time_score2 = (game2.total_ticks/10)  # use time in seconds as survival
    food_score3 = math.sqrt(math.pow(game3.score, 3)) * 3000  # weigh picking up more food heavily
    time_score3 = (game3.total_ticks/10)  # use time in seconds as survival
    dist_to_food1 = math.sqrt(math.pow((game1.snake_pos[0]-game1.food_pos[0]), 2) + math.pow((game1.snake_pos[1]-game1.food_pos[1]), 2))
    death_score1 = (1/dist_to_food1) * 10000
    dist_to_food2 = math.sqrt(math.pow((game2.snake_pos[0]-game2.food_pos[0]), 2) + math.pow((game2.snake_pos[1]-game2.food_pos[1]), 2))
    death_score2 = (1/dist_to_food2) * 10000
    dist_to_food3 = math.sqrt(math.pow((game3.snake_pos[0]-game3.food_pos[0]), 2) + math.pow((game3.snake_pos[1]-game3.food_pos[1]), 2))
    death_score3 = (1/dist_to_food3) * 10000

    avg_food_score = (food_score1 + food_score2 + food_score3)/3.0
    avg_time_score = (time_score1 + time_score2 + time_score3)/3.0
    avg_death_score = (death_score1 + death_score2 + death_score3)/3.0
    print('Foodscore: ' + str(avg_food_score) + ' Fitness: ' + str(avg_food_score + avg_time_score + avg_death_score))
    return avg_food_score + avg_time_score + avg_death_score


def tournament_selection(sample, fitnesses, population):
    scores = [fitnesses[population.index(ind)] for ind in sample]
    return sample[scores.index(max(scores))]


def random_selection(sample):
    return sample[random.randint(0, len(sample) - 1)]


def mutate_slightly(value):
    random_change = random.uniform(-0.2, 0.2)  # randomly mutates by -0.1 to 0.1

    new_weight = value + random_change
    if new_weight <= -2.0:  # keep weights above -1
        return -2.0
    elif new_weight >= 2.0:  # keep weights below 1
        return 2.0
    else:
        return new_weight

# note: can't specify number of inputs (not input nodes) because NN constructor uses inputs as args
parser = argparse.ArgumentParser()
parser.add_argument('--pop', nargs='?', type=int, default=25, help='Specify the number of individuals in the population (default 25)')
parser.add_argument('--eliteism', action='store_true', help='Enables Eliteism')
parser.add_argument('--gens', nargs='?', type=int, default=100, help='Specify the number of generations to train the population')
parser.add_argument('--mut_rate', nargs='?', type=float, default=0.5, help='Specify how frequently a gene should randomly mutate')
parser.add_argument('--big_mut_rate', nargs='?', type=float, default=0.05, help='Specify how frequently a gene should randomly mutate')
parser.add_argument('--cx_rate', nargs='?', type=float, default=0.1, help='Specify how frequently a child should cross over')
parser.add_argument('--hidden_nodes', nargs='?', type=int, default=5, help='Specify how many hidden nodes to use')
parser.add_argument('--input_nodes', nargs='?', type=int, default=3, help='Specify how many input nodes')
parser.add_argument('--inputs', nargs='?', type=int, default=3, help='Specify how many inputs will be fed to the input nodes')
parser.add_argument('--output_nodes', nargs='?', type=int, default=4, help='Specify how many output nodes')
parser.add_argument('--start_file', nargs='?', default='', help='specify the file to get the starting population from (defualt generate random new pop)')
parser.add_argument('--disable_rate', nargs='?', type=float, default=0.001, help='Specify how frequently a gene should be turned off')
parser.add_argument('--save_rate', nargs='?', type=int, default=5, help='Specify how frequently to save the current generation to a file')

args = parser.parse_args()

input_count = args.inputs
output_node_count = args.output_nodes
input_node_count = args.input_nodes
hidden_node_count = args.hidden_nodes

pop_size = args.pop
genome_size = input_count * args.input_nodes + args.input_nodes * args.hidden_nodes + args.hidden_nodes * output_node_count
num_gens = args.gens

elitism = args.eliteism
mut_rate = args.mut_rate #2 / genome_size
big_mut_rate = args.big_mut_rate
cx_rate = args.cx_rate  # 1/2
disable_rate = args.disable_rate

save_rate = args.save_rate
# For printing numbers at end to visualize.
max_fitnesses = []
avg_fitnesses = []
num_clones = []

population = []

# Initialize the population.
if args.start_file == '':
    for i in range(pop_size):
        population.append([random.uniform(-2.0, 2.0) for _ in range(genome_size)])
else:
    with open(args.start_file, 'r') as f:
        print(args.start_file)
        temp = int(f.readline())
        print(temp)
        if pop_size <= temp:
            pop_size = temp
            for x in range(0, pop_size):
                population.append(ast.literal_eval(f.readline()))
        else:
            for x in range(temp):
                population.append(ast.literal_eval(f.readline()))
            for i in range(pop_size - temp):
                population.append([random.uniform(-2.0, 2.0) for _ in range(genome_size)])
    f.close()

if __name__ == '__main__':
    gen_count = 1
    for gen in range(num_gens):
        if gen_count == 150:
            mut_rate = mut_rate/3
            cx_rate = cx_rate*0.9
            big_mut_rate = big_mut_rate/4
            disable_rate = disable_rate/3

        print("\nGeneration: {}".format(gen), end=" ")
        print("-" * 80 + " ")

        # Evaluate the population
        pool_args = [[p, input_count, args.input_nodes, args.hidden_nodes, output_node_count] for p in population]
        pool = mp.Pool()
        fitnesses = pool.starmap(fit_func, pool_args)
        pool.close()
        # fitnesses = [fit_func(p, input_count, args.input_nodes, args.hidden_nodes, output_node_count) for p in population]

        if (gen_count - 1) % save_rate == 0:
            with open('generations\\gen' + str(gen_count) + '.txt', 'w') as f:
                f.write(str(pop_size) + '\n')
                for p in population:
                    f.write(str(p) + '\n')
                f.write(str(fitnesses) + '\n')
            f.close()

        # If on the last gen, save as lastGen.txt
        if ((gen_count - 1) - gen == 0):
            with open('generations\\lastGen.txt', 'w') as f:
                f.write(str(pop_size) + '\n')
                for p in population:
                    f.write(str(p) + '\n')
                f.write(str(fitnesses) + '\n')
            f.close()

        gen_count += 1
        # Track fitnesses
        max_fitnesses.append(max(fitnesses))
        avg_fitnesses.append(sum(fitnesses) / len(fitnesses))

        # Calculate duplicates
        duplicates = copy.deepcopy(population)
        duplicates.sort()

        # Track Number of Clones in Population
        num_clones.append(pop_size - len(list(k for k, _ in itertools.groupby(duplicates))))

        print("\tNumber of Clones in Population: {}".format(num_clones[-1]))

        new_pop = []

        # Elitism
        if elitism:
            print("Keeping Elite Individual")

            top_10_idx = np.argsort(fitnesses)[-3:]
            top_10_values = [fitnesses[i] for i in top_10_idx]
            for v in top_10_values:
                new_pop.append(copy.deepcopy(population[fitnesses.index(v)]))

        for _ in range(pop_size - len(new_pop)):

            # Select two parents.
            par_1 = copy.deepcopy(tournament_selection(random.sample(population, 8), fitnesses, population))
            par_2 = copy.deepcopy(tournament_selection(random.sample(population, 4), fitnesses, population))

            # Perform crossover.
            new_ind = par_1[:]
            if random.random() < cx_rate:
                if random.random() >= 0.5:
                    crossover_point = random.choice([0, genome_size])
                    new_ind = par_1[:crossover_point] + par_2[crossover_point:]
                else:
                    gene_indeces = []
                    increment_counter = 0
                    for a in range(0, input_count):
                        temp_lst = []
                        for b in range(0, input_node_count):
                            temp_lst.append(increment_counter)
                            increment_counter += 1
                        gene_indeces.append(temp_lst)
                    for a in range(0, input_node_count):
                        temp_lst = []
                        for b in range(0, hidden_node_count):
                            temp_lst.append(increment_counter)
                            increment_counter += 1
                        gene_indeces.append(temp_lst)
                    for a in range(0, hidden_node_count):
                        temp_lst = []
                        for b in range(0, output_node_count):
                            temp_lst.append(increment_counter)
                            increment_counter += 1
                        gene_indeces.append(temp_lst)
                    num_genes_from_parent_1 = random.randint(1, (len(gene_indeces) - 1))
                    nodes_indeces_from_par_1 = random.sample(gene_indeces, num_genes_from_parent_1)
                    for a in nodes_indeces_from_par_1:
                        gene_indeces.remove(a)
                    new_ind = []
                    for a in range(0, increment_counter):
                        if any(a in indeces for indeces in nodes_indeces_from_par_1):
                            new_ind.append(par_1[a])
                        else:
                            new_ind.append(par_2[a])

            # Slightly mutate the individual.
            new_ind = [i if random.random() > mut_rate else (mutate_slightly(i)) for i in new_ind]

            # Mutate the individual.
            new_ind = [i if random.random() > big_mut_rate else random.uniform(-2.0, 2.0) for i in new_ind]

            # disable genes
            new_ind = [i if random.random() > disable_rate else 0 for i in new_ind]

            # Add to the population
            new_pop.append(new_ind)

        population = new_pop

    # Print out final tracking information.
    print()
    print("gens = " + str(num_gens))
    print("max_fit = " + str(max(max_fitnesses)))
    print("avg_fit = " + str(np.average(avg_fitnesses)))
    print("num_clones = " + str(num_clones))
