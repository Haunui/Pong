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
from socketlib import serversocket, clientsocket

GAME__SOCKET_SERVER = 0
GAME__SOCKET_CLIENT = 1

GAME__STATUS_LOBBY = 0
GAME__STATUS_WAITING_FOR_PLAYER = 1
GAME__STATUS_PRESTART = 2
GAME__STATUS_START = 3

GAME__TEXT_SIZE__WAITING_FOR_PLAYER = 64
GAME__TEXT_SIZE__COUNTDOWN = 128

# global variables
core = None
window = None
game = None
gamesock = None

player_idc = 0
ball_idc = 0

# main function
def main():
    global core
    global window
    global game
    global gamesock

    _type = ""
    ip = ""
    port = -1

    while True:
        _type = input("Mode (server, client):\n")
        if _type == "server" or _type == "client":
            break
        else:
            print("Mode not found")

    ip = input("IP Address:\n")
    
    while True:
        try:
            port = int(input("Port:\n"))
            break
        except:
            print("Invalid port")


    core = GameCore(10)

    if _type == "server":
        gamesock = GameSocket(GAME__SOCKET_SERVER, (ip, port))
    else:
        gamesock = GameSocket(GAME__SOCKET_CLIENT, (ip, port))

    window = GameWindow()
    model = Game()
    core.model = model
    core.start()

    core.status = GAME__STATUS_WAITING_FOR_PLAYER

    if gamesock.status == GAME__SOCKET_CLIENT:
        gamesock.send(None, ['check', 'connect'])


class GameCore(Thread):
    def __init__(self, delay):
        self.status = GAME__STATUS_LOBBY
        self.delay = delay
        pygame.init()
        Thread.__init__(self)

    def run(self):
        while True:
            self.model.loop()
            self.model.render()
            pygame.display.flip()
            pygame.time.delay(self.delay)


# GameWindow Class
#   This class contain the main loop of the game (started in a thread)
#   It contain the window's game too
#   At the init. of the class, the window is setup
class GameWindow:
    def __init__(self):
        # Screen setup
        self.size = self.width, self.height = 1280, 720
        self.bgcolor = (0xFF,0x55,0x55)
        self.screen = pygame.display.set_mode(self.size)


class GameSocket:
    def __init__(self, status, addr):
        self.delay = core.delay

        self.status = status
        self.addr = addr
        
        if self.status == GAME__SOCKET_SERVER:
            self.sock = serversocket.SocketServer(self.addr)
            serversocket.addActions("game", "game", self.receive)
        elif self.status == GAME__SOCKET_CLIENT:
            self.sock = clientsocket.SocketClient(self.addr)
            clientsocket.addActions("game", "game", self.receive)

        self.sock.start()


    def send(self, socket, datas):
        datas = {'type': 'custom', 'value': {'cat': 'game', 'func': 'game', 'args': datas}}
        if self.status == GAME__SOCKET_CLIENT:
            self.sock.send(datas)
        else:
            if socket == None:
                self.sock.sendtoall(datas)
            else:
                self.sock.send(socket, datas)

    def sendexcept(self, socket, datas):
        datas = {'type': 'custom', 'value': {'cat': 'game', 'func': 'game', 'args': datas}}
        self.sock.sendexcept(socket, datas)

    def receive(self, socket, args):
        _type = args[0]

        if _type == "action":
            action = args[1]
            
            if core.status == GAME__STATUS_WAITING_FOR_PLAYER or core.status == GAME__STATUS_PRESTART or core.status == GAME__STATUS_START:
                if action == "prestart":
                    if self.status == GAME__SOCKET_CLIENT:
                        core.model.prestart(args[2])
                if action == "move":
                    entity = args[2]
                    ident = args[3]
                    x = args[4]
                    y = args[5]

                    if entity == "ball":
                        if self.status == GAME__SOCKET_CLIENT:
                            for ball in core.model.balls:
                                if ball.id == ident:
                                    ball.ball_coords.center = (x, y)
                                    break
                    elif entity == "player": 
                        for player in core.model.players:
                            if player.id == ident:
                                player.racket_coords.center = (x, y)
                                break
                
                    if self.status == GAME__SOCKET_SERVER:
                        gamesock.sendexcept(socket, [_type, action, entity, ident, x, y])
       

        if core.status == GAME__STATUS_WAITING_FOR_PLAYER or core.status == GAME__STATUS_PRESTART or core.status == GAME__STATUS_START:
            if _type == "check":    
                check = args[1]
                if self.status == GAME__SOCKET_SERVER:
                    if check == "connect":
                        cdt = 5
                        core.model.prestart(cdt)
                        gamesock.send(None, ['action', 'prestart',cdt])

                elif self.status == GAME__SOCKET_CLIENT:

                    if check == "updatescore":
                        team = args[2]
                        core.model.score[team] += 1
                        core.model.updateScore()

            elif _type == "config":
                if self.status == GAME__SOCKET_CLIENT:
                    config = args[1]
                    if config == "delay":
                        core.delay = args[2]


class Model:
    def __init__(self):
        self.displayer = Displayer()

    def loop(self):
        pass

    def render(self):
        # Display entities
        window.screen.fill(window.bgcolor)

        if hasattr(self.displayer, 'display_text') and hasattr(self.displayer, 'display_text_coords'):
            window.screen.blit(self.displayer.display_text, self.displayer.display_text_coords)



