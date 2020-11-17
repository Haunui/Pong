from gameutils.displayer import Displayer

class Model:
    def __init__(self, window):
        self.window = window
        self.displayer = Displayer(self.window)

    def loop(self):
        pass

    def render(self):
        # Display entities
        self.window.screen.fill(self.window.bgcolor)

        if hasattr(self.displayer, 'display_text') and hasattr(self.displayer, 'display_text_coords'):
            self.window.screen.blit(self.displayer.display_text, self.displayer.display_text_coords)
