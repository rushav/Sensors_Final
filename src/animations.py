# animations.py
# Startup animations and splash screens
# Includes Windows logo and cockpit HUD animation

import displayio
import terminalio
from adafruit_display_text import label
import time
import math
from graphics import draw_spaceship, draw_stars

def show_windows_splash(display, buzzer, play_windows_sound_func):
    """
    Display Windows logo splash screen with sound
    This plays when game first starts
    """
    splash = displayio.Group()
    bitmap = displayio.Bitmap(128, 64, 2)
    palette = displayio.Palette(2)
    palette[0] = 0x000000  # Black background
    palette[1] = 0xFFFFFF  # White graphics
    
    # Draw Windows 4-square logo
    center_x, center_y = 64, 24
    square_size, gap = 14, 6
    
    for y in range(square_size):
        for x in range(square_size):
            # Top-left square
            bitmap[center_x - square_size - gap//2 + x, center_y - square_size - gap//2 + y] = 1
            # Top-right square
            bitmap[center_x + gap//2 + x, center_y - square_size - gap//2 + y] = 1
            # Bottom-left square
            bitmap[center_x - square_size - gap//2 + x, center_y + gap//2 + y] = 1
            # Bottom-right square
            bitmap[center_x + gap//2 + x, center_y + gap//2 + y] = 1
    
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    splash.append(tile_grid)
    
    # Add "Windows" text
    text_label = label.Label(terminalio.FONT, text="Windows", color=0xFFFFFF)
    text_label.x, text_label.y = 42, 52
    splash.append(text_label)
    
    display.root_group = splash
    play_windows_sound_func(buzzer)
    time.sleep(0.5)

def show_cockpit_hud_animation(display, buzzer, play_tone_func):
    """
    Show cockpit HUD startup sequence with rotating radar
    Plays after Windows splash before main menu
    """
    num_frames = 60
    
    for frame in range(num_frames):
        hud = displayio.Group()
        bitmap = displayio.Bitmap(128, 64, 2)
        palette = displayio.Palette(2)
        palette[0], palette[1] = 0x000000, 0xFFFFFF
        
        # Draw corner targeting brackets
        bracket_size = 8
        # Top-left corner
        for i in range(bracket_size):
            bitmap[2+i, 2] = 1
            bitmap[2, 2+i] = 1
        # Top-right corner
        for i in range(bracket_size):
            bitmap[126-i, 2] = 1
            bitmap[126, 2+i] = 1
        # Bottom-left corner
        for i in range(bracket_size):
            bitmap[2+i, 62] = 1
            bitmap[2, 62-i] = 1
        # Bottom-right corner
        for i in range(bracket_size):
            bitmap[126-i, 62] = 1
            bitmap[126, 62-i] = 1
        
        # Draw radar circle in center
        radar_x, radar_y = 64, 28
        radar_radius = 18
        
        # Draw circle outline using polar coordinates
        for angle in range(0, 360, 10):
            rad = math.radians(angle)
            x = int(radar_x + radar_radius * math.cos(rad))
            y = int(radar_y + radar_radius * math.sin(rad))
            if 0 <= x < 128 and 0 <= y < 64:
                bitmap[x, y] = 1
        
        # Draw center dot
        for dx in range(-1, 2):
            for dy in range(-1, 2):
                if abs(dx) + abs(dy) <= 1:  # Plus shape
                    bitmap[radar_x + dx, radar_y + dy] = 1
        
        # Draw rotating scan line
        scan_angle = (frame / num_frames) * 360
        rad = math.radians(scan_angle)
        for r in range(radar_radius):
            x = int(radar_x + r * math.cos(rad))
            y = int(radar_y + r * math.sin(rad))
            if 0 <= x < 128 and 0 <= y < 64:
                bitmap[x, y] = 1
        
        # Add radar blips that appear near scan line
        blip_angles = [30, 120, 200, 310]  # Fixed blip positions
        blip_distances = [12, 15, 10, 14]
        
        for ba, bd in zip(blip_angles, blip_distances):
            # Calculate angle difference
            diff = abs(scan_angle - ba)
            if diff > 180:
                diff = 360 - diff
            
            # Only show blip if scan line is nearby
            if diff < 40:
                rad = math.radians(ba)
                bx = int(radar_x + bd * math.cos(rad))
                by = int(radar_y + bd * math.sin(rad))
                if 0 <= bx < 128 and 0 <= by < 64:
                    # Draw blip as small cross
                    bitmap[bx, by] = 1
                    if bx-1 >= 0: bitmap[bx-1, by] = 1
                    if bx+1 < 128: bitmap[bx+1, by] = 1
        
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
        hud.append(tile_grid)
        
        # Add status text that changes over time
        if frame < 15:
            # First phase: initializing
            text = label.Label(terminalio.FONT, text="SYSTEMS", color=0xFFFFFF)
            text.x, text.y = 70, 20
            hud.append(text)
            text2 = label.Label(terminalio.FONT, text="INITIALIZING", color=0xFFFFFF)
            text2.x, text2.y = 70, 30
            hud.append(text2)
        elif frame < 30:
            # Second phase: online
            text = label.Label(terminalio.FONT, text="SYSTEMS", color=0xFFFFFF)
            text.x, text.y = 70, 20
            hud.append(text)
            text2 = label.Label(terminalio.FONT, text="ONLINE", color=0xFFFFFF)
            text2.x, text2.y = 70, 30
            hud.append(text2)
        else:
            # Third phase: scanning with animated dots
            dots = "." * ((frame // 5) % 4)
            text = label.Label(terminalio.FONT, text=f"SCANNING{dots}", color=0xFFFFFF)
            text.x, text.y = 70, 20
            hud.append(text)
            
            # Final phase: target acquired
            if frame > 45:
                text2 = label.Label(terminalio.FONT, text="TARGET", color=0xFFFFFF)
                text2.x, text2.y = 70, 30
                hud.append(text2)
                text3 = label.Label(terminalio.FONT, text="ACQUIRED", color=0xFFFFFF)
                text3.x, text3.y = 70, 40
                hud.append(text3)
        
        display.root_group = hud
        
        # Play radar beeps periodically
        if frame % 10 == 0:
            play_tone_func(buzzer, 800 + (frame % 3) * 200, 0.02)
        
        time.sleep(0.05)