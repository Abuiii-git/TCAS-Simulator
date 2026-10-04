import math

class Aircraft:
    def __init__(self, x: float, y: float, altitude: float, speed: float, heading: float, callsign: str):
        self.x = x
        self.y = y
        self.altitude = altitude  # feet
        self.speed = speed        # knots / pixels per second
        self.heading = heading    # degrees (0 = North, 90 = East)
        self.callsign = callsign
        self.vs = 0.0             # vertical speed (ft/min)
        self.threat_level = "OTHER"  # OTHER, PROXIMATE, TA, RA
        self.vs_command = None    # "CLIMB", "DESCEND", "MAINTAIN"

    def update(self, dt: float):
        """Update aircraft position based on speed and heading."""
        rad = math.radians(self.heading)
        # 0 deg = Up (-Y), 90 deg = Right (+X)
        dx = math.sin(rad) * self.speed * dt
        dy = -math.cos(rad) * self.speed * dt
        self.x += dx
        self.y += dy
        self.altitude += (self.vs / 60.0) * dt

    def get_velocity(self):
        rad = math.radians(self.heading)
        vx = math.sin(rad) * self.speed
        vy = -math.cos(rad) * self.speed
        return vx, vy
