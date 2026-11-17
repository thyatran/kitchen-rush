import random
import pygame
from src.layout import PEDESTRIAN_PATHS


class Pedestrian:
    def __init__(self, start, end, speed, color, radius=12):
        self.position = pygame.Vector2(start)
        self.end = pygame.Vector2(end)
        self.direction = (self.end - self.position).normalize()
        self.speed, self.color, self.radius = speed, color, radius
        self.finished = False

    @property
    def rect(self):
        return pygame.Rect(round(self.position.x - self.radius), round(self.position.y - self.radius), self.radius * 2, self.radius * 2)

    def update(self, dt, obstacles=()):
        distance = min(self.speed * dt, self.position.distance_to(self.end))
        # Check short increments so a slow frame cannot skip over a hitbox.
        steps = max(1, int(distance / 2) + 1)
        for _ in range(steps):
            previous = self.position.copy()
            self.position += self.direction * distance / steps
            if any(self.rect.colliderect(obstacle) for obstacle in obstacles):
                self.position = previous
                break
        if self.position.distance_to(self.end) < 0.1:
            self.finished = True


class PedestrianManager:
    def __init__(self):
        self.people = []
        self.timer = 1.0

    def update(self, dt, chef_rect):
        self.timer -= dt
        if self.timer <= 0:
            start, end = random.choice(PEDESTRIAN_PATHS)
            person = Pedestrian(start, end, random.uniform(42, 72), random.choice([(185, 84, 80), (95, 145, 110), (160, 115, 175), (210, 155, 75)]))
            if not any(person.rect.colliderect(rect) for rect in [chef_rect] + [p.rect for p in self.people]):
                self.people.append(person)
                self.timer = 3.5
            else:
                # Retry later instead of creating overlapping hitboxes.
                self.timer = 0.25
        for person in self.people:
            obstacles = [chef_rect] + [other.rect for other in self.people if other is not person]
            person.update(dt, obstacles)
        self.people = [person for person in self.people if not person.finished]
