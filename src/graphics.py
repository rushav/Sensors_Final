# graphics.py
# All the drawing functions for game graphics
# Includes: background grid, HUD, player ship, targeting reticle, folder icons

def draw_grid(bitmap, offset):
    """
    Draw 3D perspective grid background (like flying through space)
    offset: animation frame to make grid move
    """
    vanish_x, vanish_y = 64, 20  # Vanishing point for perspective
    
    # Draw vertical perspective lines
    for i in range(0, 128, 20):
        x = i + (offset % 20)
        if x < 128:
            for y in range(20, 64):
                # Calculate perspective depth (0.0 at top, 1.0 at bottom)
                t = (y - 20) / 44.0
                # Apply perspective transformation
                line_x = int(vanish_x + (x - vanish_x) * t)
                if 0 <= line_x < 128:
                    bitmap[line_x, y] = 1
    
    # Draw horizontal perspective lines
    for i in range(30, 64, 10):
        y = i + (offset // 2) % 10
        if y < 64:
            # Width increases as we go down (perspective)
            width = int((64 - y) * 1.5)
            for x in range(max(0, 64 - width), min(128, 64 + width)):
                bitmap[x, y] = 1

def draw_hud(bitmap):
    """
    Draw corner brackets (heads-up display frame)
    Makes it look like a cockpit view
    """
    bracket_size = 10
    
    # Draw all four corner brackets
    for i in range(bracket_size):
        # Top-left corner
        bitmap[2, 2 + i] = 1
        bitmap[2 + i, 2] = 1
        
        # Top-right corner
        bitmap[126, 2 + i] = 1
        bitmap[126 - i, 2] = 1
        
        # Bottom-left corner
        bitmap[2, 62 - i] = 1
        bitmap[2 + i, 62] = 1
        
        # Bottom-right corner
        bitmap[126, 62 - i] = 1
        bitmap[126 - i, 62] = 1

def draw_targeting_reticle(bitmap):
    """
    Draw crosshair in center of screen (targeting system)
    """
    center_x, center_y = 64, 28
    
    # Horizontal crosshair lines (with gap in middle)
    for i in range(12, 3, -1):
        if 0 <= center_x - i < 128:
            bitmap[center_x - i, center_y] = 1
        if 0 <= center_x + i < 128:
            bitmap[center_x + i, center_y] = 1
    
    # Vertical crosshair lines (with gap in middle)
    for i in range(12, 3, -1):
        if 0 <= center_y - i < 64:
            bitmap[center_x, center_y - i] = 1
        if 0 <= center_y + i < 64:
            bitmap[center_x, center_y + i] = 1

def draw_player(bitmap, lane_index, lane_positions):
    """
    Draw player spaceship as triangle
    lane_index: which lane player is in (0, 1, or 2)
    lane_positions: list of x-coordinates for lanes
    """
    x = lane_positions[lane_index]
    y = 56  # Player is near bottom of screen
    
    # Draw triangle ship (gets wider as it goes down)
    for row in range(7):
        width = row
        for col in range(-width, width + 1):
            draw_x, draw_y = x + col, y + row
            if 0 <= draw_x < 128 and 0 <= draw_y < 64:
                bitmap[draw_x, draw_y] = 1
    
    # Draw engine exhaust ports
    if 0 <= x - 2 < 128 and y + 7 < 64:
        bitmap[x - 2, y + 7] = 1
    if 0 <= x + 2 < 128 and y + 7 < 64:
        bitmap[x + 2, y + 7] = 1

def draw_folder(bitmap, x, y):
    """
    Draw folder icon for menu (Windows desktop style)
    x, y: top-left corner of folder
    """
    # Draw tab
    for i in range(4):
        bitmap[x + i, y] = 1
    
    # Draw main folder body
    for row in range(5):
        for col in range(6):
            bitmap[x + col, y + 1 + row] = 1

def draw_spaceship(bitmap, x, y):
    """
    Draw spaceship for startup animation
    x, y: position of ship
    """
    # Draw nose cone
    if 0 <= x+6 < 128 and 0 <= y+2 < 64:
        bitmap[x+6, y+2] = 1
    
    # Draw main body
    for i in range(5):
        if 0 <= x+i < 128:
            if 0 <= y+1 < 64: bitmap[x+i, y+1] = 1
            if 0 <= y+2 < 64: bitmap[x+i, y+2] = 1
            if 0 <= y+3 < 64: bitmap[x+i, y+3] = 1
    
    # Draw wings
    if 0 <= x+2 < 128:
        if 0 <= y < 64: bitmap[x+2, y] = 1
        if 0 <= y+4 < 64: bitmap[x+2, y+4] = 1
    if 0 <= x+1 < 128:
        if 0 <= y < 64: bitmap[x+1, y] = 1
        if 0 <= y+4 < 64: bitmap[x+1, y+4] = 1

def draw_stars(bitmap):
    """Draw static starfield background"""
    stars = [(10, 5), (30, 15), (50, 8), (70, 20), (90, 12), (110, 18),
             (20, 35), (45, 40), (65, 30), (85, 45), (105, 38), (15, 50)]
    for star_x, star_y in stars:
        bitmap[star_x, star_y] = 1

def check_collision(player_lane, lane_positions, obstacles):
    """
    Check if player collided with any obstacles
    Returns True if collision detected
    """
    player_x = lane_positions[player_lane]
    player_y = 56
    
    for obs in obstacles:
        if obs.active and obs.health > 0:
            # Simple distance check
            if abs(player_x - obs.x) < 12 and abs(player_y - obs.y) < 10:
                return True
    return False