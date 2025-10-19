"""
LCD Renderer for TETSUO price display on 1.44" ST7735S LCD (128x128)
Optimized layout for small screen with color support
"""

from PIL import Image, ImageDraw, ImageFont, ImageOps
from typing import Optional, Tuple
from datetime import datetime
import time
import os

try:
    from app.lcd_driver_st7735 import ST7735, InputHandler
except ImportError:
    from lcd_driver_st7735 import ST7735, InputHandler


class LCDRenderer:
    """Renders token data to 1.44" LCD display with optimized layout."""

    # Display dimensions
    WIDTH = 128
    HEIGHT = 128

    # Color scheme
    COLORS = {
        'background': (0, 0, 0),        # Black background
        'text_primary': (255, 255, 255),  # White
        'text_secondary': (180, 180, 180), # Light gray
        'price_up': (0, 255, 0),        # Green
        'price_down': (255, 0, 0),      # Red
        'price_neutral': (255, 255, 255), # White
        'accent': (0, 150, 255),        # Blue
        'warning': (255, 165, 0),       # Orange
        'border': (60, 60, 60),         # Dark gray
    }

    # Layout zones for 128x128 display
    # Compact layout optimized for small screen
    ZONE_HEADER = (0, 0, 128, 20)      # Token symbol
    ZONE_PRICE = (0, 22, 128, 35)      # Large price
    ZONE_CHANGE = (0, 59, 128, 25)     # 24h change
    ZONE_STATS = (0, 86, 128, 25)      # Vol/Liq (compact)
    ZONE_TIME = (0, 113, 128, 15)      # Update time

    def __init__(self, config, lcd: Optional[ST7735] = None):
        """
        Initialize LCD renderer.

        Args:
            config: Config instance
            lcd: ST7735 display driver instance (optional for testing)
        """
        self.config = config
        self.lcd = lcd or ST7735(
            dc_pin=config.get("display.gpio.dc_pin", 25),
            rst_pin=config.get("display.gpio.rst_pin", 17),
            cs_pin=config.get("display.gpio.cs_pin", 8),
            bl_pin=config.get("display.gpio.bl_pin", 24)
        )

        self.inputs = InputHandler()
        self.width = self.WIDTH
        self.height = self.HEIGHT

        # Display modes
        self.current_view = 0  # 0: Price, 1: Stats, 2: Chart
        self.brightness = 100  # 0-100%

        # Font loading
        self.fonts = self._load_fonts()

        # Price history for mini chart
        self.price_history = []
        self.max_history = 50

        self.initialized = False
        self.last_update = 0

    def _load_fonts(self):
        """Load fonts with different sizes."""
        fonts = {}
        font_paths = [
            "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
            "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
            "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf",
            "/System/Library/Fonts/Helvetica.ttc",  # macOS
        ]

        sizes = {
            'tiny': 9,
            'small': 11,
            'medium': 14,
            'large': 20,
            'xlarge': 28,
        }

        for size_name, size_value in sizes.items():
            font_loaded = False
            for path in font_paths:
                if os.path.exists(path):
                    try:
                        fonts[size_name] = ImageFont.truetype(path, size_value)
                        font_loaded = True
                        break
                    except:
                        continue

            if not font_loaded:
                # Fallback to default
                fonts[size_name] = ImageFont.load_default()

        return fonts

    def init(self):
        """Initialize LCD display."""
        if not self.initialized:
            self.lcd.init()
            self.show_splash()
            self.initialized = True

    def show_splash(self):
        """Show splash screen on startup."""
        img = Image.new('RGB', (self.width, self.height), color=self.COLORS['background'])
        draw = ImageDraw.Draw(img)

        # Draw TETSUO logo/text
        text = "TETSUO"
        bbox = draw.textbbox((0, 0), text, font=self.fonts['large'])
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x = (self.width - text_width) // 2
        y = 40

        # Draw with gradient effect
        for i in range(3):
            color = (0, 150 - i*30, 255 - i*30)
            draw.text((x-i, y-i), text, font=self.fonts['large'], fill=color)

        # Add subtitle
        subtitle = "Price Tracker"
        bbox = draw.textbbox((0, 0), subtitle, font=self.fonts['small'])
        subtitle_width = bbox[2] - bbox[0]
        x = (self.width - subtitle_width) // 2
        draw.text((x, 70), subtitle, font=self.fonts['small'], fill=self.COLORS['text_secondary'])

        # Loading bar
        bar_width = 80
        bar_height = 4
        bar_x = (self.width - bar_width) // 2
        bar_y = 95

        draw.rectangle([bar_x, bar_y, bar_x + bar_width, bar_y + bar_height],
                      outline=self.COLORS['border'], width=1)

        # Animated loading effect (static for now)
        draw.rectangle([bar_x + 2, bar_y + 1, bar_x + 40, bar_y + bar_height - 1],
                      fill=self.COLORS['accent'])

        self.lcd.display_image(img)
        time.sleep(1)

    def render(self, data, stale_seconds: int = 0):
        """
        Render token data to LCD display.

        Args:
            data: TokenData instance
            stale_seconds: How many seconds data is stale (0 = fresh)
        """
        if not self.initialized:
            self.init()

        # Check for input and switch views
        self._handle_input()

        # Create image based on current view
        if self.current_view == 0:
            img = self._render_price_view(data, stale_seconds)
        elif self.current_view == 1:
            img = self._render_stats_view(data, stale_seconds)
        elif self.current_view == 2:
            img = self._render_chart_view(data, stale_seconds)
        else:
            img = self._render_price_view(data, stale_seconds)

        # Display the image
        self.lcd.display_image(img)

        # Update price history
        if data and data.price_usd:
            self.price_history.append(data.price_usd)
            if len(self.price_history) > self.max_history:
                self.price_history.pop(0)

        self.last_update = time.time()

    def _handle_input(self):
        """Handle joystick and button inputs."""
        states = self.inputs.read_inputs()

        if states.get('right'):
            self.current_view = (self.current_view + 1) % 3
            time.sleep(0.2)  # Debounce
        elif states.get('left'):
            self.current_view = (self.current_view - 1) % 3
            time.sleep(0.2)
        elif states.get('up'):
            self.brightness = min(100, self.brightness + 10)
            self._set_brightness()
            time.sleep(0.1)
        elif states.get('down'):
            self.brightness = max(10, self.brightness - 10)
            self._set_brightness()
            time.sleep(0.1)

    def _set_brightness(self):
        """Adjust display brightness (if supported)."""
        # This would typically control PWM on backlight pin
        # For now, just turn on/off
        self.lcd.set_backlight(self.brightness > 0)

    def _render_price_view(self, data, stale_seconds: int):
        """Render main price view."""
        img = Image.new('RGB', (self.width, self.height), color=self.COLORS['background'])
        draw = ImageDraw.Draw(img)

        # Header - Token symbol
        symbol = self.config.get("token.symbol", "TETSUO")
        draw.rectangle([0, 0, self.width, 20], fill=(20, 20, 20))
        draw.text((5, 3), symbol, font=self.fonts['medium'], fill=self.COLORS['accent'])

        # Status indicator
        if stale_seconds == 0:
            status_color = self.COLORS['price_up']
            status_text = "LIVE"
        elif stale_seconds < 60:
            status_color = self.COLORS['warning']
            status_text = f"{stale_seconds}s"
        else:
            status_color = self.COLORS['price_down']
            status_text = f"{stale_seconds//60}m"

        bbox = draw.textbbox((0, 0), status_text, font=self.fonts['tiny'])
        status_width = bbox[2] - bbox[0]
        draw.text((self.width - status_width - 5, 4), status_text,
                 font=self.fonts['tiny'], fill=status_color)

        if data is None:
            # No data message
            draw.text((20, 50), "Waiting for", font=self.fonts['medium'],
                     fill=self.COLORS['text_secondary'])
            draw.text((35, 70), "data...", font=self.fonts['medium'],
                     fill=self.COLORS['text_secondary'])
        else:
            # Price
            price = data.price_usd
            if price >= 1:
                price_text = f"${price:,.2f}"
            elif price >= 0.01:
                price_text = f"${price:.4f}"
            else:
                price_text = f"${price:.6f}".rstrip('0').rstrip('.')

            # Center price
            bbox = draw.textbbox((0, 0), price_text, font=self.fonts['xlarge'])
            price_width = bbox[2] - bbox[0]
            x = (self.width - price_width) // 2
            draw.text((x, 28), price_text, font=self.fonts['xlarge'],
                     fill=self.COLORS['text_primary'])

            # 24h Change with color
            if data.change_24h_pct is not None:
                change = data.change_24h_pct
                if change > 0:
                    arrow = "▲"
                    change_color = self.COLORS['price_up']
                    change_text = f"+{change:.2f}%"
                elif change < 0:
                    arrow = "▼"
                    change_color = self.COLORS['price_down']
                    change_text = f"{change:.2f}%"
                else:
                    arrow = "▬"
                    change_color = self.COLORS['price_neutral']
                    change_text = "0.00%"

                # Draw change bar
                draw.rectangle([10, 62, self.width-10, 80], outline=change_color, width=1)
                combined_text = f"{arrow} {change_text}"
                bbox = draw.textbbox((0, 0), combined_text, font=self.fonts['medium'])
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                draw.text((x, 65), combined_text, font=self.fonts['medium'], fill=change_color)

            # Compact stats
            if data.volume_24h_usd:
                vol_text = f"V: ${self._format_number(data.volume_24h_usd)}"
            else:
                vol_text = "V: N/A"

            if data.liquidity_usd:
                liq_text = f"L: ${self._format_number(data.liquidity_usd)}"
            elif data.fdv_usd:
                liq_text = f"FDV: ${self._format_number(data.fdv_usd)}"
            else:
                liq_text = "L: N/A"

            draw.text((5, 88), vol_text, font=self.fonts['tiny'],
                     fill=self.COLORS['text_secondary'])
            draw.text((5, 100), liq_text, font=self.fonts['tiny'],
                     fill=self.COLORS['text_secondary'])

        # Footer - Time
        now = datetime.now()
        time_text = now.strftime("%H:%M:%S")
        draw.line([(0, 113), (self.width, 113)], fill=self.COLORS['border'], width=1)
        bbox = draw.textbbox((0, 0), time_text, font=self.fonts['small'])
        time_width = bbox[2] - bbox[0]
        x = (self.width - time_width) // 2
        draw.text((x, 115), time_text, font=self.fonts['small'],
                 fill=self.COLORS['text_secondary'])

        return img

    def _render_stats_view(self, data, stale_seconds: int):
        """Render detailed stats view."""
        img = Image.new('RGB', (self.width, self.height), color=self.COLORS['background'])
        draw = ImageDraw.Draw(img)

        # Header
        draw.rectangle([0, 0, self.width, 20], fill=(20, 20, 20))
        draw.text((5, 3), "STATS", font=self.fonts['medium'], fill=self.COLORS['accent'])

        if data is None:
            draw.text((20, 50), "No data", font=self.fonts['medium'],
                     fill=self.COLORS['text_secondary'])
        else:
            y_offset = 25
            line_height = 15

            # Price
            draw.text((5, y_offset), "Price:", font=self.fonts['small'],
                     fill=self.COLORS['text_secondary'])
            price_text = f"${data.price_usd:.6f}".rstrip('0').rstrip('.')
            draw.text((45, y_offset), price_text, font=self.fonts['small'],
                     fill=self.COLORS['text_primary'])

            # 24h Change
            y_offset += line_height
            draw.text((5, y_offset), "24h:", font=self.fonts['small'],
                     fill=self.COLORS['text_secondary'])
            if data.change_24h_pct is not None:
                change_color = (self.COLORS['price_up'] if data.change_24h_pct > 0
                              else self.COLORS['price_down'])
                draw.text((45, y_offset), f"{data.change_24h_pct:+.2f}%",
                         font=self.fonts['small'], fill=change_color)

            # Volume
            y_offset += line_height
            draw.text((5, y_offset), "Vol 24h:", font=self.fonts['small'],
                     fill=self.COLORS['text_secondary'])
            if data.volume_24h_usd:
                draw.text((45, y_offset), f"${self._format_number(data.volume_24h_usd)}",
                         font=self.fonts['small'], fill=self.COLORS['text_primary'])

            # Liquidity
            y_offset += line_height
            draw.text((5, y_offset), "Liquidity:", font=self.fonts['small'],
                     fill=self.COLORS['text_secondary'])
            if data.liquidity_usd:
                draw.text((55, y_offset), f"${self._format_number(data.liquidity_usd)}",
                         font=self.fonts['small'], fill=self.COLORS['text_primary'])

            # FDV
            y_offset += line_height
            draw.text((5, y_offset), "FDV:", font=self.fonts['small'],
                     fill=self.COLORS['text_secondary'])
            if data.fdv_usd:
                draw.text((45, y_offset), f"${self._format_number(data.fdv_usd)}",
                         font=self.fonts['small'], fill=self.COLORS['text_primary'])

            # Source
            y_offset += line_height
            draw.text((5, y_offset), "Source:", font=self.fonts['small'],
                     fill=self.COLORS['text_secondary'])
            draw.text((45, y_offset), data.source[:10], font=self.fonts['small'],
                     fill=self.COLORS['text_primary'])

        return img

    def _render_chart_view(self, data, stale_seconds: int):
        """Render price chart view."""
        img = Image.new('RGB', (self.width, self.height), color=self.COLORS['background'])
        draw = ImageDraw.Draw(img)

        # Header
        draw.rectangle([0, 0, self.width, 20], fill=(20, 20, 20))
        draw.text((5, 3), "CHART", font=self.fonts['medium'], fill=self.COLORS['accent'])

        if len(self.price_history) < 2:
            draw.text((20, 50), "Collecting", font=self.fonts['medium'],
                     fill=self.COLORS['text_secondary'])
            draw.text((30, 70), "data...", font=self.fonts['medium'],
                     fill=self.COLORS['text_secondary'])
        else:
            # Draw price chart
            chart_x = 10
            chart_y = 25
            chart_width = self.width - 20
            chart_height = 70

            # Chart border
            draw.rectangle([chart_x, chart_y, chart_x + chart_width, chart_y + chart_height],
                          outline=self.COLORS['border'], width=1)

            # Calculate chart points
            prices = self.price_history[-30:]  # Last 30 points
            if len(prices) > 1:
                min_price = min(prices)
                max_price = max(prices)
                price_range = max_price - min_price if max_price != min_price else 1

                points = []
                for i, price in enumerate(prices):
                    x = chart_x + 2 + (i * (chart_width - 4) // (len(prices) - 1))
                    y = chart_y + chart_height - 2 - int((price - min_price) / price_range * (chart_height - 4))
                    points.append((x, y))

                # Draw chart line
                for i in range(len(points) - 1):
                    color = (self.COLORS['price_up'] if prices[i+1] >= prices[i]
                            else self.COLORS['price_down'])
                    draw.line([points[i], points[i+1]], fill=color, width=2)

                # Draw last price
                if data and data.price_usd:
                    price_text = f"${data.price_usd:.6f}".rstrip('0').rstrip('.')
                    draw.text((chart_x, chart_y + chart_height + 5), price_text,
                             font=self.fonts['small'], fill=self.COLORS['text_primary'])

                    # Show high/low
                    draw.text((chart_x, chart_y + chart_height + 20),
                             f"H: ${max_price:.6f}".rstrip('0').rstrip('.'),
                             font=self.fonts['tiny'], fill=self.COLORS['price_up'])
                    draw.text((chart_x, chart_y + chart_height + 32),
                             f"L: ${min_price:.6f}".rstrip('0').rstrip('.'),
                             font=self.fonts['tiny'], fill=self.COLORS['price_down'])

        return img

    def _format_number(self, num: float) -> str:
        """Format large numbers with K/M/B suffixes."""
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.2f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.2f}K"
        else:
            return f"{num:,.2f}"

    def show_error(self, message: str):
        """Display error message on LCD."""
        img = Image.new('RGB', (self.width, self.height), color=self.COLORS['background'])
        draw = ImageDraw.Draw(img)

        # Error header
        draw.rectangle([0, 0, self.width, 25], fill=(100, 0, 0))
        draw.text((5, 5), "ERROR", font=self.fonts['medium'], fill=(255, 255, 255))

        # Error message (word wrap)
        y = 35
        words = message.split()
        line = ""
        for word in words:
            test_line = f"{line} {word}".strip()
            bbox = draw.textbbox((0, 0), test_line, font=self.fonts['small'])
            if bbox[2] > self.width - 10:
                if line:
                    draw.text((5, y), line, font=self.fonts['small'],
                             fill=self.COLORS['text_primary'])
                    y += 15
                line = word
            else:
                line = test_line

        if line:
            draw.text((5, y), line, font=self.fonts['small'],
                     fill=self.COLORS['text_primary'])

        self.lcd.display_image(img)

    def shutdown(self):
        """Clean shutdown of LCD display."""
        print("Shutting down LCD display...")

        # Show shutdown message
        img = Image.new('RGB', (self.width, self.height), color=self.COLORS['background'])
        draw = ImageDraw.Draw(img)
        draw.text((30, 55), "Goodbye!", font=self.fonts['large'],
                 fill=self.COLORS['accent'])
        self.lcd.display_image(img)
        time.sleep(1)

        # Clear and cleanup
        self.lcd.cleanup()


def main():
    """Test LCD renderer with sample data."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from app.config import Config
    from app.data_fetcher import TokenData

    print("Testing LCD renderer...")

    config = Config()
    renderer = LCDRenderer(config)

    try:
        # Initialize and show splash
        renderer.init()
        time.sleep(2)

        # Create sample data
        sample_data = TokenData(
            price_usd=0.003456,
            change_24h_pct=5.23,
            volume_24h_usd=1_234_567.89,
            liquidity_usd=456_789.12,
            fdv_usd=12_345_678,
            source="test",
            updated_at_epoch=int(time.time())
        )

        print("Displaying sample data...")
        print("Use joystick left/right to switch views")
        print("Use joystick up/down to adjust brightness")
        print("Press Ctrl+C to exit")

        # Simulate price changes
        import random
        while True:
            # Randomly adjust price
            sample_data.price_usd *= (1 + random.uniform(-0.05, 0.05))
            sample_data.change_24h_pct += random.uniform(-1, 1)

            # Render data
            renderer.render(sample_data, stale_seconds=0)

            time.sleep(2)

    except KeyboardInterrupt:
        print("\nTest interrupted")

    finally:
        renderer.shutdown()


if __name__ == "__main__":
    main()