import pygame
from gameentities.player import Player

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
