# menu.py
# Menu system, high scores, and initials entry
# Handles all UI navigation and score persistence

import displayio
import terminalio
from adafruit_display_text import label
import time
import storage
from graphics import draw_folder

# High score file location
HIGHSCORE_FILE = "/highscores.txt"

def load_highscores():
    """
    Load high scores from file
    Returns list of (name, score) tuples
    """
    try:
        with open(HIGHSCORE_FILE, "r") as f:
            lines = f.readlines()
            scores = []
            for line in lines:
                parts = line.strip().split(",")
                if len(parts) == 2:
                    scores.append((parts[0], int(parts[1])))
            
            # Pad with empty entries if less than 5 scores
            while len(scores) < 5:
                scores.append(("---", 0))
            
            return scores[:5]  # Return top 5
    except:
        # No file yet, return empty list
        return [("---", 0)] * 5

def save_highscores(scores):
    """
    Save high scores to file
    scores: list of (name, score) tuples
    """
    try:
        # Need to remount filesystem as writable
        storage.remount("/", False)
        with open(HIGHSCORE_FILE, "w") as f:
            for name, score in scores:
                f.write(f"{name},{score}\n")
        storage.remount("/", True)
    except:
        print("Error saving high scores")

def is_highscore(score, highscores):
    """Check if score is good enough for high score list"""
    return score > highscores[4][1]  # Better than 5th place

def show_menu(display, encoder, encoder_btn, sound_selection_func, buzzer):
    """
    Display main menu with difficulty selection
    Returns selected difficulty as string ("Easy", "Medium", "Hard")
    """
    menu_options = ["Easy", "Medium", "Hard", "Scores"]
    encoder.reset(0)
    
    # Build menu display (only once for performance)
    desktop = displayio.Group()
    bitmap = displayio.Bitmap(128, 64, 2)
    palette = displayio.Palette(2)
    palette[0], palette[1] = 0x000000, 0xFFFFFF
    
    # Draw folder icons
    for i in range(4):
        draw_folder(bitmap, 2, i * 12 + 2)
    
    # Draw taskbar at bottom
    for y in range(56, 64):
        for x in range(128):
            bitmap[x, y] = 1
    
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    desktop.append(tile_grid)
    
    # Create text labels for each option
    folder_labels = []
    arrow_labels = []
    
    for i, option in enumerate(menu_options):
        # Option text
        folder_label = label.Label(terminalio.FONT, text=option, color=0xFFFFFF)
        folder_label.x = 10
        folder_label.y = 4 + i * 12
        desktop.append(folder_label)
        folder_labels.append(folder_label)
        
        # Selection arrow (hidden initially)
        arrow_label = label.Label(terminalio.FONT, text=" ", color=0xFFFFFF)
        arrow_label.x = 115
        arrow_label.y = 4 + i * 12
        desktop.append(arrow_label)
        arrow_labels.append(arrow_label)
    
    # Show arrow on first option
    arrow_labels[0].text = ">"
    display.root_group = desktop
    
    # Menu navigation variables
    selected = 0
    btn_last = encoder_btn.value
    button_down_time = 0
    button_pressed = False
    PRESS_DURATION = 0.1  # Must hold button for 100ms to register
    
    print("Menu ready - rotate to select, press to confirm")
    
    # Menu loop
    while True:
        # Check if encoder rotated
        changed = encoder.update()
        
        if changed:
            new_selected = encoder.value()
            print(f"Selected: {menu_options[new_selected]}")
            
            # Move arrow
            arrow_labels[selected].text = " "
            arrow_labels[new_selected].text = ">"
            selected = new_selected
        
        # Check encoder button with proper debouncing
        btn_current = encoder_btn.value
        current_time = time.monotonic()
        
        if not btn_current and btn_last:
            # Button just pressed
            button_down_time = current_time
            button_pressed = True
        
        if btn_current and not btn_last:
            # Button released - check if held long enough
            if button_pressed and (current_time - button_down_time >= PRESS_DURATION):
                print(f"Confirmed: {menu_options[selected]}")
                sound_selection_func(buzzer)
                time.sleep(0.2)
                
                if menu_options[selected] == "Scores":
                    # Show high scores, then return to menu
                    show_highscores_screen(display, encoder_btn, sound_selection_func, buzzer)
                    display.root_group = desktop  # Restore menu display
                    print("Back to menu")
                else:
                    # Return selected difficulty
                    return menu_options[selected]
            button_pressed = False
        
        btn_last = btn_current
        time.sleep(0.001)

