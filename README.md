Group members:
	Dakota Sliter
	Austin Auckerman
	Noah Betz

Install pygame with: 
	pip3 install pygame

Run game with:
  	python3 snakegame.py

Packages used:
	os
	copy
	math
	numpy as np
	random
	pygame
	argparse
	ast
	itertools
	multiprocessing as mp
	subprocess
	pygame
	sy
	time
	neuralnet as nn
	tensorflow import keras
	keras.models import Sequential
	keras.layers import Dense
	neato import Ecosystem
	neato import Genome

Running NN:
	py .\networkFile(GA_parallel.py, genetic_alg_class.py, or testneat.py) --pop 100 --eliteism --gens 10 --mut_rate 0.005 --big_mut_rate 0.0002 --cx_rate 0.50 --hidden_nodes 20 --inputs 10 --input_nodes 5 --output_nodes 5 "--start_file generations\gen730.txt"(start file only added using parent genome) --disable_rate 0.0002 --save_rate 10
