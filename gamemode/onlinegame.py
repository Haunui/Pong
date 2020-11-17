from gamecore import core as m_core, sock as m_sock, window as m_win
from gamemode.abstractgame import AbstractGame
from gameentities.ball import Ball
from gameentities.localplayer import LocalPlayer
from gameentities.player import Player

class OnlineGame(AbstractGame):
    def __init__(self, core, window, gamesock):
        AbstractGame.__init__(self, core, window, gamesock)

        self.balls = []
        self.score = [0,0]

        for i in range(0,1):
            ball = Ball(self.window)
            self.balls.append(ball)
        

        if self.gamesock.status == m_sock.GAME__SOCKET_SERVER:
            self.players = [LocalPlayer(self.window, 0), Player(self.window, 1)]
        elif self.gamesock.status == m_sock.GAME__SOCKET_CLIENT:    
            self.players = [Player(self.window, 0), LocalPlayer(self.window, 1)]

    # Prestart the game
    def prestart(self, cdt): 
        AbstractGame.prestart(self, cdt)

        for player in self.players:
            player.positionning()
    
        if self.gamesock.status == m_sock.GAME__SOCKET_SERVER:
            for ball in self.balls:
                ball.positionning()
                self.gamesock.send(None, ["action", "move", "ball", ball.id, ball.ball_coords.center[0], ball.ball_coords.center[1]])
        

    # Start the game 
    def start(self):
        AbstractGame.start(self)

        for ball in self.balls:
            ball.throw()
            ball.launched = True
    
    def updateScore(self):
        self.displayer.displayScoreboard("%d | %d" % (self.score[0], self.score[1]))
    
    def loop(self):
        if self.core.status == m_core.GAME__STATUS_WAITING_FOR_PLAYER:
            self.displayer.displayText(["En attente de joueur ...", m_win.GAME__TEXT_SIZE__WAITING_FOR_PLAYER])
        AbstractGame.loop(self)

    def onPlayerMove(self, player):
        self.gamesock.send(None, ["action", "move", "player", player.id, player.racket_coords.center[0], player.racket_coords.center[1]])

    def onBallMove(self, ball):
        self.gamesock.send(None, ["action", "move", "ball", ball.id, ball.ball_coords.center[0], ball.ball_coords.center[1]])

    def onBorderReached(self, border):
        if border == 1:
            scorer = 0
        else:
            scorer = 1

        self.score[scorer] += 1
        self.updateScore()

        self.gamesock.send(None, ["check", "updatescore", scorer])
