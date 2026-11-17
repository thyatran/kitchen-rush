import pygame


class Chef:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 32, 32)
        self.pos = pygame.Vector2(x, y)
        self.speed = 200
        self.carrying = None

    def move(self, keys, obstacles, bounds, dt):
        dx = int(bool(keys[pygame.K_d] or keys[pygame.K_RIGHT])) - int(bool(keys[pygame.K_a] or keys[pygame.K_LEFT]))
        dy = int(bool(keys[pygame.K_s] or keys[pygame.K_DOWN])) - int(bool(keys[pygame.K_w] or keys[pygame.K_UP]))
        direction = pygame.Vector2(dx, dy)
        if direction.length_squared():
            direction.normalize_ip()
        steps = max(1, int(self.speed * dt / 4) + 1)
        for _ in range(steps):
            for axis in (0, 1):
                old = self.pos[axis]
                self.pos[axis] += direction[axis] * self.speed * dt / steps
                self.rect.topleft = (round(self.pos.x), round(self.pos.y))
                if not bounds.contains(self.rect) or any(self.rect.colliderect(o) for o in obstacles):
                    self.pos[axis] = old
                    self.rect.topleft = (round(self.pos.x), round(self.pos.y))

    def draw(self, screen):
        pygame.draw.rect(screen, (70, 130, 200), self.rect)
