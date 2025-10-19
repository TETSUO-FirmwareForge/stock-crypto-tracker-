#!/usr/bin/env python3
"""
First-run setup wizard for TETSUO display.

Guides user through initial configuration, hardware checks,
and service setup.
"""

import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config
from app.pair_resolver import PairResolver
from app.display_driver import EPD2in7, HAS_HARDWARE
from app.data_fetcher import DataFetcher


class Colors:
    """Terminal colors."""
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'


def print_header(text):
    """Print section header."""
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text:^60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'=' * 60}{Colors.END}\n")


def print_success(text):
    """Print success message."""
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")


def print_warning(text):
    """Print warning message."""
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")


def print_error(text):
    """Print error message."""
    print(f"{Colors.RED}✗ {text}{Colors.END}")


def prompt_yes_no(question, default=True):
    """
    Ask a yes/no question.

    Args:
        question: Question to ask
        default: Default answer

    Returns:
        True for yes, False for no
    """
    suffix = "[Y/n]" if default else "[y/N]"
    while True:
        response = input(f"{question} {suffix}: ").strip().lower()
        if not response:
            return default
        if response in ['y', 'yes']:
            return True
        if response in ['n', 'no']:
            return False
        print("Please answer 'yes' or 'no'")


def check_spi():
    """Check if SPI is enabled."""
    print_header("Step 1: SPI Interface Check")

    spi_devices = list(Path("/dev").glob("spidev*"))

    if spi_devices:
        print_success(f"SPI is enabled. Found devices: {', '.join(str(d) for d in spi_devices)}")
        return True
    else:
        print_error("SPI is not enabled")
        print("\nTo enable SPI:")
        print("  1. Run: sudo raspi-config")
        print("  2. Navigate to: Interface Options → SPI")
        print("  3. Select: Yes")
        print("  4. Reboot your Pi")
        return False


def check_gpio_pins(config):
    """Verify GPIO pin configuration."""
    print_header("Step 2: GPIO Pin Configuration")

    pins = {
        "DC": config.get("display.gpio.dc_pin", 25),
        "RST": config.get("display.gpio.rst_pin", 17),
        "BUSY": config.get("display.gpio.busy_pin", 24),
        "CS": config.get("display.gpio.cs_pin", 8),
    }

    print("Current GPIO pin configuration (BCM numbering):")
    for name, pin in pins.items():
        print(f"  {name:6} → GPIO {pin}")

    print("\nThis is the standard Waveshare 2.7\" HAT pinout.")

    if not prompt_yes_no("\nIs this pinout correct for your HAT?", default=True):
        print_warning("Please edit config.yaml manually to set correct pins")
        return False

    print_success("GPIO pins confirmed")
    return True


def resolve_trading_pair(config):
    """Resolve and save the primary trading pair."""
    print_header("Step 3: Trading Pair Resolution")

    mint = config.token_mint
    print(f"Token mint: {mint}")
    print(f"Searching for best Raydium pair...\n")

    resolver = PairResolver(timeout=10)
    pair_info = resolver.resolve_best_pair(mint, dex="raydium")

    if not pair_info:
        print_error("Could not find a suitable trading pair")
        print("\nPlease check:")
        print("  - Your internet connection")
        print("  - The token mint address in config.yaml")
        print("  - That the token has liquidity on Raydium")
        return False

    print(resolver.format_pair_info(pair_info))

    if not prompt_yes_no("\nUse this pair?", default=True):
        print_warning("Pair not saved. You'll need to set it manually in config.yaml")
        return False

    # Save to config
    config.set("primary.pair", pair_info["pair_address"])
    config.save()

    print_success(f"Pair saved to config.yaml")
    return True


