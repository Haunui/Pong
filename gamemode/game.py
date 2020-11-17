from gamemode.abstractgame import AbstractGame
from gameentities.ball import Ball
from gameentities.localplayer import LocalPlayer

# Game class
#   This class manage (action and checking) all entities that is present on the screen
class Game(AbstractGame):
    def __init__(self, core, window, gamesock):
        AbstractGame.__init__(self, core, window, gamesock)

        self.balls = []
        self.score = [0,0]

        for i in range(0,1):
            ball = Ball(self.window)
            self.balls.append(ball)
        
        self.players = [LocalPlayer(self.window, 0)]
        
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
