"""
ST7735S LCD Display Driver for 1.44" 128x128 TFT Display
Compatible with Raspberry Pi via SPI interface
"""

import time
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple

try:
    import RPi.GPIO as GPIO
    import spidev
    HAS_HARDWARE = True
except (ImportError, RuntimeError):
    HAS_HARDWARE = False
    print("Warning: RPi.GPIO or spidev not available. Running in simulation mode.")


class ST7735:
    """Driver for 1.44" ST7735S LCD Display (128x128 RGB)."""

    # Display dimensions
    WIDTH = 128
    HEIGHT = 128

    # ST7735S Commands
    NOP = 0x00
    SWRESET = 0x01
    RDDID = 0x04
    RDDST = 0x09

    SLPIN = 0x10
    SLPOUT = 0x11
    PTLON = 0x12
    NORON = 0x13

    INVOFF = 0x20
    INVON = 0x21
    DISPOFF = 0x28
    DISPON = 0x29
    CASET = 0x2A
    RASET = 0x2B
    RAMWR = 0x2C
    RAMRD = 0x2E

    PTLAR = 0x30
    COLMOD = 0x3A
    MADCTL = 0x36

    FRMCTR1 = 0xB1
    FRMCTR2 = 0xB2
    FRMCTR3 = 0xB3
    INVCTR = 0xB4
    DISSET5 = 0xB6

    PWCTR1 = 0xC0
    PWCTR2 = 0xC1
    PWCTR3 = 0xC2
    PWCTR4 = 0xC3
    PWCTR5 = 0xC4
    VMCTR1 = 0xC5

    RDID1 = 0xDA
    RDID2 = 0xDB
    RDID3 = 0xDC
    RDID4 = 0xDD

    PWCTR6 = 0xFC

    GMCTRP1 = 0xE0
    GMCTPN1 = 0xE1

    # Color definitions (RGB565)
    BLACK = 0x0000
    WHITE = 0xFFFF
    RED = 0xF800
    GREEN = 0x07E0
    BLUE = 0x001F
    CYAN = 0x07FF
    MAGENTA = 0xF81F
    YELLOW = 0xFFE0
    ORANGE = 0xFC00

    def __init__(self, dc_pin=25, rst_pin=17, cs_pin=8, bl_pin=24,
                 spi_bus=0, spi_device=0, spi_speed=8000000):
        """
        Initialize ST7735S display driver.

        Args:
            dc_pin: Data/Command pin (BCM numbering)
            rst_pin: Reset pin
            cs_pin: Chip Select pin
            bl_pin: Backlight pin
            spi_bus: SPI bus number
            spi_device: SPI device number
            spi_speed: SPI communication speed in Hz
        """
        self.dc_pin = dc_pin
        self.rst_pin = rst_pin
        self.cs_pin = cs_pin
        self.bl_pin = bl_pin
        self.spi = None
        self.width = self.WIDTH
        self.height = self.HEIGHT

        if not HAS_HARDWARE:
            print("Running in simulation mode (no hardware)")

    def init(self):
        """Initialize the LCD display."""
        if not HAS_HARDWARE:
            return

        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)
        GPIO.setup(self.dc_pin, GPIO.OUT)
        GPIO.setup(self.rst_pin, GPIO.OUT)
        GPIO.setup(self.cs_pin, GPIO.OUT)
        GPIO.setup(self.bl_pin, GPIO.OUT)

        # Turn on backlight
        GPIO.output(self.bl_pin, GPIO.HIGH)

        # Initialize SPI
        self.spi = spidev.SpiDev()
        self.spi.open(0, 0)
        self.spi.max_speed_hz = 8000000
        self.spi.mode = 0b00

        # Hardware reset
        self.reset()

        # Initialize display
        self._init_display()

    def reset(self):
        """Hardware reset the display."""
        if not HAS_HARDWARE:
            return

        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.1)
        GPIO.output(self.rst_pin, GPIO.LOW)
        time.sleep(0.1)
        GPIO.output(self.rst_pin, GPIO.HIGH)
        time.sleep(0.1)

    def _init_display(self):
        """Initialize display with ST7735S commands."""
        if not HAS_HARDWARE:
            return

        # Software reset
        self.write_command(self.SWRESET)
        time.sleep(0.15)

        # Out of sleep mode
        self.write_command(self.SLPOUT)
        time.sleep(0.5)

        # Frame rate control
        self.write_command(self.FRMCTR1)
        self.write_data(0x01)
        self.write_data(0x2C)
        self.write_data(0x2D)

        self.write_command(self.FRMCTR2)
        self.write_data(0x01)
        self.write_data(0x2C)
        self.write_data(0x2D)

        self.write_command(self.FRMCTR3)
        self.write_data(0x01)
        self.write_data(0x2C)
        self.write_data(0x2D)
        self.write_data(0x01)
        self.write_data(0x2C)
        self.write_data(0x2D)

        # Display inversion control
        self.write_command(self.INVCTR)
        self.write_data(0x07)

        # Power control
        self.write_command(self.PWCTR1)
        self.write_data(0xA2)
        self.write_data(0x02)
        self.write_data(0x84)

        self.write_command(self.PWCTR2)
        self.write_data(0xC5)

        self.write_command(self.PWCTR3)
        self.write_data(0x0A)
        self.write_data(0x00)

        self.write_command(self.PWCTR4)
        self.write_data(0x8A)
        self.write_data(0x2A)

        self.write_command(self.PWCTR5)
        self.write_data(0x8A)
        self.write_data(0xEE)

        # VCOM control
        self.write_command(self.VMCTR1)
        self.write_data(0x0E)

        # Display inversion off
        self.write_command(self.INVOFF)

        # Memory data access control (rotation)
        self.write_command(self.MADCTL)
        self.write_data(0xC8)  # RGB order

        # Color mode: 16-bit color
        self.write_command(self.COLMOD)
        self.write_data(0x05)

        # Column address set
        self.write_command(self.CASET)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x7F)  # 127

        # Row address set
        self.write_command(self.RASET)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x00)
        self.write_data(0x7F)  # 127

        # Gamma correction
        self.write_command(self.GMCTRP1)
        self.write_data(0x02)
        self.write_data(0x1C)
        self.write_data(0x07)
        self.write_data(0x12)
        self.write_data(0x37)
        self.write_data(0x32)
        self.write_data(0x29)
        self.write_data(0x2D)
        self.write_data(0x29)
        self.write_data(0x25)
        self.write_data(0x2B)
        self.write_data(0x39)
        self.write_data(0x00)
        self.write_data(0x01)
        self.write_data(0x03)
        self.write_data(0x10)

        self.write_command(self.GMCTRN1)
        self.write_data(0x03)
        self.write_data(0x1D)
        self.write_data(0x07)
        self.write_data(0x06)
        self.write_data(0x2E)
        self.write_data(0x2C)
        self.write_data(0x29)
        self.write_data(0x2D)
        self.write_data(0x2E)
        self.write_data(0x2E)
        self.write_data(0x37)
        self.write_data(0x3F)
        self.write_data(.00)
        self.write_data(0x00)
        self.write_data(0x02)
        self.write_data(0x10)

        # Normal display on
        self.write_command(self.NORON)
        time.sleep(0.01)

        # Display on
        self.write_command(self.DISPON)
        time.sleep(0.1)

        # Clear display
        self.clear()

    def write_command(self, cmd):
        """Write command to display."""
        if not HAS_HARDWARE:
            return

        GPIO.output(self.cs_pin, GPIO.LOW)
        GPIO.output(self.dc_pin, GPIO.LOW)
        self.spi.writebytes([cmd])
        GPIO.output(self.cs_pin, GPIO.HIGH)

    def write_data(self, data):
        """Write data byte to display."""
        if not HAS_HARDWARE:
            return

        GPIO.output(self.cs_pin, GPIO.LOW)
        GPIO.output(self.dc_pin, GPIO.HIGH)
        if isinstance(data, int):
            self.spi.writebytes([data])
        else:
            self.spi.writebytes(data)
        GPIO.output(self.cs_pin, GPIO.HIGH)

    def write_data_bulk(self, data):
        """Write multiple data bytes to display."""
        if not HAS_HARDWARE:
            return

        GPIO.output(self.cs_pin, GPIO.LOW)
        GPIO.output(self.dc_pin, GPIO.HIGH)
        self.spi.writebytes(data)
        GPIO.output(self.cs_pin, GPIO.HIGH)

    def set_window(self, x0, y0, x1, y1):
        """Set drawing window."""
        if not HAS_HARDWARE:
            return

        # Column address set
        self.write_command(self.CASET)
        self.write_data(0x00)
        self.write_data(x0)
        self.write_data(0x00)
        self.write_data(x1)

        # Row address set
        self.write_command(self.RASET)
        self.write_data(0x00)
        self.write_data(y0)
        self.write_data(0x00)
        self.write_data(y1)

        # Memory write
        self.write_command(self.RAMWR)

    def display_image(self, image):
        """
        Display PIL image on LCD.
        Image should be 128x128 RGB.
        """
        if not HAS_HARDWARE:
            return

        # Convert image to RGB if needed
        if image.mode != 'RGB':
            image = image.convert('RGB')

        # Resize if needed
        if image.size != (self.width, self.height):
            image = image.resize((self.width, self.height), Image.LANCZOS)

        # Convert to RGB565 format
        pixels = np.array(image)
        rgb565 = self.rgb888_to_rgb565(pixels)

        # Set window to full screen
        self.set_window(0, 0, self.width-1, self.height-1)

        # Write image data
        self.write_data_bulk(rgb565.tobytes())

    def rgb888_to_rgb565(self, rgb888):
        """Convert RGB888 numpy array to RGB565."""
        r = (rgb888[..., 0] >> 3) & 0x1F
        g = (rgb888[..., 1] >> 2) & 0x3F
        b = (rgb888[..., 2] >> 3) & 0x1F

        rgb565 = (r << 11) | (g << 5) | b

        # Convert to bytes (big-endian)
        rgb565_bytes = np.zeros((rgb888.shape[0], rgb888.shape[1], 2), dtype=np.uint8)
        rgb565_bytes[..., 0] = (rgb565 >> 8) & 0xFF
        rgb565_bytes[..., 1] = rgb565 & 0xFF

        return rgb565_bytes.flatten()

    def clear(self, color=BLACK):
        """Clear display with specified color."""
        if not HAS_HARDWARE:
            return

        self.fill_rect(0, 0, self.width, self.height, color)

    def fill_rect(self, x, y, w, h, color):
        """Fill rectangle with color."""
        if not HAS_HARDWARE:
            return

        # Set window
        self.set_window(x, y, x+w-1, y+h-1)

        # Prepare color bytes
        color_high = (color >> 8) & 0xFF
        color_low = color & 0xFF

        # Fill with color
        data = [color_high, color_low] * (w * h)
        self.write_data_bulk(data)

    def set_backlight(self, state):
        """Turn backlight on/off."""
        if not HAS_HARDWARE:
            return

        GPIO.output(self.bl_pin, GPIO.HIGH if state else GPIO.LOW)

    def cleanup(self):
        """Clean up GPIO and SPI resources."""
        if not HAS_HARDWARE:
            return

        self.clear()
        self.set_backlight(False)

        if self.spi:
            self.spi.close()

        GPIO.cleanup()


