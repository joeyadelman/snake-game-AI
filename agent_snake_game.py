import pygame
import random
from enum import Enum
from collections import namedtuple
import numpy as np

pygame.init()
font = pygame.font.Font('arial.ttf', 25)

# reset function after each game
# implement reward
# change play function to take an action to compute direction
# game iteration
# is_collsion


class Direction(Enum):
    RIGHT = 1
    LEFT = 2
    UP = 3
    DOWN = 4


Point = namedtuple('Point', 'x, y')

# Colors
WHITE = (255, 255, 255)
RED = (200, 0, 0)
BLUE1 = (0, 0, 255)
BLUE2 = (0, 100, 255)
BLACK = (0, 0, 0)

BLOCK_SIZE = 20
SPEED = 500

GAME_PIXELS = 768
class SnakeGameAI:
    def __init__(self, w=640, h=480):
        self.w = w
        self.h = h
        # init display
        self.display = pygame.display.set_mode((self.w, self.h))
        pygame.display.set_caption('Snake Game')
        self.clock = pygame.time.Clock()

        self.reset()

    def reset(self):
        # init the game state
        self.direction = Direction.RIGHT
        self.head = Point(self.w / 2, self.h / 2)
        # intial snake
        self.snake = [self.head, Point(self.head.x - BLOCK_SIZE, self.head.y),
                      Point(self.head.x - (2 * BLOCK_SIZE), self.head.y)]

        self.score = 0
        self.food = None
        self._place_food()
        self.frame_iteration = 0

    def _place_food(self):
        x = random.randint(0, (self.w - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        y = random.randint(0, (self.h - BLOCK_SIZE) // BLOCK_SIZE) * BLOCK_SIZE
        self.food = Point(x, y)
        if self.food in self.snake:
            self._place_food()

    def play_step(self, action):
        self.can_find_tail()
        self.frame_iteration += 1
        # collect user input (key press)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                quit()

        # move snake
        self._move(self.direction, action)
        # Update the head
        self.snake.insert(0, self.head)

        # check if the game is over
        reward = 0
        game_over = False
        if self.is_collision() or self.frame_iteration > 100*len(self.snake):
            game_over = True
            reward = -20
            return reward, game_over, self.score

        if self.head == self.food:
            self.score += 1
            reward = 10
            self._place_food()
        else:
            self.snake.pop()
        # update the clock and game ui
        self.update_ui()
        self.clock.tick(SPEED)
        # return if game is over and the score
        return reward, game_over, self.score

    def is_collision(self, pt=None):
        if pt is None:
            pt = self.head
        # Check if hit boundary
        if pt.x > self.w - BLOCK_SIZE or pt.x < 0 or pt.y > self.h - BLOCK_SIZE or pt.y < 0:
            return True
        # Check if hit self
        if pt in self.snake[1:]:
            return True

        return False

    def update_ui(self):
        self.display.fill(BLACK)

        for pt in self.snake:
            pygame.draw.rect(self.display, BLUE1, pygame.Rect(pt.x, pt.y, BLOCK_SIZE, BLOCK_SIZE))
            pygame.draw.rect(self.display, BLUE2, pygame.Rect(pt.x + 4, pt.y + 4, 12, 12))

        pygame.draw.rect(self.display, RED, pygame.Rect(self.food.x, self.food.y, BLOCK_SIZE, BLOCK_SIZE))

        text = font.render("Score: " + str(self.score), True, WHITE)
        self.display.blit(text, [0, 0])
        pygame.display.flip()

    def _move(self, direction, action):
        # [straight, left, right]
        clock_wise = [Direction.RIGHT, Direction.DOWN, Direction.LEFT, Direction.UP]
        index = clock_wise.index(self.direction)

        if np.array_equal(action, [1, 0, 0]): # straight
            new_direction = clock_wise[index]
        elif np.array_equal(action, [0, 1, 0]): # right turn
            new_direction = clock_wise[(index + 1) % 4]
        else: # left turn [0, 0, 1]
            new_direction = clock_wise[(index - 1) % 4]

        self.direction = new_direction
        x = self.head.x
        y = self.head.y

        if self.direction == Direction.RIGHT:
            x += BLOCK_SIZE
        elif self.direction == Direction.LEFT:
            x -= BLOCK_SIZE
        elif self.direction == Direction.UP:
            y -= BLOCK_SIZE
        elif self.direction == Direction.DOWN:
            y += BLOCK_SIZE

        self.head = Point(x, y)

    def can_find_tail(self):
        # can the head of the snake find the tail of the snake
        index = -1
        head_pos = Point(self.head.x, self.head.y)
        tail_pos = Point(self.snake[-1].x, self.snake[-1].y)
        blocks = [Point(head_pos.x+BLOCK_SIZE, head_pos.y), Point(head_pos.x, head_pos.y+BLOCK_SIZE),
                  Point(head_pos.x-BLOCK_SIZE, head_pos.y), Point(head_pos.x, head_pos.y-BLOCK_SIZE)]
        for block in blocks:
            index += 1
            if block.x == self.snake[-1].x and block.y == self.snake[-1].y:
                return True
            elif block in self.snake:
                blocks.pop(index)
            point = Point(head_pos.x+BLOCK_SIZE, head_pos.y)
            if block in blocks:
                pass
            else:
                blocks.append(block)

        return False

