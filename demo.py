#!/usr/bin/env python3
"""
TETSUO Display - Live Demo

Simulates the full application without hardware.
Shows what the display would show in real-time.
"""

import sys
import time
from pathlib import Path

# Add app to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import Config
from app.data_fetcher import DataFetcher
from datetime import datetime


def clear_screen():
    """Clear terminal screen."""
    print("\033[2J\033[H", end="")


def draw_display(data, stale_seconds=0):
    """Draw ASCII representation of e-paper display."""

    # Format price
    if data:
        price = data.price_usd
        if price >= 1:
            price_text = f"${price:,.2f}"
        elif price >= 0.01:
            price_text = f"${price:.4f}"
        elif price >= 0.0001:
            price_text = f"${price:.6f}"
        else:
            price_text = f"${price:.8f}"

        if '.' in price_text:
            price_text = price_text.rstrip('0').rstrip('.')
    else:
        price_text = "N/A"

    # Format change
    if data and data.change_24h_pct is not None:
        change = data.change_24h_pct
        arrow = "▲" if change >= 0 else "▼"
        sign = "+" if change >= 0 else ""
        change_text = f"{arrow} {sign}{change:.2f}%"
    else:
        change_text = "N/A"

    # Format volume
    if data and data.volume_24h_usd:
        vol = data.volume_24h_usd
        if vol >= 1_000_000:
            vol_text = f"${vol/1_000_000:.2f}M"
        elif vol >= 1_000:
            vol_text = f"${vol/1_000:.2f}K"
        else:
            vol_text = f"${vol:,.2f}"
    else:
        vol_text = "N/A"

    # Format liquidity
    if data and data.liquidity_usd:
        liq = data.liquidity_usd
        if liq >= 1_000_000:
            liq_text = f"${liq/1_000_000:.2f}M"
        elif liq >= 1_000:
            liq_text = f"${liq/1_000:.2f}K"
        else:
            liq_text = f"${liq:,.2f}"
    elif data and data.fdv_usd:
        fdv = data.fdv_usd
        if fdv >= 1_000_000:
            liq_text = f"FDV ${fdv/1_000_000:.2f}M"
        elif fdv >= 1_000:
            liq_text = f"FDV ${fdv/1_000:.2f}K"
        else:
            liq_text = f"FDV ${fdv:,.2f}"
    else:
        liq_text = "N/A"

    # Status
    if stale_seconds > 0:
        if stale_seconds < 60:
            status = f"STALE {stale_seconds}s"
        else:
            mins = stale_seconds // 60
            secs = stale_seconds % 60
            status = f"STALE {mins}m{secs}s"
    else:
        status = "LIVE"

    # Current time
    current_time = datetime.now().strftime("%H:%M")

    # Data source
    source = data.source if data else "none"

    # Draw display
    clear_screen()
    print("╔════════════════════════════════════════════════════════════╗")
    print("║                  TETSUO E-PAPER DISPLAY                    ║")
    print("║              (Simulated - No Hardware Needed)              ║")
    print("╚════════════════════════════════════════════════════════════╝")
    print()
    print("┌────────────────────────────────────────────────────────────┐")
    print("│ TETSUO (SOL)                                               │")
    print("├────────────────────────────────────────────────────────────┤")
    print(f"│                                                            │")
    print(f"│   {price_text:<30} {change_text:>27}│")
    print(f"│                                                            │")
    print("├────────────────────────────────────────────────────────────┤")
    print(f"│ Vol 24h: {vol_text:<47}│")
    print(f"│ Liq:     {liq_text:<47}│")
    print("├────────────────────────────────────────────────────────────┤")
    print(f"│ {current_time:<30} {status:>28}│")
    print("└────────────────────────────────────────────────────────────┘")
    print()
    print(f"Source: {source}")
    print()
    print("Press Ctrl+C to stop")


def main():
    """Run the demo."""
    print("TETSUO Display - Live Demo")
    print("=" * 60)
    print()
    print("Initializing...")

    try:
        # Load config
        config = Config('config.yaml')
        fetcher = DataFetcher(config)

        print(f"Token: {config.token_symbol} ({config.token_chain})")
        print(f"Mint: {config.token_mint}")
        print()
        print("Starting display simulation...")
        print("(Updates every 10s in demo mode)")
        time.sleep(2)

        # Main loop
        while True:
            try:
                # Fetch data
                data, stale_for = fetcher.fetch_with_cache()

                # Draw display
                draw_display(data, stale_for)

                # Wait before next update (10s in demo, would be 45s in production)
                time.sleep(10)

            except Exception as e:
                print(f"\n\nError fetching data: {e}")
                print("Will retry in 10 seconds...")
                time.sleep(10)

    except KeyboardInterrupt:
        clear_screen()
        print("\n\n" + "=" * 60)
        print("Demo stopped by user")
        print("=" * 60)
        print()
        print("Summary:")
        print("  ✓ Configuration loaded")
        print("  ✓ API data fetched")
        print("  ✓ Display rendered")
        print()
        print("This demo simulates what you'll see on the e-paper display")
        print("when deployed to Raspberry Pi.")
        print()
        print("Next steps:")
        print("  1. Transfer project to Raspberry Pi")
        print("  2. Run: python3 scripts/wizard.py")
        print("  3. Display will show TETSUO price 24/7")
        print()

    except Exception as e:
        print(f"\n\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
