"""Renderer for TETSUO e-paper display."""

from PIL import Image, ImageDraw, ImageFont
from typing import Optional, Tuple
from datetime import datetime
import time

try:
    from app.display_driver import EPD2in7
except ImportError:
    from display_driver import EPD2in7


class DisplayRenderer:
    """Renders token data to e-paper display with smart refresh management."""

    # Display dimensions: 264 (width) x 176 (height) - HORIZONTAL orientation
    # Layout zones (x, y, width, height) - optimized for horizontal display
    ZONE_HEADER = (0, 0, 264, 28)        # Token name
    ZONE_PRICE = (10, 32, 140, 65)       # Large price display
    ZONE_CHANGE = (155, 32, 100, 65)     # 24h change with arrow
    ZONE_STATS = (10, 102, 244, 50)      # Volume and liquidity
    ZONE_FOOTER = (0, 156, 264, 20)      # Time and status

    def __init__(self, config, epd: Optional[EPD2in7] = None):
        """
        Initialize renderer.

        Args:
            config: Config instance
            epd: EPD2in7 display driver instance (optional for testing)
        """
        self.config = config
        self.epd = epd or EPD2in7(
            dc_pin=config.get("display.gpio.dc_pin", 25),
            rst_pin=config.get("display.gpio.rst_pin", 17),
            busy_pin=config.get("display.gpio.busy_pin", 24),
            cs_pin=config.get("display.gpio.cs_pin", 8)
        )

        self.width = config.get("display.width", 264)
        self.height = config.get("display.height", 176)
        self.mode = config.get("display.mode", "normal")

        self.full_refresh_minutes = config.get("refresh.full_every_minutes", 45)
        self.full_refresh_after_partials = config.get("refresh.full_after_partials", 60)

        self.last_full_refresh = 0
        self.partial_count = 0

        # Try to load fonts (fallback to default if not available)
        # Optimized sizes for 264x176 horizontal display
        self.font_xlarge = self._load_font(48)   # Price
        self.font_large = self._load_font(32)    # Change percentage
        self.font_medium = self._load_font(18)   # Header, stats
        self.font_small = self._load_font(14)    # Footer time
        self.font_tiny = self._load_font(12)     # Status

        self.last_image = None
        self.initialized = False

    def _load_font(self, size: int):
        """Load TrueType font with fallback to default."""
        try:
            # Try common font locations
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/System/Library/Fonts/Helvetica.ttc",  # macOS
            ]
            for path in font_paths:
                try:
                    return ImageFont.truetype(path, size)
                except:
                    continue
        except:
            pass

        # Fallback to default
        return ImageFont.load_default()

    def init(self):
        """Initialize display."""
        if not self.initialized:
            self.epd.init('full')
            self.epd.clear()
            self.last_full_refresh = time.time()
            self.initialized = True

    def show_blank(self):
        """Force the display to a fully white screen and keep state."""
        if not self.initialized:
            self.init()

        # Clear to white using the driver
        self.epd.init('full')
        self.epd.clear()

        # Track last image as white to avoid accidental redraws
        image = Image.new('1', (self.width, self.height), 255)
        self.last_image = image

    def render(self, data, stale_seconds: int = 0):
        """
        Render token data to display.

        Args:
            data: TokenData instance
            stale_seconds: How many seconds data is stale (0 = fresh)
        """
        if not self.initialized:
            self.init()

        # If running in blank mode, keep the screen white and skip rendering
        if str(self.mode).lower() == "blank":
            # Ensure it stays white in case something else drew
            self.show_blank()
            return

        # Determine refresh mode
        should_full_refresh = self._should_full_refresh()

        if should_full_refresh:
            self._render_full(data, stale_seconds)
            self.last_full_refresh = time.time()
            self.partial_count = 0
        else:
            self._render_partial(data, stale_seconds)
            self.partial_count += 1

    def _should_full_refresh(self) -> bool:
        """Determine if full refresh is needed."""
        # Time-based check
        time_since_full = time.time() - self.last_full_refresh
        if time_since_full > (self.full_refresh_minutes * 60):
            return True

        # Count-based check
        if self.partial_count >= self.full_refresh_after_partials:
            return True

        return False

    def _render_full(self, data, stale_seconds: int):
        """Render complete display with full refresh."""
        print("Full refresh")

        # Create image - correct dimensions 176x264
        image = Image.new('1', (self.width, self.height), 255)  # White background
        draw = ImageDraw.Draw(image)

        # Draw all zones with new optimized layout
        self._draw_header(draw, data)
        self._draw_price(draw, data)
        self._draw_change(draw, data)
        self._draw_stats(draw, data)
        self._draw_footer(draw, stale_seconds)

        # Convert to buffer
        buffer = self._image_to_buffer(image)

        self.epd.init('full')
        self.epd.display_frame(buffer)
        self.epd.refresh('full')

        self.last_image = image

    def _render_partial(self, data, stale_seconds: int):
        """Render only dynamic zones with partial refresh."""
        print("Partial refresh")

        if self.last_image is None:
            # No previous image, do full refresh
            self._render_full(data, stale_seconds)
            return

        # Create new image based on last
        image = self.last_image.copy()
        draw = ImageDraw.Draw(image)

        # Only update dynamic zones
        self._clear_zone(draw, self.ZONE_PRICE)
        self._clear_zone(draw, self.ZONE_CHANGE)
        self._clear_zone(draw, self.ZONE_STATS)
        self._clear_zone(draw, self.ZONE_FOOTER)

        self._draw_price(draw, data)
        self._draw_change(draw, data)
        self._draw_stats(draw, data)
        self._draw_footer(draw, stale_seconds)

        # No rotation needed
        buffer = self._image_to_buffer(image)

        self.epd.init('partial')
        self.epd.display_frame(buffer)
        self.epd.refresh('partial')

        self.last_image = image

    def _draw_header(self, draw: ImageDraw, data):
        """Draw static header with token symbol."""
        symbol = self.config.get("token.symbol", "TETSUO")
        chain = self.config.get("token.chain", "SOL").upper()

        # Left-aligned header
        header_text = f"{symbol}/{chain}"
        x, y, w, h = self.ZONE_HEADER
        draw.text((x + 10, y + 5), header_text, font=self.font_medium, fill=0)

        # Draw separator line
        draw.line([(10, h - 1), (self.width - 10, h - 1)], fill=0, width=1)

    def _draw_price(self, draw: ImageDraw, data):
        """Draw price on left side."""
        if data is None:
            price_text = "-.------"
        else:
            # Format price with appropriate decimals
            price = data.price_usd
            if price >= 1:
                price_text = f"${price:,.2f}"
            elif price >= 0.01:
                price_text = f"${price:.4f}"
            elif price >= 0.0001:
                price_text = f"${price:.6f}"
            else:
                price_text = f"${price:.8f}"

            # Remove trailing zeros after decimal
            if '.' in price_text:
                price_text = price_text.rstrip('0').rstrip('.')

        x, y, w, h = self.ZONE_PRICE
        draw.text((x, y + 10), price_text, font=self.font_xlarge, fill=0)

    def _draw_change(self, draw: ImageDraw, data):
        """Draw 24h price change with arrow on right side."""
        if data is None or data.change_24h_pct is None:
            change_text = "N/A"
            arrow = ""
        else:
            change = data.change_24h_pct
            arrow = "▲" if change >= 0 else "▼"
            sign = "+" if change >= 0 else ""
            change_text = f"{sign}{change:.2f}%"

        x, y, w, h = self.ZONE_CHANGE

        # Draw arrow large
        draw.text((x + 5, y + 5), arrow, font=self.font_large, fill=0)

        # Draw percentage below arrow
        draw.text((x + 5, y + 40), change_text, font=self.font_medium, fill=0)

    def _draw_stats(self, draw: ImageDraw, data):
        """Draw volume and liquidity stats in one line."""
        x, y, w, h = self.ZONE_STATS

        if data is None:
            vol_text = "Vol: N/A"
            liq_text = "Liq: N/A"
        else:
            # Volume
            if data.volume_24h_usd:
                vol_text = f"Vol: ${self._format_number(data.volume_24h_usd)}"
            else:
                vol_text = "Vol: N/A"

            # Liquidity or FDV
            if data.liquidity_usd:
                liq_text = f"Liq: ${self._format_number(data.liquidity_usd)}"
            elif data.fdv_usd:
                liq_text = f"FDV: ${self._format_number(data.fdv_usd)}"
            else:
                liq_text = "Liq: N/A"

        # Draw stats in one line, separated
        draw.text((x, y + 5), vol_text, font=self.font_medium, fill=0)
        draw.text((x, y + 28), liq_text, font=self.font_medium, fill=0)

        # Draw separator line
        draw.line([(10, y + h - 1), (self.width - 10, y + h - 1)], fill=0, width=1)

    def _draw_footer(self, draw: ImageDraw, stale_seconds: int):
        """Draw footer with time and status - NO seconds."""
        now = datetime.now()
        time_text = now.strftime("%H:%M")  # Sin segundos

        if stale_seconds > 0:
            # Format stale time
            if stale_seconds < 60:
                status = f"STALE {stale_seconds}s"
            else:
                mins = stale_seconds // 60
                status = f"STALE {mins}m"
        else:
            status = "LIVE"

        x, y, w, h = self.ZONE_FOOTER

        # Draw time on left
        draw.text((x + 10, y + 3), time_text, font=self.font_small, fill=0)

        # Draw status on right
        bbox = draw.textbbox((0, 0), status, font=self.font_tiny)
        status_width = bbox[2] - bbox[0]
        draw.text((x + w - status_width - 10, y + 4), status, font=self.font_tiny, fill=0)

    def _clear_zone(self, draw: ImageDraw, zone: Tuple[int, int, int, int]):
        """Clear a zone to white."""
        x, y, w, h = zone
        draw.rectangle([x, y, x + w, y + h], fill=255)

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

    def _image_to_buffer(self, image: Image) -> bytes:
        """Convert PIL Image to display buffer for V2 (0xFF=white, 0x00=black)."""
        buffer = []

        # Use image dimensions
        img_width, img_height = image.size

        for y in range(img_height):
            for x in range(0, img_width, 8):
                byte = 0
                for bit in range(8):
                    if x + bit < img_width:
                        pixel = image.getpixel((x + bit, y))
                        # V2 format: 0xFF byte = white, 0x00 byte = black
                        # PIL: pixel 0 = BLACK, pixel 255 = WHITE
                        # So we set bit when pixel is WHITE (255)
                        if pixel == 255:
                            byte |= (0x80 >> bit)
                buffer.append(byte)

        return bytes(buffer)

    def shutdown(self):
        """Clean shutdown of display."""
        print("Shutting down display...")
        self.epd.cleanup()

    def show_test_pattern(self):
        """Display a test pattern with new layout."""
        if not self.initialized:
            self.init()

        print("Showing test pattern...")

        image = Image.new('1', (self.width, self.height), 255)
        draw = ImageDraw.Draw(image)

        # Draw border
        draw.rectangle([0, 0, self.width - 1, self.height - 1], outline=0, width=2)

        # Draw zones for debugging
        for zone in [self.ZONE_HEADER, self.ZONE_PRICE, self.ZONE_CHANGE,
                     self.ZONE_STATS, self.ZONE_FOOTER]:
            x, y, w, h = zone
            draw.rectangle([x, y, x + w, y + h], outline=0)

        # Draw sample content using actual rendering methods
        from app.data_fetcher import TokenData
        import time

        sample_data = TokenData(
            price_usd=0.001555,
            change_24h_pct=-10.75,
            volume_24h_usd=11223.17,
            liquidity_usd=597312.54,
            fdv_usd=None,
            source="test",
            updated_at_epoch=int(time.time())
        )

        self._draw_header(draw, sample_data)
        self._draw_price(draw, sample_data)
        self._draw_change(draw, sample_data)
        self._draw_stats(draw, sample_data)
        self._draw_footer(draw, 0)

        # Display
        buffer = self._image_to_buffer(image)

        self.epd.init('full')
        self.epd.display_frame(buffer)
        self.epd.refresh('full')

        self.last_image = image

        print("Test pattern displayed")


def main():
    """Test renderer with sample data."""
    import sys
    from pathlib import Path
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from app.config import Config
    from app.data_fetcher import TokenData

    print("Testing renderer...")

    config = Config()
    renderer = DisplayRenderer(config)

    # Show test pattern
    renderer.show_test_pattern()

    time.sleep(2)

    # Create sample data
    sample_data = TokenData(
        price_usd=0.003456,
        change_24h_pct=5.23,
        volume_24h_usd=1_234_567.89,
        liquidity_usd=456_789.12,
        fdv_usd=None,
        source="test",
        updated_at_epoch=int(time.time())
    )

    # Render sample data
    renderer.render(sample_data, stale_seconds=0)

    print("Renderer test complete. Display will show sample data.")


if __name__ == "__main__":
    main()
