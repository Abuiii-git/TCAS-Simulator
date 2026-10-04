import pygame
from aircraft import Aircraft

pygame.init()

WIDTH = 1000
HEIGHT = 700

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TCAS Simulator - V1")

clock = pygame.time.Clock()

font = pygame.font.SysFont("Arial", 20)

# Our aircraft
own_aircraft = Aircraft(
    WIDTH // 2,
    HEIGHT // 2,
    10000,
    0,
    0,
    "OWN"
)

# Nearby aircraft
traffic = [
    Aircraft(250, 200, 10500, 50, 90, "A1"),
    Aircraft(750, 300, 9800, 40, 270, "A2"),
    Aircraft(300, 550, 10200, 30, 0, "A3"),
]


running = True

while running:

    dt = clock.tick(60) / 1000

    for event in pygame.event.get():

        if event.type == pygame.QUIT:
            running = False

    # Update aircraft
    for aircraft in traffic:
        aircraft.update(dt)

    # Clear screen
    screen.fill((10, 15, 25))

    # Radar circle
    center = (WIDTH // 2, HEIGHT // 2)

    pygame.draw.circle(
        screen,
        (40, 100, 40),
        center,
        250,
        2
    )

    pygame.draw.circle(
        screen,
        (40, 100, 40),
        center,
        150,
        1
    )

    pygame.draw.circle(
        screen,
        (40, 100, 40),
        center,
        75,
        1
    )

    # Crosshair
    pygame.draw.line(
        screen,
        (40, 100, 40),
        (WIDTH // 2 - 250, HEIGHT // 2),
        (WIDTH // 2 + 250, HEIGHT // 2),
        1
    )

    pygame.draw.line(
        screen,
        (40, 100, 40),
        (WIDTH // 2, HEIGHT // 2 - 250),
        (WIDTH // 2, HEIGHT // 2 + 250),
        1
    )

    # Draw own aircraft
    pygame.draw.circle(
        screen,
        (255, 255, 255),
        center,
        8
    )

    text = font.render(
        "OWN AIRCRAFT  10,000 ft",
        True,
        (255, 255, 255)
    )

    screen.blit(
        text,
        (center[0] + 15, center[1] - 10)
    )

    # Draw traffic
    for aircraft in traffic:

        pygame.draw.circle(
            screen,
            (255, 200, 50),
            (int(aircraft.x), int(aircraft.y)),
            8
        )

        label = font.render(
            f"{aircraft.name}  {aircraft.altitude} ft",
            True,
            (255, 200, 50)
        )

        screen.blit(
            label,
            (aircraft.x + 12, aircraft.y - 10)
        )

    # Title
    title = font.render(
        "TCAS-INSPIRED SIMULATOR",
        True,
        (255, 255, 255)
    )

    screen.blit(title, (20, 20))

    pygame.display.flip()


pygame.quit()