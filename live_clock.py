#!/usr/bin/env python3
"""
Live clock - updates every minute automatically
"""
import sys
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, '/home/sa/tetsuo-display')
from app.display_driver import EPD2in7

def get_buffer(time_text, font):
    """Create buffer with time text"""
    # Display is VERTICAL: 176 width x 264 height
    image = Image.new('1', (176, 264), 255)  # White background
    draw = ImageDraw.Draw(image)

    bbox = draw.textbbox((0, 0), time_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Bottom center
    x_pos = (176 - text_width) // 2
    y_pos = 264 - text_height - 10

    draw.text((x_pos, y_pos), time_text, font=font, fill=0)

    # Convert to buffer
    buf = [0xFF] * (int(176 / 8) * 264)
    image_mono = image.convert('1')
    pixels = image_mono.load()

    for y in range(264):
        for x in range(176):
            if pixels[x, y] == 0:
                buf[int((x + y * 176) / 8)] &= ~(0x80 >> (x % 8))

    return bytes(buf)

def main():
    print("Starting live clock...")

    # Initialize display
    epd = EPD2in7()
    epd.init('full')

    # Load font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    last_minute = -1

    try:
        while True:
            now = datetime.now()
            current_minute = now.minute

            # Only update when minute changes
            if current_minute != last_minute:
                time_text = now.strftime("%H:%M")
                print(f"Updating display: {time_text}")

                # Create buffer and display
                buffer = get_buffer(time_text, font)
                epd.display_frame(buffer)
                epd.refresh('full')

                last_minute = current_minute

            # Check every 5 seconds
            time.sleep(5)

    except KeyboardInterrupt:
        print("\nStopping clock...")
        epd.sleep()
        epd.cleanup()

if __name__ == "__main__":
    main()
