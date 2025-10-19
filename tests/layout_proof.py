#!/usr/bin/env python3
"""
Layout proof generator for TETSUO display.

Renders sample data to a PNG file for visual inspection.
No hardware required.
"""

import sys
import time
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from PIL import Image, ImageDraw, ImageFont
from app.config import Config
from app.data_fetcher import TokenData


class LayoutProofRenderer:
    """Renders layout to PNG for inspection."""

    def __init__(self, width=264, height=176):
        """
        Initialize renderer.

        Args:
            width: Display width
            height: Display height
        """
        self.width = width
        self.height = height

        # Load fonts with fallback
        self.font_large = self._load_font(48)
        self.font_medium = self._load_font(24)
        self.font_small = self._load_font(16)
        self.font_tiny = self._load_font(12)

    def _load_font(self, size: int):
        """Load TrueType font with fallback."""
        try:
            font_paths = [
                "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf",
                "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf",
                "/System/Library/Fonts/Helvetica.ttc",
                "/Library/Fonts/Arial.ttf",
            ]
            for path in font_paths:
                try:
                    return ImageFont.truetype(path, size)
                except:
                    continue
        except:
            pass

        return ImageFont.load_default()

    def render(self, data: TokenData, stale_seconds: int = 0) -> Image:
        """
        Render layout with sample data.

        Args:
            data: TokenData to display
            stale_seconds: Staleness indicator

        Returns:
            PIL Image
        """
        # Create white background
        image = Image.new('RGB', (self.width, self.height), 'white')
        draw = ImageDraw.Draw(image)

        # Draw zones (for reference)
        zones = [
            (0, 0, 264, 30, "HEADER"),
            (10, 35, 180, 60, "PRICE"),
            (195, 35, 69, 60, "CHANGE"),
            (10, 100, 254, 40, "STATS"),
            (0, 145, 264, 31, "FOOTER"),
        ]

        for x, y, w, h, label in zones:
            # Draw zone border (light gray)
            draw.rectangle([x, y, x + w, y + h], outline='lightgray', width=1)

            # Draw zone label (very light)
            draw.text((x + 2, y + 2), label, font=self.font_tiny, fill='lightgray')

        # Draw actual content
        self._draw_header(draw)
        self._draw_price(draw, data)
        self._draw_change(draw, data)
        self._draw_stats(draw, data)
        self._draw_footer(draw, stale_seconds)

        return image

    def _draw_header(self, draw: ImageDraw):
        """Draw header."""
        draw.text((10, 5), "TETSUO (SOL)", font=self.font_medium, fill='black')

    def _draw_price(self, draw: ImageDraw, data: TokenData):
        """Draw price."""
        price = data.price_usd

        if price >= 1:
            price_text = f"${price:,.2f}"
        elif price >= 0.01:
            price_text = f"${price:.4f}"
        elif price >= 0.0001:
            price_text = f"${price:.6f}"
        else:
            price_text = f"${price:.8f}"

        if '.' in price_text:
            price_text = price_text.rstrip('0').rstrip('.')

        draw.text((10, 40), price_text, font=self.font_large, fill='black')

    def _draw_change(self, draw: ImageDraw, data: TokenData):
        """Draw 24h change."""
        if data.change_24h_pct is None:
            arrow = ""
            change_text = "N/A"
        else:
            change = data.change_24h_pct
            arrow = "▲" if change >= 0 else "▼"
            change_text = f"{abs(change):.2f}%"

        draw.text((195, 40), arrow, font=self.font_large, fill='black')
        draw.text((200, 80), change_text, font=self.font_small, fill='black')

    def _draw_stats(self, draw: ImageDraw, data: TokenData):
        """Draw stats."""
        if data.volume_24h_usd:
            vol_text = f"Vol 24h: ${self._format_number(data.volume_24h_usd)}"
        else:
            vol_text = "Vol: N/A"

        if data.liquidity_usd:
            liq_text = f"Liq: ${self._format_number(data.liquidity_usd)}"
        elif data.fdv_usd:
            liq_text = f"FDV: ${self._format_number(data.fdv_usd)}"
        else:
            liq_text = "Liq: N/A"

        draw.text((10, 105), vol_text, font=self.font_small, fill='black')
        draw.text((10, 125), liq_text, font=self.font_small, fill='black')

    def _draw_footer(self, draw: ImageDraw, stale_seconds: int):
        """Draw footer."""
        from datetime import datetime
        time_text = datetime.now().strftime("%H:%M")

        if stale_seconds > 0:
            if stale_seconds < 60:
                status = f"STALE {stale_seconds}s"
            else:
                mins = stale_seconds // 60
                secs = stale_seconds % 60
                status = f"STALE {mins}m{secs}s"
        else:
            status = "LIVE"

        draw.text((10, 150), time_text, font=self.font_small, fill='black')

        # Right-align status
        bbox = draw.textbbox((0, 0), status, font=self.font_tiny)
        status_width = bbox[2] - bbox[0]
        draw.text((self.width - status_width - 10, 153), status, font=self.font_tiny, fill='black')

    def _format_number(self, num: float) -> str:
        """Format number with K/M/B suffix."""
        if num >= 1_000_000_000:
            return f"{num / 1_000_000_000:.2f}B"
        elif num >= 1_000_000:
            return f"{num / 1_000_000:.2f}M"
        elif num >= 1_000:
            return f"{num / 1_000:.2f}K"
        else:
            return f"{num:,.2f}"


