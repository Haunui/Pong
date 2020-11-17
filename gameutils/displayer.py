import pygame

class Displayer:
    def __init__(self, window):
        self.window = window

    def displayText(self, args):
        if isinstance(args, str) == False:
            dtext = args[0]
            dtext_size = args[1]

        font = pygame.font.Font(pygame.font.get_default_font(), dtext_size)
        self.display_text = font.render(dtext, True, (255,255,255), (255,85,85))
        self.display_text_coords = self.display_text.get_rect()
        self.display_text_coords.center = (self.window.width / 2, self.window.height / 2)

    def hideText(self):
        self.displayText(["", 0])

    def displayScoreboard(self, scores):
        font = pygame.font.Font(pygame.font.get_default_font(), 32)
        self.scoreboard = font.render('%s' % (scores), True, (255,255,255), (255,85,85))
        self.scoreboard_coords = self.scoreboard.get_rect()
        self.scoreboard_coords.center = (self.window.width / 2, self.scoreboard_coords.height)

    def hideScoreboard(self): 
        self.displayScoreboard(self, scores)
 
