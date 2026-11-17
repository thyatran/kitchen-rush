import random


class Order:
    def __init__(self, dish, time_limit=30):
        self.dish = dish
        self.time_remaining = float(time_limit)
        self.completed = False

    def update(self, dt):
        self.time_remaining = max(0, self.time_remaining - dt)

    def is_expired(self):
        return self.time_remaining <= 0

    def complete(self, dish):
        if not self.completed and not self.is_expired() and dish == self.dish:
            self.completed = True
            return True
        return False


class OrderManager:
    def __init__(self, dishes, spawn_interval=10, time_limit=60, max_orders=3):
        self.orders = []
        self.dishes = list(dishes)
        self.spawn_interval = spawn_interval
        self.time_limit = time_limit
        self.spawn_timer = 0
        self.max_orders = max_orders

    def add_order(self):
        if len(self.orders) < self.max_orders:
            self.orders.append(Order(random.choice(self.dishes), self.time_limit))

    def update(self, dt):
        for order in self.orders:
            order.update(dt)
        expired = sum(order.is_expired() for order in self.orders)
        self.orders = [order for order in self.orders if not order.is_expired() and not order.completed]
        self.spawn_timer += dt
        while self.spawn_timer >= self.spawn_interval:
            self.spawn_timer -= self.spawn_interval
            self.add_order()
        return expired

    def serve_order(self, dish):
        for order in self.orders:
            if order.complete(dish):
                self.orders.remove(order)
                return True
        return False
