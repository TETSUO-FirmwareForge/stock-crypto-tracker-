#!/bin/bash
cd ~/tetsuo-lcd

# Backup and check line 223
python3 << 'CHECK'
with open('app/lcd_renderer.py', 'r') as f:
    lines = f.readlines()
    print(f"Total lines: {len(lines)}")
    if len(lines) >= 223:
        print(f"Line 223: {repr(lines[222])}")
        print(f"Line 222: {repr(lines[221])}")
        print(f"Line 224: {repr(lines[223])}")
CHECK

# Fix by removing all malformed _render_price_view and adding clean one
python3 << 'FIXPYTHON'
# Read file
with open('app/lcd_renderer.py', 'r') as f:
    content = f.read()

# Remove everything from first _render_price_view to return img
import re

# Find the class and preserve everything before _render_price_view
parts = content.split('def _render_price_view', 1)
if len(parts) == 2:
    before_method = parts[0]
    
    # Find the next method after _render_price_view (should be _render_stats_view or similar)
    remaining = parts[1]
    
    # Find where the next method starts (look for 'def ' at the class level indentation)
    next_method_match = re.search(r'\n    def [^_]', remaining)
    if next_method_match:
        after_position = next_method_match.start()
        after_methods = remaining[after_position:]
    else:
        # Try to find any next method
        next_method_match = re.search(r'\n    def ', remaining)
        if next_method_match:
            after_position = next_method_match.start()
            after_methods = remaining[after_position:]
        else:
            after_methods = ''
    
    # Clean method definition
    clean_method = '''def _render_price_view(self, data, stale_seconds: int):
        """Horizontal layout for 128x128 display."""
        img = Image.new('RGB', (128, 128), (0, 0, 10))
        draw = ImageDraw.Draw(img)
        
        # Top bar
        draw.rectangle([0, 0, 128, 18], fill=(0, 30, 60))
        draw.text((4, 2), "TETSUO", font=self.fonts['small'], fill=(255, 255, 100))
        
        # Status dot
        if stale_seconds == 0:
            dot_color = (0, 255, 0)
        else:
            dot_color = (255, 100, 0)
        draw.ellipse([108, 4, 116, 12], fill=dot_color)
        
        if data:
            # Price
            price = data.price_usd
            if price >= 0.01:
                price_text = f"${price:.4f}"
            else:
                price_text = f"${price:.6f}"
            
            # Price box
            draw.rectangle([4, 22, 124, 52], fill=(10, 10, 30), outline=(40, 40, 80))
            draw.text((20, 28), price_text, font=self.fonts['large'], fill=(255, 255, 0))
            
            # Change indicator
            if data.change_24h_pct is not None:
                change = data.change_24h_pct
                if change > 0:
                    arrow, bg, fg = "▲", (0, 60, 0), (100, 255, 100)
                    txt = f"+{change:.1f}%"
                else:
                    arrow, bg, fg = "▼", (60, 0, 0), (255, 100, 100)
                    txt = f"{change:.1f}%"
                
                draw.rectangle([4, 56, 124, 76], fill=bg)
                draw.text((30, 60), f"{arrow} {txt}", font=self.fonts['medium'], fill=fg)
        
        # Time footer
        draw.text((45, 112), datetime.now().strftime("%H:%M"), font=self.fonts['small'], fill=(150, 150, 200))
        
        return img

    '''
    
    # Reconstruct
    new_content = before_method + clean_method + after_methods
    
    # Write back
    with open('app/lcd_renderer.py', 'w') as f:
        f.write(new_content)
    
    print("Renderer fixed!")
else:
    print("Could not split file")
FIXPYTHON

# Test import
python3 -c "from app.lcd_renderer import LCDRenderer; print('Import OK!')"

# Run
sudo python3 main_lcd.py
