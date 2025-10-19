#!/bin/bash
cd ~/tetsuo-lcd

# Stop monitor
sudo pkill -f main_lcd.py

# Add backlight
python3 << 'PY1'
with open('app/lcd_driver_st7735.py', 'r') as f: c = f.read()
if 'def set_backlight' not in c:
    p = c.find('def cleanup')
    if p > 0:
        c = c[:p] + '    def set_backlight(self, s):\n        if not HAS_HARDWARE: return\n        try: GPIO.output(self.bl_pin, GPIO.HIGH if s else GPIO.LOW)\n        except: pass\n\n' + c[p:]
        with open('app/lcd_driver_st7735.py', 'w') as f: f.write(c)
print("OK1")
PY1

# Fix horizontal layout
python3 << 'PY2'
import re
with open('app/lcd_renderer.py', 'r') as f: content = f.read()
new = '''    def _render_price_view(self, data, stale_seconds: int):
        img = Image.new('RGB', (128, 128), (0, 0, 10))
        draw = ImageDraw.Draw(img)
        draw.rectangle([0,0,128,18], fill=(0,30,60))
        draw.text((4,2), "TETSUO", font=self.fonts['small'], fill=(255,255,100))
        if data:
            p = f"${data.price_usd:.4f}" if data.price_usd >= 0.01 else f"${data.price_usd:.6f}"
            draw.rectangle([4,22,124,52], fill=(10,10,30))
            draw.text((20,28), p, font=self.fonts['large'], fill=(255,255,0))
            if data.change_24h_pct:
                c = data.change_24h_pct
                a = "▲" if c > 0 else "▼"
                bg = (0,60,0) if c > 0 else (60,0,0)
                fg = (100,255,100) if c > 0 else (255,100,100)
                draw.rectangle([4,56,124,76], fill=bg)
                draw.text((30,60), f"{a} {c:.1f}%", font=self.fonts['medium'], fill=fg)
        draw.text((45,112), datetime.now().strftime("%H:%M"), font=self.fonts['small'], fill=(150,150,200))
        return img'''
content = re.sub(r'def _render_price_view.*?return img', new, content, flags=re.DOTALL)
with open('app/lcd_renderer.py', 'w') as f: f.write(content)
print("OK2")
PY2

# Run
sudo python3 main_lcd.py