def show_highscores_screen(display, encoder_btn, sound_selection_func, buzzer):
    """Display high scores screen"""
    highscores = load_highscores()
    
    # Build high scores display
    scores_screen = displayio.Group()
    bitmap = displayio.Bitmap(128, 64, 2)
    palette = displayio.Palette(2)
    palette[0], palette[1] = 0x000000, 0xFFFFFF
    
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    scores_screen.append(tile_grid)
    
    # Title
    title = label.Label(terminalio.FONT, text="HIGH SCORES", color=0xFFFFFF)
    title.x, title.y = 22, 4
    scores_screen.append(title)
    
    # Show all 5 high scores
    for i, (name, score) in enumerate(highscores):
        score_text = f"{i+1}. {name} {score}"
        score_label = label.Label(terminalio.FONT, text=score_text, color=0xFFFFFF)
        score_label.x, score_label.y = 10, 16 + i * 9
        scores_screen.append(score_label)
    
    # Exit instruction
    back_label = label.Label(terminalio.FONT, text="Press to exit", color=0xFFFFFF)
    back_label.x, back_label.y = 18, 56
    scores_screen.append(back_label)
    
    display.root_group = scores_screen
    
    # Wait for previous button press to clear
    time.sleep(0.3)
    while not encoder_btn.value:
        time.sleep(0.01)
    
    # Wait for button press to exit
    btn_last = encoder_btn.value
    button_down_time = 0
    button_pressed = False
    PRESS_DURATION = 0.1
    
    print("High scores screen - waiting for button press to exit")
    
    while True:
        btn_current = encoder_btn.value
        current_time = time.monotonic()
        
        if not btn_current and btn_last:
            button_down_time = current_time
            button_pressed = True
        
        if btn_current and not btn_last:
            if button_pressed and (current_time - button_down_time >= PRESS_DURATION):
                print("Valid button press - exiting high scores")
                sound_selection_func(buzzer)
                time.sleep(0.2)
                return
            button_pressed = False
        
        btn_last = btn_current
        time.sleep(0.001)

def get_initials(display, encoder, encoder_btn, sound_selection_func, buzzer):
    """
    Let player enter 3-letter initials using rotary encoder
    Returns 3-character string
    """
    alphabet = "ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    initials = ["A", "A", "A"]
    position = 0  # Which letter we're editing
    
    # Configure encoder for alphabet (0-25 for A-Z)
    encoder.reset(0)
    encoder._min_val = 0
    encoder._max_val = 25
    
    btn_last = encoder_btn.value
    button_down_time = 0
    button_pressed = False
    PRESS_DURATION = 0.1
    
    # Build initials entry display
    keyboard_screen = displayio.Group()
    bitmap = displayio.Bitmap(128, 64, 2)
    palette = displayio.Palette(2)
    palette[0], palette[1] = 0x000000, 0xFFFFFF
    
    tile_grid = displayio.TileGrid(bitmap, pixel_shader=palette)
    keyboard_screen.append(tile_grid)
    
    # Title
    title = label.Label(terminalio.FONT, text="ENTER INITIALS", color=0xFFFFFF)
    title.x, title.y = 16, 8
    keyboard_screen.append(title)
    
    # Display current initials
    initials_label = label.Label(terminalio.FONT, text=f"{initials[0]} {initials[1]} {initials[2]}", color=0xFFFFFF)
    initials_label.x, initials_label.y = 46, 28
    keyboard_screen.append(initials_label)
    
    # Underline cursors for each position
    underline_labels = []
    for i in range(3):
        underline = label.Label(terminalio.FONT, text=" ", color=0xFFFFFF)
        underline.x = 46 + i * 12
        underline.y = 34
        keyboard_screen.append(underline)
        underline_labels.append(underline)
    
    # Show cursor under first position
    underline_labels[0].text = "_"
    display.root_group = keyboard_screen
    
    # Entry loop
    while position < 3:
        # Check if encoder rotated
        changed = encoder.update()
        
        if changed:
            letter_index = encoder.value()
            initials[position] = alphabet[letter_index]
            initials_label.text = f"{initials[0]} {initials[1]} {initials[2]}"
        
        # Check button press to confirm letter
        btn_current = encoder_btn.value
        current_time = time.monotonic()
        
        if not btn_current and btn_last:
            button_down_time = current_time
            button_pressed = True
        
        if btn_current and not btn_last:
            if button_pressed and (current_time - button_down_time >= PRESS_DURATION):
                sound_selection_func(buzzer)
                underline_labels[position].text = " "  # Remove cursor
                position += 1
                
                if position < 3:
                    # Move to next letter
                    underline_labels[position].text = "_"
                    encoder.reset(0)  # Start at 'A' again
                
                time.sleep(0.2)
            button_pressed = False
        
        btn_last = btn_current
        time.sleep(0.001)
    
    # Restore encoder to menu range (0-3)
    encoder._min_val = 0
    encoder._max_val = 3
    encoder.reset(0)
    
    return "".join(initials)