import pygame as pg
import sys
from button import *


class Event:
    def __init__(self, game):
        self.game = game
        self.settings = game.settings

        self.mode = "Main Menu"
        self.settings_popup = False
        self.rules_popup = False
        self.paused = False
        self.current_page = 1

        self.passed = False
        self.may_click = True
        self.timer = None

        self._init_main_menu()
        self._init_settings_menu()
        self._init_pause_menu()
        self._init_rules_menu()
        self._init_play_menu()
        self._init_win_screen()


    def check_events(self, event):
        mouse_pos = self._scaled_mouse_pos()

        if event.type == pg.QUIT:
            sys.exit()
        elif event.type == pg.KEYDOWN:
            self._check_keydown(event)

        if self.mode == "Main Menu":
            self._main_menu_update(event, mouse_pos)
        if self.mode == "Play":
            self._play_menu_update(event, mouse_pos)
            if self.game.winner is not None:
                self._win_screen_update(event, mouse_pos)

        if self.paused:
            self._pause_update(event, mouse_pos)
        if self.settings_popup:
            self._settings_menu_update(event, mouse_pos)
        if self.rules_popup:
            self._rules_menu_update(event, mouse_pos)


    def _init_main_menu(self):
        self.play_button = Image_Button(self.game, x=250, y=400, image1="play", image2="play_hover")
        self.rules_button = Image_Button(self.game, x=250, y=600, image1="how_to_play", image2="how_to_play_hover")
        self.settings_button = Image_Button(self.game, x=250, y=800, image1="settings", image2="settings_hover")
        self.quit_button = Image_Button(self.game, x=250, y=1000, image1="quit", image2="quit_hover")

    def _init_pause_menu(self):
        self.resume_button = Image_Button(self.game, y=400, center=True, image1="resume", image2="resume_hover")
        self.settings_pause = Image_Button(self.game, y=600, center=True, image1="settings", image2="settings_hover")
        self.rules_pause = Image_Button(self.game, y=800, center=True, image1="how_to_play", image2="how_to_play_hover")
        self.main_menu_pause = Image_Button(self.game, y=1000, center=True, image1="main_menu", image2="main_menu_hover")

    def _init_play_menu(self):
        self.pause_button = Image_Button(self.game, x=2360, y=1725, image1="pause", image2="pause_hover", scaleX=400, scaleY=118)

    def _init_settings_menu(self):
        self.x_settings = Image_Button(self.game, x=2360, y=100, image1="x", image2="x_hover", scaleX=200, scaleY=200)
        self.sound_toggle = Swap_Button(self.game, x=1000, y=550)
        self.timer_toggle = Swap_Button(self.game, x=1000, y=850)
        self.text_speed_toggle = Swap_Button(self.game, x=1000, y=1150, image1="slow", image2="fast", scaleX=300, scaleY=200)

    def _init_rules_menu(self):
        self.x_rules = Image_Button(self.game, x=2600, y=100, image1="x", image2="x_hover", scaleX=120, scaleY=120)
        self.next_page = Swap_Button(self.game, x=2160, y=100, image1="next", image2="back", scaleX=400, scaleY=118)

    def _init_win_screen(self):
        self.win_main_menu = Image_Button(self.game, x=240, y=1600, image1="main_menu", image2="main_menu_hover")
        self.win_play_again = Image_Button(self.game, x=2100, y=1600, image1="play_again", image2="play_again_hover")


    def draw_buttons(self):
        mouse_pos = self._scaled_mouse_pos()

        if self.mode == "Main Menu" and not self._overlay():
            self.play_button.update(mouse_pos)
            self.rules_button.update(mouse_pos)
            self.settings_button.update(mouse_pos)
            self.quit_button.update(mouse_pos)

        if self.mode == "Play" and self.game.winner is None and not self._overlay():
            self.pause_button.update(mouse_pos)

        if self._overlay():
            self.game.dim_screen()

        if self.paused and not self.settings_popup and not self.rules_popup:
            self.resume_button.update(mouse_pos)
            self.rules_pause.update(mouse_pos)
            self.settings_pause.update(mouse_pos)
            self.main_menu_pause.update(mouse_pos)

        if self.settings_popup:
            self.x_settings.update(mouse_pos)
            self.sound_toggle.update(mouse_pos)
            self.timer_toggle.update(mouse_pos)
            self.text_speed_toggle.update(mouse_pos)
            self.game.display_text(80, "Sound:", 400, 600, color=(255, 255, 255))
            self.game.display_text(80, "Timer:", 400, 900, color=(255, 255, 255))
            self.game.display_text(80, "Text Speed:", 400, 1200, color=(255, 255, 255))

        if self.rules_popup:
            if self.current_page == 1 and self.game.rules1:
                self.game.screen.blit(self.game.rules1, (0, 0))
            if self.current_page == 2 and self.game.rules2:
                self.game.screen.blit(self.game.rules2, (0, 0))
            self.x_rules.update(mouse_pos)
            self.next_page.update(mouse_pos)

        if self.mode == "Play" and self.game.winner is not None:
            self.game.dim_screen()
            self.game._draw_win_screen()
            self.win_main_menu.update(mouse_pos)
            self.win_play_again.update(mouse_pos)

    def _main_menu_update(self, event, mouse_pos):
        if self._overlay():
            return
        if self.play_button.press_logic(event, mouse_pos):
            self.mode = "Play"
        if self.rules_button.press_logic(event, mouse_pos):
            self.rules_popup = True
        if self.settings_button.press_logic(event, mouse_pos):
            self.settings_popup = True
        if self.quit_button.press_logic(event, mouse_pos):
            sys.exit()

    def _pause_update(self, event, mouse_pos):
        if self.settings_popup or self.rules_popup:
            return
        if self.resume_button.press_logic(event, mouse_pos):
            self.paused = False
        if self.settings_pause.press_logic(event, mouse_pos):
            self.settings_popup = True
        if self.rules_pause.press_logic(event, mouse_pos):
            self.rules_popup = True
        if self.main_menu_pause.press_logic(event, mouse_pos):
            self.mode = "Main Menu"
            self.paused = False

    def _play_menu_update(self, event, mouse_pos):
        if self.timer is None and not self.may_click:
            self.timer = pg.time.get_ticks()
        elif self.timer is not None:
            delay = 2600 if self.settings.text_speed == 1.0 else 100
            if pg.time.get_ticks() - self.timer >= delay:
                self.timer = None
                self.may_click = True

        if not self._overlay():
            if self.pause_button.press_logic(event, mouse_pos):
                self.paused = True

    def _settings_menu_update(self, event, mouse_pos):
        if self.x_settings.press_logic(event, mouse_pos):
            self.settings_popup = False
        if self.sound_toggle.press_logic(event, mouse_pos):
            self.settings.sound = not self.settings.sound
        if self.timer_toggle.press_logic(event, mouse_pos):
            self.settings.turntimerexists = not self.settings.turntimerexists
        if self.text_speed_toggle.press_logic(event, mouse_pos):
            self.settings.text_speed = 0.6 if self.settings.text_speed == 1.0 else 1.0

    def _rules_menu_update(self, event, mouse_pos):
        if self.x_rules.press_logic(event, mouse_pos):
            self.rules_popup = False
        if self.next_page.press_logic(event, mouse_pos):
            self.current_page = 2 if self.current_page == 1 else 1

    def _win_screen_update(self, event, mouse_pos):
        if self.win_main_menu.press_logic(event, mouse_pos):
            self.mode = "Main Menu"
            self.paused = False
        if self.win_play_again.press_logic(event, mouse_pos):
            self.game._start_new_game()

    def _overlay(self):
        return self.paused or self.settings_popup or self.rules_popup

    def _scaled_mouse_pos(self):
        s = self.settings
        mousePos = pg.mouse.get_pos()
        rawMouseX = mousePos[0]
        rawMouseY = mousePos[1]
        scaleX = s.screen_width / s.WINDOW_W
        scaleY = s.screen_height / s.WINDOW_H
        return int(rawMouseX * scaleX), int(rawMouseY * scaleY)

    def _check_keydown(self, event):
        if (event.key == pg.K_ESCAPE
                and not self.settings_popup
                and not self.rules_popup):
            self.paused = not self.paused

        directions = {pg.K_UP: "up", pg.K_w: "up", pg.K_DOWN: "down", pg.K_s: "down", pg.K_LEFT: "left", pg.K_a: "left", pg.K_RIGHT: "right", pg.K_d: "right"}

        if event.key in directions and self.mode == "Play" and not self._overlay():
            self.queued_direction = directions[event.key]

    def reset_play_state(self):
        self.passed = False
        self.may_click = True
        self.timer = None
        self.paused = False
        self.settings_popup = False
        self.rules_popup = False
        self.current_page = 1
        self.queued_direction = None