#!/usr/bin/env python3
"""
Simple clock - only show time in large black text on white background
"""
import sys
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, '/home/sa/tetsuo-display')
from app.display_driver import EPD2in7

def main():
    print("Initializing display...")
    epd = EPD2in7()
    epd.init('full')

    # Create white image
    image = Image.new('1', (264, 176), 255)  # White background
    draw = ImageDraw.Draw(image)

    # Load large font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 80)
    except:
        font = ImageFont.load_default()

    # Get current time
    now = datetime.now()
    time_text = now.strftime("%H:%M")

    # Draw time centered
    bbox = draw.textbbox((0, 0), time_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    x = (264 - text_width) // 2
    y = (176 - text_height) // 2

    draw.text((x, y), time_text, font=font, fill=0)  # Black text

    print(f"Displaying: {time_text}")

    # Convert to buffer
    buffer = []
    for y in range(176):
        for x in range(0, 264, 8):
            byte = 0
            for bit in range(8):
                if x + bit < 264:
                    pixel = image.getpixel((x + bit, y))
                    # V2: white pixel (255) -> bit 1
                    if pixel == 255:
                        byte |= (0x80 >> bit)
            buffer.append(byte)

    # Display
    epd.display_frame(bytes(buffer))
    epd.refresh('full')

    print("Done!")

    epd.sleep()
    epd.cleanup()

if __name__ == "__main__":
    main()