def main():
    """Generate layout proofs."""
    output_dir = Path(__file__).parent
    output_dir.mkdir(exist_ok=True)

    print("Generating layout proofs...\n")

    renderer = LayoutProofRenderer()

    # Test cases
    test_cases = [
        (
            "normal",
            TokenData(
                price_usd=0.003456,
                change_24h_pct=5.23,
                volume_24h_usd=1_234_567.89,
                liquidity_usd=456_789.12,
                fdv_usd=None,
                source="test",
                updated_at_epoch=int(time.time())
            ),
            0
        ),
        (
            "high_price",
            TokenData(
                price_usd=123.45,
                change_24h_pct=-2.67,
                volume_24h_usd=45_678_901.23,
                liquidity_usd=12_345_678.90,
                fdv_usd=None,
                source="test",
                updated_at_epoch=int(time.time())
            ),
            0
        ),
        (
            "low_price",
            TokenData(
                price_usd=0.00000123,
                change_24h_pct=125.5,
                volume_24h_usd=567_890.12,
                liquidity_usd=234_567.89,
                fdv_usd=None,
                source="test",
                updated_at_epoch=int(time.time())
            ),
            0
        ),
        (
            "stale_data",
            TokenData(
                price_usd=0.00456,
                change_24h_pct=-0.42,
                volume_24h_usd=890_123.45,
                liquidity_usd=345_678.90,
                fdv_usd=None,
                source="test",
                updated_at_epoch=int(time.time()) - 300
            ),
            300
        ),
        (
            "minimal_data",
            TokenData(
                price_usd=0.00789,
                change_24h_pct=None,
                volume_24h_usd=None,
                liquidity_usd=None,
                fdv_usd=1_234_567.89,
                source="test",
                updated_at_epoch=int(time.time())
            ),
            0
        ),
    ]

    for name, data, stale in test_cases:
        print(f"Rendering '{name}'...")
        image = renderer.render(data, stale)

        # Save at 2x scale for better visibility
        scaled = image.resize((image.width * 2, image.height * 2), Image.NEAREST)
        output_path = output_dir / f"layout_{name}.png"
        scaled.save(output_path)

        print(f"  Saved: {output_path}")

    print(f"\n✓ Generated {len(test_cases)} layout proofs")
    print(f"  Location: {output_dir}")
    print("\nOpen the PNG files to inspect the layout")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
