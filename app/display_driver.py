"""
E-Paper display driver for Waveshare 2.7" V2 HAT (264x176).

Based on Waveshare's official epd2in7_V2.py driver.
The V2 uses DIFFERENT commands than V1!
"""

import time
from typing import Optional

try:
    import RPi.GPIO as GPIO
    import spidev
    HAS_HARDWARE = True
except (ImportError, RuntimeError):
    HAS_HARDWARE = False
    print("Warning: RPi.GPIO or spidev not available. Hardware functions disabled.")


class EPD2in7:
    """Driver for Waveshare 2.7" V2 e-Paper display (264x176)."""

    # Display dimensions
    WIDTH = 176
    HEIGHT = 264

    def __init__(self, dc_pin=25, rst_pin=17, busy_pin=24, cs_pin=8):
        """
        Initialize display driver for V2.

        Args:
            dc_pin: Data/Command pin (BCM numbering)
            rst_pin: Reset pin
            busy_pin: Busy status pin
            cs_pin: SPI chip select (not used, handled by SPI hardware)
        """
        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.busy_pin = busy_pin
        self.cs_pin = cs_pin
        self.spi = None
        self.width = self.WIDTH
        self.height = self.HEIGHT

        if not HAS_HARDWARE:
            print("Running in simulation mode (no hardware)")

    def init(self, mode='full'):
        """
        Initialize the V2 display.

        Args:
            mode: 'full' or 'partial' refresh mode (V2 uses same init for both)
        """
        if not HAS_HARDWARE:
            return

        # Initialize GPIO (CS pin is handled by SPI hardware)
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.busy_pin, GPIO.IN)

        # Initialize SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)  # Bus 0, Device 0
        self.spi.max_speed_hz = 4000000
        self.spi.mode = 0b00

        # Hardware reset
        self.reset()
        self.wait_until_idle()

        # V2 initialization sequence
        self.send_command(0x12)  # SWRESET
        self.wait_until_idle()

        # Set Ram-Y address start/end position
        self.send_command(0x45)
        self.send_data(0x00)
        self.send_data(0x00)
        self.send_data(0x07)  # 0x0107 = 264
        self.send_data(0x01)

        # Set RAM y address count to 0
        self.send_command(0x4F)
        self.send_data(0x00)
        self.send_data(0x00)

        # Data entry mode
        self.send_command(0x11)
        self.send_data(0x03)

    def reset(self):
        """Hardware reset."""
        if not HAS_HARDWARE:
            return

        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.2)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.002)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.2)

    def send_command(self, command):
        """Send command to display."""
        if not HAS_HARDWARE:
            return

        GPIO.output(self.dc_pin, GPIO.LOW)
        self.spi.writebytes([command])

    def send_data(self, data):
        """Send data to display."""
        if not HAS_HARDWARE:
            return

        GPIO.output(self.dc_pin, GPIO.HIGH)
        self.spi.writebytes([data])

    def wait_until_idle(self):
        """Wait until display is idle with timeout."""
        if not HAS_HARDWARE:
            return

        timeout = 0
        while GPIO.input(self.busy_pin) == 1 and timeout < 100:
            time.sleep(0.1)
            timeout += 1

        if timeout >= 100:
            print("WARNING: Display BUSY timeout")

        time.sleep(0.2)

    def display_frame(self, frame_buffer):
        """
        Display a frame buffer using V2 commands.

        Args:
            frame_buffer: Bytes representing image data (width*height/8 bytes)
        """
        if not HAS_HARDWARE:
            return

        # V2 uses command 0x24 (not 0x10/0x13 like V1!)
        self.send_command(0x24)
        for byte in frame_buffer:
            self.send_data(byte)

    def refresh(self, mode='full'):
        """
        Refresh the display using V2 TurnOnDisplay sequence.

        Args:
            mode: 'full' or 'partial'
        """
        if not HAS_HARDWARE:
            return

        # V2 TurnOnDisplay sequence
        self.send_command(0x22)  # Display Update Control
        if mode == 'partial':
            self.send_data(0xFF)  # Partial update
        elif mode == 'fast':
            self.send_data(0xC7)  # Fast update
        else:
            self.send_data(0xF7)  # Full update

        self.send_command(0x20)  # Activate Display Update Sequence
        self.wait_until_idle()

    def sleep(self):
        """Put display into deep sleep mode."""
        if not HAS_HARDWARE:
            return

        self.send_command(0x10)  # Deep sleep
        self.send_data(0x01)
        time.sleep(0.1)

    def clear(self):
        """Clear display to white (0xFF for V2)."""
        if not HAS_HARDWARE:
            return

        frame_buffer = [0xFF] * (self.width * self.height // 8)
        self.display_frame(frame_buffer)
        self.refresh('full')

    def cleanup(self):
        """Clean up GPIO and SPI resources."""
        if not HAS_HARDWARE:
            return

        self.sleep()

        if self.spi:
            self.spi.close()

        GPIO.cleanup()


def main():
    """Test the V2 display driver."""
    print("Testing EPD 2.7\" V2 display driver...")

    if not HAS_HARDWARE:
        print("No hardware available for testing")
        return

    epd = EPD2in7()

    try:
        print("Initializing display...")
        epd.init('full')

        print("Clearing display to white...")
        epd.clear()

        print("Display test complete - should be WHITE")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("Cleaning up...")
        epd.cleanup()


if __name__ == "__main__":
    main()