# Input handling for joystick and buttons
class InputHandler:
    """Handle joystick and button inputs."""

    def __init__(self, up_pin=6, down_pin=19, left_pin=5, right_pin=26,
                 center_pin=13, k1_pin=21, k2_pin=20, k3_pin=16):
        """
        Initialize input handler.

        Args:
            up_pin: Joystick up
            down_pin: Joystick down
            left_pin: Joystick left
            right_pin: Joystick right
            center_pin: Joystick center press
            k1_pin: Button K1
            k2_pin: Button K2
            k3_pin: Button K3
        """
        self.pins = {
            'up': up_pin,
            'down': down_pin,
            'left': left_pin,
            'right': right_pin,
            'center': center_pin,
            'k1': k1_pin,
            'k2': k2_pin,
            'k3': k3_pin
        }

        if HAS_HARDWARE:
            self._setup_gpio()

    def _setup_gpio(self):
        """Setup GPIO pins for input."""
        GPIO.setmode(GPIO.BCM)
        GPIO.setwarnings(False)

        for pin in self.pins.values():
            GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    def read_inputs(self):
        """Read all input states."""
        if not HAS_HARDWARE:
            return {}

        states = {}
        for name, pin in self.pins.items():
            # Buttons are active low (pressed = 0)
            states[name] = GPIO.input(pin) == 0

        return states

    def wait_for_input(self, timeout=None):
        """Wait for any input with optional timeout."""
        if not HAS_HARDWARE:
            return None

        start_time = time.time()

        while True:
            states = self.read_inputs()
            for name, pressed in states.items():
                if pressed:
                    return name

            if timeout and (time.time() - start_time) > timeout:
                return None

            time.sleep(0.05)


