import pygame
import math
import sys
from aircraft import Aircraft

# Initialize Pygame
pygame.init()
pygame.font.init()

# Screen dimensions
WIDTH, HEIGHT = 800, 800
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("TCAS II - Traffic Alert & Collision Avoidance System")

# Colors
BG_COLOR = (15, 20, 28)
RADAR_GREEN = (0, 180, 90)
GRID_LINE = (30, 60, 45)
TEXT_COLOR = (220, 230, 240)

# TCAS Threat Colors
COLOR_OTHER = (0, 220, 220)       # Cyan (Hollow Diamond)
COLOR_PROXIMATE = (240, 240, 240)  # White (Solid Diamond)
COLOR_TA = (255, 200, 0)          # Yellow (Solid Circle)
COLOR_RA = (255, 40, 40)          # Red (Solid Square)

# Fonts
FONT_SMALL = pygame.font.SysFont("Consolas", 12, bold=True)
FONT_MED = pygame.font.SysFont("Consolas", 16, bold=True)
FONT_LARGE = pygame.font.SysFont("Consolas", 24, bold=True)
FONT_ALERT = pygame.font.SysFont("Consolas", 32, bold=True)

# Center of radar display
CENTER = (WIDTH // 2, HEIGHT // 2)

# Ownship setup
ownship = Aircraft(
    x=CENTER[0],
    y=CENTER[1],
    altitude=10000,
    speed=120,
    heading=0,
    callsign="OWN"
)

# Nearby traffic setup
traffic = [
    Aircraft(250, 200, 10500, 110, 135, "A1"),
    Aircraft(650, 300, 9800, 90, 270, "A2"),
    Aircraft(300, 550, 10200, 80, 45, "A3"),
    Aircraft(420, 180, 10100, 130, 180, "A4"),
]

def calculate_tcas(own: Aircraft, intruder: Aircraft):
    """Calculate TCAS threat level between ownship and intruder."""
    dx = intruder.x - own.x
    dy = intruder.y - own.y
    dist_px = math.hypot(dx, dy)
    
    # Relative altitude in feet
    rel_alt = intruder.altitude - own.altitude
    abs_alt_diff = abs(rel_alt)

    # Relative velocity
    vx_own, vy_own = own.get_velocity()
    vx_int, vy_int = intruder.get_velocity()
    rel_vx = vx_int - vx_own
    rel_vy = vy_int - vy_own

    # Closure rate (pixels per second)
    # R * dR/dt = x*vx + y*vy
    if dist_px > 0:
        closure_rate = -(dx * rel_vx + dy * rel_vy) / dist_px
    else:
        closure_rate = 0

    # Calculate TAU (time to closest point of approach in seconds)
    if closure_rate > 0:
        tau = dist_px / closure_rate
    else:
        tau = 999.0  # Diverging or parallel

    # TCAS II Threat Classification Criteria
    # Distance thresholds (in pixels: 25px = ~1 NM)
    # RA: Tau < 25s or (dist < 50px (~2NM) and abs_alt_diff < 600ft)
    # TA: Tau < 40s or (dist < 100px (~4NM) and abs_alt_diff < 850ft)
    # Proximate: dist < 150px (~6NM) and abs_alt_diff < 1200ft
    # Other: otherwise
    
    if (tau < 25 or dist_px < 50) and abs_alt_diff <= 600:
        threat = "RA"
        if rel_alt < 0:
            command = "CLIMB, CLIMB!"
        else:
            command = "DESCEND, DESCEND!"
    elif (tau < 40 or dist_px < 100) and abs_alt_diff <= 850:
        threat = "TA"
        command = "TRAFFIC, TRAFFIC"
    elif dist_px < 150 and abs_alt_diff <= 1200:
        threat = "PROXIMATE"
        command = None
    else:
        threat = "OTHER"
        command = None

    return threat, command, rel_alt

def draw_radar_grid(screen, center):
    """Draw radar display range rings and crosshairs."""
    # Outer ring (9 NM / 225 px)
    pygame.draw.circle(screen, GRID_LINE, center, 225, 1)
    # Mid ring (6 NM / 150 px)
    pygame.draw.circle(screen, RADAR_GREEN, center, 150, 1)
    # Inner ring (3 NM / 75 px)
    pygame.draw.circle(screen, RADAR_GREEN, center, 75, 1)

    # Range Labels
    lbl3 = FONT_SMALL.render("3 NM", True, RADAR_GREEN)
    lbl6 = FONT_SMALL.render("6 NM", True, RADAR_GREEN)
    lbl9 = FONT_SMALL.render("9 NM", True, GRID_LINE)
    screen.blit(lbl3, (center[0] + 5, center[1] - 75 + 2))
    screen.blit(lbl6, (center[0] + 5, center[1] - 150 + 2))
    screen.blit(lbl9, (center[0] + 5, center[1] - 225 + 2))

    # Crosshairs
    pygame.draw.line(screen, GRID_LINE, (center[0], center[1] - 250), (center[0], center[1] + 250), 1)
    pygame.draw.line(screen, GRID_LINE, (center[0] - 250, center[1]), (center[0] + 250, center[1]), 1)

def draw_ownship(screen, own: Aircraft):
    """Draw ownship icon at center."""
    cx, cy = own.x, own.y
    # White Aircraft Chevron
    points = [
        (cx, cy - 12),
        (cx + 8, cy + 8),
        (cx, cy + 4),
        (cx - 8, cy + 8)
    ]
    pygame.draw.polygon(screen, (255, 255, 255), points)
    pygame.draw.polygon(screen, COLOR_OTHER, points, 2)

def draw_aircraft_symbol(screen, aircraft: Aircraft, threat: str, rel_alt: float):
    """Draw intruder aircraft symbol according to TCAS threat level."""
    x, y = int(aircraft.x), int(aircraft.y)

    # Draw velocity vector line (flight path)
    rad = math.radians(aircraft.heading)
    vec_len = (aircraft.speed / 10.0) * 1.5
    end_x = x + math.sin(rad) * vec_len
    end_y = y - math.cos(rad) * vec_len
    pygame.draw.line(screen, (150, 150, 150), (x, y), (end_x, end_y), 1)

    # Draw TCAS Symbol
    if threat == "RA":
        # Solid Red Square
        pygame.draw.rect(screen, COLOR_RA, (x - 7, y - 7, 14, 14))
    elif threat == "TA":
        # Solid Yellow Circle
        pygame.draw.circle(screen, COLOR_TA, (x, y), 7)
    elif threat == "PROXIMATE":
        # Solid White Diamond
        pts = [(x, y - 8), (x + 8, y), (x, y + 8), (x - 8, y)]
        pygame.draw.polygon(screen, COLOR_PROXIMATE, pts)
    else:
        # Hollow Cyan Diamond (OTHER)
        pts = [(x, y - 8), (x + 8, y), (x, y + 8), (x - 8, y)]
        pygame.draw.polygon(screen, COLOR_OTHER, pts, 2)

    # Relative Altitude Tag (e.g. +05 for +500ft, -02 for -200ft)
    alt_hundreds = int(rel_alt / 100)
    sign = "+" if alt_hundreds >= 0 else "-"
    tag_str = f"{sign}{abs(alt_hundreds):02d}"
    
    # Arrow indicator for vertical trend
    if aircraft.vs > 100:
        tag_str += " ↑"
    elif aircraft.vs < -100:
        tag_str += " ↓"

    color_map = {
        "RA": COLOR_RA,
        "TA": COLOR_TA,
        "PROXIMATE": COLOR_PROXIMATE,
        "OTHER": COLOR_OTHER
    }
    txt_color = color_map.get(threat, COLOR_OTHER)
    alt_lbl = FONT_SMALL.render(tag_str, True, txt_color)
    screen.blit(alt_lbl, (x + 10, y - 8))
    
    # Callsign tag
    call_lbl = FONT_SMALL.render(aircraft.callsign, True, (160, 170, 180))
    screen.blit(call_lbl, (x + 10, y + 4))

def draw_hud(screen, own: Aircraft, highest_threat: str, active_command: str):
    """Draw status telemetry banner and TCAS advisory overlay."""
    # Top Control Panel
    hud_bg = pygame.Rect(10, 10, 780, 50)
    pygame.draw.rect(screen, (25, 32, 44), hud_bg)
    pygame.draw.rect(screen, (50, 70, 90), hud_bg, 2)

    telemetry = f"OWNSHIP | ALT: {int(own.altitude)} FT | SPD: {int(own.speed)} KTS | HDG: {int(own.heading)}° | VS: {int(own.vs)} FPM"
    txt_tele = FONT_MED.render(telemetry, True, TEXT_COLOR)
    screen.blit(txt_tele, (20, 24))

    # Controls legend at bottom
    ctrl_str = "CONTROLS: [←/→] Heading | [↑/↓] Speed | [W/S] Altitude | [R] Reset"
    txt_ctrl = FONT_SMALL.render(ctrl_str, True, (120, 140, 160))
    screen.blit(txt_ctrl, (20, HEIGHT - 30))

    # Alert Advisory Box (if TA or RA active)
    if highest_threat == "RA":
        box_rect = pygame.Rect(WIDTH // 2 - 200, 70, 400, 60)
        pygame.draw.rect(screen, (60, 0, 0), box_rect)
        pygame.draw.rect(screen, COLOR_RA, box_rect, 3)
        lbl_ra = FONT_ALERT.render(f"RA: {active_command}", True, COLOR_RA)
        screen.blit(lbl_ra, (WIDTH // 2 - lbl_ra.get_width() // 2, 82))
    elif highest_threat == "TA":
        box_rect = pygame.Rect(WIDTH // 2 - 180, 70, 360, 50)
        pygame.draw.rect(screen, (50, 40, 0), box_rect)
        pygame.draw.rect(screen, COLOR_TA, box_rect, 3)
        lbl_ta = FONT_LARGE.render(f"TA: {active_command}", True, COLOR_TA)
        screen.blit(lbl_ta, (WIDTH // 2 - lbl_ta.get_width() // 2, 82))

# Clock setup
clock = pygame.time.Clock()
running = True

while running:
    dt = clock.tick(60) / 1000.0  # seconds per frame

    # Event Handling
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            running = False
        elif event.type == pygame.KEYDOWN:
            if event.key == pygame.K_r:
                # Reset traffic position
                ownship.x, ownship.y, ownship.altitude = CENTER[0], CENTER[1], 10000
                traffic[0].x, traffic[0].y, traffic[0].altitude = 250, 200, 10500
                traffic[1].x, traffic[1].y, traffic[1].altitude = 650, 300, 9800
                traffic[2].x, traffic[2].y, traffic[2].altitude = 300, 550, 10200
                traffic[3].x, traffic[3].y, traffic[3].altitude = 420, 180, 10100

    # User Input for Ownship
    keys = pygame.key.get_pressed()
    if keys[pygame.K_LEFT]:
        ownship.heading = (ownship.heading - 45 * dt) % 360
    if keys[pygame.K_RIGHT]:
        ownship.heading = (ownship.heading + 45 * dt) % 360
    if keys[pygame.K_UP]:
        ownship.speed = min(300, ownship.speed + 20 * dt)
    if keys[pygame.K_DOWN]:
        ownship.speed = max(0, ownship.speed - 20 * dt)
    if keys[pygame.K_w]:
        ownship.altitude += 500 * dt
        ownship.vs = 500
    elif keys[pygame.K_s]:
        ownship.altitude -= 500 * dt
        ownship.vs = -500
    else:
        ownship.vs = 0

    # Clear screen
    screen.fill(BG_COLOR)

    # Draw Radar Display
    draw_radar_grid(screen, CENTER)

    # Update and evaluate traffic TCAS
    highest_threat = "OTHER"
    active_command = None

    for target in traffic:
        target.update(dt)
        threat, command, rel_alt = calculate_tcas(ownship, target)
        target.threat_level = threat
        draw_aircraft_symbol(screen, target, threat, rel_alt)

        if threat == "RA":
            highest_threat = "RA"
            active_command = command
        elif threat == "TA" and highest_threat != "RA":
            highest_threat = "TA"
            active_command = command

    # Update & Draw Ownship
    draw_ownship(screen, ownship)

    # Draw Telemetry & Advisory Overlay
    draw_hud(screen, ownship, highest_threat, active_command)

    # Render Frame
    pygame.display.flip()

pygame.quit()
sys.exit()
