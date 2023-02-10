import pygame, sys, time, random
# import kerastest as kt
import neuralnet as nn
import numpy as np

class SnakeGame:
    def __init__(self, difficulty, genome, pygame):    
        # Difficulty settings
        # Easy      ->  10
        # Medium    ->  25
        # Hard      ->  40
        # Harder    ->  60
        # Impossible->  120
        self.difficulty = difficulty
        self.genome = genome
        # Window size
        self.frame_size_x = 720
        self.frame_size_y = 480

        self.total_ticks = 0
        # Checks for errors encountered
        check_errors = pygame.init()
        # pygame.init() example output -> (6, 0)
        # second number in tuple gives number of errors
        if check_errors[1] > 0:
            print(f'[!] Had {check_errors[1]} errors when initialising game, exiting...')
            sys.exit(-1)
        else:
            print('[+] Game successfully initialised')
        
        # Colors (R, G, B)
        self.black = pygame.Color(0, 0, 0)
        self.white = pygame.Color(255, 255, 255)
        self.red = pygame.Color(255, 0, 0)
        self.green = pygame.Color(0, 255, 0)
        self.blue = pygame.Color(0, 0, 255)
        self.magenta = pygame.Color(255, 0, 255)

        # FPS (frames per second) controller
        self.fps_controller = pygame.time.Clock()

        # Game variables
        self.snake_pos = [100, 50]
        self.snake_body = [[100, 50], [100-10, 50], [100-(2*10), 50]]

        self.food_pos = [random.randrange(1, (self.frame_size_x//10)) * 10, random.randrange(1, (self.frame_size_y//10)) * 10]
        self.food_spawn = True

        self.direction = 'RIGHT'
        self.change_to = self.direction

        self.score = 0
        # Initialise game window
        pygame.display.set_caption('Snake Eater')
        self.game_window = pygame.display.set_mode((self.frame_size_x, self.frame_size_y))
        self.pygame = pygame


    # Game Over
    def game_over(self):
        pygame.quit()
        #sys.exit()

    def runGame(self):
        # Initialise game window
        pygame.display.set_caption('Snake Eater')
        game_window = pygame.display.set_mode((self.frame_size_x, self.frame_size_y))

        neural_net = nn.NeuralNetwork((3, ), 3, (3, 5), 5, (5, 4), 4)
        neural_net.set_weights_from_genome(self.genome)

        # Main logic
        while True:
            choice = neural_net.runModel(np.array([[self.food_pos[0], self.snake_pos[0], self.food_pos[1]]], dtype=np.float32))
            
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    print('total_ticks ' + str(self.total_ticks))
                    print('score ' + str(self.score))
                    break
                    #sys.exit()
                # Whenever a key is pressed down
                elif event.type == pygame.KEYDOWN:
                    # W -> Up; S -> Down; A -> Left; D -> Right
                    if event.key == pygame.K_UP or event.key == ord('w'):
                        self.change_to = 'UP'
                    if event.key == pygame.K_DOWN or event.key == ord('s'):
                        self.change_to = 'DOWN'
                    if event.key == pygame.K_LEFT or event.key == ord('a'):
                        self.change_to = 'LEFT'
                    if event.key == pygame.K_RIGHT or event.key == ord('d'):
                        self.change_to = 'RIGHT'
                    # Esc -> Create event to quit the game
                    if event.key == pygame.K_ESCAPE:
                        pygame.event.post(pygame.event.Event(pygame.QUIT))
                # running AI
                else:
                    # choice = nn.runModel(np.array([[food_pos[0], snake_pos[0], food_pos[1]]], dtype=np.float32))
                    if choice == 0:
                        self.change_to = 'UP'
                    if choice == 1:
                        self.change_to = 'RIGHT'
                    if choice == 2:
                        self.change_to = 'DOWN'
                    if choice == 3:
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
            if self.direction == 'DOWN':
                self.snake_pos[1] += 10
            if self.direction == 'LEFT':
                self.snake_pos[0] -= 10
            if self.direction == 'RIGHT':
                self.snake_pos[0] += 10

            # Snake body growing mechanism
            self.snake_body.insert(0, list(self.snake_pos))
            if self.snake_pos[0] == self.food_pos[0] and self.snake_pos[1] == self.food_pos[1]:
                self.score += 1
                self.food_spawn = False
            else:
                self.snake_body.pop()

            # Spawning food on the screen
            if not self.food_spawn:
                self.food_pos = [random.randrange(1, (self.frame_size_x//10)) * 10, random.randrange(1, (self.frame_size_y//10)) * 10]
            self.food_spawn = True

            # GFX
            game_window.fill(self.black)
            body_part = 0
            for pos in self.snake_body:
                # Snake body
                # .draw.rect(play_surface, color, xy-coordinate)
                # xy-coordinate -> .Rect(x, y, size_x, size_y)
                if body_part == 0:
                    pygame.draw.rect(game_window, self.magenta, pygame.Rect(pos[0], pos[1], 10, 10))
                else:
                    pygame.draw.rect(game_window, self.green, pygame.Rect(pos[0], pos[1], 10, 10))

                body_part += 1

            # Snake food
            pygame.draw.rect(game_window, self.white, pygame.Rect(self.food_pos[0], self.food_pos[1], 10, 10))

            # Game Over conditions
            # Getting out of bounds
            if self.snake_pos[0] < 0 or self.snake_pos[0] > self.frame_size_x-10:
                self.game_over()
                print('total_ticks ' + str(self.total_ticks))
                print('score ' + str(self.score))
                break
            if self.snake_pos[1] < 0 or self.snake_pos[1] > self.frame_size_y-10:
                self.game_over()
                print('total_ticks ' + str(self.total_ticks))
                print('score ' + str(self.score))
                break
            # Touching the snake body
            for block in self.snake_body[1:]:
                if self.snake_pos[0] == block[0] and self.snake_pos[1] == block[1]:
                    self.game_over()
                    print('total_ticks ' + str(self.total_ticks))
                    print('score ' + str(self.score))
                    break
            # Refresh game screen
            pygame.display.update()
            # Refresh rate
            self.fps_controller.tick(self.difficulty)
            self.total_ticks += self.difficulty