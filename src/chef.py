# chef movement and interactions


import pygame


class Chef:
    def __init__(self, x, y):
        self.rect = pygame.Rect(x, y, 35, 35)
        self.speed = 4
        self.color = (70, 130, 200)
        self.carrying = None

    def move(self, keys, obstacles, screen_width, screen_height):
        dx = 0
        dy = 0

        if keys[pygame.K_w] or keys[pygame.K_UP]:
            dy -= self.speed
        if keys[pygame.K_s] or keys[pygame.K_DOWN]:
            dy += self.speed
        if keys[pygame.K_a] or keys[pygame.K_LEFT]:
            dx -= self.speed
        if keys[pygame.K_d] or keys[pygame.K_RIGHT]:
            dx += self.speed

        # Move horizontally and check collision
        self.rect.x += dx
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                self.rect.x -= dx
                break

        # Move vertically and check collision
        self.rect.y += dy
        for obstacle in obstacles:
            if self.rect.colliderect(obstacle):
                self.rect.y -= dy
                break

        # Keep chef inside the window
        self.rect.clamp_ip(
            pygame.Rect(0, 0, screen_width, screen_height)
        )

    def interact(self, ingredient):
        # Pick up an ingredient when close enough
        if self.carrying is None:
            if self.rect.inflate(30, 30).colliderect(ingredient):
                self.carrying = ingredient
                return True

        return False

    def drop(self):
        if self.carrying is not None:
            self.carrying.x = self.rect.right + 10
            self.carrying.y = self.rect.y
            self.carrying = None

    def draw(self, screen):
        pygame.draw.rect(screen, self.color, self.rect)

        # Show carried ingredient above the chef
        if self.carrying is not None:
            carried_rect = pygame.Rect(
                self.rect.centerx - 10,
                self.rect.y - 20,
                20,
                20
            )
            pygame.draw.rect(screen, (220, 70, 70), carried_rect)