class AbstractGame(Model):
    def prestart(self, cdt):
        global core
        core.status = GAME__STATUS_PRESTART
        cd = countdown.Countdown(cdt * 1000, self.start)
        cd.addPerMSFunc(countdown.CD_PER_D1000, self.displayer.displayText, "{CD_PER_D1000}", GAME__TEXT_SIZE__COUNTDOWN)
        cd.start()

    def start(self):
        global core
        core.status = GAME__STATUS_START
        
        self.updateScore()

        self.displayer.displayText(["Go !", GAME__TEXT_SIZE__COUNTDOWN])
        cd = countdown.Countdown(2000, self.displayer.hideText)
        cd.start()


    # Update scoreboard
    def updateScore(self):
        self.displayer.displayScoreboard(self.score[0])

    # This function manage all entities move
    def loop(self):
        global window
        global gamesock
        
        if core.status == GAME__STATUS_START:
            for player in self.players:
                if isinstance(player, LocalPlayer):
                    player.checkMove()
                    player.move()
                    self.onPlayerMove(player)


            if gamesock.status == GAME__SOCKET_SERVER:
                for ball in self.balls:
                    if ball.launched == False:
                        continue

                    ball.move()
                    self.onBallMove(ball)
        
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
                                scorer = 1
                            else:
                                scorer = 0

                            self.onScore(border_reached)
                            

    def onBallMove(self, ball):
        raise NotImplementedError("Please Implement this method")

    def onPlayerMove(self, player):
        raise NotImplementedError("Please Implement this method")

    def onScore(self, scorer):
        raise NotImplementedError("Please Implement this method")

    def render(self):
        Model.render(self)
        if core.status == GAME__STATUS_START:
            if hasattr(self.displayer, 'scoreboard') and hasattr(self.displayer, 'scoreboard_coords'):
                window.screen.blit(self.displayer.scoreboard, self.displayer.scoreboard_coords)

        for player in self.players:
            player.render()

        for ball in self.balls:
            ball.render()


class Displayer:
    def displayText(self, args):
        if isinstance(args, str) == False:
            dtext = args[0]
            dtext_size = args[1]

        global window

        font = pygame.font.Font(pygame.font.get_default_font(), dtext_size)
        self.display_text = font.render(dtext, True, (255,255,255), (255,85,85))
        self.display_text_coords = self.display_text.get_rect()
        self.display_text_coords.center = (window.width / 2, window.height / 2)

    def hideText(self):
        self.displayText(["", 0])

    def displayScoreboard(self, scores):
        font = pygame.font.Font(pygame.font.get_default_font(), 32)
        self.scoreboard = font.render('%s' % (scores), True, (255,255,255), (255,85,85))
        self.scoreboard_coords = self.scoreboard.get_rect()
        self.scoreboard_coords.center = (window.width / 2, self.scoreboard_coords.height)

    def hideScoreboard(self): 
        self.displayScoreboard(self, scores)


# Game class
#   This class manage (action and checking) all entities that is present on the screen
class Game(AbstractGame):
    def __init__(self):
        Model.__init__(self)
        self.balls = []
        self.score = [0,0]

        for i in range(0,1):
            ball = Ball()
            self.balls.append(ball)
        
        self.players = [LocalPlayer(0)]
        
        self.prestart(5)


    # Prestart the game
    def prestart(self, cdt): 
        AbstractGame.prestart(self, cdt)

        for player in self.players:
            player.positionning()
    
        for ball in self.balls:
            ball.positionning()
        

    # Start the game 
    def start(self):
        AbstractGame.start(self)

        for ball in self.balls:
            ball.throw()
            ball.launched = True


    def onBorderReached(self, border):
        if self.players[0].team == border:
            self.score[self.players[0].team] += 1
            self.updateScore()


class OnlineGame(AbstractGame):
    def __init__(self):
        Model.__init__(self)
        self.balls = []
        self.score = [0,0]

        for i in range(0,1):
            ball = Ball()
            self.balls.append(ball)
        

        global gamesock
        if gamesock.status == GAME__SOCKET_SERVER:
            self.players = [LocalPlayer(0), Player(1)]
        elif gamesock.status == GAME__SOCKET_CLIENT:    
            self.players = [Player(0), LocalPlayer(1)]

    # Prestart the game
    def prestart(self, cdt): 
        AbstractGame.prestart(self, cdt)

        for player in self.players:
            player.positionning()
    
        if gamesock.status == GAME__SOCKET_SERVER:
            for ball in self.balls:
                ball.positionning()
                gamesock.send(None, ["action", "move", "ball", ball.id, ball.ball_coords.center[0], ball.ball_coords.center[1]])
        

    # Start the game 
    def start(self):
        AbstractGame.start(self)

        for ball in self.balls:
            ball.throw()
            ball.launched = True
    
    def updateScore(self):
        self.displayer.displayScoreboard("%d | %d" % (self.score[0], self.score[1]))
    
    def loop(self):
        if core.status == GAME__STATUS_WAITING_FOR_PLAYER:
            self.displayer.displayText(["En attente de joueur ...", GAME__TEXT_SIZE__WAITING_FOR_PLAYER])
        AbstractGame.loop(self)

    def onPlayerMove(self, player):
        gamesock.send(None, ["action", "move", "player", player.id, player.racket_coords.center[0], player.racket_coords.center[1]])

    def onBallMove(self, ball):
        gamesock.send(None, ["action", "move", "ball", ball.id, ball.ball_coords.center[0], ball.ball_coords.center[1]])

    def onBorderReached(self, border):
        if border == 1:
            scorer = 0
        else:
            scorer = 1

        self.score[scorer] += 1
        self.updateScore()

        gamesock.send(None, ["check", "updatescore", scorer])



# Ball class
#   Ball entity's class with some checking and action
class Ball:
    def __init__(self):
        global ball_idc
        self.id = ball_idc
        ball_idc += 1

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
        global player_idc
        self.id = player_idc
        player_idc += 1

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
        
    # Render the entity
    def render(self):
        global window
        window.screen.blit(self.racket, self.racket_coords)

class LocalPlayer(Player):
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

main()


