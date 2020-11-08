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

import sys
import pygame
from threading import Thread
import random

window = None
game = None

def main():
    global window
    global game

    game = Game()
    window = GameWindow()

    window.game = game

    window.start()
    game.start()

class GameWindow(Thread):
    def __init__(self):
        # Screen setup
        self.size = self.width, self.height = 1280, 720
        self.bgcolor = (0xCC,0xCC,0xCC)
        
        # Pygame initialization
        pygame.init()
        self.screen = pygame.display.set_mode(self.size)

        Thread.__init__(self)

    def run(self):
        while True:
            self.game.loop()
            pygame.display.flip()
            pygame.time.delay(10)

class Game:
    def __init__(self):
        self.balls = []

        for i in range(0,1):
            ball = Ball()
            self.balls.append(ball)


        self.players = [Player(0)]

    def start(self):
        for ball in self.balls:
            ball.throw()
        
    def loop(self):
        global window
        for player in self.players:
            player.checkMove()
            player.move()
        
        for ball in self.balls:
            ball.move()
        
            # Racket reached racket position?
            border_reached = ball.getBorderReached()
            
            if border_reached > -1:
                # print("border %d reached" % (border_reached))

                hit = False
                for player in self.players:
                    if player.team == border_reached:
                        if ball.isHit(player):
                            hit = True
                            break

                if hit == False:
                    if ball.launched == False:
                        ball.launched = True
                    else:
                        print("Team %d lost the round" % (border_reached))

        # Display everything
        window.screen.fill(window.bgcolor)
        
        for player in self.players:
            player.render()

        for ball in self.balls:
            ball.render()


class Ball:
    def __init__(self):
        self.ball_speed = [0, 0]
        
        self._ball = pygame.image.load("image/ball.png")
        self.ball_coords = self._ball.get_rect()

        self.launched = False

    def throw(self):
        global window
        window_middle = window.width / 2
        sw = random.randint(window_middle - 200, window_middle + 200)
        print("spawn x : %d" % (sw))
        self.ball_coords.left = sw
        
        
        speed = random.randint(2, 5)

        if sw < window_middle / 2:
            vw = speed
        else:
            vw = -speed
        
        sh = random.randint(10, window.height - 10)
        self.ball_coords.top = sh

        vh = speed

        self.ball_speed = [vw, vh]


    def getBorderReached(self):
        global window
        if self.ball_coords.left <= 0: 
            return 0
        elif self.ball_coords.right >= window.width:
            return 1
        else:
            return -1

    def isHit(self, player):
        return (self.ball_coords.bottom <= player.racket_coords.top or self.ball_coords.top >= player.racket_coords.bottom) == False

    def move(self):
        # Move ball
        self.ball_coords = self.ball_coords.move(self.ball_speed)
        # Bounce ball on walls
        if self.ball_coords.left < 0 or self.ball_coords.right >= window.width:
            self.ball_speed[0] = -self.ball_speed[0]
        if self.ball_coords.top < 0 or self.ball_coords.bottom >= window.height:
            self.ball_speed[1] = -self.ball_speed[1]

    def render(self):
        window.screen.blit(self._ball, self.ball_coords)


class Player:
    def __init__(self, team):
        self.team = team
        self.racket_speed = [0, 0]
        self.racket = pygame.image.load("image/racket.png")
        self.racket_coords = self.racket.get_rect()

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

    def render(self):
        global window
        window.screen.blit(self.racket, self.racket_coords)

main()
