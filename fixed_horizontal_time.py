#!/usr/bin/env python3
"""
Show CURRENT TIME on display - VERTICAL 176x264
Uses system timezone (configure Pi to Europe/Berlin)
"""
import sys
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, '/home/sa/tetsuo-display')
from app.display_driver import EPD2in7

def main():
    print("Creating image for VERTICAL display (176x264)...")

    # Display is physically VERTICAL: 176 width x 264 height
    image = Image.new('1', (176, 264), 255)  # White background
    draw = ImageDraw.Draw(image)

    # Load font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    # Get CURRENT TIME (uses system timezone)
    now = datetime.now()
    time_text = now.strftime("%H:%M")

    print(f"Current time: {time_text}")
    bbox = draw.textbbox((0, 0), time_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Bottom center - along the longest side (height=264)
    x_pos = (176 - text_width) // 2  # Centered horizontally
    y_pos = 264 - text_height - 10    # Near bottom of the tall side

    print(f"Drawing '{time_text}' at ({x_pos}, {y_pos})")
    print(f"Text size: {text_width}x{text_height}")

    draw.text((x_pos, y_pos), time_text, font=font, fill=0)  # Black text

    # Convert using OFFICIAL Waveshare V2 method for VERTICAL orientation
    print("Converting to buffer (VERTICAL orientation)...")

    # Start with all white (0xFF)
    buf = [0xFF] * (int(176 / 8) * 264)

    # Convert image to mono
    image_mono = image.convert('1')
    pixels = image_mono.load()

    imwidth = 176
    imheight = 264

    print("Processing pixels (vertical mode)...")
    for y in range(imheight):
        for x in range(imwidth):
            # VERTICAL mode - no rotation needed
            # If pixel is BLACK (0), clear the bit
            if pixels[x, y] == 0:
                buf[int((x + y * imwidth) / 8)] &= ~(0x80 >> (x % 8))

    print(f"Buffer created: {len(buf)} bytes")

    # Send to display
    print("Initializing display...")
    epd = EPD2in7()
    epd.init('full')

    print("Sending buffer...")
    epd.display_frame(bytes(buf))

    print("Refreshing...")
    epd.refresh('full')

    print("✅ DONE!")

    epd.sleep()
    epd.cleanup()

if __name__ == "__main__":
    main()
