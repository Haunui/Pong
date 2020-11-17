import pygame
from threading import Thread

GAME__STATUS_LOBBY = 0
GAME__STATUS_WAITING_FOR_PLAYER = 1
GAME__STATUS_PRESTART = 2
GAME__STATUS_START = 3

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
