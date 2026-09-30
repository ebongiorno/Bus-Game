import sys, os
import pygame

from settings import *
from board import Board
from event import Event


def resource_path(relative_path):
    #HAS TO BE ADDED TO MAKE THIS FUNCTION AS AN .EXE
    base_path = getattr(sys, '_MEIPASS', os.path.dirname(os.path.abspath(__file__)))
    return os.path.join(base_path, relative_path)



class BusGame():
    def __init__(self):
        pygame.init()
        pygame.mixer.init()
        self.clock = pygame.time.Clock()

        self.settings = Settings()
        self.screen = pygame.Surface((self.settings.screen_width, self.settings.screen_height))
        self.scaled_screen = pygame.display.set_mode((self.settings.WINDOW_W, self.settings.WINDOW_H), pygame.HWSURFACE | pygame.DOUBLEBUF)
        pygame.display.set_caption("Bus Game")

        self.board = Board()
        self.event = Event(self)

        self.sprites = {}
        sprite_size = (80, 80)
        for name in ("player_bus", "greedy_dot", "sa_dot", "ga_dot", "astar_dot"):
            self.sprites[name] = self.load_sprite(resource_path(f"images/{name}.png"), sprite_size)


        self.blue_background = self.load_image(resource_path("images/blue_background.bmp"))
        self.funny = self.load_image_alpha(resource_path("images/funny.png"), (self.settings.screen_width-200, self.settings.screen_height-500))
        self.detailed = self.load_image_alpha(resource_path("images/detailed.png"), (self.settings.screen_width, self.settings.screen_height))
        self.rules1 = self.load_image_alpha(resource_path("images/HowToPlay1.png"), (self.settings.screen_width, self.settings.screen_height))
        self.rules2 = self.load_image_alpha(resource_path("images/HowToPlay2.png"), (self.settings.screen_width, self.settings.screen_height))

        self.winner = None
        self.game_over = False
        self.turn_timer = None
        self.directionQ = None



    def load_sprite(self, path, size):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, size)
        except (FileNotFoundError, pygame.error) as e:
            print(f"[sprite] could not load '{path}': {e}")
            return None

    def load_image(self, path):
        try:
            return pygame.image.load(path).convert()
        except (FileNotFoundError, pygame.error) as e:
            print(f"[image] could not load '{path}': {e}")
            return None

    def load_image_alpha(self, path, size):
        try:
            img = pygame.image.load(path).convert_alpha()
            return pygame.transform.smoothscale(img, size)
        except (FileNotFoundError, pygame.error) as e:
            print(f"[image] could not load '{path}': {e}")
            return None


    def display_text(self, font_size=40, text="", x=0, y=0, center=False, color=WHITE):
        try:
            font = pygame.font.Font("fonts/youngserif-regular.ttf", font_size)
        except FileNotFoundError:
            font = pygame.font.SysFont("arial", font_size)
        surf = font.render(text, True, color)
        rect = surf.get_rect()
        if center:
            rect.centerx = self.screen.get_rect().centerx
        else:
            rect.x = x
        rect.y = y
        self.screen.blit(surf, rect)

    def scaled_blit(self):
        transformed = pygame.transform.smoothscale(self.screen, (self.settings.WINDOW_W, self.settings.WINDOW_H))
        self.scaled_screen.blit(transformed, (0, 0))
        pygame.display.flip()

    def dim_screen(self, alpha=168, color=(0, 0, 0)):
        overlay = pygame.Surface(self.screen.get_size())
        overlay.fill(color)
        overlay.set_alpha(alpha)
        self.screen.blit(overlay, (0, 0))

    def blit_sprite(self, name, pos, backup_color, backup_radius, label=None, label_color=WHITE):
        sprite = self.sprites.get(name)
        if sprite:
            rect = sprite.get_rect(center=pos)
            self.screen.blit(sprite, rect)
        else:
            pygame.draw.circle(self.screen, backup_color, pos, backup_radius)
        if label:
            self.display_text(22, label, pos[0] - 14, pos[1] - 11, color=label_color)

    def time_remaining_ms(self):
        if self.turn_timer is None: return 0
        if not self.settings.turntimerexists: return 99
        return max(0, 5000 - (pygame.time.get_ticks() - self.turn_timer))



    def draw_backgrounds(self, menu=False):
        if menu:
            self.screen.blit(self.blue_background, (0, 0))
            self.screen.blit(self.funny, (1000, 500))
            



    #DRAWS
    def draw_overlay(self):
        if self.detailed:
            self.screen.blit(self.detailed, (0, 0))

    def draw_title(self):
        self.display_text(160, "Bus Game", x=1450, y=200)
        self.display_text(60, "Beat the traffic, find the path with rival AIs.", x=1200, y=420)

    def draw_hud(self):
        timeleft = self.time_remaining_ms()
        timer2time = timeleft / 5000

        bar_w = int(900 * timeleft / 5000)
        bar_col = (int(220 * (1 - timer2time)), int(200 * timer2time), 50)
        pygame.draw.rect(self.screen, (60, 60, 60), (self.settings.screen_width // 2 - 450, 60, 900, 40))
        pygame.draw.rect(self.screen, bar_col,      (self.settings.screen_width // 2 - 450, 60, bar_w, 40))
        self.display_text(36, f"{timeleft/1000:.1f}s", self.settings.screen_width // 2 - 30, 110, color=WHITE)
        self.display_text(48, f"Your cost: {self.board.player[1]}", 80, 60, color=YELLOW)
        self.display_text(40, "AI Costs:", self.settings.screen_width - 240, 60, color=GRAY)

        for i, agent in enumerate(self.board.agents):
            self.display_text(36, f"{agent['name']}: {agent['cost']}", self.settings.screen_width - 240, 120 + i * 60, color=WHITE)
        self.display_text(36, "Arrow keys / WASD to move", 80, self.settings.screen_height - 140, color=GRAY)

    def _draw_board(self):
        rows = self.board.rows
        cols = self.board.columns
        x_margin = 300
        y_margin = 250
        linewidth = (self.settings.screen_width  - 2 * x_margin) // (cols - 1)
        lineheight = (self.settings.screen_height - 2 * y_margin) // (rows - 1)

        def node_pos(r, c):
            return x_margin + c * linewidth, y_margin + r * lineheight

        for r in range(rows):
            for c in range(cols):
                nodeX = node_pos(r, c)[0]
                nodeY = node_pos(r, c)[1]
                for neighborRow, neighborCol in [(r, c + 1), (r + 1, c)]:
                    if neighborRow < rows and neighborCol < cols:
                        neighborNodeX = node_pos(neighborRow, neighborCol)[0]
                        neighborNodeY = node_pos(neighborRow, neighborCol)[1]
                        cost = self.board.edge_weight((r, c), (neighborRow, neighborCol))
                        edgeExtreme = (cost - 1) / 49.0
                        edgeColor = (int(220 * edgeExtreme), int(200 * (1 - edgeExtreme)), 60)
                        pygame.draw.line(self.screen, edgeColor, (nodeX, nodeY), (neighborNodeX, neighborNodeY), 6)
                        midpoint = ((nodeX + neighborNodeX) // 2, (nodeY + neighborNodeY) // 2)
                        self.display_text(28, str(cost), midpoint[0] - 15, midpoint[1] - 18, color=(220, 220, 220))

        goalX = node_pos(*self.board.goal)[0]
        goalY = node_pos(*self.board.goal)[1]
        pygame.draw.circle(self.screen, GREEN, (goalX, goalY), 28)
        self.display_text(28, "GOAL", goalX - 35, goalY + 30, color=GREEN)


        startX = node_pos(*self.board.start)[0]
        startY = node_pos(*self.board.start)[1]
        pygame.draw.circle(self.screen, GRAY, (startX, startY), 20, 3)
        self.display_text(28, "START", startX - 35, startY + 30, color=GRAY)

        #darn I never got to implement images for the agents XD
        colors = [BLUE, (180, 80, 220), (220, 140, 40), (80, 220, 200), (220, 80, 80)]
        for index, agent in enumerate(self.board.agents):
            agentX = node_pos(*agent["pos"])[0]
            agentY = node_pos(*agent["pos"])[1]
            self.blit_sprite(agent.get("image", ""), (agentX, agentY), colors[index % len(colors)], 18, label=agent["name"][:3])

        playerRow = self.board.player[0][0]
        playerCol = self.board.player[0][1]
        playerX = node_pos(playerRow, playerCol)[0]
        playerY = node_pos(playerRow, playerCol)[1]
        self.blit_sprite("player_bus", (playerX, playerY), YELLOW, 24, label="YOU", label_color=BLUE)

    def _draw_win_screen(self):
        screenW = self.settings.screen_width
        screenH = self.settings.screen_height
        banner = pygame.Rect(0, screenH // 2 - 300, screenW, 750)
        pygame.draw.rect(self.screen, (30, 30, 30), banner)
        if self.winner == "You":
            self.display_text(160, "YOU WIN!", center=True, y=screenH // 2 - 260, color=GREEN)
        else:
            self.display_text(120, f"{self.winner} wins!", center=True, y=screenH // 2 - 240, color=RED)
        for i, (name, cost) in enumerate(self.board.results()):
            col = YELLOW if name == "You" else WHITE
            self.display_text(60, f"#{i+1}  {name}: {cost}", center=True, y=screenH // 2 - 60 + i * 80, color=col)



    # Other Game ================================================================
    def check_turn_timer(self):
        if self.turn_timer is None or self.game_over:
            return
        if pygame.time.get_ticks() - self.turn_timer >= 5000 and self.settings.turntimerexists:
            self.board.advance_agents()
            self.directionQ = None
            self.turn_timer = pygame.time.get_ticks()
            self.check_win()

    def check_win(self):
        if self.board.player_at_goal():
            results = self.board.results()
            best_cost = results[0][1]
            self.winner = "You" if self.board.player[1] <= best_cost else results[0][0]
            self.game_over = True

    def _start_new_game(self):
        self.board = Board()
        self.winner = None
        self.game_over = False
        self.turn_timer = pygame.time.get_ticks()
        self.directionQ = None
        self.event.reset_play_state()
        self.event.mode = "Play"

    def _reset_play(self):
        self.winner = None
        self.game_over = False
        self.turn_timer = None
        self.directionQ = None
        self.event.reset_play_state()



    # Main Loop ================================================================
    def run_game(self):
        while True:
            while self.event.mode == "Main Menu": # MAIN MENU ==================
                self.screen.fill(self.settings.bg_color)
                self.draw_backgrounds(menu=True)
                self.draw_title()
                self.event.draw_buttons()
                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        sys.exit()
                    self.event.check_events(e)

                self.draw_overlay()
                self.scaled_blit()
                self.clock.tick(60)

            self._start_new_game()
            while self.event.mode == "Play": # PLAY STARTS HERE EZ FIND ==================
                self.screen.fill(self.settings.bg_color)
                self.draw_backgrounds()
                self._draw_board()
                self.draw_hud()

                self.event.draw_buttons()
                self.check_turn_timer()

                if self.directionQ is not None and self.turn_timer is not None:
                    if self.board.move_player(self.directionQ):
                        self.board.advance_agents()
                        self.directionQ = None
                        self.turn_timer = None
                        self.check_win()
                        if self.event.mode == "Play" and not self.game_over:
                            self.turn_timer = pygame.time.get_ticks()

                for e in pygame.event.get():
                    if e.type == pygame.QUIT:
                        sys.exit()
                    self.event.check_events(e)

                if hasattr(self.event, "queued_direction") and self.event.queued_direction is not None:
                    self.directionQ = self.event.queued_direction
                    self.event.queued_direction = None

                self.draw_overlay()
                self.scaled_blit()
                self.clock.tick(60)

            self._reset_play()

game = BusGame()
game.run_game()