import math

import pygame, sys, time, random
import neuralnet as nn
import numpy as np


def calcDistFromPoints(snakehead, food):
    # distance formula (normalized to board size)
    distance = math.sqrt(math.pow((snakehead[0] - food[0]), 2) + math.pow((snakehead[1] - food[1]), 2)) / 850
    return distance

class SnakeGame:
    def __init__(self, difficulty, genome, input_count=11, input_node_count=11, hidden_node_count=16, hidden_node2_count=12, hidden_node3_count=8, output_node_count=4,
                 pygame=pygame):
        self.delta_sum = 0
        self.last_eat_time = None
        self.input_count = input_count
        self.input_node_count = input_node_count
        self.hidden_node_count = hidden_node_count
        self.output_node_count = output_node_count
        self.hidden_node2_count = hidden_node2_count
        self.hidden_node3_count = hidden_node3_count
        # Difficulty settings
        # Easy      ->  10, Medium    ->  25, Hard      ->  40, Harder    ->  60, Impossible->  120
        self.difficulty = difficulty
        self.genome = genome
        # Window size
        self.frame_size_x = 720
        self.frame_size_y = 480

        self.total_ticks = 0
        # Checks for errors encountered
        check_errors = pygame.init()
        # pygame.init() example output -> (6, 0)
        if check_errors[1] > 0:
            print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
            pygame.init()
        # FPS (frames per second) controller
        self.fps_controller = pygame.time.Clock()

        # Game variables
        self.snake_pos = [100, 50]
        self.snake_body = [[100, 50], [100 - 10, 50], [100 - (2 * 10), 50]]

        self.food_pos = [random.randrange(1, (self.frame_size_x // 10)) * 10,
                         random.randrange(1, (self.frame_size_y // 10)) * 10]
        self.food_spawn = True

        self.direction = 'RIGHT'
        self.change_to = self.direction

        self.score = 0
        self.pygame = pygame

    # Game Over
    def game_over(self):
        self.pygame.quit()

    def runGame(self):
        # Initialise game window
        neural_net = nn.NeuralNetwork((self.input_count,), self.input_node_count,
                                      (self.input_node_count, self.hidden_node_count), self.hidden_node_count,
                                      (self.hidden_node_count, self.output_node_count), self.output_node_count)
        neural_net.set_weights_from_genome(self.genome)
        self.last_choice = 1
        self.last_eat_time = 0
        last_choice_x = 1
        last_choice_y = 0
        # Main logic
        while True:
            up_pos = self.snake_pos[1] - 10
            down_pos = self.snake_pos[1] + 10
            left_pos = self.snake_pos[0] - 10
            right_pos = self.snake_pos[0] + 10

            dist_current = calcDistFromPoints(self.snake_pos, self.food_pos)
            dist_up = calcDistFromPoints([self.snake_pos[0], up_pos], self.food_pos)
            dist_down = calcDistFromPoints([self.snake_pos[0], down_pos], self.food_pos)
            dist_left = calcDistFromPoints([left_pos, self.snake_pos[1]], self.food_pos)
            dist_right = calcDistFromPoints([right_pos, self.snake_pos[1]], self.food_pos)

            left_safe = 0
            right_safe = 0
            down_safe = 0
            up_safe = 0

            if up_pos <= 0 or [self.snake_pos[0], up_pos] in self.snake_body:
                up_safe = -1
            else:
                up_safe = 1
            if right_pos >= self.frame_size_y or [right_pos, self.snake_pos[1]] in self.snake_body:
                right_safe = -1
            else:
                right_safe = 1
            if left_pos <= 0 or [left_pos, self.snake_pos[1]] in self.snake_body:
                left_safe = -1
            else:
                left_safe = 1
            if down_pos >= self.frame_size_y or [self.snake_pos[0], down_pos] in self.snake_body:
                down_safe = -1
            else:
                down_safe = 1

            delta_up = dist_current - dist_up
            delta_down = dist_current - dist_down
            delta_left = dist_current - dist_left
            delta_right = dist_current - dist_right

            # Neural net makes a choice
            choice = neural_net.runModel(np.array([[delta_up, delta_down, delta_left, delta_right,
                                                    str(((self.total_ticks - self.last_eat_time) / 100000)),
                                                    last_choice_x, last_choice_y, up_safe, down_safe, left_safe,
                                                    right_safe]], dtype=np.float32))
            self.last_choice = choice
            # Based on choice, set direction to change to
            if choice == 0:
                last_choice_x = 0
                last_choice_y = -1
                if self.direction != 'DOWN':
                    self.change_to = 'UP'
            if choice == 1:
                last_choice_x = 1
                last_choice_y = 0
                if self.direction != 'LEFT':  # up = 0, right = 1, down = 2, left = 3
                    self.change_to = 'RIGHT'
            if choice == 2:
                last_choice_x = 0
                last_choice_y = 1
                if self.direction != 'UP':
                    self.change_to = 'DOWN'
            if choice == 3:
                last_choice_x = -1
                last_choice_y = 0
                if self.direction != 'RIGHT':
                    self.change_to = 'LEFT'
            # Making sure the snake cannot move in the opposite self.direction instantaneously
            if self.change_to == 'UP' and self.direction != 'DOWN':
                self.direction = 'UP'
            if self.change_to == 'DOWN' and self.direction != 'UP':
                self.direction = 'DOWN'
            if self.change_to == 'LEFT' and self.direction != 'RIGHT':
                self.direction = 'LEFT'
            if self.change_to == 'RIGHT' and self.direction != 'LEFT':
                self.direction = 'RIGHT'

            # Moving the snake
            if self.direction == 'UP':
                self.snake_pos[1] -= 10
                self.delta_sum += delta_up
            if self.direction == 'DOWN':
                self.snake_pos[1] += 10
                self.delta_sum += delta_down
            if self.direction == 'LEFT':
                self.snake_pos[0] -= 10
                self.delta_sum += delta_left
            if self.direction == 'RIGHT':
                self.snake_pos[0] += 10
                self.delta_sum += delta_right

            # Snake body growing mechanism
            self.snake_body.insert(0, list(self.snake_pos))
            if self.snake_pos[0] == self.food_pos[0] and self.snake_pos[1] == self.food_pos[1]:
                self.score += 1
                self.food_spawn = False
                self.last_eat_time = self.total_ticks
                last_y_dist_head_to_food = 0
                last_x_dist_head_to_food = 0
            else:
                self.snake_body.pop()

            # Spawning food on the screen
            if not self.food_spawn:
                self.food_pos = [random.randrange(1, (self.frame_size_x // 10)) * 10,
                                 random.randrange(1, (self.frame_size_y // 10)) * 10]
            self.food_spawn = True

            # Game Over conditions -----------------------------------------------
            if self.total_ticks > self.last_eat_time + 100000:
                self.game_over()
                break
            # Getting out of bounds
            if self.snake_pos[0] < 0 or self.snake_pos[0] > self.frame_size_x - 10:
                self.game_over()
                break
            if self.snake_pos[1] < 0 or self.snake_pos[1] > self.frame_size_y - 10:
                self.game_over()
                break
            # Touching the snake body
            for block in self.snake_body[1:]:
                if self.snake_pos[0] == block[0] and self.snake_pos[1] == block[1]:
                    self.game_over()
                    break

            # Refresh rate
            self.fps_controller.tick(self.difficulty)
            self.total_ticks += 100
