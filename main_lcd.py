#!/usr/bin/env python3
"""
Main application for TETSUO price display on 1.44" LCD
Runs on Raspberry Pi Zero 2 with ST7735S LCD display
"""

import sys
import time
import signal
import logging
from pathlib import Path
from threading import Thread, Event

# Add app directory to path
sys.path.insert(0, str(Path(__file__).parent))

from app.config import Config
from app.data_fetcher import DataFetcher
from app.lcd_renderer import LCDRenderer
from app.cache import Cache


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('tetsuo_lcd.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)


class TetsuoLCDDisplay:
    """Main application class for TETSUO LCD display."""

    def __init__(self, config_file='config_lcd.yaml'):
        """Initialize the application."""
        self.config = Config(config_file)
        self.fetcher = DataFetcher(self.config)
        self.renderer = LCDRenderer(self.config)
        self.cache = Cache(self.config)

        self.running = False
        self.stop_event = Event()

        # Price tracking
        self.last_price = None
        self.price_alert_threshold = self.config.get('features.alert_threshold_percent', 10)

        # Auto-rotation settings
        self.auto_rotate = self.config.get('display.auto_rotate', True)
        self.rotation_interval = self.config.get('display.rotation_interval', 10)
        self.last_rotation_time = 0

        # Setup signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum, frame):
        """Handle shutdown signals."""
        logger.info("Shutdown signal received")
        self.stop()

    def start(self):
        """Start the display application."""
        logger.info("Starting TETSUO LCD Display")
        self.running = True

        try:
            # Initialize display
            self.renderer.init()
            logger.info("LCD initialized successfully")

            # Start main loop
            self._run_display_loop()

        except Exception as e:
            logger.error(f"Fatal error: {e}")
            self.renderer.show_error(str(e))
            time.sleep(5)

        finally:
            self.stop()

    def _run_display_loop(self):
        """Main display update loop."""
        poll_interval = self.config.get('poll.interval_seconds', 5)
        last_fetch_time = 0
        last_data = None
        consecutive_errors = 0
        max_consecutive_errors = 5

        while self.running and not self.stop_event.is_set():
            try:
                current_time = time.time()

                # Fetch new data if needed
                if current_time - last_fetch_time >= poll_interval:
                    logger.debug("Fetching new price data...")

                    # Try to fetch new data
                    data = self.fetcher.fetch()

                    if data:
                        logger.info(f"Price: ${data.price_usd:.8f} | "
                                  f"24h: {data.change_24h_pct:+.2f}% | "
                                  f"Source: {data.source}")

                        # Check for price alerts
                        self._check_price_alert(data)

                        # Cache the data
                        self.cache.save(data)

                        last_data = data
                        last_fetch_time = current_time
                        consecutive_errors = 0
                    else:
                        consecutive_errors += 1
                        logger.warning(f"Failed to fetch data (attempt {consecutive_errors}/{max_consecutive_errors})")

                        # Try to load from cache if too many errors
                        if consecutive_errors >= max_consecutive_errors and not last_data:
                            logger.info("Loading data from cache...")
                            last_data = self.cache.load()
                            if last_data:
                                logger.info("Using cached data")

                # Calculate staleness
                stale_seconds = 0
                if last_data:
                    stale_seconds = int(current_time - last_fetch_time)
                    if stale_seconds > self.config.get('fallback.stale_threshold_seconds', 180):
                        logger.warning(f"Data is stale: {stale_seconds} seconds old")

                # Handle auto-rotation
                if self.auto_rotate:
                    self._handle_auto_rotation(current_time)

                # Render current data
                self.renderer.render(last_data, stale_seconds)

                # Small delay to prevent CPU overuse
                time.sleep(0.1)

            except KeyboardInterrupt:
                logger.info("Keyboard interrupt received")
                break

            except Exception as e:
                logger.error(f"Error in display loop: {e}", exc_info=True)
                consecutive_errors += 1

                if consecutive_errors >= max_consecutive_errors * 2:
                    logger.critical("Too many consecutive errors. Shutting down.")
                    self.renderer.show_error("Too many errors")
                    time.sleep(5)
                    break

                time.sleep(1)

    def _check_price_alert(self, data):
        """Check if price has changed significantly for alerts."""
        if not self.config.get('features.price_alerts', False):
            return

        if self.last_price and data.price_usd:
            percent_change = abs((data.price_usd - self.last_price) / self.last_price * 100)

            if percent_change >= self.price_alert_threshold:
                logger.info(f"PRICE ALERT: {percent_change:.2f}% change detected!")
                # Here you could trigger a buzzer, LED, or other alert mechanism

        self.last_price = data.price_usd

    def _handle_auto_rotation(self, current_time):
        """Handle automatic view rotation."""
        if current_time - self.last_rotation_time >= self.rotation_interval:
            self.renderer.current_view = (self.renderer.current_view + 1) % 3
            self.last_rotation_time = current_time
            logger.debug(f"Auto-rotated to view {self.renderer.current_view}")

    def stop(self):
        """Stop the application gracefully."""
        logger.info("Stopping TETSUO LCD Display...")
        self.running = False
        self.stop_event.set()

        # Shutdown display
        if self.renderer:
            self.renderer.shutdown()

        logger.info("TETSUO LCD Display stopped")


def main():
    """Main entry point."""
    import argparse

    parser = argparse.ArgumentParser(description='TETSUO LCD Price Display')
    parser.add_argument('--config', '-c', default='config_lcd.yaml',
                      help='Configuration file (default: config_lcd.yaml)')
    parser.add_argument('--test', action='store_true',
                      help='Run in test mode with sample data')
    parser.add_argument('--debug', action='store_true',
                      help='Enable debug logging')

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)

    if args.test:
        # Run test mode
        logger.info("Running in test mode...")
        from app.lcd_renderer import main as test_renderer
        test_renderer()
    else:
        # Run main application
        app = TetsuoLCDDisplay(config_file=args.config)

        try:
            app.start()
        except KeyboardInterrupt:
            logger.info("Application interrupted by user")
        except Exception as e:
            logger.error(f"Application error: {e}", exc_info=True)
        finally:
            app.stop()


if __name__ == "__main__":
    main()