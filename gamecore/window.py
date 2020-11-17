import pygame

GAME__TEXT_SIZE__WAITING_FOR_PLAYER = 64
GAME__TEXT_SIZE__COUNTDOWN = 128

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