def configure_birdeye_key(config):
    """Configure Birdeye API key."""
    print_header("Step 4: Birdeye API Key (Optional)")

    print("Birdeye is used as a fallback data source.")
    print("An API key is optional but recommended for reliability.\n")
    print("Get a free key at: https://docs.birdeye.so/docs/authentication-api-keys\n")

    if not prompt_yes_no("Do you have a Birdeye API key?", default=False):
        print_warning("Skipping Birdeye configuration")
        print("The app will use Dexscreener and GeckoTerminal only.")
        return True

    api_key = input("\nEnter your Birdeye API key: ").strip()

    if not api_key:
        print_warning("No key entered, skipping")
        return True

    # Save to .env
    env_path = Path(".env")
    if env_path.exists():
        with open(env_path, 'r') as f:
            lines = f.readlines()

        # Update or append
        updated = False
        for i, line in enumerate(lines):
            if line.startswith("BIRDEYE_API_KEY="):
                lines[i] = f"BIRDEYE_API_KEY={api_key}\n"
                updated = True
                break

        if not updated:
            lines.append(f"BIRDEYE_API_KEY={api_key}\n")

        with open(env_path, 'w') as f:
            f.writelines(lines)
    else:
        with open(env_path, 'w') as f:
            f.write(f"BIRDEYE_API_KEY={api_key}\n")

    print_success("API key saved to .env")
    return True


def test_api_sources(config):
    """Test API connectivity."""
    print_header("Step 5: API Source Test")

    print("Testing data sources...\n")

    fetcher = DataFetcher(config)

    # Test each source
    sources_tested = 0
    sources_working = 0

    for source_name in config.get("fallback.order", []):
        sources_tested += 1
        print(f"Testing {source_name}...", end=" ")

        try:
            if source_name == "dexscreener_pair":
                data = fetcher._fetch_dexscreener_pair()
            elif source_name == "dexscreener_token":
                data = fetcher._fetch_dexscreener_token()
            elif source_name == "birdeye":
                data = fetcher._fetch_birdeye()
            elif source_name == "geckoterminal":
                data = fetcher._fetch_geckoterminal()
            else:
                continue

            if data:
                sources_working += 1
                print_success(f"OK (${data.price_usd:.8f})")
            else:
                print_error("No data")

        except Exception as e:
            print_error(f"Failed: {e}")

    print(f"\n{sources_working}/{sources_tested} sources working")

    if sources_working == 0:
        print_error("No data sources are working!")
        print("\nPlease check:")
        print("  - Your internet connection")
        print("  - The primary pair is set correctly")
        print("  - API keys (if using Birdeye)")
        return False

    print_success("At least one data source is working")
    return True


def test_display(config):
    """Test e-paper display."""
    print_header("Step 6: Display Test")

    if not HAS_HARDWARE:
        print_error("Display hardware not available (RPi.GPIO or spidev missing)")
        print("This is expected if you're not running on a Raspberry Pi")
        return False

    print("This will display a test pattern on your e-paper screen.")
    print_warning("The display will flash during the test")

    if not prompt_yes_no("\nRun display test?", default=True):
        print_warning("Skipping display test")
        return True

    try:
        from app.renderer import DisplayRenderer

        print("\nInitializing display...")
        renderer = DisplayRenderer(config)
        renderer.show_test_pattern()

        print_success("Test pattern displayed!")
        print("\nCheck your e-paper display. You should see:")
        print("  - A border rectangle")
        print("  - Zone dividers")
        print("  - Sample text and numbers")

        if prompt_yes_no("\nDo you see the test pattern?", default=True):
            print_success("Display is working correctly")
            renderer.shutdown()
            return True
        else:
            print_error("Display test failed")
            renderer.shutdown()
            return False

    except Exception as e:
        print_error(f"Display test failed: {e}")
        return False


