# game_objects.py
# Game entities: Obstacles and Bullets
# These are the things that move on screen during gameplay

import random

class Obstacle:
    """
    Enemy obstacle that moves down the screen
    Player must dodge or shoot these
    """
    
    def __init__(self, lane, lane_positions):
        """
        Create obstacle in a random lane
        lane: which lane (0, 1, or 2)
        lane_positions: list of x-coordinates for each lane
        """
        self.lane = lane
        self.x = lane_positions[lane]
        self.y = 10  # Start at top of screen
        self.width = 16
        self.height = 6
        self.health = 3  # Takes 3 hits to destroy
        self.active = True
        
    def update(self, speed):
        """
        Move obstacle down the screen
        Returns True if obstacle passed bottom (player dodged it)
        """
        self.y += speed
        if self.y > 64:  # Off bottom of screen
            self.active = False
            return True  # Player successfully dodged
        return False
        
    def draw(self, bitmap):
        """Draw obstacle as filled rectangle"""
        if self.health > 0:
            start_x = int(self.x - self.width // 2)
            for row in range(self.height):
                for col in range(self.width):
                    px = start_x + col
                    py = int(self.y) + row
                    # Make sure we're drawing within screen bounds
                    if 0 <= px < 128 and 0 <= py < 64:
                        bitmap[px, py] = 1
                        
    def hit(self):
        """
        Obstacle got hit by bullet
        Returns True if obstacle is destroyed
        """
        self.health -= 1
        if self.health <= 0:
            self.active = False
            return True  # Obstacle destroyed
        return False  # Still has health left


class Bullet:
    """
    Bullet fired by player that moves up the screen
    Destroys obstacles on contact
    """
    
    def __init__(self, x, y):
        """
        Create bullet at player's position
        x, y: starting coordinates
        """
        self.x = x
        self.y = y
        self.active = True
        
    def update(self):
        """Move bullet upward"""
        self.y -= 4  # Move 4 pixels up per frame
        if self.y < 0:  # Off top of screen
            self.active = False
            
    def draw(self, bitmap):
        """Draw bullet as small filled square (3x3 pixels)"""
        for dy in range(-1, 2):
            for dx in range(-1, 2):
                px = int(self.x) + dx
                py = int(self.y) + dy
                # Make sure we're drawing within screen bounds
                if 0 <= px < 128 and 0 <= py < 64:
                    bitmap[px, py] = 1