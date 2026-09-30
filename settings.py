import pygame
import os

BASE_DIR = os.path.dirname(__file__)
WHITE = (255, 255, 255); BLACK = (0,0,0); GRAY = (180, 180, 180); RED = (220, 60, 60); BLUE = (80, 140, 220); GREEN = (60, 200, 80); YELLOW = (255, 220, 50); PURPLE = (128, 0, 128); ORANGE = (255, 165, 0)


class Settings():
    def __init__(self):
        self.screen_width  = 2796
        self.screen_height = 1864

        # Window size
        self.WINDOW_W = 1440
        self.WINDOW_H = 960

        self.sound      = True
        self.text_speed = 1.0 # 1.0 = normal, 0.6 = fast

        self.bg_color = (30, 30, 40)

        self.turntimerexists = True #5000ms