import copy
import itertools
import random
import subprocess,ast


def fit_func(individual):
    print(individual)
    """ Calculate the fitness of an individual. """
    arguments = ' '.join(map(str, individual))
    command_string = 'python snakegame.py --genome ' + arguments
    output = str(subprocess.check_output(command_string, shell=True))
    useful_outputs_only = output.split("total_ticks")[1]
    useful_outputs_only_2 = useful_outputs_only.split("\\r\\nscore")
    tick_time = int(useful_outputs_only_2[0].strip())
    score = int(useful_outputs_only_2[1].split("\\r\\n")[0].strip())

    food_score = score * 1000  # weigh picking up more food heavily
    time_score = tick_time  # use time in seconds as survival time
    print(food_score + time_score)
    return food_score + time_score

def tournament_selection(sample):
    scores = [sum(ind) for ind in sample]
    return sample[scores.index(max(scores))]


def random_selection(sample):
    return sample[random.randint(0, len(sample) - 1)]

def mutate_slightly(value):
    random_val = random.random()
    if random_val > 0.5:
        random_val = random_val / 10.
        if value - random_val < 0:
            return 0.0
        return value - random_val
    elif random_val > 0.2:
        random_val = random_val / 3.0
    if value + random_val > 1:
        return 1
    return value + random_val


pop_size = 100
genome_size = 44
num_gens = 100

elitism = False
mut_rate = 1 / genome_size
cx_rate = 0  # 1/2

# For printing numbers at end to visualize.
max_fitnesses = []
avg_fitnesses = []
num_clones = []

population = []

# Initialize the population.
for i in range(pop_size):
    population.append([random.random() for _ in range(genome_size)])

for gen in range(num_gens):

    print("\n" + "-" * 80 + " ")

    # Evaluate the population
    fitnesses = [fit_func(p) for p in population]

    # Track fitnesses
    max_fitnesses.append(max(fitnesses))
    avg_fitnesses.append(sum(fitnesses) / len(fitnesses))

    print("Generation: {}".format(gen), end=" ")
    print("Max Fitness: {}".format(max_fitnesses[-1]))
    print("Avg Fitness: {}".format(avg_fitnesses[-1]))

    # Print out the population.
    # Note: Comment out if you have larger populations as it might be hard to read.
    print("Population Genomes:")
    for p in population:
        print("\t\t\t", p)

    # Calculate duplicates
    duplicates = copy.deepcopy(population)
    duplicates.sort()

    # Track Number of Clones in Population
    num_clones.append(pop_size - len(list(k for k, _ in itertools.groupby(duplicates))))

    print("\tNumber of Clones in Population: {}".format(num_clones[-1]))
    print("\tUnique Genomes in Population: ")
    for clone in list(k for k, _ in itertools.groupby(duplicates)):
        print("\t\t\t\t", clone)

    new_pop = []

    # Elitism
    if elitism:
        print("Keeping Elite Individual")
        new_pop.append(copy.deepcopy(population[fitnesses.index(max(fitnesses))]))

    for _ in range(pop_size - len(new_pop)):

        # Select two parents.
        par_1 = copy.deepcopy(tournament_selection(random.sample(population, 3)))
        par_2 = copy.deepcopy(tournament_selection(random.sample(population, 3)))

        # Perform crossover.
        new_ind = par_1[:]
        if random.random() < cx_rate:
            crossover_point = random.choice([0, genome_size])
            new_ind = par_1[:crossover_point] + par_2[crossover_point:]

        # Mutate the individual.
        new_ind = [i if random.random() > mut_rate else (mutate_slightly(i)) for i in new_ind]

        # Add to the population
        new_pop.append(new_ind)

    population = new_pop

# Print out final population
print("\n\n\nFinal Population is:")
for p in population:
    print(f"Fitness: {fit_func(p)}, Individual: {p}")

# Print out final tracking information.
print()
print("gens = " + str([g for g in range(num_gens)]))
print("max_fit = " + str(max_fitnesses))
print("avg_fit = " + str(avg_fitnesses))
print("num_clones = " + str(num_clones))

