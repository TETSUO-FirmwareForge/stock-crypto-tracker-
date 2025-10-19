# TETSUO Display - Deployment Checklist

Step-by-step deployment guide for Raspberry Pi Zero 2 W.

## Pre-Deployment Checklist

### Hardware
- [ ] Raspberry Pi Zero 2 W
- [ ] MicroSD card (8GB+) with Pi OS Lite installed
- [ ] Waveshare 2.7" e-Paper HAT (264×176)
- [ ] Power supply (5V 2A recommended)
- [ ] (Optional) Case for protection

### Network
- [ ] Wi-Fi credentials configured
- [ ] SSH enabled on Pi
- [ ] Know Pi's IP address

### Software
- [ ] Pi OS Lite (64-bit recommended) installed and updated
- [ ] Python 3 available (pre-installed on Pi OS)
- [ ] SPI interface enabled in raspi-config

### Accounts (Optional)
- [ ] Birdeye API key (optional, for fallback redundancy)

## Deployment Steps

### Step 1: Prepare the Pi

```bash
# SSH into your Pi
ssh pi@<PI_IP_ADDRESS>

# Update system
sudo apt update && sudo apt upgrade -y

# Install required packages
sudo apt install python3 python3-pip python3-venv git -y

# Enable SPI if not already enabled
sudo raspi-config
# Navigate to: Interface Options → SPI → Enable
# Reboot if prompted
```

### Step 2: Clone and Setup Project

```bash
# Clone repository
cd ~
git clone <YOUR_REPO_URL> tetsuo-display
cd tetsuo-display

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install --upgrade pip
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env if you have a Birdeye API key
nano .env
# Add: BIRDEYE_API_KEY=your_key_here
# Save: Ctrl+O, Enter, Ctrl+X
```

### Step 4: Run Setup Wizard

```bash
# Ensure venv is activated
source venv/bin/activate

# Run wizard
python3 scripts/wizard.py
```

**Wizard will guide you through:**
1. SPI verification
2. GPIO pin confirmation
3. Trading pair resolution (finds best TETSUO/SOL pair)
4. Birdeye API key setup (optional)
5. API source testing
6. Display hardware test (shows test pattern)
7. Systemd service installation

**Answer prompts:**
- Confirm SPI is enabled → Yes
- GPIO pins correct → Yes (unless custom HAT)
- Use discovered pair → Yes
- Have Birdeye key → Yes/No (based on your setup)
- Run display test → Yes
- Install service → Yes
- Start service now → Yes

### Step 5: Verify Deployment

```bash
# Check service status
sudo systemctl status tetsuo-display

# Should show:
# ● tetsuo-display.service - TETSUO E-Paper Display
#    Loaded: loaded
#    Active: active (running)

# View live logs
sudo journalctl -u tetsuo-display -f

# Should see:
# Starting TETSUO display...
# Token: TETSUO (solana)
# [HH:MM:SS] Fetching data...
#   Price: $0.00123456
#   Display updated
```

### Step 6: Physical Check

**Look at the e-paper display. You should see:**

- [ ] "TETSUO (SOL)" header
- [ ] Current price in USD
- [ ] 24h change percentage with ▲/▼ arrow
- [ ] Volume 24h and Liquidity
- [ ] Current time (bottom left)
- [ ] "LIVE" indicator (bottom right)

**The display should:**
- [ ] Update every ~45 seconds (watch logs)
- [ ] Show price changes
- [ ] Full refresh (screen "blinks") occasionally

## Post-Deployment Validation

### Functional Tests

#### Test 1: Service Auto-Start
```bash
# Reboot Pi
sudo reboot

# Wait 30 seconds, then SSH back in
ssh pi@<PI_IP_ADDRESS>

# Check service started automatically
sudo systemctl status tetsuo-display
# Should be active (running)
```

#### Test 2: Network Recovery
```bash
# Disconnect Wi-Fi (disable router or Pi Wi-Fi)
# Wait 2-3 minutes
# Check display shows "STALE" with elapsed time

# Reconnect Wi-Fi
# Within 45-60 seconds:
# - Logs should show "Fetching data..."
# - Display should update to "LIVE"
```

#### Test 3: API Fallback
```bash
# Run smoke test to verify all sources work
cd ~/tetsuo-display
source venv/bin/activate
python3 tests/smoke_test.py

# Should show 3-4 sources working
```

#### Test 4: Manual Restart
```bash
# Stop service
sudo systemctl stop tetsuo-display

# Verify display powered down

# Start service
sudo systemctl start tetsuo-display

# Verify:
# - Service starts
# - Cached data appears immediately
# - Fresh data fetches within 45s
```

### Performance Checks

```bash
# Check memory usage
free -h
# Display app should use ~50-80MB

# Check CPU usage
top -bn1 | grep python3
# Should be <5% most of the time

# Check logs for errors
sudo journalctl -u tetsuo-display -p err -n 50
# Should be no errors (or only transient network errors)

# Check cache file
ls -lh ~/tetsuo-display/data/
cat ~/tetsuo-display/data/last_snapshot.json
# Should contain valid JSON with recent timestamp
```

## Configuration Tuning

### Adjust Poll Interval

```bash
nano ~/tetsuo-display/config.yaml

# Change:
poll:
  interval_seconds: 45  # Change to 30 for faster updates, 60 for slower

# Restart service
sudo systemctl restart tetsuo-display
```

