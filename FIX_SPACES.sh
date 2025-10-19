#!/bin/bash
cd ~/tetsuo-lcd

# Fix the exact indentation problem at line 223
python3 << 'PYFIX'
with open('app/lcd_renderer.py', 'r') as f:
    lines = f.readlines()

# Fix line 223 - remove extra indentation
if len(lines) >= 223:
    # Line 223 has 16 spaces, should have 4
    lines[222] = lines[222].replace('                def _render_price_view', '    def _render_price_view')

with open('app/lcd_renderer.py', 'w') as f:
    f.writelines(lines)

print("Fixed line 223!")
PYFIX

# Verify
python3 -c "from app.lcd_renderer import LCDRenderer; print('✓ Import works!')" && sudo python3 main_lcd.py
