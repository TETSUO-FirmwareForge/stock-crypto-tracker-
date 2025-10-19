# 👋 START HERE

Welcome to the TETSUO E-Paper Display project!

## What Is This?

A complete, production-ready application that displays real-time **$TETSUO** token price and stats on a Waveshare 2.7" e-paper display attached to a Raspberry Pi Zero 2 W.

## What You Got

A fully-functional headless crypto display with:

- **Multi-source data fetching** with automatic fallback
- **Smart e-paper refresh** (partial for speed, full for ghosting prevention)
- **Network resilience** (survives Wi-Fi drops, shows stale indicator)
- **Auto-start on boot** (systemd service)
- **Interactive setup wizard** (handles everything)
- **Complete test suite** (test without hardware)
- **Comprehensive docs** (5 documentation files)

## Quick Navigation

### I want to deploy this right now
→ Read **QUICKSTART.md** (10 minutes to running display)

### I want step-by-step deployment instructions
→ Read **DEPLOY.md** (complete deployment checklist)

### I want to understand how it works
→ Read **PROJECT_OVERVIEW.md** (architecture & design)

### I need the full documentation
→ Read **README.md** (complete reference)

### I want to see the project structure
→ Read **STRUCTURE.txt** or **SUMMARY.txt**

## Fastest Path to Running Display

**If you have a Raspberry Pi with the display already:**

1. Copy this folder to your Pi:
   ```bash
   scp -r tetsuo-display/ pi@<PI_IP>:~/
   ```

2. SSH to Pi and run:
   ```bash
   cd ~/tetsuo-display
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 scripts/wizard.py
   ```

3. Answer the wizard's questions, and you're done!

The wizard handles:
- ✓ SPI verification
- ✓ GPIO pin check
- ✓ Trading pair resolution
- ✓ API testing
- ✓ Display test
- ✓ Service installation

## Project Structure

```
tetsuo-display/
├── 📖 START_HERE.md          ← You are here
├── 📖 QUICKSTART.md           ← 10-minute setup
├── 📖 DEPLOY.md               ← Deployment checklist
├── 📖 README.md               ← Full documentation
├── 📖 PROJECT_OVERVIEW.md     ← Architecture details
├── 📖 SUMMARY.txt             ← What was built
│
├── 🔧 app/                    ← Core application (7 files)
├── 🎯 scripts/wizard.py       ← Setup wizard
├── 🧪 tests/                  ← Test suite (3 tests)
├── ⚙️  config.yaml            ← Configuration
└── 🚀 tetsuo-display.service  ← Systemd service
```

## Key Features

**Data Acquisition:**
- 4-tier fallback (Dexscreener → Birdeye → GeckoTerminal)
- Exponential backoff on errors
- Persistent cache

**Display:**
- Partial refresh (fast, minimal flicker)
- Full refresh every 45min (anti-ghosting)
- Clean layout with price, 24h change, volume, liquidity

**Reliability:**
- Survives network outages
- Auto-restarts on failure
- Shows "STALE" indicator when offline
- Auto-recovers when online

## What You Need

**Hardware:**
- Raspberry Pi Zero 2 W (or any Pi)
- Waveshare 2.7" e-Paper HAT (264×176)
- MicroSD card with Pi OS Lite
- Power supply

**Optional:**
- Birdeye API key (for extra data source redundancy)

## First-Time Setup

1. **Prepare Pi:**
   - Install Pi OS Lite
   - Enable SPI (`sudo raspi-config`)
   - Connect to Wi-Fi
   - Enable SSH

2. **Copy project to Pi**

3. **Run wizard** (it does everything):
   ```bash
   python3 scripts/wizard.py
   ```

4. **Verify**:
   ```bash
   sudo systemctl status tetsuo-display
   ```

Done! Your display will now show TETSUO price and auto-update.

## Testing Without Hardware

You can test the APIs and layout without a Raspberry Pi:

```bash
# Test all API sources
python3 tests/smoke_test.py

# Generate PNG layout previews
python3 tests/layout_proof.py
```

## Common Questions

**Q: Do I need to code anything?**
A: No! Everything is ready to run. Just configure via `config.yaml` or the wizard.

**Q: What if I want to display a different token?**
A: Edit `config.yaml` → change `token.mint`, run wizard to resolve new pair.

**Q: Can I customize the layout?**
A: Yes! Edit `app/renderer.py` → adjust zones, fonts, labels.

**Q: Does it work without internet?**
A: It shows cached data with a "STALE" indicator until internet returns.

**Q: How do I update the price faster?**
A: Edit `config.yaml` → decrease `poll.interval_seconds` (min ~30s).

**Q: The screen is ghosting (image retention)?**
A: Edit `config.yaml` → decrease `refresh.full_every_minutes`.

## Getting Help

- **Setup issues:** Check QUICKSTART.md troubleshooting
- **Deployment:** See DEPLOY.md checklist
- **Configuration:** See README.md
- **Architecture:** See PROJECT_OVERVIEW.md

## What's Included

- ✅ ~2,800 lines of Python code
- ✅ 7 core modules
- ✅ Interactive setup wizard
- ✅ 3 test scripts
- ✅ Systemd service
- ✅ 5 documentation files
- ✅ MIT license

## Success Indicators

You'll know it's working when:

1. Service shows "active (running)"
2. Logs show "Display updated" every 45s
3. E-paper displays current TETSUO price
4. Price updates automatically
5. Shows "STALE" during outages and recovers

## Next Steps

Choose your path:

- **Quick deployment** → QUICKSTART.md
- **Careful deployment** → DEPLOY.md
- **Understanding first** → PROJECT_OVERVIEW.md
- **Full reference** → README.md

---

## Support

This is a complete, production-ready implementation. All features from the requirements are implemented and tested.

If you need to customize:
- Token → Edit `config.yaml`
- Layout → Edit `app/renderer.py`
- Timing → Edit `config.yaml`
- Data sources → Edit `app/data_fetcher.py`

**Ready to deploy?** → Go to QUICKSTART.md or DEPLOY.md

**Have questions?** → Check README.md

---

**Status: Production Ready**
**Version: 1.0.0**
**License: MIT**

Enjoy your TETSUO display! 🚀
