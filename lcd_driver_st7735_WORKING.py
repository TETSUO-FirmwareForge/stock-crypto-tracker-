"""LCD Driver for SEENGREAT 1.44" ST7735S Display
Based on official SEENGREAT code: https://github.com/seengreat/1.44inch-LCD-Display
"""
import time
import numpy as np
from PIL import Image

try:
    import spidev
    from gpiozero import DigitalOutputDevice, PWMOutputDevice, Button
    HAS_HARDWARE = True
except ImportError:
    HAS_HARDWARE = False
    print("Warning: Running without hardware support")

# GPIO pins (BCM numbering)
RST_PIN = 27
DC_PIN = 25
BL_PIN = 24

# Button pins
KEY_UP_PIN = 6
KEY_DOWN_PIN = 19
KEY_LEFT_PIN = 5
KEY_RIGHT_PIN = 26
KEY_PRESS_PIN = 13
KEY1_PIN = 21
KEY2_PIN = 20
KEY3_PIN = 16

class ST7735:
    """Driver for ST7735S 128x128 LCD Display"""

    def __init__(self, rst_pin=RST_PIN, dc_pin=DC_PIN, bl_pin=BL_PIN,
                 spi_bus=0, spi_device=0, spi_speed=8000000):
        self.width = 128
        self.height = 128

        if not HAS_HARDWARE:
            return

        # Initialize GPIO
        self.dc = DigitalOutputDevice(dc_pin, active_high=True, initial_value=False)
        self.rst = DigitalOutputDevice(rst_pin, active_high=True, initial_value=False)
        self.bl = PWMOutputDevice(bl_pin, frequency=1000)
        self.bl.value = 0.9  # 90% brightness

        # Initialize SPI
        self.spi = spidev.SpiDev()
        self.spi.open(spi_bus, spi_device)
        self.spi.max_speed_hz = spi_speed
        self.spi.mode = 0b00

    def write_cmd(self, cmd):
        """Write command to display"""
        if not HAS_HARDWARE:
            return
        self.dc.off()
        self.spi.writebytes([cmd])

    def write_data(self, value):
        """Write data to display"""
        if not HAS_HARDWARE:
            return
        self.dc.on()
        self.spi.writebytes([value])

    def reset(self):
        """Reset the display"""
        if not HAS_HARDWARE:
            return
        self.rst.on()
        time.sleep(0.01)
        self.rst.off()
        time.sleep(0.01)
        self.rst.on()
        time.sleep(0.01)

    def init_display(self):
        """Initialize display with ST7735S configuration"""
        if not HAS_HARDWARE:
            return

        self.reset()

        self.write_cmd(0x01)  # Software reset
        time.sleep(0.02)

        self.write_cmd(0x11)  # Sleep out
        time.sleep(0.05)

        # Frame Rate Control
        self.write_cmd(0xB1)
        self.write_data(0x02)
        self.write_data(0x35)
        self.write_data(0x36)

        self.write_cmd(0xB2)
        self.write_data(0x02)
        self.write_data(0x35)
        self.write_data(0x36)

        self.write_cmd(0xB3)
        self.write_data(0x02)
        self.write_data(0x35)
        self.write_data(0x36)
        self.write_data(0x02)
        self.write_data(0x35)
        self.write_data(0x36)

        # Display Inversion Control
        self.write_cmd(0xB4)
        self.write_data(0x03)

        # Power Control
        self.write_cmd(0xC0)
        self.write_data(0xA2)
        self.write_data(0x02)
        self.write_data(0x84)

        self.write_cmd(0xC1)
        self.write_data(0xC5)

        self.write_cmd(0xC2)
        self.write_data(0x0D)
        self.write_data(0x00)

        self.write_cmd(0xC3)
        self.write_data(0x8D)
        self.write_data(0x2A)

        self.write_cmd(0xC4)
        self.write_data(0x8D)
        self.write_data(0xEE)

        self.write_cmd(0xC5)  # VCOM
        self.write_data(0x0A)

        self.write_cmd(0x36)  # Memory Access Control
        self.write_data(0x68)  # Horizontal orientation

        # Gamma Control
        self.write_cmd(0xE0)
        self.write_data(0x12)
        self.write_data(0x1C)
        self.write_data(0x10)
        self.write_data(0x18)
        self.write_data(0x33)
        self.write_data(0x2C)
        self.write_data(0x25)
        self.write_data(0x28)
        self.write_data(0x28)
        self.write_data(0x27)
        self.write_data(0x2F)
        self.write_data(0x3C)
        self.write_data(0x00)
        self.write_data(0x03)
        self.write_data(0x03)
        self.write_data(0x10)

        self.write_cmd(0xE1)
        self.write_data(0x12)
        self.write_data(0x1C)
        self.write_data(0x10)
        self.write_data(0x18)
        self.write_data(0x2D)
        self.write_data(0x28)
        self.write_data(0x23)
        self.write_data(0x28)
        self.write_data(0x28)
        self.write_data(0x26)
        self.write_data(0x2F)
        self.write_data(0x3B)
        self.write_data(0x00)
        self.write_data(0x03)
        self.write_data(0x03)
        self.write_data(0x10)

        self.write_cmd(0xF0)
        self.write_data(0x01)

        self.write_cmd(0xF6)
        self.write_data(0x00)

        self.write_cmd(0x3A)  # Pixel Format
        self.write_data(0x05)  # 16-bit color

        self.write_cmd(0x29)  # Display on
        time.sleep(0.05)

    def set_window(self, x0, y0, x1, y1):
        """Set display window"""
        if not HAS_HARDWARE:
            return

        # Offset for 0x68 orientation
        x0 += 1
        x1 += 1
        y0 += 2
        y1 += 2

        self.write_cmd(0x2A)  # Column address
        self.write_data(x0 >> 8)
        self.write_data(x0 & 0xFF)
        self.write_data(x1 >> 8)
        self.write_data(x1 & 0xFF)

        self.write_cmd(0x2B)  # Row address
        self.write_data(y0 >> 8)
        self.write_data(y0 & 0xFF)
        self.write_data(y1 >> 8)
        self.write_data(y1 & 0xFF)

        self.write_cmd(0x2C)  # Memory write

    def display_image(self, image):
        """Display PIL Image on screen"""
        if not HAS_HARDWARE:
            return

        # Convert PIL image to RGB565 format using numpy
        img_array = np.asarray(image)
        pixel = np.zeros((self.width, self.height, 2), dtype=np.uint8)

        # Convert RGB888 to RGB565
        pixel[..., [0]] = np.add(
            np.bitwise_and(img_array[..., [0]], 0xF8),
            np.right_shift(img_array[..., [1]], 5)
        )
        pixel[..., [1]] = np.add(
            np.bitwise_and(np.left_shift(img_array[..., [1]], 3), 0xE0),
            np.right_shift(img_array[..., [2]], 3)
        )

        pixel_data = pixel.flatten().tolist()

        self.set_window(0, 0, 127, 127)
        self.dc.on()

        # Send in 4KB chunks to avoid buffer overflow
        for i in range(0, len(pixel_data), 4096):
            self.spi.writebytes(pixel_data[i:i+4096])

    def clear(self, color=(0, 0, 0)):
        """Clear display to specified color"""
        if not HAS_HARDWARE:
            return
        img = Image.new('RGB', (self.width, self.height), color)
        self.display_image(img)

    def set_backlight(self, state):
        """Set backlight on/off or brightness (0.0 to 1.0)"""
        if not HAS_HARDWARE:
            return
        if isinstance(state, bool):
            self.bl.value = 0.9 if state else 0.0
        else:
            self.bl.value = max(0.0, min(1.0, state))

    def cleanup(self):
        """Cleanup GPIO resources"""
        if not HAS_HARDWARE:
            return
        try:
            self.bl.close()
            self.dc.close()
            self.rst.close()
            self.spi.close()
        except:
            pass


class InputHandler:
    """Handle joystick and button inputs"""

    def __init__(self):
        if not HAS_HARDWARE:
            return

        self.buttons = {
            'up': Button(KEY_UP_PIN),
            'down': Button(KEY_DOWN_PIN),
            'left': Button(KEY_LEFT_PIN),
            'right': Button(KEY_RIGHT_PIN),
            'press': Button(KEY_PRESS_PIN),
            'key1': Button(KEY1_PIN),
            'key2': Button(KEY2_PIN),
            'key3': Button(KEY3_PIN),
        }

    def on_button(self, button_name, callback):
        """Register callback for button press"""
        if not HAS_HARDWARE:
            return
        if button_name in self.buttons:
            self.buttons[button_name].when_pressed = callback

    def cleanup(self):
        """Cleanup button resources"""
        if not HAS_HARDWARE:
            return
        for btn in self.buttons.values():
            btn.close()
