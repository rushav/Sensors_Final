# rotary_encoder.py
# Rotary encoder driver with quadrature decoding
# Uses state machine to track rotation direction

import digitalio

# Direction constants
_DIR_CW = 0x10   # Clockwise rotation
_DIR_CCW = 0x20  # Counter-clockwise rotation

# State machine states
_R_START = 0x0
_R_CW_1 = 0x1
_R_CW_2 = 0x2
_R_CW_3 = 0x3
_R_CCW_1 = 0x4
_R_CCW_2 = 0x5
_R_CCW_3 = 0x6

# State transition table for quadrature decoding
_transition_table = [
    [_R_START, _R_CCW_1, _R_CW_1,  _R_START],
    [_R_CW_2,  _R_START, _R_CW_1,  _R_START],
    [_R_CW_2,  _R_CW_3,  _R_CW_1,  _R_START],
    [_R_CW_2,  _R_CW_3,  _R_START, _R_START | _DIR_CW],
    [_R_CCW_2, _R_CCW_1, _R_START, _R_START],
    [_R_CCW_2, _R_CCW_1, _R_CCW_3, _R_START],
    [_R_CCW_2, _R_START, _R_CCW_3, _R_START | _DIR_CCW],
]

_STATE_MASK = 0x07
_DIR_MASK = 0x30

class RotaryEncoder:
    """
    Rotary encoder with quadrature decoding
    Tracks position with wrapping at min/max values
    """
    
    def __init__(self, pin_clk, pin_dt, min_val=0, max_val=25):
        """
        Initialize encoder
        pin_clk: CLK pin (board.D1)
        pin_dt: DT pin (board.D0)
        min_val: minimum position value
        max_val: maximum position value
        """
        # Setup CLK pin
        self._pin_clk = digitalio.DigitalInOut(pin_clk)
        self._pin_clk.direction = digitalio.Direction.INPUT
        self._pin_clk.pull = digitalio.Pull.UP
        
        # Setup DT pin
        self._pin_dt = digitalio.DigitalInOut(pin_dt)
        self._pin_dt.direction = digitalio.Direction.INPUT
        self._pin_dt.pull = digitalio.Pull.UP
        
        # Position tracking
        self._min_val = min_val
        self._max_val = max_val
        self._value = min_val
        self._state = _R_START
        
    def update(self):
        """
        Read encoder and update position
        Call this every loop iteration
        Returns True if position changed
        """
        old_value = self._value
        
        # Read both pins and combine into 2-bit value
        clk_dt_pins = (self._pin_clk.value << 1) | self._pin_dt.value
        
        # Look up next state in transition table
        self._state = _transition_table[self._state & _STATE_MASK][clk_dt_pins]
        direction = self._state & _DIR_MASK
        
        # Update position based on direction
        if direction == _DIR_CW:
            self._value += 1
            if self._value > self._max_val:
                self._value = self._min_val  # Wrap around
        elif direction == _DIR_CCW:
            self._value -= 1
            if self._value < self._min_val:
                self._value = self._max_val  # Wrap around
        
        # Return True if position changed
        return old_value != self._value
    
    def value(self):
        """Get current position"""
        return self._value
    
    def reset(self, val=0):
        """Reset position to specific value"""
        self._value = val