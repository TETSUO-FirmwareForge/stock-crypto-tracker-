"""LCD Renderer for TETSUO Price Display - Modern Redesigned GUI
Complete redesign with centered price, 5 decimals, modern look
"""
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

class LCDRenderer:
    """Modern redesigned LCD renderer for 128x128 display"""

    def __init__(self, config, lcd=None):
        self.config = config
        self.width = 128
        self.height = 128

        # Initialize LCD
        from app.lcd_driver_st7735 import ST7735, InputHandler
        self.lcd = lcd or ST7735(
            dc_pin=config.get("display.gpio.dc_pin", 25),
            rst_pin=config.get("display.gpio.rst_pin", 27),
            cs_pin=config.get("display.gpio.cs_pin", 8),
            bl_pin=config.get("display.gpio.bl_pin", 24)
        )

        self.inputs = InputHandler()
        self.lcd.init()

        # Load fonts
        self.fonts = {}
        try:
            font_path = Path("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf")
            self.fonts['tiny'] = ImageFont.truetype(str(font_path), 10)
            self.fonts['small'] = ImageFont.truetype(str(font_path), 12)
            self.fonts['medium'] = ImageFont.truetype(str(font_path), 16)
            self.fonts['large'] = ImageFont.truetype(str(font_path), 20)
            self.fonts['huge'] = ImageFont.truetype(str(font_path), 24)
        except:
            self.fonts = {k: ImageFont.load_default() for k in ['tiny', 'small', 'medium', 'large', 'huge']}

        self.current_view = 0
        self.last_input_time = time.time()

    def render(self, data, stale_seconds: int = 0):
        """Render the new modern GUI"""
        img = self._render_modern_view(data, stale_seconds)

        # Handle input
        self._handle_input()

        # Display
        self.lcd.display_image(img)

    def _render_modern_view(self, data, stale_seconds: int):
        """Modern redesigned GUI with centered price and 5 decimals"""
        # Create base with gradient
        img = Image.new('RGB', (128, 128), (0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Gradient background (dark blue to black)
        for y in range(128):
            color_val = int(30 * (1 - y / 128))
            draw.line([(0, y), (128, y)], fill=(0, 0, color_val))

        # Helper for text with shadow
        def draw_shadow_text(xy, text, font, fill=(255, 255, 255)):
            x, y = xy
            draw.text((x+1, y+1), text, font=font, fill=(0, 0, 0))
            draw.text((x, y), text, font=font, fill=fill)

        # Top bar
        draw.rectangle([0, 0, 128, 22], fill=(10, 10, 40))
        draw.rectangle([0, 21, 128, 22], fill=(0, 200, 255))

        # TETSUO title centered
        title = "TETSUO"
        bbox = draw.textbbox((0, 0), title, font=self.fonts['medium'])
        title_w = bbox[2] - bbox[0]
        title_x = (128 - title_w) // 2
        draw_shadow_text((title_x, 4), title, self.fonts['medium'], fill=(0, 255, 255))

        # Status dot
        status_color = (0, 255, 0) if stale_seconds == 0 else (255, 150, 0)
        draw.ellipse([110, 6, 120, 16], fill=status_color)

        if data:
            # PRICE - CENTERED with 5 decimals
            price = data.price_usd
            price_text = f"${price:.5f}"

            bbox = draw.textbbox((0, 0), price_text, font=self.fonts['large'])
            price_w = bbox[2] - bbox[0]
            price_x = (128 - price_w) // 2

            # Price box with glow
            pad = 8
            box_x1, box_y1 = price_x - pad, 30
            box_x2, box_y2 = price_x + price_w + pad, 58

            draw.rectangle([box_x1-1, box_y1-1, box_x2+1, box_y2+1],
                          fill=(0, 100, 200), outline=(0, 150, 255))
            draw.rectangle([box_x1, box_y1, box_x2, box_y2],
                          fill=(5, 5, 25), outline=(0, 200, 255), width=2)

            # Price text - gold
            draw_shadow_text((price_x, 35), price_text,
                           self.fonts['large'], fill=(255, 220, 0))

            # 24h Change - CENTERED
            if data.change_24h_pct is not None:
                change = data.change_24h_pct

                if change > 0:
                    arrow = "▲"
                    bg_start = (0, 100, 0)
                    bg_end = (0, 150, 0)
                    txt_color = (100, 255, 100)
                    change_txt = f"+{change:.1f}%"
                else:
                    arrow = "▼"
                    bg_start = (100, 0, 0)
                    bg_end = (150, 0, 0)
                    txt_color = (255, 100, 100)
                    change_txt = f"{change:.1f}%"

                full = f"{arrow} {change_txt}"
                bbox = draw.textbbox((0, 0), full, font=self.fonts['medium'])
                change_w = bbox[2] - bbox[0]
                change_x = (128 - change_w) // 2

                # Gradient box
                cy1, cy2 = 65, 88
                for y in range(cy1, cy2):
                    ratio = (y - cy1) / (cy2 - cy1)
                    r = int(bg_start[0] + (bg_end[0] - bg_start[0]) * ratio)
                    g = int(bg_start[1] + (bg_end[1] - bg_start[1]) * ratio)
                    b = int(bg_start[2] + (bg_end[2] - bg_start[2]) * ratio)
                    draw.line([(change_x - 6, y), (change_x + change_w + 6, y)], fill=(r, g, b))

                draw.rectangle([change_x - 6, cy1, change_x + change_w + 6, cy2],
                              outline=(200, 200, 200))

                draw_shadow_text((change_x, 70), full, self.fonts['medium'], fill=txt_color)

            # Bottom bar
            draw.rectangle([0, 95, 128, 96], fill=(0, 150, 200))

            # Time - right aligned
            time_txt = datetime.now().strftime("%H:%M:%S")
            bbox = draw.textbbox((0, 0), time_txt, font=self.fonts['tiny'])
            time_w = bbox[2] - bbox[0]
            draw.text((124 - time_w, 100), time_txt,
                     font=self.fonts['tiny'], fill=(150, 200, 255))

            # Volume (if available)
            if hasattr(data, 'volume_24h') and data.volume_24h:
                vol = f"Vol: ${data.volume_24h/1000:.0f}K"
                draw.text((4, 100), vol, font=self.fonts['tiny'], fill=(150, 200, 255))

        else:
            # No data
            msg = "Loading..."
            bbox = draw.textbbox((0, 0), msg, font=self.fonts['small'])
            msg_w = bbox[2] - bbox[0]
            draw_shadow_text(((128 - msg_w) // 2, 55), msg,
                           self.fonts['small'], fill=(255, 255, 0))

        return img

    def _handle_input(self):
        """Handle button inputs"""
        try:
            states = self.inputs.read_inputs()
        except:
            pass

    def show_splash(self):
        """Show startup splash"""
        img = Image.new('RGB', (128, 128), (0, 0, 50))
        draw = ImageDraw.Draw(img)

        for i in range(3):
            img = Image.new('RGB', (128, 128), (0, 0, 50))
            draw = ImageDraw.Draw(img)

            title = "TETSUO"
            bbox = draw.textbbox((0, 0), title, font=self.fonts['large'])
            title_w = bbox[2] - bbox[0]

            bright = int(255 * (i + 1) / 3)
            draw.text(((128 - title_w) // 2, 40), title,
                     font=self.fonts['large'], fill=(0, bright, 255))

            sub = "Price Tracker"
            bbox = draw.textbbox((0, 0), sub, font=self.fonts['small'])
            sub_w = bbox[2] - bbox[0]
            draw.text(((128 - sub_w) // 2, 75), sub,
                     font=self.fonts['small'], fill=(150, 150, 255))

            self.lcd.display_image(img)
            time.sleep(0.3)

    def show_error(self, message: str):
        """Display error"""
        img = Image.new('RGB', (128, 128), (50, 0, 0))
        draw = ImageDraw.Draw(img)

        draw.rectangle([0, 0, 128, 25], fill=(150, 0, 0))
        draw.text((35, 5), "ERROR", font=self.fonts['medium'], fill=(255, 255, 255))

        words = message.split()
        lines = []
        current = ""
        for word in words:
            test = f"{current} {word}".strip()
            bbox = draw.textbbox((0, 0), test, font=self.fonts['small'])
            if bbox[2] < 120:
                current = test
            else:
                if current:
                    lines.append(current)
                current = word
        if current:
            lines.append(current)

        y = 35
        for line in lines[:4]:
            draw.text((5, y), line, font=self.fonts['small'], fill=(255, 200, 200))
            y += 15

        self.lcd.display_image(img)

    def shutdown(self):
        """Clean shutdown"""
        img = Image.new('RGB', (128, 128), (0, 0, 50))
        draw = ImageDraw.Draw(img)

        msg = "Goodbye!"
        bbox = draw.textbbox((0, 0), msg, font=self.fonts['large'])
        msg_w = bbox[2] - bbox[0]
        draw.text(((128 - msg_w) // 2, 55), msg,
                 font=self.fonts['large'], fill=(0, 255, 255))

        self.lcd.display_image(img)
        time.sleep(1)
        self.lcd.cleanup()
