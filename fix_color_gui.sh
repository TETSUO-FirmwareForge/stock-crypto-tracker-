#!/bin/bash

# Fix the GUI to show proper colors and better layout

cd ~/tetsuo-lcd

# Stop any running instance
sudo pkill -f main_lcd.py

# Create improved color renderer
cat > fix_gui.py << 'ENDFIX'
#!/usr/bin/env python3

import re

# Read current renderer
with open('app/lcd_renderer.py', 'r') as f:
    content = f.read()

# Replace _render_price_view with colorful version
new_render = '''    def _render_price_view(self, data, stale_seconds: int):
        """Render main price view with colors."""
        img = Image.new('RGB', (self.width, self.height), color=(0, 0, 0))
        draw = ImageDraw.Draw(img)

        # Header with gradient
        for y in range(22):
            color = (0, int(30 + y*1.5), int(60 + y*2))
            draw.line([(0, y), (128, y)], fill=color)

        # Token symbol
        symbol = self.config.get("token.symbol", "TETSUO")
        draw.text((5, 4), symbol, font=self.fonts['medium'], fill=(255, 255, 0))

        # Status LED
        if stale_seconds == 0:
            led_color = (0, 255, 0)
        elif stale_seconds < 60:
            led_color = (255, 165, 0)
        else:
            led_color = (255, 0, 0)
        draw.ellipse([108, 5, 118, 15], fill=led_color)

        if data is None:
            draw.text((15, 55), "Loading...", font=self.fonts['medium'], fill=(180, 180, 180))
        else:
            # Price box with background
            price = data.price_usd
            if price >= 1:
                price_text = f"${price:,.3f}"
            elif price >= 0.01:
                price_text = f"${price:.4f}"
            else:
                price_text = f"${price:.6f}".rstrip('0')

            # Price background
            draw.rectangle([2, 24, 126, 56], fill=(10, 10, 40), outline=(50, 50, 150), width=2)

            # Center price text
            bbox = draw.textbbox((0, 0), price_text, font=self.fonts['large'])
            price_width = bbox[2] - bbox[0]
            x = (self.width - price_width) // 2
            draw.text((x, 30), price_text, font=self.fonts['large'], fill=(255, 255, 0))

            # Change indicator with color
            if data.change_24h_pct is not None:
                change = data.change_24h_pct
                if change > 0:
                    arrow = "▲"
                    bg_color = (0, 80, 0)
                    text_color = (0, 255, 0)
                    change_text = f"+{change:.2f}%"
                elif change < 0:
                    arrow = "▼"
                    bg_color = (80, 0, 0)
                    text_color = (255, 80, 80)
                    change_text = f"{change:.2f}%"
                else:
                    arrow = "="
                    bg_color = (40, 40, 40)
                    text_color = (200, 200, 200)
                    change_text = "0.00%"

                # Change box
                draw.rectangle([2, 59, 126, 82], fill=bg_color, outline=text_color, width=1)
                combined = f"{arrow} {change_text} 24h"
                bbox = draw.textbbox((0, 0), combined, font=self.fonts['small'])
                text_width = bbox[2] - bbox[0]
                x = (self.width - text_width) // 2
                draw.text((x, 64), combined, font=self.fonts['small'], fill=text_color)

            # Stats
            y = 87

            if data.volume_24h_usd:
                vol_text = f"Vol: ${self._format_number(data.volume_24h_usd)}"
                draw.text((5, y), vol_text, font=self.fonts['tiny'], fill=(100, 200, 255))

            if data.liquidity_usd:
                liq_text = f"Liq: ${self._format_number(data.liquidity_usd)}"
                draw.text((5, y+11), liq_text, font=self.fonts['tiny'], fill=(255, 180, 100))

        # Footer time
        draw.rectangle([0, 111, 128, 128], fill=(20, 20, 20))
        now = datetime.now()
        time_text = now.strftime("%H:%M:%S")
        bbox = draw.textbbox((0, 0), time_text, font=self.fonts['small'])
        time_width = bbox[2] - bbox[0]
        x = (self.width - time_width) // 2
        draw.text((x, 114), time_text, font=self.fonts['small'], fill=(150, 200, 255))

        return img'''

# Replace the method
pattern = r'def _render_price_view\(self.*?\n        return img'
content = re.sub(pattern, new_render.strip(), content, flags=re.DOTALL)

with open('app/lcd_renderer.py', 'w') as f:
    f.write(content)

print("GUI updated with colors!")
ENDFIX

# Run the fix
python3 fix_gui.py

# Test colors first
echo "Testing color display..."
sudo python3 << 'COLORTEST'
import sys
sys.path.append('.')

from app.lcd_driver_st7735 import ST7735
from PIL import Image, ImageDraw

lcd = ST7735(dc_pin=25, rst_pin=27, cs_pin=8, bl_pin=24)
lcd.init()
lcd.set_backlight(True)

# Create colorful test
img = Image.new('RGB', (128, 128), color='black')
draw = ImageDraw.Draw(img)

# Rainbow gradient
for y in range(128):
    if y < 32:
        color = (255, int(y*8), 0)  # Red to yellow
    elif y < 64:
        color = (int(255-(y-32)*8), 255, 0)  # Yellow to green
    elif y < 96:
        color = (0, int(255-(y-64)*8), int((y-64)*8))  # Green to blue
    else:
        color = (int((y-96)*8), 0, 255)  # Blue to purple
    draw.line([(0, y), (128, y)], fill=color)

# Text overlay
draw.rectangle([10, 40, 118, 70], fill=(0, 0, 0, 128))
draw.text((25, 48), "TETSUO", fill=(255, 255, 0))

print("Displaying rainbow test...")
lcd.display_image(img)

import time
time.sleep(3)

print("Colors displayed!")
lcd.cleanup()
COLORTEST

# Run the main app
echo ""
echo "========================================"
echo "STARTING TETSUO WITH COLOR GUI"
echo "========================================"

sudo python3 main_lcd.py