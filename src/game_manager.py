import json
import math
from pathlib import Path
import pygame
from src.chef import Chef
from src.ingredient import Dish
from src.layout import KITCHEN, make_stations, counter_rects
from src.pedestrian import PedestrianManager
from src.plates import PlateSupply
from src.rendering import draw_scene, draw_station, draw_item, draw_chef
from src.order import OrderManager
from src.recipes import RecipeBook
from src.save_manager import SaveManager

ROOT = Path(__file__).resolve().parent.parent
WIDTH, HEIGHT = 1000, 720


class GameManager:
    def __init__(self, screen, save_path=None):
        self.screen = screen
        self.font = pygame.font.Font(None, 25)
        self.small = pygame.font.Font(None, 21)
        self.big = pygame.font.Font(None, 42)
        self.recipes = RecipeBook(ROOT / 'data/recipes.json')
        self.levels = json.loads((ROOT / 'data/levels.json').read_text())
        self.saves = SaveManager(save_path or ROOT / 'data/players.db')
        self.state = 'profile'
        self.username = ''
        self.profile = None
        self.message = 'Type a username and press Enter.'

    def text(self, value, x, y, color=(30, 30, 30), font=None):
        self.screen.blit((font or self.font).render(str(value), True, color), (x, y))

    def start_round(self, level):
        self.level = min(max(1, level), len(self.levels), self.profile['highest_level'])
        config = self.levels[self.level - 1]
        self.remaining = float(config['duration'])
        self.scoring = {'score': 0, 'reward': config['reward'], 'penalty': config['penalty']}
        self.chef = Chef(620, 330)
        self.stations = make_stations()
        self.floor_items = []
        self.pedestrians = PedestrianManager()
        self.plates = PlateSupply()
        self.show_recipes = False
        self.orders = OrderManager(self.recipes.recipes, config['order_interval'], config['order_time'])
        self.orders.add_order()
        self.state = 'playing'
        self.message = 'Collect ingredients to make a dish.'

    def finish_round(self):
        config = self.levels[self.level - 1]
        self.success = self.scoring['score'] >= config['target']
        unlocked = min(len(self.levels), self.level + 1) if self.success else self.level
        self.profile = self.saves.save_round(self.username, self.scoring['score'], unlocked)
        self.state = 'finished'

    def nearby_station(self):
        nearby = [s for s in self.stations if self.chef.rect.inflate(70, 70).colliderect(s.rect)]
        return min(nearby, key=lambda s: pygame.Vector2(self.chef.rect.center).distance_squared_to(s.rect.center), default=None)

    def interact(self):
        station = self.nearby_station()
        # Dropped items have priority when standing next to them with empty hands.
        if self.chef.carrying is None:
            for item, rect in self.floor_items:
                if self.chef.rect.inflate(35, 35).colliderect(rect):
                    self.chef.carrying = item
                    self.floor_items.remove((item, rect))
                    self.message = f'Picked up {item.label}.'
                    return
        if station:
            self.message = station.interact(self.chef, self.recipes, self.orders, self.scoring, self.plates)
        else:
            self.message = 'Move closer to a station or dropped item.'

    def drop(self):
        if self.chef.carrying is None:
            self.message = 'Nothing to drop.'
            return
        rect = pygame.Rect(self.chef.rect.centerx - 10, self.chef.rect.centery - 10, 20, 20)
        self.floor_items.append((self.chef.carrying, rect))
        self.message = f'Dropped {self.chef.carrying.label}.'
        self.chef.carrying = None

    def handle_event(self, event):
        if event.type != pygame.KEYDOWN:
            return
        if self.state == 'profile':
            if event.key == pygame.K_RETURN and self.username.strip():
                self.username = self.username.strip()
                self.profile = self.saves.load(self.username)
                self.state = 'menu'
            elif event.key == pygame.K_BACKSPACE:
                self.username = self.username[:-1]
            elif event.unicode.isprintable() and len(self.username) < 20:
                self.username += event.unicode
        elif self.state == 'menu':
            if event.key == pygame.K_RETURN:
                self.start_round(self.profile['highest_level'])
            elif event.key == pygame.K_1:
                self.start_round(1)
            elif event.key == pygame.K_2 and self.profile['highest_level'] >= 2:
                self.start_round(2)
        elif self.state == 'playing':
            if event.key == pygame.K_e:
                self.interact()
            elif event.key == pygame.K_q:
                self.drop()
            elif event.key == pygame.K_TAB:
                self.show_recipes = not self.show_recipes
            elif event.key == pygame.K_r:
                station = self.nearby_station()
                if station and station.kind == 'assembly':
                    station.parts.clear()
                    self.message = 'Assembly counter cleared.'
        elif self.state == 'finished':
            if event.key == pygame.K_r:
                self.start_round(self.level)
            elif event.key == pygame.K_n and self.success and self.level < len(self.levels):
                self.start_round(self.level + 1)
            elif event.key == pygame.K_m:
                self.state = 'menu'

    def update(self, dt, keys):
        if self.state != 'playing':
            return
        elapsed = min(dt, self.remaining)
        solids = [s.rect for s in self.stations] + counter_rects()
        self.chef.move(keys, solids + [p.rect for p in self.pedestrians.people], KITCHEN, elapsed)
        self.pedestrians.update(elapsed, self.chef.rect)
        self.plates.update(elapsed)
        for station in self.stations:
            station.update(elapsed)
        self.scoring['score'] -= self.orders.update(elapsed) * self.scoring['penalty']
        self.remaining = max(0, self.remaining - elapsed)
        if self.remaining == 0:
            self.finish_round()

    def draw(self):
        self.screen.fill((245, 235, 220))
        if self.state == 'profile':
            self.text('Kitchen Rush', 340, 160, font=self.big)
            self.text('Enter a username (up to 20 characters):', 220, 245)
            self.text(self.username + '_', 220, 280)
            self.text('Press Enter to create or load your local profile.', 220, 330)
            return
        if self.state == 'menu':
            self.text(f'Welcome, {self.username}', 250, 160, font=self.big)
            self.text(f'High score: {self.profile["high_score"]}   Highest unlocked level: {self.profile["highest_level"]}', 250, 225)
            self.text('Enter: continue highest unlocked level    1: Level 1', 250, 270)
            if self.profile['highest_level'] >= 2:
                self.text('2: Level 2', 250, 300)
            self.text('Reach the score target before the round ends to unlock the next level.', 200, 350)
            return
        if self.state == 'finished':
            self.text('Round complete!', 330, 160, font=self.big)
            self.text(f'Level {self.level}   Score: {self.scoring["score"]}   Target: {self.levels[self.level-1]["target"]}', 280, 225)
            self.text('Target reached!' if self.success else 'Target not reached. Try again!', 280, 260)
            self.text(f'Best score: {self.profile["high_score"]}   Unlocked: Level {self.profile["highest_level"]}', 280, 295)
            self.text('R: retry    M: menu', 280, 340)
            if self.success and self.level < len(self.levels):
                self.text('N: next level', 280, 370)
            return
        pygame.draw.rect(self.screen, (45, 48, 48), (0, 0, WIDTH, 104))
        self.text(f'{self.username}  |  Level {self.level}  |  Score {self.scoring["score"]} / {self.levels[self.level-1]["target"]}  |  {math.ceil(self.remaining)}s', 20, 10, (250, 248, 235))
        self.text('Orders:', 20, 43, (250, 248, 235))
        for index, order in enumerate(self.orders.orders):
            x = 95 + index * 165
            pygame.draw.rect(self.screen, (245, 232, 203), (x, 39, 155, 28), border_radius=4)
            self.text(f'{order.dish}  {math.ceil(order.time_remaining)}s', x + 7, 44, font=self.small)
        held = self.chef.carrying.label.title() if self.chef.carrying else 'Nothing'
        self.text(f'Plates: {self.plates.clean} clean / {self.plates.dirty} dirty', 620, 13, (250, 248, 235), self.small)
        self.text('Carrying: ' + held, 620, 45, (250, 248, 235), self.small)
        self.text('Move: WASD / arrows    E: interact    Q: drop    R: clear assembly    Tab: recipes', 20, 78, (220, 220, 210), self.small)
        draw_scene(self.screen)
        for station in self.stations:
            draw_station(self.screen, station, self.small, self.plates)
        for item, rect in self.floor_items:
            draw_item(self.screen, item, rect.center)
        for person in self.pedestrians.people:
            pygame.draw.circle(self.screen, person.color, (round(person.position.x), round(person.position.y)), person.radius)
            pygame.draw.circle(self.screen, (50, 50, 50), (round(person.position.x), round(person.position.y)), person.radius, 2)
        draw_chef(self.screen, self.chef)
        if self.show_recipes:
            pygame.draw.rect(self.screen, (250, 243, 221), (270, 255, 460, 145), border_radius=6)
            pygame.draw.rect(self.screen, (90, 70, 50), (270, 255, 460, 145), 2, border_radius=6)
            self.text('RECIPES  (Tab to close)', 290, 270)
            self.text('Burger: raw bun + cooked patty', 290, 300, font=self.small)
            self.text('Salad: chopped lettuce + chopped tomato', 290, 325, font=self.small)
            self.text('Soup: cooked tomato + cooked mushroom', 290, 350, font=self.small)
        station = self.nearby_station()
        if station and station.kind == 'source' and not self.chef.carrying:
            hint = f'Press E to pick up {station.name}.'
        elif station:
            hint = f'Press E to interact with {station.name}.'
        else:
            hint = 'Move near a station or dropped item to interact.'
        self.text(hint, 20, 645)
        self.text(self.message, 20, 675)
