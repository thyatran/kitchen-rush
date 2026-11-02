# game window and main loop
import pygame
from src.chef import Chef
from src.order import OrderManager

pygame.init()

WIDTH, HEIGHT = 800, 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Kitchen Rush")

clock = pygame.time.Clock()

# create chef

chef = Chef(100, 100)

# order manager
order_manager = OrderManager()
order_manager.add_order()

# temporary serving counter
serving_counter = pygame.Rect(650, 400, 100, 60)

# temporary kitchen obstacles
obstacles = [
    pygame.Rect(250, 150, 120, 60),
    pygame.Rect(500, 300, 120, 60),
    pygame.Rect(200, 450, 150, 50),
    serving_counter
]

# temporary ingredient
ingredient = pygame.Rect(400, 200, 20, 20)
ingredient_available = True

font = pygame.font.SysFont(None, 28)

running = True

while running:
    dt = clock.tick(60) / 1000
    order_manager.update(dt)
    
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False

        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_e:
                if chef.carrying is None and ingredient_available:
                    if chef.interact(ingredient):
                        ingredient_available = False
                elif chef.carrying is not None:
                    chef.drop()
                    ingredient_available = True
            if event.key == pygame.K_f:
                if chef.rect.inflate(30, 30).colliderect(serving_counter):
                    if order_manager.orders:
                        test_dish = order_manager.orders[0].dish
                        order_manager.serve_order(test_dish)                   

    keys = pygame.key.get_pressed()
    chef.move(keys, obstacles, WIDTH, HEIGHT)

    screen.fill((245, 235, 220))

    # draw temporary obstacles
    for obstacle in obstacles:
        pygame.draw.rect(screen, (140, 100, 70), obstacle)

    # draw ingredient when not carried
    if ingredient_available:
        pygame.draw.rect(screen, (220, 70, 70), ingredient)

    chef.draw(screen)

    # display instructions
    instructions = font.render(
        "WASD / Arrows: Move | E: Pick up / Drop | F: Serve Order",
        True,
        (40, 40, 40)
    )
    screen.blit(instructions, (20, 20))

    pygame.draw.rect(
    screen, (80, 160, 100), serving_counter
)

    order_manager.draw(screen)

    pygame.display.flip()

pygame.quit()
