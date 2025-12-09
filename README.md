# ESP32-C3 Space Shooter Game

A vertical scrolling space shooter game for the ESP32-C3 microcontroller with OLED display, accelerometer-based tap controls, and rotary encoder navigation.

## Project Overview

This game features a player-controlled spaceship that must dodge or destroy incoming obstacles. The game includes multiple difficulty levels, progressive speed increases, and a high score system with persistent storage. Players navigate menus using a rotary encoder and control the ship using physical buttons.

## Hardware Requirements

- ESP32-C3 microcontroller
- 128x64 OLED display (I2C, address 0x3C)
- MPU-6050 accelerometer (I2C, address 0x68)
- Rotary encoder with push button
- 3 momentary push buttons (for gameplay)
- PWM-capable buzzer
- Single RGB NeoPixel LED

## Hardware Connections

### Display and Sensors
- OLED Display: I2C bus (SCL, SDA pins)
- MPU-6050 Accelerometer: I2C bus (address 0x68)

### Input Controls
- Rotary Encoder: D0 (DT), D1 (CLK), D2 (Button)
- Left Button (move left): D8
- Middle Button (shoot): D10
- Right Button (move right): D7

### Output Devices
- Buzzer: D6 (PWM output)
- NeoPixel LED: D3

## File Structure

### Core Files

**code.py**
Main game loop and entry point. Handles game state management, player input processing, collision detection, and scoring. This file coordinates all game systems and is the first file executed when the device powers on.

**hardware.py**
Centralizes all hardware initialization. Sets up I2C communication, display, accelerometer, buzzer, NeoPixel LED, buttons, and rotary encoder. Provides utility functions for LED control and color conversion.

**rotary_encoder.py**
Implements a state machine-based rotary encoder driver. Uses quadrature decoding to reliably detect rotation direction and track position with automatic wrapping at boundaries.

### Game Systems

**game_objects.py**
Defines the Obstacle and Bullet classes. Obstacles move down the screen and can be dodged or destroyed. Bullets move upward and damage obstacles on contact. Each class manages its own position, rendering, and collision detection.

**graphics.py**
Contains all drawing functions for game visuals. Includes the 3D perspective grid background, HUD elements, targeting reticle, player ship rendering, and collision checking logic.

**accelerometer_filter.py**
Implements tap detection with noise filtering using an Exponential Moving Average (EMA) algorithm. Handles accelerometer calibration at startup and provides reliable tap gesture recognition for the level-up mechanic.

### User Interface

**animations.py**
Contains startup animations displayed before the main menu. Includes the Windows logo splash screen and an animated cockpit HUD with a rotating radar display.

**menu.py**
Manages the main menu system, difficulty selection, high score display, and initials entry. Handles persistent storage of high scores to the filesystem and provides rotary encoder-based navigation.

**sounds.py**
Centralizes all audio feedback. Includes sound effects for menu navigation, weapon fire, player movement, game over, and victory. Uses PWM frequency modulation to generate tones.

## Game Mechanics

### Controls

**Menu Navigation**
- Rotate encoder: Navigate through menu options
- Press encoder button: Select highlighted option

**Gameplay**
- Left button: Move spaceship to the left lane
- Middle button: Fire weapon
- Right button: Move spaceship to the right lane
- Tap device: Continue to next level (during level-up sequence)

### Difficulty Levels

The game offers three difficulty settings that affect starting conditions and score multipliers:

**Easy**
- Starting Speed: 2
- Starting Level: 1
- Score Multiplier: 1.0x

**Medium**
- Starting Speed: 4
- Starting Level: 2
- Score Multiplier: 1.5x

**Hard**
- Starting Speed: 6
- Starting Level: 3
- Score Multiplier: 2.0x

### Scoring System

- Dodging an obstacle (letting it pass): 10 points x multiplier
- Destroying an obstacle with weapon: 20 points x multiplier
- Level progression: Every 100 points advances to the next level
- Victory condition: Reach 300 points

### Level Progression

Every 100 points triggers a level-up sequence:
1. Screen inverts colors (black and white swap)
2. LED flashes white and black alternately
3. Player must tap the device within 5 seconds to continue
4. Game resumes with increased difficulty

### Victory Condition

Upon reaching 300 points:
- "YOU WIN!" message displays on screen
- NeoPixel LED cycles through rainbow colors for 3 seconds
- Victory fanfare plays
- Gameplay continues normally after the celebration

### Visual Feedback

- White LED: Normal gameplay
- Blue LED flash: Lane change
- Green LED flash: Weapon fired
- Red LED: Game over
- Rainbow LED: Victory mode

## High Score System

The game maintains a persistent list of the top 5 scores. When a player achieves a qualifying score, they can enter their three-letter initials using the rotary encoder. High scores are saved to the device's filesystem and persist across power cycles.

## Installation

1. Ensure CircuitPython is installed on your ESP32-C3
2. Copy all Python files to the root directory of the device:
   - code.py
   - hardware.py
   - rotary_encoder.py
   - game_objects.py
   - graphics.py
   - accelerometer_filter.py
   - animations.py
   - menu.py
   - sounds.py

3. Connect all hardware components according to the pin configuration
4. Reset or power cycle the device

The game will automatically start, display animations, and present the main menu.

## Accelerometer Calibration

The accelerometer calibrates automatically during startup. Keep the device still on a flat surface during the "Calibrating..." message. This establishes a baseline for tap detection. The system uses an Exponential Moving Average filter with a 0.3 alpha value to reduce noise and prevent false tap detections.

## Troubleshooting

**Display shows nothing**
- Verify I2C connections (SCL, SDA)
- Check display address (should be 0x3C)
- Ensure displayio.release_displays() runs before display initialization

**Rotary encoder not responding**
- Confirm D0 and D1 pin connections
- Verify pull-up resistors are enabled
- Check that encoder button (D2) has proper pull-up

**Buttons not working**
- Verify button pins: D8 (left), D10 (middle), D7 (right)
- Confirm buttons are connected to ground when pressed
- Check pull-down configuration

**Tap detection too sensitive or not working**
- Recalibrate by restarting device on a flat surface
- Adjust TAP_THRESHOLD in accelerometer_filter.py (default: 2.5)
- Modify FILTER_ALPHA for more/less smoothing (default: 0.3)

**High scores not saving**
- Check filesystem permissions
- Verify device has write access to root directory
- Ensure proper storage.remount() calls in menu.py

## Customization

**Difficulty Adjustment**
Edit starting_speed, starting_level, and score_multiplier values in code.py (around line 42)

**Victory Condition**
Change the score threshold in code.py (around line 214): `if score >= 300`

**Tap Sensitivity**
Modify TAP_THRESHOLD in accelerometer_filter.py (line 20)

**Sound Effects**
Adjust frequencies and durations in sounds.py

**Visual Elements**
Modify drawing functions in graphics.py

**Filter Responsiveness**
Change FILTER_ALPHA in accelerometer_filter.py (line 26): lower values = more smoothing

## Technical Implementation

The game uses a state machine architecture with a main loop running at approximately 50 FPS. The rotary encoder employs quadrature decoding for reliable position tracking. Tap detection uses an Exponential Moving Average filter to reduce accelerometer noise. All graphics are rendered to a 1-bit bitmap before display to optimize performance. The menu system uses edge detection for button presses to prevent repeat triggers.

## Credits

Game developed for ESP32-C3 using CircuitPython. Rotary encoder driver based on state machine principles for quadrature decoding. Sound design inspired by classic arcade games.