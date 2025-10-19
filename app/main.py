#!/usr/bin/env python3
"""
TETSUO E-Paper Display - Main Daemon

Continuously fetches and displays TETSUO token data on e-paper.
"""

import sys
import time
import signal
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config
from app.data_fetcher import DataFetcher
from app.renderer import DisplayRenderer
from app.buttons import ButtonHandler


class TetsuoDisplay:
    """Main application controller."""

    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize application.

        Args:
            config_path: Path to configuration file
        """
        self.config = Config(config_path)
        self.fetcher = DataFetcher(self.config)
        self.renderer = DisplayRenderer(self.config)
        self.mode = str(self.config.get("display.mode", "normal")).lower()
        self.buttons = ButtonHandler()
        self.running = False
        self.force_full_refresh = False
        self.manual_refresh_requested = False

        # Register signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        print(f"\nReceived signal {signum}, shutting down...")
        self.running = False

    def _on_force_full_refresh(self):
        """Callback for KEY1: Force full refresh on next update."""
        print("\n[BUTTON] KEY1: Force full refresh requested")
        self.renderer.partial_count = self.renderer.full_refresh_after_partials
        self.manual_refresh_requested = True

    def _on_show_test_pattern(self):
        """Callback for KEY2: Show test pattern."""
        print("\n[BUTTON] KEY2: Showing test pattern")
        try:
            self.renderer.show_test_pattern()
            print("[BUTTON] Test pattern displayed")
        except Exception as e:
            print(f"[BUTTON] Failed to show test pattern: {e}")

    def _on_manual_refresh(self):
        """Callback for KEY4: Trigger immediate data refresh."""
        print("\n[BUTTON] KEY4: Manual refresh requested")
        self.manual_refresh_requested = True

    def start(self):
        """Start the display daemon."""
        print("Starting TETSUO display...")
        print(f"Mode: {self.mode}")
        if self.mode != "blank":
            print(f"Token: {self.config.token_symbol} ({self.config.token_chain})")
            print(f"Mint: {self.config.token_mint}")
            print(f"Poll interval: {self.config.poll_interval}s")

        # Initialize display
        try:
            self.renderer.init()
        except Exception as e:
            print(f"Failed to initialize display: {e}")
            return

        # Initialize buttons unless in blank mode
        if self.mode != "blank":
            try:
                self.buttons.init()
                # Register button callbacks
                self.buttons.on_key1(self._on_force_full_refresh)
                self.buttons.on_key2(self._on_show_test_pattern)
                self.buttons.on_key4(self._on_manual_refresh)
            except Exception as e:
                print(f"Failed to initialize buttons: {e}")
                # Continue without buttons

        # If in blank mode, clear to white and idle
        if self.mode == "blank":
            print("\nBlank mode: clearing display to pure white and idling...")
            try:
                self.renderer.show_blank()
                print("Display set to white. Service will remain idle.")
            except Exception as e:
                print(f"Failed to set blank display: {e}")

            # Idle loop to keep service alive until stopped
            self.running = True
            while self.running:
                time.sleep(60)

            print("\nShutting down blank mode...")
            try:
                self.renderer.shutdown()
            except Exception as e:
                print(f"Error during shutdown: {e}")
            try:
                self.buttons.cleanup()
            except Exception as e:
                print(f"Error cleaning up buttons: {e}")
            print("TETSUO display stopped")
            return

        # Load and display cached data immediately (normal mode)
        print("\nLoading cached data...")
        cached_data, stale_for = self.fetcher.fetch_with_cache()

        if cached_data:
            print(f"Displaying cached data (stale for {stale_for}s)")
            try:
                self.renderer.render(cached_data, stale_for)
            except Exception as e:
                print(f"Failed to render cached data: {e}")
        else:
            print("No cached data available")

        # Main loop
        self.running = True
        poll_interval = self.config.poll_interval

        print(f"\nStarting polling loop (every {poll_interval}s)...")
        print("Press Ctrl+C to stop\n")

        last_poll = 0

        while self.running:
            current_time = time.time()

            # Check if it's time to poll or if manual refresh requested
            should_poll = (current_time - last_poll >= poll_interval) or self.manual_refresh_requested

            if should_poll:
                try:
                    self._poll_and_update()
                    last_poll = current_time
                    self.manual_refresh_requested = False

                except Exception as e:
                    print(f"Error in poll cycle: {e}")

                    # Try to display cached data with stale indicator
                    try:
                        cached_data, stale_for = self.fetcher.fetch_with_cache()
                        if cached_data:
                            self.renderer.render(cached_data, stale_for)
                    except Exception as render_error:
                        print(f"Failed to render cached data: {render_error}")

            # Sleep briefly to avoid tight loop
            time.sleep(1)

        # Cleanup
        print("\nShutting down...")
        try:
            self.renderer.shutdown()
        except Exception as e:
            print(f"Error during shutdown: {e}")

        try:
            self.buttons.cleanup()
        except Exception as e:
            print(f"Error cleaning up buttons: {e}")

        print("TETSUO display stopped")

    def _poll_and_update(self):
        """Poll for data and update display."""
        print(f"[{time.strftime('%H:%M:%S')}] Fetching data...")

        data, stale_for = self.fetcher.fetch_with_cache()

        if data:
            print(f"  Price: ${data.price_usd:.8f}")

            if data.change_24h_pct is not None:
                sign = "+" if data.change_24h_pct >= 0 else ""
                print(f"  Change 24h: {sign}{data.change_24h_pct:.2f}%")

            if data.volume_24h_usd:
                print(f"  Volume 24h: ${data.volume_24h_usd:,.2f}")

            if data.liquidity_usd:
                print(f"  Liquidity: ${data.liquidity_usd:,.2f}")

            print(f"  Source: {data.source}")

            if stale_for > 0:
                print(f"  ⚠ Data is stale ({stale_for}s old)")

            # Update display
            try:
                self.renderer.render(data, stale_for)
                print("  Display updated")
            except Exception as e:
                print(f"  Failed to update display: {e}")

        else:
            print("  ✗ No data available")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(
        description="TETSUO E-Paper Display Daemon"
    )
    parser.add_argument(
        "--config",
        default="config.yaml",
        help="Path to config.yaml (default: config.yaml)"
    )
    parser.add_argument(
        "--test-pattern",
        action="store_true",
        help="Show test pattern and exit"
    )

    args = parser.parse_args()

    if args.test_pattern:
        # Show test pattern only
        config = Config(args.config)
        renderer = DisplayRenderer(config)
        renderer.show_test_pattern()
        print("Test pattern displayed. Exiting.")
        return

    # Run main daemon
    try:
        app = TetsuoDisplay(args.config)
        app.start()
    except KeyboardInterrupt:
        print("\nInterrupted by user")
    except Exception as e:
        print(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
