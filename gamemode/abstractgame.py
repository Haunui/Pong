from gameutils import countdown
from gamecore.model import Model
from gamecore import core as m_core, window as m_win, sock as m_sock
from gameentities.localplayer import LocalPlayer

class AbstractGame(Model):
    def __init__(self, core, window, gamesock):
        Model.__init__(self, window)

        self.displayer = Displayer(self.window)
        
        self.core = core
        self.gamesock = gamesock


    def prestart(self, cdt):
        self.core.status = m_core.GAME__STATUS_PRESTART
        
        cd = countdown.Countdown(cdt * 1000, self.start)
        cd.addPerMSFunc(countdown.CD_PER_D1000, self.displayer.displayText, "{CD_PER_D1000}", m_win.GAME__TEXT_SIZE__COUNTDOWN)
        cd.start()

    def start(self):
        self.core.status = m_core.GAME__STATUS_START
        
        self.updateScore()

        self.displayer.displayText(["Go !", m_win.GAME__TEXT_SIZE__COUNTDOWN])
        cd = countdown.Countdown(2000, self.displayer.hideText)
        cd.start()


    # Update scoreboard
    def updateScore(self):
        self.displayer.displayScoreboard(self.score[0])

    # This function manage all entities move
    def loop(self):
        if self.core.status == m_core.GAME__STATUS_START:
            for player in self.players:
                if isinstance(player, LocalPlayer):
                    player.checkMove()
                    player.move()
                    self.onPlayerMove(player)


            if self.gamesock.status == m_sock.GAME__SOCKET_SERVER:
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
                            self.onBorderReached(border_reached)
                        else:
                            self.onRacketReached(border_reached)
                            

    def onBallMove(self, ball):
        pass

    def onPlayerMove(self, player):
        pass

    def onBorderReached(self, border):
        pass
    
    def onRacketReached(self, border):
        pass

    def render(self):
        # Display entities
        self.window.screen.fill(self.window.bgcolor)

        if hasattr(self.displayer, 'display_text') and hasattr(self.displayer, 'display_text_coords'):
            self.window.screen.blit(self.displayer.display_text, self.displayer.display_text_coords)
        
        if self.core.status == m_core.GAME__STATUS_START:
            if hasattr(self.displayer, 'scoreboard') and hasattr(self.displayer, 'scoreboard_coords'):
                self.window.screen.blit(self.displayer.scoreboard, self.displayer.scoreboard_coords)

        for player in self.players:
            player.render()

        for ball in self.balls:
            ball.render()
