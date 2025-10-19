#!/bin/bash
cd ~/tetsuo-lcd

# Fix indentation error
python3 << 'PYFIX'
# Read the file
with open('app/lcd_renderer.py', 'r') as f:
    lines = f.readlines()

# Find and remove duplicate _render_price_view definitions
new_lines = []
skip_until_next_def = False
found_first = False

for i, line in enumerate(lines):
    if 'def _render_price_view' in line:
        if not found_first:
            found_first = True
            new_lines.append(line)
        else:
            # Skip duplicate definition
            skip_until_next_def = True
            continue
    elif skip_until_next_def:
        if line.strip().startswith('def ') and not line.startswith('        '):
            skip_until_next_def = False
            new_lines.append(line)
    else:
        new_lines.append(line)

# Write back
with open('app/lcd_renderer.py', 'w') as f:
    f.writelines(new_lines)

print("Indentation fixed!")
PYFIX

# Now run the monitor
sudo python3 main_lcd.py
