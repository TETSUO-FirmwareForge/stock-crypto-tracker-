"""
Button handler for Waveshare 2.7" e-paper HAT.

The HAT has 4 physical buttons:
- KEY1 (GPIO 5): Force full refresh
- KEY2 (GPIO 6): Show test pattern
- KEY3 (GPIO 13): Toggle display mode (future use)
- KEY4 (GPIO 19): Manual data refresh
"""

import time
from typing import Callable, Optional

try:
    import RPi.GPIO as GPIO
    HAS_HARDWARE = True
except (ImportError, RuntimeError):
    HAS_HARDWARE = False
    print("Warning: RPi.GPIO not available. Button functions disabled.")


class ButtonHandler:
    """Handles physical button inputs from the e-paper HAT."""

    # Button GPIO pins (BCM numbering)
    KEY1 = 5   # Force full refresh
    KEY2 = 6   # Show test pattern
    KEY3 = 13  # Reserved for future use
    KEY4 = 19  # Manual data refresh

    def __init__(self):
        """Initialize button handler."""
        self.callbacks = {
            self.KEY1: None,
            self.KEY2: None,
            self.KEY3: None,
            self.KEY4: None,
        }
        self.last_press_time = {
            self.KEY1: 0,
            self.KEY2: 0,
            self.KEY3: 0,
            self.KEY4: 0,
        }
        self.debounce_time = 0.3  # 300ms debounce
        self.initialized = False

    def init(self):
        """Initialize GPIO for buttons."""
        if not HAS_HARDWARE:
            print("Running in simulation mode (no button hardware)")
            return

        if self.initialized:
            return

        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        # Setup all button pins as inputs with pull-up resistors
        for pin in [self.KEY1, self.KEY2, self.KEY3, self.KEY4]:
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
            # Add event detection for falling edge (button press)
            GPIO.add_event_detect(
                pin,
                GPIO.FALLING,
                callback=self._button_callback,
                bouncetime=300
            )

        self.initialized = True
        print("Button handler initialized")
        print("  KEY1 (GPIO 5): Force full refresh")
        print("  KEY2 (GPIO 6): Show test pattern")
        print("  KEY3 (GPIO 13): Reserved")
        print("  KEY4 (GPIO 19): Manual data refresh")

    def _button_callback(self, channel):
        """Internal callback for button press events."""
        current_time = time.time()

        # Debounce check
        if current_time - self.last_press_time[channel] < self.debounce_time:
            return

        self.last_press_time[channel] = current_time

        # Call registered callback if available
        callback = self.callbacks.get(channel)
        if callback:
            try:
                callback()
            except Exception as e:
                print(f"Error in button callback for GPIO {channel}: {e}")

    def on_key1(self, callback: Callable):
        """Register callback for KEY1 (Force full refresh)."""
        self.callbacks[self.KEY1] = callback

    def on_key2(self, callback: Callable):
        """Register callback for KEY2 (Show test pattern)."""
        self.callbacks[self.KEY2] = callback

    def on_key3(self, callback: Callable):
        """Register callback for KEY3 (Reserved)."""
        self.callbacks[self.KEY3] = callback

    def on_key4(self, callback: Callable):
        """Register callback for KEY4 (Manual data refresh)."""
        self.callbacks[self.KEY4] = callback

    def cleanup(self):
        """Clean up GPIO resources."""
        if not HAS_HARDWARE or not self.initialized:
            return

        # Remove event detection
        for pin in [self.KEY1, self.KEY2, self.KEY3, self.KEY4]:
            try:
                GPIO.remove_event_detect(pin)
            except:
                pass

        print("Button handler cleaned up")


def main():
    """Test button handler."""
    print("Testing button handler...")
    print("Press buttons to test (Ctrl+C to exit)")

    if not HAS_HARDWARE:
        print("No hardware available for testing")
        return

    handler = ButtonHandler()
    handler.init()

    # Register test callbacks
    handler.on_key1(lambda: print("KEY1 pressed: Force full refresh"))
    handler.on_key2(lambda: print("KEY2 pressed: Show test pattern"))
    handler.on_key3(lambda: print("KEY3 pressed: Reserved"))
    handler.on_key4(lambda: print("KEY4 pressed: Manual data refresh"))

    try:
        # Keep program running to detect button presses
        while True:
            time.sleep(0.1)
    except KeyboardInterrupt:
        print("\nStopping...")
    finally:
        handler.cleanup()


if __name__ == "__main__":
    main()