def main():
    """Test the LCD display driver."""
    print("Testing ST7735S 1.44\" LCD Display...")

    if not HAS_HARDWARE:
        print("No hardware available for testing")
        return

    lcd = ST7735()
    inputs = InputHandler()

    try:
        print("Initializing display...")
        lcd.init()

        print("Display initialized. Showing test pattern...")

        # Create test image
        img = Image.new('RGB', (128, 128), color='black')
        draw = ImageDraw.Draw(img)

        # Draw test pattern
        draw.rectangle([0, 0, 127, 127], outline='white', width=2)
        draw.text((30, 50), "TETSUO", fill='white')
        draw.text((25, 70), "LCD TEST", fill='green')

        lcd.display_image(img)

        print("Test pattern displayed")
        print("Press any button or move joystick to test inputs...")

        while True:
            input_name = inputs.wait_for_input(timeout=0.1)
            if input_name:
                print(f"Input detected: {input_name}")

                # Show input on display
                img = Image.new('RGB', (128, 128), color='black')
                draw = ImageDraw.Draw(img)
                draw.text((20, 60), f"Input: {input_name}", fill='yellow')
                lcd.display_image(img)

                if input_name == 'k3':  # Exit on K3
                    break

    except KeyboardInterrupt:
        print("\nTest interrupted")

    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()

    finally:
        print("Cleaning up...")
        lcd.cleanup()
        GPIO.cleanup()


if __name__ == "__main__":
    main()