import pygame

# Player class
#   Player entity's class with some checking and action
class Player:
    player_idc = 0

    def __init__(self, window, team):
        self.window = window

        self.id = Player.player_idc
        Player.player_idc += 1

        self.team = team
        self.racket_speed = [0, 0]
        self.racket = pygame.image.load("image/racket.png")
        self.racket_coords = self.racket.get_rect()

    # Positionning the racket before the beginning of the game
    # Allow, if the player is in team 1, to position his racket on the right side of the window
    def positionning(self):
        if self.team == 1:
            self.racket_coords.right = self.window.width

    # Move the racket
    def move(self):
        # Move racket
        self.racket_coords = self.racket_coords.move(self.racket_speed)
        # Clip racket on court
        if self.racket_coords.left < 0:
            self.racket_coords.left = 0
        elif self.racket_coords.right >= self.window.width:
            self.racket_coords.right = self.window.width-1
        if self.racket_coords.top < 0:
            self.racket_coords.top = 0
        elif self.racket_coords.bottom >= self.window.height:
            self.racket_coords.bottom = self.window.height-1
        
    # Render the entity
    def render(self):
        self.window.screen.blit(self.racket, self.racket_coords)
