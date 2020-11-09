#!/usr/bin/python3

# Copyright (c) 2017, 2020 Samuel Thibault <samuel.thibault@ens-lyon.org>
# All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without
# modification, are permitted provided that the following conditions
# are met:
# 1. Redistributions of source code must retain the above copyright
#    notice, this list of conditions and the following disclaimer.
# 2. Redistributions in binary form must reproduce the above copyright
#    notice, this list of conditions and the following disclaimer in the
#    documentation and/or other materials provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY Samuel Thibault ``AS IS'' AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
# IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE
# ARE DISCLAIMED.  IN NO EVENT SHALL THE REGENTS OR CONTRIBUTORS BE LIABLE
# FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL
# DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS
# OR SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION)
# HOWEVER CAUSED AND ON ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT
# LIABILITY, OR TORT (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY
# OUT OF THE USE OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF
# SUCH DAMAGE.

# import libraries
import sys
import pygame
from threading import Thread
import random
from gamelib import countdown

GAME__STATUS_LOBBY = 0
GAME__STATUS_PRESTART = 1
GAME__STATUS_START = 2

# global variables
window = None
game = None


# main function
def main():
    global window
    global game

    game = Game()
    window = GameWindow()

    window.game = game

    window.start()
    game.prestart()


# GameWindow Class
#   This class contain the main loop of the game (started in a thread)
#   It contain the window's game too
#   At the init. of the class, the window is setup
class GameWindow(Thread):
    def __init__(self):
        # Screen setup
        self.size = self.width, self.height = 1280, 720
        self.bgcolor = (0xFF,0x55,0x55)
        
        # Pygame initialization
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)

        Thread.__init__(self)

    def run(self):
        while True:
            self.game.loop()
            pygame.display.flip()
            pygame.time.delay(10)




# Game class
#   This class manage (action and checking) all entities that is present on the screen
class Game:
    def __init__(self):
        self.status = GAME__STATUS_LOBBY
        self.balls = []
        self.score = [0,0]

        for i in range(0,1):
            ball = Ball()
            self.balls.append(ball)


        self.players = [Player(0)]

    # Prestart the game
    def prestart(self): 
        self.status = GAME__STATUS_PRESTART
        for player in self.players:
            player.positionning()

        for ball in self.balls:
            ball.positionning()
        
        cd = countdown.Countdown(5000, self.start)
        cd.addPerMSFunc(countdown.CD_PER_D1000, self.displayCountdown, "{CD_PER_D1000}")
        cd.start()

    # Start the game 
    def start(self):
        self.status = GAME__STATUS_START
        for ball in self.balls:
            ball.throw()
            ball.launched = True

        self.updateScore()

        self.displayCountdown("Go !")
        cd = countdown.Countdown(2000, self.displayCountdown, "")
        cd.start()
    
    def displayCountdown(self, dtext):
        if isinstance(dtext, str) == False:
            dtext = dtext[0]

        global window

        font = pygame.font.Font(pygame.font.get_default_font(), 128)
        self.display_text = font.render(dtext, True, (255,255,255), (255,85,85))
        self.display_text_coords = self.display_text.get_rect()
        self.display_text_coords.center = (window.width / 2, window.height / 2)
    
    # Update scoreboard
    def updateScore(self):
        global window
        font = pygame.font.Font(pygame.font.get_default_font(), 32)
        self.scoreboard = font.render('%d | %d' % (self.score[0], self.score[1]), True, (255,255,255), (255,85,85))
        self.scoreboard_coords = self.scoreboard.get_rect()
        self.scoreboard_coords.center = (window.width / 2, self.scoreboard_coords.height)

    # This function manage all entities move
    def loop(self):
        global window

        if self.status == GAME__STATUS_START:
            for player in self.players:
                player.checkMove()
                player.move()
        
            for ball in self.balls:
                if ball.launched == False:
                    continue

                ball.move()
        
                # check if ball hit border
                border_reached = ball.getBorderReached()
            
                if border_reached > -1:
                    # print("border %d reached" % (border_reached))


                    # check if someone in the team hit the ball
                    hit = False
                    for player in self.players:
                        if player.team == border_reached:
                            if ball.isHit(player):
                                hit = True
                                break
                
                    if hit == False:
                        if border_reached == 0:
                            self.score[1] += 1
                        elif border_reached == 1:
                            self.score[0] += 1

                        self.updateScore()
                        # print("Team %d lost the round" % (border_reached))
                        # print("ball.x = %d" % (ball.ball_coords.left))


        # Display entities
        window.screen.fill(window.bgcolor)

        if hasattr(self, 'display_text') and hasattr(self, 'display_text_coords'):
            window.screen.blit(self.display_text, self.display_text_coords)
        
        if self.status == GAME__STATUS_START:
            try:
                window.screen.blit(self.scoreboard, self.scoreboard_coords)
            except AttributeError:
                self.updateScore()

        for player in self.players:
            player.render()

        for ball in self.balls:
            ball.render()


