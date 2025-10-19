#!/usr/bin/env python3
"""
Smooth clock - uses partial refresh to avoid flashing
"""
import sys
import time
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont

sys.path.insert(0, '/home/sa/tetsuo-display')
from app.display_driver import EPD2in7

def create_time_image(time_text, font):
    """Create image with time text"""
    image = Image.new('1', (176, 264), 255)  # White background
    draw = ImageDraw.Draw(image)

    bbox = draw.textbbox((0, 0), time_text, font=font)
    text_width = bbox[2] - bbox[0]
    text_height = bbox[3] - bbox[1]

    # Bottom center
    x_pos = (176 - text_width) // 2
    y_pos = 264 - text_height - 10

    draw.text((x_pos, y_pos), time_text, font=font, fill=0)

    return image

def image_to_buffer(image):
    """Convert image to buffer"""
    buf = [0xFF] * (int(176 / 8) * 264)
    image_mono = image.convert('1')
    pixels = image_mono.load()

    for y in range(264):
        for x in range(176):
            if pixels[x, y] == 0:
                buf[int((x + y * 176) / 8)] &= ~(0x80 >> (x % 8))

    return bytes(buf)

def main():
    print("Starting smooth clock...")

    # Initialize display
    epd = EPD2in7()

    # First time: full refresh
    epd.init('full')

    # Load font
    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 40)
    except:
        font = ImageFont.load_default()

    # Show initial time with full refresh
    now = datetime.now()
    time_text = now.strftime("%H:%M")
    print(f"Initial time: {time_text}")

    image = create_time_image(time_text, font)
    buffer = image_to_buffer(image)
    epd.display_frame(buffer)
    epd.refresh('full')

    last_minute = now.minute
    full_refresh_counter = 0

    try:
        while True:
            now = datetime.now()
            current_minute = now.minute

            # Update when minute changes
            if current_minute != last_minute:
                time_text = now.strftime("%H:%M")
                print(f"Updating: {time_text}")

                image = create_time_image(time_text, font)
                buffer = image_to_buffer(image)

                # Use partial refresh to avoid flashing
                # Every 10 minutes do a full refresh to clear ghosting
                full_refresh_counter += 1
                if full_refresh_counter >= 10:
                    print("  (full refresh)")
                    epd.init('full')
                    epd.display_frame(buffer)
                    epd.refresh('full')
                    full_refresh_counter = 0
                else:
                    print("  (partial refresh)")
                    epd.display_frame(buffer)
                    epd.refresh('partial')

                last_minute = current_minute

            # Check every 10 seconds
            time.sleep(10)

    except KeyboardInterrupt:
        print("\nStopping clock...")
        epd.sleep()
        epd.cleanup()

if __name__ == "__main__":
    main()
