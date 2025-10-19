#!/bin/bash
cd ~/tetsuo-lcd

echo "Fixing all indentation errors..."

# Fix driver line 502
python3 << 'FIX1'
with open('app/lcd_driver_st7735.py', 'r') as f:
    lines = f.readlines()

# Find and fix line 502
for i in range(len(lines)):
    if i == 501:  # Line 502 (0-indexed)
        # Make sure it has proper indentation
        lines[i] = '        ' + lines[i].lstrip()

with open('app/lcd_driver_st7735.py', 'w') as f:
    f.writelines(lines)

print("✓ Fixed driver")
FIX1

# Verify both imports
python3 << 'TEST'
try:
    from app.lcd_driver_st7735 import ST7735
    print("✓ Driver imports OK")
except Exception as e:
    print(f"✗ Driver error: {e}")

try:
    from app.lcd_renderer import LCDRenderer
    print("✓ Renderer imports OK")
except Exception as e:
    print(f"✗ Renderer error: {e}")
TEST

echo ""
echo "Starting monitor..."
sudo python3 main_lcd.py
