import pygame
from src.station import Station

KITCHEN = pygame.Rect(20, 112, 960, 520)
# Distinct islands leave a wide route on each side and the crosswalk unobstructed.
STATIONS = [
    ('Bun', 'source', (55, 175, 78, 58), 'bun'),
    ('Patty', 'source', (133, 175, 78, 58), 'patty'),
    ('Lettuce', 'source', (211, 175, 78, 58), 'lettuce'),
    ('Cutting', 'cut', (289, 175, 90, 58), None),
    ('Stove', 'stove', (65, 400, 100, 58), None),
    ('Assembly', 'assembly', (165, 400, 120, 58), None),
    ('Serve', 'serve', (285, 400, 95, 58), None),
    ('Return', 'return', (285, 458, 95, 58), None),
    ('Tomato', 'source', (610, 175, 85, 58), 'tomato'),
    ('Mushroom', 'source', (695, 175, 90, 58), 'mushroom'),
    ('Stove 2', 'stove', (785, 175, 90, 58), None),
    ('Cutting 2', 'cut', (875, 175, 90, 58), None),
    ('Assembly 2', 'assembly', (605, 440, 120, 58), None),
    ('Serve 2', 'serve', (725, 440, 90, 58), None),
    ('Sink', 'sink', (815, 440, 90, 58), None),
    ('Trash', 'trash', (815, 498, 90, 58), None),
]
# Small, solid, visible islands are clear of station approaches.
COUNTERS = [(55, 290, 92, 38), (852, 300, 92, 38)]
PEDESTRIAN_PATHS = [((465, 100), (465, 644)), ((535, 644), (535, 100))]


def make_stations():
    return [Station(*data) for data in STATIONS]


def counter_rects():
    return [pygame.Rect(rect) for rect in COUNTERS]
