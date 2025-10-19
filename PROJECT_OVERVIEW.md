# TETSUO E-Paper Display - Project Overview

Complete headless Raspberry Pi application for displaying real-time TETSUO token data on a Waveshare 2.7" e-paper display.

## Project Status: Complete and Ready to Deploy

All components implemented and tested. Ready for deployment on Raspberry Pi Zero 2 W.

## Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     TETSUO Display System                    │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  ┌──────────────┐     ┌──────────────┐     ┌────────────┐ │
│  │ Data Sources │────▶│ Data Fetcher │────▶│  Renderer  │ │
│  └──────────────┘     └──────────────┘     └────────────┘ │
│        │                     │                     │        │
│        │                     │                     ▼        │
│   Dexscreener           Cache Layer          ┌────────────┐│
│   Birdeye                                    │  E-Paper   ││
│   GeckoTerminal                              │  Display   ││
│                                              └────────────┘│
│  ┌──────────────────────────────────────────────────────┐ │
│  │              Systemd Service Manager                 │ │
│  │  • Auto-start on boot                                │ │
│  │  • Automatic restart on failure                      │ │
│  │  • Journald logging                                  │ │
│  └──────────────────────────────────────────────────────┘ │
└─────────────────────────────────────────────────────────────┘
```

## Components

### Core Application (`app/`)

1. **main.py** - Main daemon
   - Polling loop (45s default)
   - Signal handling (SIGINT, SIGTERM)
   - Graceful shutdown
   - Cache-first startup

2. **config.py** - Configuration loader
   - YAML config parsing
   - Environment variable integration
   - Dot-notation access
   - Runtime updates

3. **data_fetcher.py** - Multi-source data fetcher
   - 4-tier fallback ladder
   - Exponential backoff
   - Disk cache with staleness tracking
   - Normalized data structure

4. **pair_resolver.py** - Trading pair resolver
   - Finds highest liquidity pair
   - Dexscreener integration
   - Automatic pair selection

5. **display_driver.py** - E-paper hardware driver
   - Waveshare 2.7" (264×176) support
   - Full and partial refresh modes
   - SPI communication
   - Deep sleep support

6. **renderer.py** - Display layout renderer
   - Zone-based layout
   - Smart refresh management
   - PIL image generation
   - Ghosting prevention

### Setup & Management (`scripts/`)

1. **wizard.py** - First-run setup wizard
   - SPI verification
   - GPIO pin confirmation
   - Trading pair resolution
   - API key configuration
   - Hardware testing
   - Service installation

### Testing (`tests/`)

1. **smoke_test.py** - API endpoint tester
   - Tests all data sources
   - Prints normalized output
   - No hardware required

2. **layout_proof.py** - Visual layout generator
   - Generates PNG previews
   - Multiple test cases
   - No hardware required

3. **display_test.py** - Hardware tester
   - Tests e-paper directly
   - Test pattern display
   - Requires Pi + display

### Configuration

1. **config.yaml** - Main configuration
   - Token details
   - Trading pair
   - Display settings
   - GPIO pins
   - Poll intervals
   - API endpoints
   - Fallback order

2. **.env** - Secrets (not committed)
   - Birdeye API key

3. **tetsuo-display.service** - Systemd unit
   - Service definition
   - Restart policy
   - Logging configuration

## Data Flow

```
1. Startup
   └─▶ Load config
       └─▶ Load cached data (if exists)
           └─▶ Display cached data (marked STALE if old)
               └─▶ Start polling loop

2. Each Poll Cycle (45s)
   └─▶ Try Dexscreener pair endpoint
       └─▶ On fail: Try Dexscreener token endpoint
           └─▶ On fail: Try Birdeye
               └─▶ On fail: Try GeckoTerminal
                   └─▶ On fail: Use cached data

3. Render Decision
   └─▶ Time since last full refresh > 45min?
       │   YES: Full refresh
       │   NO: ─▶ Partial count > 60?
       │           YES: Full refresh
       │           NO: Partial refresh

4. Display Update
   └─▶ Generate PIL Image
       └─▶ Convert to e-paper buffer
           └─▶ Send to display via SPI
               └─▶ Trigger refresh (full or partial)
