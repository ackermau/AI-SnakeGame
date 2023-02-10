import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '1'
from tensorflow import keras
from keras.models import Sequential
from keras.layers import Dense
import numpy as np


class NeuralNetwork:
    def __init__(self, in_dim, num_in_nodes, in_hidden_dim, num_hidden_nodes, hidden_out_dim, num_output_nodes):
        # Set number of nodes for each layer, and dimensionality
        self.in_dim = in_dim
        self.num_in_nodes = num_in_nodes
        self.in_hidden_dim = in_hidden_dim
        self.num_hidden_nodes = num_hidden_nodes
        self.hidden_out_dim = hidden_out_dim
        self.num_output_nodes = num_output_nodes
        self.genes_populated=0

        # Create the neural network model
        self.model = Sequential()

        # Add layers to the model
        self.input_layer = self.model.add(Dense(num_in_nodes, input_shape=in_dim, activation="relu", name="Input"))
        self.hidden_layer1 = self.model.add(Dense(num_hidden_nodes, activation="relu", name="Hidden"))
        self.hidden_layer2 = self.model.add(Dense(num_hidden_nodes, activation="relu", name="Hidden2"))
        self.hidden_layer3 = self.model.add(Dense(num_hidden_nodes, activation="relu", name="Hidden3"))
        self.out_layer = self.model.add(Dense(num_output_nodes, activation="relu", name="Output"))

        # Compiles the model, allows us to call it below
        self.model.compile(loss='binary_crossentropy', optimizer='adam', metrics=['accuracy'])

    def get_genome(self):
        # Get weights from neural network
        weights = self.model.get_weights()
        # Creates an array for genome, empty at start
        genome = np.array([], dtype=np.float32)
        # Skips the bias values from get_weights
        for x in range(0, len(weights), 2):
            # Append weights to genome copy, overwrite genome with new array
            genome = np.append(genome, weights[x])
        return genome

    def increment_gene_count(self, gene):
        self.genes_populated += 1
        return gene

    def set_weights_from_genome(self, genome):
        # Implement function that takes in the genome, then sets weights of the net
        # properly in accordance with the provided 1D array. Tricky, requires
        # reshaping segments of the genome array, setting bias values to 0, etc.
        num_inputs = self.in_dim[0]
        dyn_wts = [
            np.array([[genome[i] for i in range(0, self.num_in_nodes)] for _ in range(0, num_inputs)], dtype=np.float32),
            np.array([0.0 for _ in range(0, self.num_in_nodes)], dtype=np.float32),
            np.array([[genome[i] for i in range(0, self.num_hidden_nodes)] for _ in range(0, self.num_in_nodes)], dtype=np.float32),
            np.array([0.0 for _ in range(0, self.num_hidden_nodes)], dtype=np.float32),
            np.array([[genome[i] for i in range(0, self.num_hidden_nodes)] for _ in range(0, self.num_hidden_nodes)], dtype=np.float32),
            np.array([0.0 for _ in range(0, self.num_hidden_nodes)], dtype=np.float32),
            np.array([[genome[i] for i in range(0, self.num_hidden_nodes)] for _ in range(0, self.num_hidden_nodes)], dtype=np.float32),
            np.array([0.0 for _ in range(0, self.num_hidden_nodes)], dtype=np.float32),
            np.array([[genome[i] for i in range(0, self.num_output_nodes)] for _ in range(0, self.num_hidden_nodes)], dtype=np.float32),
            np.array([0.0 for _ in range(0, self.num_output_nodes)], dtype=np.float32)
        ]
        # Need to build the shape of wts above from provided genome
        self.model.set_weights(dyn_wts)

    # Runs data through model as a function
    def runModel(self, data):
        # Normalize input data to reduce magnitude differences
        normalized_data = keras.layers.UnitNormalization()(data)
        # Runs our data through the model
        q = self.model(normalized_data)
        # Sets action to the output node index with highest value
        action = np.argmax(q)
        return action
