import copy
import math

import pygame, sys, time, random
import neuralnet as nn
import numpy as np


def normalize(data, min, max):
    return (data - min) / (max - min)


def calcDistFromPoints(snakehead, food):
    # distance formula (normalized to board size)
    distance = math.sqrt(math.pow((snakehead[0] - food[0]), 2) + math.pow((snakehead[1] - food[1]), 2)) / 850
    return distance


class SnakeGame:
    def __init__(self, difficulty, genome, pygame=pygame):
        frame_size_x = 720
        frame_size_y = 480

        self.black = pygame.Color(0, 0, 0)
        self.white = pygame.Color(255, 255, 255)
        self.red = pygame.Color(255, 0, 0)
        self.green = pygame.Color(0, 255, 0)
        self.blue = pygame.Color(0, 0, 255)
        self.magenta = pygame.Color(255, 0, 255)

        pygame.display.set_caption('Snake Eater')
        self.game_window = pygame.display.set_mode((frame_size_x, frame_size_y))
        self.delta_sum = 0
        self.last_eat_time = None
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
        my_font = pygame.font.SysFont('times new roman', 90)
        game_over_surface = my_font.render('YOU DIED', True, self.red)
        game_over_rect = game_over_surface.get_rect()
        game_over_rect.midtop = (self.frame_size_x/2, self.frame_size_y/4)
        self.game_window.fill(self.black)
        self.game_window.blit(game_over_surface, game_over_rect)
        self.show_score(0)
        pygame.display.flip()
        time.sleep(3)
        pygame.quit()
        #sys.exit()

    def show_score(self, choice):
        score_font = pygame.font.SysFont('consolas', 20)
        score_surface = score_font.render('Score : ' + str(self.score), True, self.white)
        score_rect = score_surface.get_rect()
        if choice == 1:
            score_rect.midtop = (self.frame_size_x/10, 15)
        else:
            score_rect.midtop = (self.frame_size_x/2, self.frame_size_y/1.25)
        self.game_window.blit(score_surface, score_rect)
        # pygame.display.flip()

    def runGame(self):
        # Initialise game window
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

            # test if directional move is safe for NN inputs
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

            # get change in distance between current position and each possible next position for NN inputs
            delta_up = dist_current - dist_up
            delta_down = dist_current - dist_down
            delta_left = dist_current - dist_left
            delta_right = dist_current - dist_right

            # Test if there is a body piece in the closest path of length 4 to the food for NN input
            body_in_way = 0
            loops = 0
            x_dif = math.fabs(self.snake_pos[0] - self.food_pos[0])
            y_dif = math.fabs(self.snake_pos[1] - self.food_pos[1])
            new_pos = copy.deepcopy(self.snake_pos)
            while (x_dif > 0 or y_dif > 0) and loops < 4:
                if new_pos[0] < self.food_pos[0]:
                    new_pos[0] += 10
                    if new_pos in self.snake_body:
                        body_in_way = 1
                        break
                elif new_pos[0] > self.food_pos[0]:
                    new_pos[0] -= 10
                    if new_pos in self.snake_body:
                        body_in_way = 1
                        break
                if new_pos[1] < self.food_pos[1]:
                    new_pos[1] += 10
                    if new_pos in self.snake_body:
                        body_in_way = 1
                        break
                elif new_pos[1] > self.food_pos[1]:
                    new_pos[1] -= 10
                    if new_pos in self.snake_body:
                        body_in_way = 1
                        break
                loops += 1
                x_dif = math.fabs(new_pos[0] - self.food_pos[0])
                y_dif = math.fabs(new_pos[1] - self.food_pos[1])

            # Neural net makes a choice
            nn_choice = self.genome(np.array([delta_up * 85, delta_down * 85, delta_left * 85, delta_right * 85,
                                              str((1 - ((self.total_ticks - self.last_eat_time) / 100000))),
                                              body_in_way,
                                              up_safe, down_safe, left_safe,
                                              right_safe], dtype=np.float32))  # last_choice_x, last_choice_y,
            if nn_choice[0] > nn_choice[1] and nn_choice[0] > nn_choice[2] and nn_choice[0] > nn_choice[3]:
                choice = 0
            elif nn_choice[1] > nn_choice[0] and nn_choice[1] > nn_choice[2] and nn_choice[1] > nn_choice[3]:
                choice = 1
            elif nn_choice[2] > nn_choice[0] and nn_choice[2] > nn_choice[1] and nn_choice[2] > nn_choice[3]:
                choice = 2
            else:
                choice = 3

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

            self.game_window.fill(self.black)
            body_part = 0
            for pos in self.snake_body:
                # Snake body
                # .draw.rect(play_surface, color, xy-coordinate)
                # xy-coordinate -> .Rect(x, y, size_x, size_y)
                if body_part == 0:
                    pygame.draw.rect(self.game_window, self.magenta, pygame.Rect(pos[0], pos[1], 10, 10))
                else:
                    pygame.draw.rect(self.game_window, self.green, pygame.Rect(pos[0], pos[1], 10, 10))

                body_part += 1

            pygame.draw.rect(self.game_window, self.white, pygame.Rect(self.food_pos[0], self.food_pos[1], 10, 10))

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

            self.show_score(1)
            # Refresh game screen
            pygame.display.update()

            # Refresh rate
            self.fps_controller.tick(self.difficulty)
            self.total_ticks += 100
