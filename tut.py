import pygame
import math
pygame.init()

WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Planet Simulation")

WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
YELLOW = (255, 255, 0)
BLUE = (100, 149, 237)
RED = (188, 39, 50)
DARK_GREY = (80, 78, 81)

FONT = pygame.font.SysFont("comicsans", 16)

class Planet:
    # distance from the sun in meters
    AU = 149.6e6 * 1000
    G = 6.67428e-11
    SCALE = 250 / AU    # 1 AU = 100px
    TIMESTEP = 3600 * 24    # 1 day in seconds

    def __init__(self, x, y, radius, color, mass, name) -> None:
        self.x = x
        self.y = y
        self.radius = radius
        self.color = color
        self.mass = mass

        self.orbit = []
        self.sun = False
        self.name = name
        self.distance_to_sun = 0

        self.x_vel = 0
        self.y_vel = 0
    
    def draw(self, win):
        x = self.x * self.SCALE + WIDTH / 2
        y = self.y * self.SCALE + HEIGHT / 2

        if len(self.orbit) > 2:
            updated_points = []
            for point in self.orbit:
                point_x, point_y = point
                point_x = point_x * self.SCALE + WIDTH / 2
                point_y = point_y * self.SCALE + HEIGHT / 2
                updated_points.append((point_x, point_y))

            pygame.draw.lines(win, self.color, False, updated_points, 2)

        # if not self.sun:
            # distance_text = FONT.render(f"{round(self.distance_to_sun / 1000, 1)}km", 1, WHITE)
        label_text = FONT.render(self.name, 1, WHITE)

        pygame.draw.circle(win, self.color, (x, y), self.radius)
        win.blit(label_text, (x - label_text.get_width() / 2, y - label_text.get_height() / 2))


    def attraction(self, other):
        other_x, other_y = other.x, other.y
        distance_x = other_x - self.x
        distance_y = other_y - self.y
        distance = math.sqrt(distance_y ** 2 + distance_x ** 2)

        if other.sun:
            self.distance_to_sun = distance
        
        force = self.G * self.mass * other.mass / distance ** 2
        theta = math.atan2(distance_y, distance_x)
        force_x = math.cos(theta) * force
        force_y = math.sin(theta) * force
        return force_x, force_y

    def update_position(self, planets):
        total_fx = total_fy = 0

        for planet in planets:
            if self == planet:
                continue

            fx, fy = self.attraction(planet)
            total_fx += fx
            total_fy += fy

        self.x_vel += total_fx / self.mass * self.TIMESTEP
        self.y_vel += total_fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))

def main():
    run = True
    clock = pygame.time.Clock()

    sun = Planet(0, 0, 30, YELLOW, 1.98892 * 10**30, "SUN")
    sun.sun = True

    earth = Planet(-1 * Planet.AU, 0, 16, BLUE, 5.9742 * 10**24, "EARTH")
    earth.y_vel = 29.783 * 1000 

    mars = Planet(-1.524 * Planet.AU, 0, 12, RED, 6.39 * 10**23, "MARS")
    mars.y_vel = 24.077 * 1000

    mercury = Planet(0.387 * Planet.AU, 0, 8, DARK_GREY, 3.30 * 10**23, "MERCURY")
    mercury.y_vel = -47.4 * 1000

    venus = Planet(0.723 * Planet.AU, 0, 14, WHITE, 4.8685 * 10**24, "VENUS")
    venus.y_vel = -35.02 * 1000

    # planets = [sun, earth, mars, mercury, venus]
    planets = [sun, earth, mars]

    while run:
        clock.tick(60)
        WIN.fill(BLACK)
        # pygame.display.update()
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for planet in planets:
            planet.update_position(planets)
            planet.draw(WIN)
        
        EARTH_COOR = (earth.x * Planet.SCALE + WIDTH / 2, earth.y * Planet.SCALE + HEIGHT / 2)
        MARS_COOR = (mars.x * Planet.SCALE + WIDTH / 2, mars.y * Planet.SCALE + HEIGHT / 2)
        pygame.draw.line(WIN, WHITE, EARTH_COOR, MARS_COOR)

        distance = math.sqrt((earth.x - mars.x) ** 2 + (earth.y - mars.y) ** 2)
        distance_text = FONT.render(str(distance) + " km", 1, WHITE)
        x = (EARTH_COOR[0] + MARS_COOR[0]) / 2
        y = (EARTH_COOR[1] + MARS_COOR[1]) / 2
        WIN.blit(distance_text, (x - distance_text.get_width() / 2, y - distance_text.get_height() / 2))

        pygame.display.update()
    
    pygame.quit()

main()