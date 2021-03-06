import pygame
import math

# Initialize pygame
pygame.init()

# Initialize window
WIDTH, HEIGHT = 800, 800
WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Retrograde motion Simulation")

# Colors used
Colors = {
    "WHITE": (255, 255, 255),
    "BLACK": (0, 0, 0),
    "YELLOW": (255, 255, 0),
    "EARTH": (100, 149, 237),
    "MARS": (188, 39, 50)
}

# Planets data
planets_dict = {
    "SUN": {
        "start_x": 0,
        "start_y": 0,
        "radius": 30, # in pixels
        "color": Colors["YELLOW"],
        "mass": 1.989 * 10**30,
        "init_y_vel": 0,
        "init_x_vel": 0
    },
    "EARTH": {
        "start_x": -1,
        "start_y": 0,
        "radius": 16, # in pixels
        "color": Colors["EARTH"],
        "mass": 5.9722 * 10**24,
        "init_y_vel": 29.78 * 1000,
        "init_x_vel": 0
    },
    "MARS": {
        "start_x": -1.5,
        "start_y": 0,
        "radius": 12, # in pixels
        "color": Colors["MARS"],
        "mass": 6.4169 * 10**23,
        "init_y_vel": 24.07 * 1000,
        "init_x_vel": 0
    }
}

# FONT properties
FONT = pygame.font.SysFont("comicsans", 16)

# Limit of frames per second
FPS = 60

# OFFSET
OFFSET_X, OFFSET_Y = WIDTH / 2, HEIGHT / 2

# Planet class
class Planet:
    AU = 1.496e+11     # distance from the sun in meters
    G = 6.67e-11
    SCALE = 50 / AU         # to scale the screen to distances, scale: 1 AU is 20px of screen
    TIMESTEP = 3600 * 24    # 1 day in seconds

    def __init__(self, planet, name) -> None:
        self.x = planet["start_x"] * self.AU
        self.y = planet["start_y"] * self.AU
        self.radius = planet["radius"]
        self.color = planet["color"]
        self.mass = planet["mass"]

        self.orbit = []
        self.sun = (name == "SUN")
        self.name = name

        self.x_vel = planet["init_x_vel"]
        self.y_vel = planet["init_y_vel"]

    def draw(self, win):
        x = self.x * self.SCALE + OFFSET_X
        y = self.y * self.SCALE + OFFSET_Y

        if len(self.orbit) > 2:
            orbit_points = []
            for point in self.orbit:
                point_x, point_y = point
                point_x = point_x * self.SCALE + OFFSET_X
                point_y = point_y * self.SCALE + OFFSET_Y
                orbit_points.append((point_x, point_y))

            pygame.draw.lines(win, self.color, False, orbit_points, 2)
        
        color = "WHITE"
        if self.name == "SUN":
            color = "BLACK"
        
        label_text = FONT.render(self.name, 1, Colors[color])

        pygame.draw.circle(win, self.color, (x, y), self.radius)
        win.blit(label_text, (x - label_text.get_width() / 2, y - label_text.get_height() / 2))


    def get_force(self, sun):
        sun_x, sun_y = sun.x, sun.y
        dist_x = sun_x - self.x
        dist_y = sun_y - self.y
        dist = math.sqrt(dist_y * dist_y + dist_x * dist_x)
        
        # F = G * M * m / R^2
        # calculate fx and fy using magnitude and angle
        magnitude = (self.G * self.mass * sun.mass) / (dist ** 2)
        angle = math.atan2(dist_y, dist_x)
        fx = math.cos(angle) * magnitude
        fy = math.sin(angle) * magnitude
        return fx, fy

    def update_position(self, sun):
        fx, fy = self.get_force(sun)

        self.x_vel += fx / self.mass * self.TIMESTEP
        self.y_vel += fy / self.mass * self.TIMESTEP

        self.x += self.x_vel * self.TIMESTEP
        self.y += self.y_vel * self.TIMESTEP
        self.orbit.append((self.x, self.y))

def get_intersection(R, center, coor1, coor2):
    # shift origin
    x1, y1 = (coor1[0] - center[0]), (coor1[1] - center[1])
    x2, y2 = (coor2[0] - center[0]), (coor2[1] - center[1])

    # convert 2 points to ax + by + c = 0
    A = y1 - y2
    B = x2 - x1
    C = y2 * x1 - x2 * y1

    x0 = (-1 * A * C) / (A ** 2 + B ** 2)
    y0 = (-1 * B * C) / (A ** 2 + B ** 2)
    d = (R ** 2) - ((C ** 2) / (A ** 2 + B ** 2))
    m = math.sqrt(d / (A ** 2 + B ** 2))

    ax, ay = x0 + B * m, y0 - A * m
    bx, by = x0 - B * m, y0 + A * m

    # check if 2 points lie on the same side of the line perpendicular to current line segment
    # new line perpendicular: a1x + b1y + c1 = 0
    a1, b1, c1 = -B, A, (B * x1 - A * y1)
    if (a1 * ax + b1 * ay + c1 > 0) == (a1 * x2 + b1 * y2 + c1 > 0):
        return ax + center[0], ay + center[1]
    
    return bx + center[0], by + center[0]

def main():
    run = True
    clock = pygame.time.Clock()

    sun = Planet(planets_dict["SUN"], "SUN")
    earth = Planet(planets_dict["EARTH"], "EARTH")
    mars = Planet(planets_dict["MARS"], "MARS")

    planets = [sun, earth, mars]

    while run:
        clock.tick(FPS)
        WIN.fill(Colors["BLACK"])
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False

        for planet in planets:
            if planet != sun:
                planet.update_position(sun)
            planet.draw(WIN)

        # draw line bw earth and mars
        EARTH_COOR = (earth.x * Planet.SCALE + OFFSET_X, earth.y * Planet.SCALE + OFFSET_Y)
        MARS_COOR = (mars.x * Planet.SCALE + OFFSET_X, mars.y * Planet.SCALE + OFFSET_Y)

        # find projection and show it
        RADIUS = 380
        CENTER = (OFFSET_X, OFFSET_Y)
        pygame.draw.circle(WIN, Colors["WHITE"], CENTER, RADIUS, 1)

        # find the point of intersection and draw it
        point = get_intersection(RADIUS, CENTER, EARTH_COOR, MARS_COOR)
        pygame.draw.circle(WIN, mars.color, point, mars.radius)
        pygame.draw.line(WIN, Colors["WHITE"], EARTH_COOR, point)

        # find distance and show it bw earth and mars
        distance = math.sqrt((earth.x - mars.x) ** 2 + (earth.y - mars.y) ** 2)
        distance_text = FONT.render("Distance between Earth and Mars: " + str(distance) + " km", 1, Colors["WHITE"])
        WIN.blit(distance_text, (0, 0))

        pygame.display.update()
    
    pygame.quit()


# Call the main function
main()