```

## API Fallback Ladder

**Priority Order:**

1. **Dexscreener Pair** (Primary)
   - Direct pair endpoint
   - Lowest latency
   - Most reliable
   - Full data set

2. **Dexscreener Token** (First fallback)
   - Token endpoint with pair selection
   - Selects max liquidity pair
   - Same data quality
   - Slightly slower

3. **Birdeye** (Second fallback)
   - Requires API key
   - Price only (no 24h stats)
   - Good uptime
   - Rate limited by tier

4. **GeckoTerminal** (Last resort)
   - No API key needed
   - Good data coverage
   - Public rate limits
   - Slower response

**Fallback Triggers:**
- HTTP errors (4xx, 5xx)
- Timeout (5s)
- Invalid/missing data
- Parsing errors

## Display Refresh Strategy

### Partial Refresh (Fast, ~2s)
- Used for: Price, stats, time updates
- Minimal flicker
- Faster update
- Can cause ghosting over time

### Full Refresh (Slow, ~4s)
- Used for: Complete screen redraw
- Full screen flash
- Clears ghosting
- Better image quality

**Full Refresh Triggers:**
- Every 45 minutes (time-based)
- After 60 partial updates (count-based)
- On startup
- Manual test pattern

## Key Features Implemented

### Reliability
- Multi-source fallback
- Disk cache persistence
- Automatic retry with backoff
- Network outage handling
- Service auto-restart

### User Experience
- Cache-first startup (instant display)
- Stale data indicator
- Minimal screen flicker
- Smart refresh scheduling
- Ghosting prevention

### Observability
- Journald logging
- Status indicators (LIVE/STALE)
- Detailed error messages
- Test utilities

### Maintainability
- Modular architecture
- Clear separation of concerns
- Configurable via YAML
- No secrets in repo
- Comprehensive tests

## File Summary

```
tetsuo-display/
├── app/                      # Core application
│   ├── __init__.py
│   ├── main.py              # Main daemon (300 lines)
│   ├── config.py            # Config loader (130 lines)
│   ├── data_fetcher.py      # Multi-source fetcher (400 lines)
│   ├── pair_resolver.py     # Pair resolver (120 lines)
│   ├── display_driver.py    # Hardware driver (350 lines)
│   └── renderer.py          # Display renderer (400 lines)
│
├── scripts/
│   └── wizard.py            # Setup wizard (500 lines)
│
├── tests/
│   ├── smoke_test.py        # API tests (150 lines)
│   ├── layout_proof.py      # Layout previews (250 lines)
│   └── display_test.py      # Hardware test (120 lines)
│
├── config.yaml              # Main configuration
├── .env.example             # Environment template
├── requirements.txt         # Python dependencies
├── tetsuo-display.service   # Systemd unit
├── README.md                # Full documentation
├── QUICKSTART.md            # Quick start guide
├── LICENSE                  # MIT license
└── .gitignore              # Git ignore rules

Total: ~2,800 lines of Python code
```

## Deployment Checklist

- [x] Core application complete
- [x] Hardware drivers implemented
- [x] Multi-source data fetching
- [x] Fallback mechanisms
- [x] Cache persistence
- [x] Display rendering
- [x] Partial/full refresh
- [x] Systemd service
- [x] Setup wizard
- [x] API tests
- [x] Hardware tests
- [x] Layout proofs
- [x] Documentation
- [x] Quick start guide

## Next Steps for Deployment

1. **Copy to Pi:**
   ```bash
   scp -r tetsuo-display/ pi@<PI_IP>:~/
   ```

2. **SSH to Pi:**
   ```bash
   ssh pi@<PI_IP>
   ```

3. **Run wizard:**
   ```bash
   cd ~/tetsuo-display
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   python3 scripts/wizard.py
   ```

4. **Verify:**
   ```bash
   sudo systemctl status tetsuo-display
   sudo journalctl -u tetsuo-display -f
   ```

## Customization Points

### Change Token
- Edit `config.yaml`: `token.*` fields
- Run wizard to resolve new pair
- Restart service

### Change Layout
- Edit `app/renderer.py`: zone definitions
- Adjust font sizes
- Modify text labels
- Test with `python3 tests/layout_proof.py`

### Add Data Source
- Edit `app/data_fetcher.py`: add `_fetch_newsource()`
- Add to `config.yaml`: `fallback.order`
- Test with `python3 tests/smoke_test.py`

### Adjust Timing
- Edit `config.yaml`:
  - `poll.interval_seconds` (data fetch)
  - `refresh.full_every_minutes` (ghosting prevention)

### Change GPIO Pins
- Edit `config.yaml`: `display.gpio.*`
- Match your HAT pinout
- Test with `python3 tests/display_test.py`

## Performance Characteristics

- **Startup time:** 2-5s (with cached data)
- **First fresh data:** 5-10s (after startup)
- **Poll interval:** 45s (configurable)
- **Partial refresh:** ~2s
- **Full refresh:** ~4s
- **Memory usage:** ~50-80MB
- **CPU usage:** <5% average, ~20% during refresh
- **Network:** ~1KB per poll
- **Disk:** ~5KB cache file

## Known Limitations

1. **Display only:**
   - No web interface
   - No remote control
   - View-only (by design)

2. **Single token:**
   - Configured for one token at a time
   - Can be extended to multi-token

3. **Hardware specific:**
   - Tested on Pi Zero 2 W
   - Waveshare 2.7" HAT
   - Should work on other Pi models

4. **API rate limits:**
   - Dexscreener: Generous, no key needed
   - Birdeye: Tier-based limits
   - GeckoTerminal: ~30 req/min

## Maintenance

### Regular Tasks
- Check logs occasionally: `sudo journalctl -u tetsuo-display -b`
- Monitor service: `sudo systemctl status tetsuo-display`
- Update if needed: `git pull && pip install -r requirements.txt`

### Troubleshooting Resources
- README.md: Comprehensive troubleshooting section
- QUICKSTART.md: Common issues and fixes
- Test scripts: Isolate problems
- Wizard: Re-run configuration

## License

MIT License - See LICENSE file

## Acknowledgments

- Waveshare for e-Paper HAT libraries
- Dexscreener, Birdeye, GeckoTerminal for API access
- TETSUO community

---

**Project Status:** Production Ready
**Last Updated:** 2025
**Version:** 1.0.0