# Ball class
#   Ball entity's class with some checking and action
class Ball:
    def __init__(self):
        self.ball_speed = [0, 0]
        
        self._ball = pygame.image.load("image/ball.png")
        self.ball_coords = self._ball.get_rect()
        
        # fix : border hit before the ball has been throwed
        self.launched = False

    # Positionning the ball before the beginning of the game
    def positionning(self):
        global window
        window_middle = window.width / 2
        sw = random.randint(window_middle - 200, window_middle + 200)
        # print("spawn x : %d" % (sw))
        self.ball_coords.left = sw
        
        sh = random.randint(100, window.height - 100)
        self.ball_coords.top = sh

    # Throw the ball at the beginning of the game
    def throw(self):
        global window
        window_middle = window.width / 2
        
        speed = random.randint(5, 5)

        if self.ball_coords.left < window_middle / 2:
            vw = speed
        else:
            vw = -speed
        
        if self.ball_coords.top < window.height / 2:
            vh = -speed
        else:
            vh = speed

        self.ball_speed = [vw, vh]


    # Check if the ball reached the border
    #   return 0  for border left
    #   return 1  for border right
    #   return -1  doesn't reach the border
    def getBorderReached(self):
        global window
        if self.ball_coords.left <= 0: 
            return 0
        elif self.ball_coords.right >= window.width:
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
        if self.ball_coords.left <= 0 or self.ball_coords.right >= window.width:
            self.ball_speed[0] = -self.ball_speed[0]
        if self.ball_coords.top <= 0 or self.ball_coords.bottom >= window.height:
            self.ball_speed[1] = -self.ball_speed[1]

    # Render the entity
    def render(self):
        window.screen.blit(self._ball, self.ball_coords)


# Player class
#   Player entity's class with some checking and action
class Player:
    def __init__(self, team):
        self.team = team
        self.racket_speed = [0, 0]
        self.racket = pygame.image.load("image/racket.png")
        self.racket_coords = self.racket.get_rect()

    # Positionning the racket before the beginning of the game
    # Allow, if the player is in team 1, to position his racket on the right side of the window
    def positionning(self):
        if self.team == 1:
            global window
            self.racket_coords.right = window.width

    # Move the racket
    def move(self):
        # Move racket
        self.racket_coords = self.racket_coords.move(self.racket_speed)
        # Clip racket on court
        if self.racket_coords.left < 0:
            self.racket_coords.left = 0
        elif self.racket_coords.right >= window.width:
            self.racket_coords.right = window.width-1
        if self.racket_coords.top < 0:
            self.racket_coords.top = 0
        elif self.racket_coords.bottom >= window.height:
            self.racket_coords.bottom = window.height-1
    
    # Listen keyboard
    def checkMove(self):
        for e in pygame.event.get():
            # Check for exit
            if e.type == pygame.QUIT:
                sys.exit()

            # Check for racket movements
            elif e.type == pygame.KEYDOWN:
                if e.key == pygame.K_UP:
                    self.racket_speed[1] = -4
                    pass
                elif e.key == pygame.K_DOWN:
                    self.racket_speed[1] = 4
                    pass

            elif e.type == pygame.KEYUP:
                if e.key == pygame.K_UP:
                    self.racket_speed[1] = 0
                    pass
                elif e.key == pygame.K_DOWN:
                    self.racket_speed[1] = 0
                    pass
    
    # Render the entity
    def render(self):
        global window
        window.screen.blit(self.racket, self.racket_coords)

main()
