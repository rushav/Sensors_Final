# accelerometer_filter.py
# Handles accelerometer calibration and tap detection with filtering
# Uses Exponential Moving Average (EMA) filter to reduce noise

import time

class AccelerometerTapDetector:
    """
    Detects taps on the accelerometer with noise filtering
    Uses EMA filter to smooth out readings and reduce false positives
    """
    
    def __init__(self, accelerometer):
        self.accelerometer = accelerometer
        
        # Calibration values (set during calibration)
        self.baseline_x = 0
        self.baseline_y = 0
        self.baseline_z = 0
        
        # Filter variables
        self.filtered_x = 0
        self.prev_x = 0
        
        # Tap detection settings
        self.TAP_THRESHOLD = 2.5  # How hard you need to tap
        self.tap_cooldown = 0  # Prevents detecting one tap multiple times
        
        # EMA filter parameter (lower = more smoothing, less responsive)
        self.FILTER_ALPHA = 0.3
    
    def calibrate(self, num_samples=30):
        """
        Calibrate by taking average of readings while device is still
        Call this at startup before the game begins
        """
        print("Calibrating accelerometer...")
        samples = []
        
        # Collect samples
        for i in range(num_samples):
            x, y, z = self.accelerometer.acceleration
            samples.append((x, y, z))
            time.sleep(0.05)
        
        # Calculate baseline (average of all samples)
        self.baseline_x = sum(s[0] for s in samples) / len(samples)
        self.baseline_y = sum(s[1] for s in samples) / len(samples)
        self.baseline_z = sum(s[2] for s in samples) / len(samples)
        
        # Initialize filter with baseline
        self.filtered_x = self.baseline_x
        self.prev_x = self.baseline_x
        
        print(f"Calibration complete: baseline=({self.baseline_x:.2f}, {self.baseline_y:.2f}, {self.baseline_z:.2f})")
    
    def detect_tap(self):
        """
        Check if a tap occurred
        Returns True if tap detected, False otherwise
        Call this every game loop iteration
        """
        # Read raw accelerometer value
        x, y, z = self.accelerometer.acceleration
        
        # Apply Exponential Moving Average filter to smooth noise
        # Formula: filtered = alpha * new_value + (1-alpha) * old_filtered
        self.filtered_x = self.FILTER_ALPHA * x + (1 - self.FILTER_ALPHA) * self.filtered_x
        
        # Calculate how different current reading is from baseline
        dev_x = abs(self.filtered_x - self.baseline_x)
        
        # Calculate how much the reading changed since last check
        delta_x = abs(self.filtered_x - self.prev_x)
        self.prev_x = self.filtered_x
        
        # Check if tap occurred (must exceed threshold AND show sudden change)
        tap_detected = False
        if self.tap_cooldown == 0:
            if dev_x > self.TAP_THRESHOLD and delta_x > 1.5:
                tap_detected = True
                self.tap_cooldown = 10  # Prevent re-detecting same tap
        
        # Decrease cooldown counter
        if self.tap_cooldown > 0:
            self.tap_cooldown -= 1
        
        return tap_detected
    
    def reset_for_level(self):
        """Reset filter state when starting a new level"""
        self.filtered_x = self.baseline_x
        self.prev_x = self.baseline_x
        self.tap_cooldown = 0