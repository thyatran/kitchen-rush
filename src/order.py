# order system with timers and serving counter

import pygame
import random


class Order:
    def __init__(self, dish, time_limit=30):
        self.dish = dish
        self.time_remaining = float(time_limit)
        self.completed = False

    def update(self, dt):
        if not self.completed:
            self.time_remaining = max(
                0, self.time_remaining - dt
            )

    def is_expired(self):
        return self.time_remaining <= 0

    def complete(self, dish):
        if dish == self.dish and not self.is_expired():
            self.completed = True
            return True
        return False


class OrderManager:
    def __init__(self):
        self.orders = []
        self.dishes = ["Burger", "Salad", "Soup"]
        self.spawn_interval = 10
        self.spawn_timer = 0
        self.max_orders = 3

    def update(self, dt):
        for order in self.orders:
            order.update(dt)

        # Remove expired orders
        self.orders = [
            order for order in self.orders
            if not order.is_expired() and not order.completed
        ]

        # Generate new orders
        self.spawn_timer += dt

        if self.spawn_timer >= self.spawn_interval:
            self.spawn_timer = 0

            if len(self.orders) < self.max_orders:
                self.add_order()

    def add_order(self):
        if len(self.orders) < self.max_orders:
            dish = random.choice(self.dishes)
            self.orders.append(Order(dish))

    def serve_order(self, dish):
        for order in self.orders:
            if order.complete(dish):
                self.orders.remove(order)
                return True
        return False

    def draw(self, screen):
        font = pygame.font.SysFont(None, 26)

        for i, order in enumerate(self.orders):
            text = f"{order.dish}: {int(order.time_remaining)}s"
            label = font.render(text, True, (40, 40, 40))
            screen.blit(label, (20, 60 + i * 30))