def setup_systemd_service():
    """Guide user through systemd service setup."""
    print_header("Step 7: Systemd Service Setup")

    print("The service will auto-start on boot and restart on failure.\n")

    service_file = Path(__file__).parent.parent / "tetsuo-display.service"

    if not service_file.exists():
        print_error(f"Service file not found: {service_file}")
        return False

    print("To install the service, run these commands:\n")
    print(f"  cd {service_file.parent}")
    print(f"  sudo cp {service_file.name} /etc/systemd/system/")
    print(f"  sudo systemctl daemon-reload")
    print(f"  sudo systemctl enable tetsuo-display.service")
    print(f"  sudo systemctl start tetsuo-display.service")

    print("\nTo check status:")
    print("  sudo systemctl status tetsuo-display")

    print("\nTo view logs:")
    print("  sudo journalctl -u tetsuo-display -f")

    if prompt_yes_no("\nInstall service now?", default=True):
        import subprocess

        try:
            subprocess.run(
                ["sudo", "cp", str(service_file), "/etc/systemd/system/"],
                check=True
            )
            subprocess.run(["sudo", "systemctl", "daemon-reload"], check=True)
            subprocess.run(["sudo", "systemctl", "enable", "tetsuo-display.service"], check=True)

            print_success("Service installed and enabled")

            if prompt_yes_no("\nStart service now?", default=True):
                subprocess.run(["sudo", "systemctl", "start", "tetsuo-display.service"], check=True)
                print_success("Service started")

                print("\nCheck status with:")
                print("  sudo systemctl status tetsuo-display")

            return True

        except subprocess.CalledProcessError as e:
            print_error(f"Failed to install service: {e}")
            return False
        except Exception as e:
            print_error(f"Error: {e}")
            return False
    else:
        print_warning("Service not installed. Run the commands above manually when ready.")
        return True


def main():
    """Run the setup wizard."""
    print_header("TETSUO E-Paper Display - Setup Wizard")

    print("This wizard will guide you through the initial setup.\n")
    print("Make sure you have:")
    print("  - Raspberry Pi with SPI enabled")
    print("  - Waveshare 2.7\" e-Paper HAT connected")
    print("  - Internet connection")

    if not prompt_yes_no("\nContinue with setup?", default=True):
        print("\nSetup cancelled")
        return

    # Load config
    try:
        config = Config()
    except Exception as e:
        print_error(f"Failed to load config: {e}")
        return

    # Run setup steps
    steps = [
        ("SPI check", lambda: check_spi()),
        ("GPIO pins", lambda: check_gpio_pins(config)),
        ("Trading pair", lambda: resolve_trading_pair(config)),
        ("Birdeye key", lambda: configure_birdeye_key(config)),
        ("API test", lambda: test_api_sources(config)),
        ("Display test", lambda: test_display(config)),
        ("Service setup", lambda: setup_systemd_service()),
    ]

    results = []

    for step_name, step_func in steps:
        try:
            success = step_func()
            results.append((step_name, success))

            if not success and not prompt_yes_no(f"\n{step_name} failed. Continue anyway?", default=False):
                print("\nSetup aborted")
                return

        except KeyboardInterrupt:
            print("\n\nSetup interrupted")
            return
        except Exception as e:
            print_error(f"Unexpected error in {step_name}: {e}")
            results.append((step_name, False))

    # Summary
    print_header("Setup Complete!")

    print("Results:")
    for step_name, success in results:
        status = "✓" if success else "✗"
        color = Colors.GREEN if success else Colors.RED
        print(f"  {color}{status} {step_name}{Colors.END}")

    print("\nNext steps:")
    print("  - Check service status: sudo systemctl status tetsuo-display")
    print("  - View logs: sudo journalctl -u tetsuo-display -f")
    print("  - Edit config: nano config.yaml")
    print("  - Restart service: sudo systemctl restart tetsuo-display")

    print("\nFor help, see README.md or visit the GitHub repository")

    print_success("\nSetup wizard complete!")


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nSetup interrupted by user")
    except Exception as e:
        print_error(f"Fatal error: {e}")
        import traceback
        traceback.print_exc()
