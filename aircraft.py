import math


class Aircraft:
    def __init__(self, x, y, altitude, speed, heading, name):
        self.x = x
        self.y = y
        self.altitude = altitude
        self.speed = speed
        self.heading = heading
        self.name = name

    def update(self, dt):
        # Convert heading from degrees to radians
        angle = math.radians(self.heading)

        # Convert speed into X/Y movement
        self.x += math.sin(angle) * self.speed * dt
        self.y += math.cos(angle) * self.speed * dt