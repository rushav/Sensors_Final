# code.py
# MAIN GAME FILE - ESP32-C3 Space Shooter
# This is the entry point for my game
# Hardware: ESP32-C3, OLED display, MPU-6050, rotary encoder, buttons

import displayio
import terminalio
from adafruit_display_text import label
import time
import random

# Import my custom modules
from hardware import (display, accelerometer, buzzer, encoder, encoder_btn,
                     button_a, button_c, button_d, set_neopixel, hsv_to_rgb)
from sounds import (play_tone, sound_selection, sound_blaster, sound_dodge,
                   sound_game_over, sound_victory, play_windows_sound)
from accelerometer_filter import AccelerometerTapDetector
from game_objects import Obstacle, Bullet
from graphics import (draw_grid, draw_hud, draw_targeting_reticle, draw_player,
                     check_collision)
from animations import show_windows_splash, show_cockpit_hud_animation
from menu import (show_menu, load_highscores, save_highscores, is_highscore,
                 get_initials)

# Initialize and calibrate accelerometer tap detector
tap_detector = AccelerometerTapDetector(accelerometer)
tap_detector.calibrate(num_samples=30)

# Show startup animations
set_neopixel(255, 255, 255)  # White LED during startup
show_windows_splash(display, buzzer, play_windows_sound)
show_cockpit_hud_animation(display, buzzer, play_tone)

