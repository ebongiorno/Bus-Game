import pygame as pg
import sys, os
from settings import Settings



def resource_path(relative_path):
    #HAS TO BE ADDED TO MAKE THIS FUNCTION AS AN .EXE
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)



class Button:
    

    def __init__(self, game, x=500, y=500, center=False):
        self.game = game
        self.screen = game.screen
        self.screen_rect = self.screen.get_rect()

        self.rect = pg.Rect(0, 0, 9, 9)
        if center:
            self.rect.centerx = self.screen_rect.centerx
        else:
            self.rect.x = x
        self.rect.y = y
        self.click = False

        self.button_sound = pg.mixer.Sound("sounds/button_click.mp3")

    def press_logic(self, event, mouse_pos):
        if event.type == pg.MOUSEBUTTONDOWN and self.rect.collidepoint(mouse_pos):
            self.click = True
        elif (event.type == pg.MOUSEBUTTONUP
              and self.rect.collidepoint(mouse_pos)
              and self.click):
            if self.game.settings.sound:
                self.button_sound.play()
            self.click = False
            self.function()
            return True
        else:
            self.click = False
        return False

    def function(self):
        pass

    def draw(self):
        pass

class Image_Button(Button):
    def __init__(self, game, x=500, y=500, center=False, image1="placeholder", image2="placeholder", scaleX=450, scaleY=138):
        super().__init__(game, x=x, y=y, center=center)
        self.normalimage = pg.transform.smoothscale(
            pg.image.load(resource_path(f"images/{image1}.png")).convert_alpha(), (scaleX, scaleY))
        self.hoverimage = pg.transform.smoothscale(
            pg.image.load(resource_path(f"images/{image2}.png")).convert_alpha(), (scaleX, scaleY))

        self.image = self.normalimage
        self.rect = self.image.get_rect()

        if center:
            self.rect.centerx = self.screen_rect.centerx
        else:
            self.rect.x = x
        self.rect.y = y

    def when_hover(self, mouse_pos):
        self.image = self.hoverimage if self.rect.collidepoint(mouse_pos) else self.normalimage

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def update(self, mouse_pos):
        self.when_hover(mouse_pos)
        self.draw()

    def function(self):
        pass

class Swap_Button(Button):
    

    def __init__(self, game, x=500, y=500, center=False, image1="check_button", image2="x", scaleX=200, scaleY=200):
        super().__init__(game, x=x, y=y, center=center)
        self.normalimage = pg.transform.smoothscale(
            pg.image.load(resource_path(f"images/{image1}.png")).convert_alpha(), (scaleX, scaleY))
        self.hoverimage = pg.transform.smoothscale(
            pg.image.load(resource_path(f"images/{image2}.png")).convert_alpha(), (scaleX, scaleY))

        self.image = self.normalimage
        self.rect = self.image.get_rect()
        if center:
            self.rect.centerx = self.screen_rect.centerx
        else:
            self.rect.x = x
        self.rect.y = y

    def function(self):
        self.image = (self.hoverimage if self.image is self.normalimage else self.normalimage)

    def draw(self):
        self.screen.blit(self.image, self.rect)

    def update(self, mouse_pos):
        self.draw()

class Font_Button(Button):
    

    def __init__(self, game, x=600, y=600, center=True, msg="default_message", font=None, button_width=200, button_height=50):
        super().__init__(game, x=x, y=y, center=center)
        self.width, self.height = button_width, button_height
        self.normal_color = (80, 80, 80)
        self.hover_color = (140, 140, 60)
        self.button_color = self.normal_color
        self.text_color = (255, 255, 255)

        font_size = 30 if font else 48
        self.font = pg.font.Font(font, font_size)

        self.rect = pg.Rect(0, 0, self.width, self.height)
        if center:
            self.rect.centerx = self.screen_rect.centerx
        else:
            self.rect.x = x
        self.rect.y = y

        self.prep_msg(msg)

    def prep_msg(self, msg):
        self.msg_image = self.font.render(msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def change_msg(self, msg):
        self.prep_msg(msg)

    def when_hover(self, mouse_pos):
        self.button_color = (self.hover_color if self.rect.collidepoint(mouse_pos) else self.normal_color)

    def draw(self):
        self.screen.fill(self.button_color, self.rect)
        self.screen.blit(self.msg_image, self.msg_image_rect)

    def update(self, mouse_pos):
        self.when_hover(mouse_pos)
        self.draw()

    def function(self):
        pass