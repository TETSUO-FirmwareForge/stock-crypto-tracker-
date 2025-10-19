# TETSUO Display - Quick Start Guide

This guide will get your TETSUO e-paper display running in under 10 minutes.

## Prerequisites

- Raspberry Pi Zero 2 W (or any Pi)
- Waveshare 2.7" e-Paper HAT connected
- Pi OS Lite installed
- Internet connection

## Installation (5 steps)

### 1. Clone the repository

```bash
cd ~
git clone <YOUR_REPO_URL> tetsuo-display
cd tetsuo-display
```

### 2. Create Python environment

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3. Copy environment template

```bash
cp .env.example .env
# Edit .env to add your Birdeye API key (optional)
nano .env
```

### 4. Run the setup wizard

```bash
python3 scripts/wizard.py
```

The wizard will:
- Check SPI is enabled
- Verify GPIO pins
- Find the best trading pair
- Test API connections
- Display a test pattern
- Install the systemd service

### 5. Start the service

If the wizard installed the service:

```bash
sudo systemctl start tetsuo-display
```

Otherwise, run manually:

```bash
python3 app/main.py
```

## Verify It's Working

Check the service status:

```bash
sudo systemctl status tetsuo-display
```

View live logs:

```bash
sudo journalctl -u tetsuo-display -f
```

You should see:
- "Starting TETSUO display..."
- "Fetching data..."
- "Display updated"

## Troubleshooting

### SPI Not Enabled

```bash
sudo raspi-config
# Interface Options → SPI → Enable
sudo reboot
```

### Display Shows Nothing

1. Check connections (HAT should be firmly seated on GPIO pins)
2. Verify GPIO pins in `config.yaml` match your HAT
3. Run hardware test: `python3 tests/display_test.py`

### No Data / API Errors

1. Check internet connection: `ping 8.8.8.8`
2. Test API sources: `python3 tests/smoke_test.py`
3. Verify primary pair is set in `config.yaml`

### Service Won't Start

```bash
# Check logs for errors
sudo journalctl -u tetsuo-display -n 50

# Try running manually to see errors
source venv/bin/activate
python3 app/main.py
```

## Common Commands

```bash
# Service management
sudo systemctl start tetsuo-display
sudo systemctl stop tetsuo-display
sudo systemctl restart tetsuo-display
sudo systemctl status tetsuo-display

# View logs
sudo journalctl -u tetsuo-display -f    # Follow logs
sudo journalctl -u tetsuo-display -n 50 # Last 50 lines

# Manual run
source venv/bin/activate
python3 app/main.py

# Test pattern
python3 app/main.py --test-pattern

# Test APIs
python3 tests/smoke_test.py

# Generate layout previews
python3 tests/layout_proof.py
```

## Configuration

Edit `config.yaml` to adjust:

- `poll.interval_seconds`: How often to fetch data (default: 45s)
- `refresh.full_every_minutes`: Full refresh interval (default: 45min)
- `display.gpio.*`: GPIO pin numbers if different HAT

After editing config:

```bash
sudo systemctl restart tetsuo-display
```

## Next Steps

- Customize the display layout: edit `app/renderer.py`
- Add more data sources: edit `app/data_fetcher.py`
- Adjust polling frequency: edit `config.yaml`
- Set up boot monitoring: `sudo systemctl enable tetsuo-display`

## Getting Help

- Check `README.md` for detailed documentation
- Run `python3 scripts/wizard.py` again to reconfigure
- Review logs: `sudo journalctl -u tetsuo-display`

## Success Indicators

You'll know it's working when:

1. Service status shows "active (running)"
2. Logs show "Display updated" every 45 seconds
3. E-paper shows current TETSUO price
4. Price updates automatically
5. After network drops, shows "STALE" indicator
6. Full refresh happens every 45 minutes (screen "blinks")

Enjoy your TETSUO display!