### Adjust Refresh Cadence

```bash
nano ~/tetsuo-display/config.yaml

# Change:
refresh:
  full_every_minutes: 45  # Decrease if seeing ghosting
  full_after_partials: 60 # Or adjust count threshold

# Restart service
sudo systemctl restart tetsuo-display
```

### Enable/Disable Data Sources

```bash
nano ~/tetsuo-display/config.yaml

# Change fallback order:
fallback:
  order:
    - dexscreener_pair
    - dexscreener_token
    # - birdeye          # Comment out to disable
    - geckoterminal

# Restart service
sudo systemctl restart tetsuo-display
```

## Troubleshooting

### Service Won't Start

```bash
# Check logs
sudo journalctl -u tetsuo-display -n 50 --no-pager

# Common issues:
# 1. SPI not enabled → sudo raspi-config
# 2. Missing dependencies → pip install -r requirements.txt
# 3. Wrong paths in service file → check WorkingDirectory in .service
# 4. Permission issues → check file ownership
```

### Display Shows Nothing

```bash
# Test display directly
cd ~/tetsuo-display
source venv/bin/activate
python3 tests/display_test.py

# If test fails:
# 1. Check HAT is firmly seated on GPIO pins
# 2. Verify GPIO pin numbers in config.yaml
# 3. Check SPI is enabled: ls /dev/spidev*
# 4. Check wiring if not using standard HAT
```

### No Data / API Errors

```bash
# Test API sources
python3 tests/smoke_test.py

# If all fail:
# 1. Check internet: ping 8.8.8.8
# 2. Check DNS: nslookup api.dexscreener.com
# 3. Check primary pair is set in config.yaml
# 4. Re-run wizard to resolve pair
```

### Display Shows Stale Data

```bash
# Check network
ping api.dexscreener.com

# Check logs for API errors
sudo journalctl -u tetsuo-display -n 100 | grep -i error

# Common causes:
# 1. No internet connection
# 2. API rate limits (adjust poll interval)
# 3. Invalid API key (Birdeye)
# 4. Pair address changed (re-run wizard)
```

## Maintenance Commands

```bash
# View logs (live)
sudo journalctl -u tetsuo-display -f

# View logs (last 100 lines)
sudo journalctl -u tetsuo-display -n 100

# Restart service
sudo systemctl restart tetsuo-display

# Stop service
sudo systemctl stop tetsuo-display

# Start service
sudo systemctl start tetsuo-display

# Disable auto-start
sudo systemctl disable tetsuo-display

# Enable auto-start
sudo systemctl enable tetsuo-display

# Update code
cd ~/tetsuo-display
git pull
source venv/bin/activate
pip install -r requirements.txt
sudo systemctl restart tetsuo-display

# Re-run wizard
cd ~/tetsuo-display
source venv/bin/activate
python3 scripts/wizard.py
```

## Monitoring

### Set Up Log Rotation (Optional)

```bash
sudo nano /etc/systemd/journald.conf

# Set:
SystemMaxUse=100M
MaxRetentionSec=1week

sudo systemctl restart systemd-journald
```

### Create Health Check Script (Optional)

```bash
cat > ~/check_display.sh << 'EOF'
#!/bin/bash
if systemctl is-active --quiet tetsuo-display; then
  echo "✓ Service running"
  exit 0
else
  echo "✗ Service down"
  exit 1
fi
EOF

chmod +x ~/check_display.sh

# Add to crontab for alerts
crontab -e
# Add: */15 * * * * ~/check_display.sh || echo "Display down!" | mail -s "Alert" your@email.com
```

## Security Hardening (Optional)

```bash
# Limit service permissions
sudo nano /etc/systemd/system/tetsuo-display.service

# Add under [Service]:
NoNewPrivileges=true
PrivateTmp=true
ProtectSystem=strict
ProtectHome=true
ReadWritePaths=/home/pi/tetsuo-display/data

sudo systemctl daemon-reload
sudo systemctl restart tetsuo-display
```

## Backup Configuration

```bash
# Backup config and cache
tar -czf tetsuo-backup-$(date +%Y%m%d).tar.gz \
  ~/tetsuo-display/config.yaml \
  ~/tetsuo-display/.env \
  ~/tetsuo-display/data/

# Restore if needed
tar -xzf tetsuo-backup-YYYYMMDD.tar.gz -C ~/
```

## Success Criteria

Your deployment is successful when:

- [ ] Service shows "active (running)"
- [ ] Logs show regular "Display updated" messages
- [ ] E-paper displays current TETSUO price
- [ ] Price updates automatically every ~45s
- [ ] Display survives reboot (auto-starts)
- [ ] Display shows "STALE" during network outage and recovers
- [ ] Full refresh happens periodically (screen blinks)
- [ ] No recurring errors in logs

## Support

- **Documentation**: See README.md for detailed info
- **Quick fixes**: See QUICKSTART.md
- **Architecture**: See PROJECT_OVERVIEW.md
- **Re-configure**: Run `python3 scripts/wizard.py`
- **Test APIs**: Run `python3 tests/smoke_test.py`
- **Test hardware**: Run `python3 tests/display_test.py`

---

**Deployment Complete!**

Your TETSUO display is now running 24/7, showing real-time token data with automatic fallback and recovery. Enjoy!
