# sounds.py
# All sound effects for my game
# Uses PWM buzzer to play different tones and melodies

import time
import math

def play_tone(buzzer, frequency, duration):
    """
    Play a single tone on the buzzer
    buzzer: PWM buzzer object
    frequency: tone frequency in Hz
    duration: how long to play in seconds
    """
    if frequency > 0:
        buzzer.frequency = frequency
        buzzer.duty_cycle = 16384  # 25% volume to avoid being too loud
    time.sleep(duration)
    buzzer.duty_cycle = 0  # Turn off sound

def sound_selection(buzzer):
    """Quick beep when selecting menu items"""
    play_tone(buzzer, 800, 0.05)
    play_tone(buzzer, 1000, 0.05)

def sound_blaster(buzzer):
    """Laser sound effect when shooting"""
    for freq in range(800, 200, -50):
        buzzer.frequency = freq
        buzzer.duty_cycle = 16384
        time.sleep(0.01)
    buzzer.duty_cycle = 0

def sound_dodge(buzzer):
    """Quick swoosh when changing lanes"""
    play_tone(buzzer, 600, 0.05)
    time.sleep(0.01)
    play_tone(buzzer, 800, 0.05)

def sound_game_over(buzzer):
    """Sad descending tones with vibrato when you lose"""
    notes = [466, 440, 415, 392]
    for note in notes:
        # Add vibrato effect by varying frequency slightly
        for i in range(8):
            offset = int(10 * math.sin(i * 0.5))
            buzzer.frequency = note + offset
            buzzer.duty_cycle = 16384
            time.sleep(0.06)
    buzzer.duty_cycle = 0

def sound_victory(buzzer):
    """Happy ascending fanfare when reaching level 10"""
    notes = [(523, 0.15), (659, 0.15), (784, 0.15), (1047, 0.4)]
    for freq, duration in notes:
        play_tone(buzzer, freq, duration)

def play_windows_sound(buzzer):
    """Classic Windows startup sound"""
    play_tone(buzzer, 622, 0.35)
    time.sleep(0.05)
    play_tone(buzzer, 415, 0.25)
    time.sleep(0.05)
    play_tone(buzzer, 932, 0.25)
    time.sleep(0.05)
    play_tone(buzzer, 831, 0.20)
    time.sleep(0.05)
    play_tone(buzzer, 311, 0.30)
    time.sleep(0.05)
    play_tone(buzzer, 622, 0.35)
    time.sleep(0.05)
    play_tone(buzzer, 466, 0.50)