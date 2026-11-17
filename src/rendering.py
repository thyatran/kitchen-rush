"""Temporary shape-based artwork; game state and collisions live elsewhere."""
import pygame
from src.ingredient import Dish
from src.plates import Plate
from src.layout import KITCHEN, COUNTERS

FOOD = {'bun': (232, 177, 72), 'patty': (117, 53, 42), 'lettuce': (76, 170, 76),
        'tomato': (218, 62, 48), 'mushroom': (150, 105, 76)}
DISH_FOODS = {'Burger': ['bun', 'patty'], 'Salad': ['lettuce', 'tomato'], 'Soup': ['tomato', 'mushroom']}


def draw_item(screen, item, center, radius=9):
    if isinstance(item, Plate):
        color = (248, 247, 234) if item.state == 'clean' else (155, 150, 137)
        pygame.draw.circle(screen, color, center, radius + 3)
        pygame.draw.circle(screen, (75, 75, 70), center, radius + 3, 2)
    elif isinstance(item, Dish):
        pygame.draw.circle(screen, (248, 247, 234), center, radius + 4)
        pygame.draw.circle(screen, (120, 120, 120), center, radius + 4, 1)
        for offset, name in zip((-4, 4), DISH_FOODS.get(item.name, [])):
            pygame.draw.circle(screen, FOOD[name], (center[0] + offset, center[1]), max(3, radius // 2))
    else:
        pygame.draw.circle(screen, FOOD.get(item.name, (190, 160, 120)), center, radius)
        pygame.draw.circle(screen, (65, 60, 50), center, radius, 1)
        if item.state != 'raw':
            pygame.draw.line(screen, (245, 245, 220), (center[0] - 4, center[1]), (center[0] + 4, center[1]), 2)


def draw_scene(screen):
    pygame.draw.rect(screen, (107, 109, 108), KITCHEN)
    # Sidewalk bands, central road and crosswalk create distinct street work areas.
    pygame.draw.rect(screen, (165, 164, 153), (20, 112, 960, 48))
    pygame.draw.rect(screen, (165, 164, 153), (20, 580, 960, 52))
    pygame.draw.rect(screen, (83, 86, 87), (420, 112, 160, 520))
    for y in range(145, 580, 55):
        pygame.draw.rect(screen, (239, 237, 222), (435, y, 130, 25), border_radius=2)
    for x in range(55, 950, 110):
        if not 400 < x < 590:
            pygame.draw.rect(screen, (220, 206, 165), (x, 355, 50, 4))
    for rect in COUNTERS:
        pygame.draw.rect(screen, (193, 149, 98), rect)
        pygame.draw.rect(screen, (95, 70, 52), rect, 2)
    pygame.draw.rect(screen, (65, 65, 60), KITCHEN, 3)


def draw_station(screen, station, font, plates):
    rect = station.rect
    pygame.draw.rect(screen, (194, 151, 100), rect)
    pygame.draw.rect(screen, (101, 74, 52), rect, 2)
    pygame.draw.line(screen, (230, 189, 133), (rect.left + 3, rect.top + 4), (rect.right - 3, rect.top + 4), 2)
    if station.kind == 'source':
        pygame.draw.rect(screen, (110, 85, 65), rect.inflate(-12, -22), border_radius=4)
        from src.ingredient import Ingredient
        for x in (rect.centerx - 20, rect.centerx, rect.centerx + 20):
            draw_item(screen, Ingredient(station.source), (x, rect.centery + 6), 7)
    elif station.kind == 'cut':
        pygame.draw.rect(screen, (237, 207, 156), rect.inflate(-18, -22), border_radius=3)
    elif station.kind == 'stove':
        pygame.draw.rect(screen, (64, 67, 66), rect.inflate(-12, -16), border_radius=3)
        pygame.draw.circle(screen, (160, 160, 145), (rect.centerx, rect.centery + 5), 16, 3)
    elif station.kind == 'assembly':
        pygame.draw.circle(screen, (250, 249, 234), (rect.centerx, rect.centery + 5), 19)
        for index, item in enumerate(station.parts):
            draw_item(screen, item, (rect.centerx - 8 + index * 16, rect.centery + 5), 7)
        if station.dish:
            draw_item(screen, station.dish, (rect.centerx, rect.centery + 5), 12)
    elif station.kind == 'serve':
        pygame.draw.circle(screen, (250, 249, 234), (rect.centerx, rect.centery + 6), 17, 3)
    elif station.kind == 'sink':
        basin = rect.inflate(-14, -20)
        pygame.draw.rect(screen, (100, 154, 175), basin, border_radius=4)
        pygame.draw.rect(screen, (49, 78, 90), basin, 2, border_radius=4)
        pygame.draw.line(screen, (215, 225, 225), (rect.centerx + 18, rect.top + 20), (rect.centerx + 18, rect.top + 10), 3)
        pygame.draw.line(screen, (215, 225, 225), (rect.centerx + 18, rect.top + 10), (rect.centerx + 8, rect.top + 10), 3)
        if station.item is None:
            pygame.draw.circle(screen, (240, 240, 230), (rect.centerx, rect.centery + 8), 10, 2)
    elif station.kind == 'return':
        pygame.draw.circle(screen, (155, 150, 137), (rect.centerx, rect.centery + 8), 13)
        count = font.render(str(plates.dirty), True, (35, 29, 23))
        screen.blit(count, (rect.centerx + 15, rect.centery + 1))
    elif station.kind == 'trash':
        pygame.draw.rect(screen, (54, 91, 67), rect.inflate(-35, -18), border_radius=3)
        pygame.draw.line(screen, (30, 50, 35), (rect.centerx - 19, rect.top + 18), (rect.centerx + 19, rect.top + 18), 4)
    if station.item:
        draw_item(screen, station.item, (rect.centerx, rect.centery + 6), 10)
        if station.remaining:
            bar = pygame.Rect(rect.x + 8, rect.bottom - 8, rect.width - 16, 5)
            pygame.draw.rect(screen, (45, 45, 45), bar)
            pygame.draw.rect(screen, (103, 211, 105), (bar.x, bar.y, round(bar.width * (1 - station.remaining / station.duration)), bar.height))
    label = font.render(station.name, True, (35, 29, 23))
    screen.blit(label, (rect.x + 5, rect.y + 3))


def draw_chef(screen, chef):
    chef.draw(screen)
    if chef.carrying:
        draw_item(screen, chef.carrying, (chef.rect.centerx, chef.rect.top - 7))
