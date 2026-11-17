import os
import tempfile
import unittest
from pathlib import Path

os.environ['SDL_VIDEODRIVER'] = 'dummy'
os.environ['SDL_AUDIODRIVER'] = 'dummy'
import pygame
from src.chef import Chef
from src.game_manager import GameManager, WIDTH, HEIGHT
from src.ingredient import Ingredient, Dish
from src.order import Order, OrderManager
from src.recipes import RecipeBook
from src.save_manager import SaveManager
from src.station import Station
from src.layout import KITCHEN, PEDESTRIAN_PATHS, make_stations, counter_rects
from src.pedestrian import Pedestrian, PedestrianManager
from src.plates import Plate, PlateSupply

ROOT = Path(__file__).resolve().parent.parent


class LogicTests(unittest.TestCase):
    def setUp(self):
        self.recipes = RecipeBook(ROOT / 'data/recipes.json')
        self.chef = Chef(0, 0)
        self.orders = OrderManager(self.recipes.recipes)
        self.score = {'score': 0, 'reward': 100, 'penalty': 20}
        self.plates = PlateSupply()

    def test_station_to_serving_and_invalid_actions(self):
        stove = Station('Stove', 'stove', (0, 0, 80, 50))
        assembly = Station('Assembly', 'assembly', (0, 0, 80, 50))
        serve = Station('Serve', 'serve', (0, 0, 80, 50))
        self.chef.carrying = Ingredient('lettuce')
        stove.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertIsNone(stove.item)
        self.chef.carrying = Ingredient('patty')
        stove.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        stove.update(4)
        stove.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertEqual(self.chef.carrying.state, 'cooked')
        assembly.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertIsNone(self.chef.carrying)
        self.chef.carrying = Ingredient('bun')
        assembly.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertIsNone(self.chef.carrying)
        self.assertEqual(assembly.dish, Dish('Burger'))
        assembly.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertEqual(self.chef.carrying, Dish('Burger'))
        self.orders.orders = [Order('Salad'), Order('Burger'), Order('Burger')]
        serve.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertEqual(self.score['score'], 100)
        self.assertEqual(len(self.orders.orders), 2)
        self.chef.carrying = Dish('Soup')
        serve.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertEqual(self.score['score'], 100)
        self.assertIsNotNone(self.chef.carrying)

    def test_chopping_recipe_and_expiration(self):
        cut = Station('Cut', 'cut', (0, 0, 80, 50))
        self.chef.carrying = Ingredient('tomato')
        cut.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        cut.update(2)
        cut.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertEqual(self.chef.carrying.state, 'chopped')
        self.assertEqual(self.recipes.match([self.chef.carrying, Ingredient('lettuce', 'chopped')]), 'Salad')
        self.orders.orders = [Order('Salad', 1)]
        self.assertEqual(self.orders.update(1), 1)
        self.assertFalse(self.orders.serve_order('Salad'))
        self.assertEqual(self.orders.update(1), 0)

    def test_sources_and_pedestrian_collisions(self):
        for station in make_stations():
            if station.kind == 'source':
                self.chef.carrying = None
                station.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
                self.assertEqual(self.chef.carrying.name, station.source)
                station.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
                self.assertEqual(self.chef.carrying.name, station.source)
        walker = Pedestrian((465, 120), (465, 620), 50, (1, 2, 3))
        chef_rect = pygame.Rect(450, 190, 32, 32)
        walker.update(2, [chef_rect])
        self.assertFalse(walker.rect.colliderect(chef_rect))
        stopped = walker.position.y
        walker.update(10, [chef_rect])
        self.assertEqual(walker.position.y, stopped)
        self.assertFalse(walker.finished)
        walker.update(1, [])
        self.assertGreater(walker.position.y, stopped)
        self.assertEqual(walker.position.x, 465)
        # Chef movement also stops at the pedestrian, even on a slow frame.
        keys = {key: False for key in (pygame.K_d, pygame.K_RIGHT, pygame.K_a, pygame.K_LEFT, pygame.K_s, pygame.K_DOWN, pygame.K_w, pygame.K_UP)}
        keys[pygame.K_s] = True
        chef = Chef(450, 120)
        chef.move(keys, [walker.rect], pygame.Rect(0, 0, 1000, 720), 2)
        self.assertFalse(chef.rect.colliderect(walker.rect))
        self.assertLessEqual(chef.rect.bottom, walker.rect.top)

    def test_pedestrians_queue_without_overlap(self):
        manager = PedestrianManager()
        manager.timer = 100
        first = Pedestrian((465, 200), (465, 644), 40, (1, 2, 3))
        second = Pedestrian((465, 165), (465, 644), 100, (1, 2, 3))
        manager.people = [first, second]
        blocker = pygame.Rect(450, 270, 32, 32)
        manager.update(4, blocker)
        self.assertFalse(first.rect.colliderect(second.rect))
        self.assertFalse(first.rect.colliderect(blocker))
        self.assertEqual(len(manager.people), 2)
        self.assertFalse(first.finished or second.finished)
        first_y = first.position.y
        manager.update(1, pygame.Rect(700, 400, 32, 32))
        self.assertGreater(first.position.y, first_y)
        self.assertFalse(first.rect.colliderect(second.rect))

    def test_paths_and_station_accessibility(self):
        from collections import deque
        stations = make_stations()
        obstacles = [s.rect for s in stations] + counter_rects()
        for start, end in PEDESTRIAN_PATHS:
            self.assertEqual(start[0], end[0])
            direction = pygame.Vector2(end) - start
            for i in range(101):
                point = pygame.Vector2(start) + direction * (i / 100)
                rect = pygame.Rect(round(point.x - 12), round(point.y - 12), 24, 24)
                self.assertFalse(any(rect.colliderect(o) for o in obstacles), (start, end, point))
        # Flood-fill possible chef positions on a 10-pixel grid from spawn.
        start = (620, 330)
        queue, seen = deque([start]), {start}
        while queue:
            x, y = queue.popleft()
            for point in ((x+10,y), (x-10,y), (x,y+10), (x,y-10)):
                rect = pygame.Rect(*point, 32, 32)
                if point not in seen and KITCHEN.contains(rect) and not any(rect.colliderect(o) for o in obstacles):
                    seen.add(point)
                    queue.append(point)
        for station in stations:
            reachable = False
            for x, y in seen:
                chef_rect = pygame.Rect(x, y, 32, 32)
                candidates = [s for s in stations if chef_rect.inflate(70, 70).colliderect(s.rect)]
                nearest = min(candidates, key=lambda s: pygame.Vector2(chef_rect.center).distance_squared_to(s.rect.center), default=None)
                if nearest is station:
                    reachable = True
                    break
            self.assertTrue(reachable, station.name)

    def test_plate_lifecycle_and_no_plate_loss(self):
        assembly = Station('Assembly', 'assembly', (0, 0, 80, 50))
        serve = Station('Serve', 'serve', (0, 0, 80, 50))
        returned = Station('Return', 'return', (0, 0, 80, 50))
        sink = Station('Sink', 'sink', (0, 0, 80, 50))
        trash = Station('Trash', 'trash', (0, 0, 80, 50))
        self.plates = PlateSupply(1)
        self.chef.carrying = Ingredient('bun')
        assembly.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.chef.carrying = Ingredient('patty', 'cooked')
        assembly.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertEqual(self.plates.clean, 0)
        assembly.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.orders.orders = [Order('Burger')]
        serve.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertEqual((self.plates.clean, self.plates.dirty, self.score['score']), (0, 0, 100))
        self.plates.update(2.99)
        self.assertEqual(self.plates.dirty, 0)
        self.plates.update(0.01)
        self.assertEqual(self.plates.dirty, 1)
        self.chef.carrying = Ingredient('bun')
        assembly.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.chef.carrying = Ingredient('patty', 'cooked')
        message = assembly.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertIn('No clean plates', message)
        self.assertEqual(self.chef.carrying.name, 'patty')
        self.chef.carrying = None
        returned.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        sink.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        sink.update(3)
        sink.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertEqual(self.chef.carrying, Plate('clean'))
        assembly.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertEqual(self.plates.clean, 1)
        self.chef.carrying = Ingredient('patty', 'cooked')
        assembly.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        assembly.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        # Expiring an order does not destroy the carried dish or its plate.
        self.orders.orders = [Order('Burger', 1)]
        self.orders.update(1)
        serve.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertIsInstance(self.chef.carrying, Dish)
        trash.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.assertEqual((self.plates.clean, self.plates.dirty), (1, 0))

    def test_independent_plate_returns(self):
        serve = Station('Serve', 'serve', (0, 0, 80, 50))
        self.orders.orders = [Order('Burger'), Order('Salad')]
        self.chef.carrying = Dish('Burger')
        serve.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.plates.update(1)
        self.chef.carrying = Dish('Salad')
        serve.interact(self.chef, self.recipes, self.orders, self.score, self.plates)
        self.plates.update(1.99)
        self.assertEqual(self.plates.dirty, 0)
        self.plates.update(0.01)
        self.assertEqual(self.plates.dirty, 1)
        self.plates.update(1)
        self.assertEqual(self.plates.dirty, 2)
        self.plates.update(20)
        self.assertEqual(self.plates.dirty, 2)
        self.assertEqual(self.plates.pending_returns, [])

    def test_profiles_never_regress(self):
        with tempfile.TemporaryDirectory() as directory:
            saves = SaveManager(Path(directory) / 'players.db')
            self.assertEqual(saves.load('Thy')['highest_level'], 1)
            saves.save_round('Thy', 200, 2)
            result = saves.save_round('Thy', -20, 1)
            self.assertEqual((result['high_score'], result['highest_level'], result['games_played']), (200, 2, 2))
            self.assertEqual(SaveManager(saves.path).load('Thy'), result)

    def test_round_end_restart_and_collision(self):
        pygame.init()
        with tempfile.TemporaryDirectory() as directory:
            game = GameManager(pygame.display.set_mode((WIDTH, HEIGHT)), Path(directory) / 'save.db')
            game.username = 'Thy'
            game.profile = game.saves.load('Thy')
            game.start_round(1)
            game.plates.schedule_return()
            game.scoring['score'] = 100
            game.remaining = 0.01
            game.update(game.remaining, pygame.key.get_pressed())
            self.assertEqual(game.state, 'finished')
            self.assertEqual(game.profile['highest_level'], 2)
            game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_n))
            self.assertEqual((game.state, game.level, game.scoring['score']), ('playing', 2, 0))
            self.assertEqual((game.plates.clean, game.plates.dirty, game.plates.pending_returns), (3, 0, []))
            game.handle_event(pygame.event.Event(pygame.KEYDOWN, key=pygame.K_q))
            game.chef.carrying = Ingredient('bun')
            game.drop()
            game.interact()
            self.assertEqual(game.chef.carrying.name, 'bun')
            keys = {key: False for key in (pygame.K_d, pygame.K_RIGHT, pygame.K_a, pygame.K_LEFT, pygame.K_s, pygame.K_DOWN, pygame.K_w, pygame.K_UP)}
            keys[pygame.K_LEFT] = True
            chef = Chef(180, 200)
            chef.move(keys, [pygame.Rect(100, 180, 60, 80)], pygame.Rect(0, 0, 500, 500), 1)
            self.assertGreaterEqual(chef.rect.left, 160)
        pygame.quit()


if __name__ == '__main__':
    unittest.main()
