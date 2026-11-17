import pygame
from src.ingredient import Ingredient, Dish
from src.plates import Plate


class Station:
    def __init__(self, name, kind, rect, source=None):
        self.name, self.kind, self.rect, self.source = name, kind, pygame.Rect(rect), source
        self.item = None
        self.remaining = 0
        self.parts = []
        self.dish = None
        self.duration = 0

    def update(self, dt):
        if self.remaining > 0:
            self.remaining = max(0, self.remaining - dt)
            if self.remaining == 0:
                self.item.state = {'cut': 'chopped', 'stove': 'cooked', 'sink': 'clean'}[self.kind]

    def interact(self, chef, recipes, orders, scoring, plates):
        held = chef.carrying
        if self.kind == 'source':
            if held is None:
                chef.carrying = Ingredient(self.source)
                return f'Picked up raw {self.source}.'
            return 'Hands full. Place or discard your item first.'
        if self.kind == 'trash':
            if isinstance(held, Plate) and held.state == 'dirty':
                plates.return_dirty()
            elif isinstance(held, (Dish, Plate)):
                plates.store_clean()
            if held is not None:
                chef.carrying = None
                return 'Item discarded.'
            return 'Nothing carried to discard.'
        if self.kind == 'return':
            if held is None:
                chef.carrying = plates.collect_dirty()
                return 'Picked up a dirty plate.' if chef.carrying else 'No dirty plates to collect.'
            if isinstance(held, Plate) and held.state == 'clean':
                plates.store_clean()
                chef.carrying = None
                return 'Clean plate returned to storage.'
            return 'Collect dirty plates here, or return a clean plate.'
        if self.kind == 'sink':
            if self.remaining:
                return f'Washing: {self.remaining:.1f}s.'
            if self.item is not None:
                if held is None:
                    chef.carrying, self.item = self.item, None
                    return 'Picked up clean plate. Return it to assembly or return area.'
                return 'Hands full; pick up the clean plate first.'
            if isinstance(held, Plate) and held.state == 'dirty':
                self.item, chef.carrying = held, None
                self.remaining = self.duration = 3
                return 'Washing plate.'
            return 'Bring a dirty plate to wash.'
        if self.kind in ('cut', 'stove'):
            if self.remaining > 0:
                return f'{self.name} working: {self.remaining:.1f}s.'
            if self.item is not None:
                if held is None:
                    chef.carrying, self.item = self.item, None
                    return f'Picked up {chef.carrying.label}.'
                return 'Hands full; pick up the finished ingredient first.'
            allowed = {'cut': {'lettuce', 'tomato'}, 'stove': {'patty', 'tomato', 'mushroom'}}
            if isinstance(held, Ingredient) and held.state == 'raw' and held.name in allowed[self.kind]:
                self.item, chef.carrying = held, None
                self.remaining = 2 if self.kind == 'cut' else 4
                self.duration = self.remaining
                return f'{self.name} started.'
            return f'This {self.name.lower()} cannot process that item.'
        if self.kind == 'assembly':
            if isinstance(held, Plate) and held.state == 'clean':
                plates.store_clean()
                chef.carrying = None
                return 'Clean plate returned to storage.'
            if self.dish is not None:
                if held is None:
                    chef.carrying, self.dish = self.dish, None
                    return f'Picked up {chef.carrying.name}. Take it to Serve.'
                return 'Hands full; pick up the finished dish first.'
            if isinstance(held, Ingredient):
                if not recipes.can_add(self.parts, held):
                    return 'Ingredient does not fit the current recipe.'
                dish = recipes.match([*self.parts, held])
                if dish and not plates.take_clean():
                    return 'No clean plates! Wash and return a plate first.'
                self.parts.append(held)
                chef.carrying = None
                if dish:
                    self.parts.clear()
                    self.dish = Dish(dish)
                    return f'{dish} assembled! Press E to pick it up.'
                return 'Added ingredient. Add another, or press R to clear assembly.'
            return 'Carry an ingredient here to add it. R clears assembly.'
        if self.kind == 'serve':
            if not isinstance(held, Dish):
                return 'Only a finished dish can be served.'
            if orders.serve_order(held.name):
                chef.carrying = None
                plates.schedule_return()
                scoring['score'] += scoring['reward']
                return f'Served {held.name}! +{scoring["reward"]} points.'
            return 'No matching active order. Keep or discard the dish.'
        return ''
