import pygame
import random

# Ball class
#   Ball entity's class with some checking and action
class Ball:
    ball_idc = 0

    def __init__(self, window):
        self.window = window

        self.id = Ball.ball_idc
        Ball.ball_idc += 1

        self.ball_speed = [0, 0]
        
        self._ball = pygame.image.load("image/ball.png")
        self.ball_coords = self._ball.get_rect()
        
        # fix : border hit before the ball has been throwed
        self.launched = False

    # Positionning the ball before the beginning of the game
    def positionning(self):
        window_middle = self.window.width / 2
        sw = random.randint(window_middle - 200, window_middle + 200)
        # print("spawn x : %d" % (sw))
        self.ball_coords.left = sw
        
        sh = random.randint(100, self.window.height - 100)
        self.ball_coords.top = sh


    # Throw the ball at the beginning of the game
    def throw(self):
        window_middle = self.window.width / 2
        
        speed = random.randint(5, 5)

        if self.ball_coords.left < window_middle / 2:
            vw = speed
        else:
            vw = -speed
        
        if self.ball_coords.top < self.window.height / 2:
            vh = -speed
        else:
            vh = speed

        self.ball_speed = [vw, vh]


    # Check if the ball reached the border
    #   return 0  for border left
    #   return 1  for border right
    #   return -1  doesn't reach the border
    def getBorderReached(self):
        if self.ball_coords.left <= 0:
            return 0
        elif self.ball_coords.right >= self.window.width:
            return 1
        else:
            return -1

    # Check if 'player' hit the ball
    def isHit(self, player):
        return (self.ball_coords.bottom <= player.racket_coords.top or self.ball_coords.top >= player.racket_coords.bottom) == False

    def move(self):
        # Move ball
        self.ball_coords = self.ball_coords.move(self.ball_speed)
        # Bounce ball on walls
        if self.ball_coords.left <= 0 or self.ball_coords.right >= self.window.width:
            self.ball_speed[0] = -self.ball_speed[0]
        if self.ball_coords.top <= 0 or self.ball_coords.bottom >= self.window.height:
            self.ball_speed[1] = -self.ball_speed[1]

    # Render the entity
    def render(self):
        self.window.screen.blit(self._ball, self.ball_coords)