# MAIN GAME LOOP
# This runs forever, returning to menu after each game
while True:
    # Show menu and get difficulty selection
    difficulty = show_menu(display, encoder, encoder_btn, sound_selection, buzzer)
    
    # Configure game based on difficulty
    if difficulty == "Easy":
        starting_speed = 2
        starting_level = 1
        score_multiplier = 1.0  # 1x points
    elif difficulty == "Medium":
        starting_speed = 4
        starting_level = 2
        score_multiplier = 1.5  # 1.5x points
    elif difficulty == "Hard":
        starting_speed = 6
        starting_level = 3
        score_multiplier = 2.0  # 2x points
    else:
        # Fallback in case something weird happens
        starting_speed = 2
        starting_level = 1
        score_multiplier = 1.0
    
    print(f"Starting game - Difficulty: {difficulty}, Speed: {starting_speed}, Level: {starting_level}, Multiplier: {score_multiplier}x")
    
    # GAME STATE VARIABLES
    # Player position
    player_lanes = [40, 64, 88]  # X-coordinates of 3 lanes
    player_lane_index = 1  # Start in middle lane
    
    # Scoring and progression
    score = 0
    speed = starting_speed
    speed_level = starting_level
    
    # Game flags
    frame_count = 0
    game_over = False
    inverted = False  # Screen inversion during level-up
    waiting_for_tap = False  # Waiting for tap to continue
    tap_start_time = 0
    TAP_TIMEOUT = 5.0  # 5 seconds to tap or game over
    
    # Victory mode (reached level 10)
    victory_mode = False
    victory_start_time = 0
    VICTORY_DURATION = 3.0
    
    # Set LED to white for normal gameplay
    set_neopixel(255, 255, 255)
    
    # Game entity lists
    obstacles = []
    bullets = []
    
    # Obstacle spawning
    spawn_timer = 0
    spawn_delay = 30  # Frames between obstacles
    
    # Button state tracking (for edge detection)
    button_a_last = False
    button_c_last = False
    button_d_last = False
    
    # GAME LOOP
    # Runs until player dies or quits
    while not game_over:
        frame_count += 1
        
        # Check for quit (all 3 buttons pressed)
        if button_a.value and button_c.value and button_d.value:
            print("Returning to menu...")
            break
        
        # VICTORY MODE HANDLING
        # Flash rainbow LED when level 10 reached
        if victory_mode:
            elapsed = time.monotonic() - victory_start_time
            if elapsed >= VICTORY_DURATION:
                # Victory display over, return to normal
                victory_mode = False
                set_neopixel(255, 255, 255)
                print("Victory mode ended")
            else:
                # Rainbow LED effect
                hue = (frame_count * 10) % 360
                r, g, b = hsv_to_rgb(hue, 1.0, 1.0)
                set_neopixel(r, g, b)
        
        # LEVEL UP TAP MECHANIC
        # Screen inverts, player must tap to continue
        if waiting_for_tap:
            # Flash LED white/black
            if frame_count % 3 == 0:
                set_neopixel(255, 255, 255)
            else:
                set_neopixel(0, 0, 0)
            
            # Check timeout
            elapsed = time.monotonic() - tap_start_time
            time_left = TAP_TIMEOUT - elapsed
            
            if time_left <= 0:
                # Ran out of time!
                game_over = True
                print("TIME OUT!")
            
            # Check for tap
            if tap_detector.detect_tap():
                # Tap detected! Continue game
                inverted = False
                waiting_for_tap = False
                set_neopixel(255, 255, 255)
                print(f"Level {speed_level} complete!")
        
        # NORMAL GAMEPLAY
        if not waiting_for_tap:
            # PLAYER CONTROLS
            # Detect button press edges (only trigger once per press)
            button_a_pressed = button_a.value and not button_a_last
            button_c_pressed = button_c.value and not button_c_last
            button_d_pressed = button_d.value and not button_d_last
            
            # Update button states for next frame
            button_a_last = button_a.value
            button_c_last = button_c.value
            button_d_last = button_d.value
            
            # Button A - Move left
            if button_a_pressed and player_lane_index > 0:
                player_lane_index -= 1
                if not victory_mode:
                    set_neopixel(0, 0, 255)  # Blue flash
                sound_dodge(buzzer)
                time.sleep(0.05)
                if not victory_mode:
                    set_neopixel(255, 255, 255)
            
            # Button C - Move right
            if button_c_pressed and player_lane_index < 2:
                player_lane_index += 1
                if not victory_mode:
                    set_neopixel(0, 0, 255)  # Blue flash
                sound_dodge(buzzer)
                time.sleep(0.05)
                if not victory_mode:
                    set_neopixel(255, 255, 255)
            
            # Button D - Shoot
            if button_d_pressed:
                bullets.append(Bullet(player_lanes[player_lane_index], 56))
                if not victory_mode:
                    set_neopixel(0, 255, 0)  # Green flash
                sound_blaster(buzzer)
                time.sleep(0.05)
                if not victory_mode:
                    set_neopixel(255, 255, 255)
            
            # OBSTACLE SPAWNING
            spawn_timer += 1
            if spawn_timer >= spawn_delay:
                spawn_timer = 0
                lane = random.randint(0, 2)
                obstacles.append(Obstacle(lane, player_lanes))
            
            # UPDATE BULLETS
            for bullet in bullets[:]:
                bullet.update()
                if not bullet.active:
                    bullets.remove(bullet)
            
            # UPDATE OBSTACLES
            for obs in obstacles[:]:
                passed = obs.update(speed)
                if passed:
                    # Player dodged obstacle - award points
                    points = int(10 * score_multiplier)
                    score += points
                if not obs.active:
                    obstacles.remove(obs)
            
            # BULLET-OBSTACLE COLLISION
            for bullet in bullets[:]:
                for obs in obstacles[:]:
                    if obs.active and bullet.active:
                        # Simple distance check
                        if abs(bullet.x - obs.x) < 8 and abs(bullet.y - obs.y) < 8:
                            bullet.active = False
                            if obs.hit():
                                # Obstacle destroyed - award bonus points
                                points = int(20 * score_multiplier)
                                score += points
            
            # PLAYER-OBSTACLE COLLISION
            if check_collision(player_lane_index, player_lanes, obstacles):
                game_over = True
                set_neopixel(255, 0, 0)  # Red LED
                sound_game_over(buzzer)
            
            # LEVEL PROGRESSION
            # Every 100 points = next level
            new_speed_level = starting_level + (score // 100)
            if new_speed_level > speed_level:
                speed_level = new_speed_level
                
                # Check for victory at level 5
                if speed_level >= 10 and not victory_mode:
                    victory_mode = True
                    victory_start_time = time.monotonic()
                    sound_victory(buzzer)
                    print("YOU WIN! Level 10 reached!")
                
                # Trigger level-up sequence
                inverted = True
                waiting_for_tap = True
                tap_start_time = time.monotonic()
                tap_detector.reset_for_level()
            
            # DIFFICULTY SCALING
            # Make game harder as you progress
            if spawn_delay > 15:
                if score > 0 and score % 100 == 0:
                    spawn_delay -= 1  # Spawn obstacles faster
                    speed += 0.2  # Move obstacles faster
        
        # RENDER FRAME
        # Draw everything to screen
        game_screen = displayio.Group()
        bitmap = displayio.Bitmap(128, 64, 2)
        palette = displayio.Palette(2)
        
        # Set colors (inverted during level-up)
        if inverted:
            palette[0], palette[1] = 0xFFFFFF, 0x000000
        else:
            palette[0], palette[1] = 0x000000, 0xFFFFFF
        
        # Draw background elements
        draw_grid(bitmap, frame_count * 4)  # Animated grid
        draw_targeting_reticle(bitmap)
        draw_hud(bitmap)
        
        # Draw game entities
        for obs in obstacles:
            obs.draw(bitmap)
        
        for bullet in bullets:
            bullet.draw(bitmap)
        
        draw_player(bitmap, player_lane_index, player_lanes)
        
        # Add bitmap to display group
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
        game_screen.append(tile_grid)
        
        # Choose text color based on inversion
        text_color = 0x000000 if inverted else 0xFFFFFF
        
        # Display victory message
        if victory_mode:
            win_label = label.Label(terminalio.FONT, text="YOU WIN!", color=text_color)
            win_label.x, win_label.y = 42, 4
            game_screen.append(win_label)
        
        # Display score
        score_label = label.Label(terminalio.FONT, text=f"SC:{score}", color=text_color)
        score_label.x, score_label.y = 4, 8
        game_screen.append(score_label)
        
        # Display level
        speed_label = label.Label(terminalio.FONT, text=f"LVL:{speed_level}", color=text_color)
        speed_label.x, speed_label.y = 92, 8
        game_screen.append(speed_label)
        
        # Display tap prompt during level-up
        if waiting_for_tap:
            elapsed = time.monotonic() - tap_start_time
            time_left = max(0, TAP_TIMEOUT - elapsed)
            
            tap_label = label.Label(terminalio.FONT, text="TAP!", color=text_color)
            tap_label.x, tap_label.y = 50, 28
            game_screen.append(tap_label)
            
            # Countdown timer
            timer_label = label.Label(terminalio.FONT, text=f"{int(time_left) + 1}", color=text_color)
            timer_label.x, timer_label.y = 60, 40
            game_screen.append(timer_label)
        
        # Show frame on display
        display.root_group = game_screen
        time.sleep(0.02)  # ~50 FPS
    
    # GAME OVER
    # Check if we exited due to quit (return to menu immediately)
    if not game_over:
        continue
    
    # HIGH SCORE HANDLING
    highscores = load_highscores()
    
    if is_highscore(score, highscores):
        # New high score! Get initials
        print("NEW HIGH SCORE!")
        initials = get_initials(display, encoder, encoder_btn, sound_selection, buzzer)
        
        # Add to list and re-sort
        highscores.append((initials, score))
        highscores.sort(key=lambda x: x[1], reverse=True)
        highscores = highscores[:5]  # Keep top 5
        save_highscores(highscores)
    
    # GAME OVER SCREEN
    # Flash game over message 3 times
    for _ in range(3):
        game_over_screen = displayio.Group()
        bitmap = displayio.Bitmap(128, 64, 2)
        palette = displayio.Palette(2)
        palette[0], palette[1] = 0x000000, 0xFFFFFF
        
        tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
        game_over_screen.append(tile_grid)
        
        # "GAME OVER" text
        game_over_label = label.Label(terminalio.FONT, text="GAME OVER", color=0xFFFFFF)
        game_over_label.x, game_over_label.y = 34, 24
        game_over_screen.append(game_over_label)
        
        # Final score
        score_label = label.Label(terminalio.FONT, text=f"Score: {score}", color=0xFFFFFF)
        score_label.x, score_label.y = 38, 40
        game_over_screen.append(score_label)
        
        display.root_group = game_over_screen
        set_neopixel(255, 0, 0)  # Red LED
        time.sleep(1)
    
    # Loop back to menu