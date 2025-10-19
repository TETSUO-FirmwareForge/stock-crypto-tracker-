#!/usr/bin/env python3
"""
Smoke test for TETSUO display data sources.

Tests each API source and prints normalized output.
No hardware required.
"""

import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.config import Config
from app.data_fetcher import DataFetcher


def print_separator():
    """Print a visual separator."""
    print("\n" + "=" * 70 + "\n")


def test_source(fetcher: DataFetcher, source_name: str):
    """
    Test a single data source.

    Args:
        fetcher: DataFetcher instance
        source_name: Name of source to test
    """
    print(f"Testing: {source_name}")
    print("-" * 70)

    try:
        # Call the appropriate fetch method
        if source_name == "dexscreener_pair":
            data = fetcher._fetch_dexscreener_pair()
        elif source_name == "dexscreener_token":
            data = fetcher._fetch_dexscreener_token()
        elif source_name == "birdeye":
            data = fetcher._fetch_birdeye()
        elif source_name == "geckoterminal":
            data = fetcher._fetch_geckoterminal()
        else:
            print(f"Unknown source: {source_name}")
            return False

        if data:
            print("✓ SUCCESS\n")
            print("Normalized data:")
            print(f"  price_usd:       ${data.price_usd:.8f}")
            print(f"  change_24h_pct:  {data.change_24h_pct if data.change_24h_pct is not None else 'N/A'}")
            print(f"  volume_24h_usd:  ${data.volume_24h_usd:,.2f}" if data.volume_24h_usd else "  volume_24h_usd:  N/A")
            print(f"  liquidity_usd:   ${data.liquidity_usd:,.2f}" if data.liquidity_usd else "  liquidity_usd:   N/A")
            print(f"  fdv_usd:         ${data.fdv_usd:,.2f}" if data.fdv_usd else "  fdv_usd:         N/A")
            print(f"  source:          {data.source}")
            print(f"  updated_at:      {data.updated_at_epoch}")
            print(f"  age:             {data.age_seconds()}s")
            return True
        else:
            print("✗ FAILED: No data returned")
            return False

    except Exception as e:
        print(f"✗ FAILED: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run smoke tests on all data sources."""
    print_separator()
    print("TETSUO Display - API Smoke Test")
    print_separator()

    # Load config
    try:
        config = Config()
    except Exception as e:
        print(f"Failed to load config: {e}")
        sys.exit(1)

    print("Configuration:")
    print(f"  Token: {config.token_symbol}")
    print(f"  Chain: {config.token_chain}")
    print(f"  Mint:  {config.token_mint}")
    print(f"  Pair:  {config.primary_pair or '(not set)'}")
    print_separator()

    # Create fetcher
    fetcher = DataFetcher(config)

    # Test each source
    sources = config.get("fallback.order", [])
    results = {}

    for source_name in sources:
        success = test_source(fetcher, source_name)
        results[source_name] = success
        print_separator()

    # Summary
    print("SUMMARY")
    print("-" * 70)

    successful = sum(1 for v in results.values() if v)
    total = len(results)

    for source, success in results.items():
        status = "✓" if success else "✗"
        print(f"  {status} {source}")

    print(f"\nTotal: {successful}/{total} sources working")

    if successful == 0:
        print("\n⚠ WARNING: No data sources are working!")
        print("   Check your internet connection and configuration.")
        sys.exit(1)
    elif successful < total:
        print(f"\n⚠ WARNING: {total - successful} source(s) failed")
        print("   The app will work but may have limited redundancy.")
    else:
        print("\n✓ All sources working correctly!")

    print_separator()


if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\nTest interrupted")
        sys.exit(1)
    except Exception as e:
        print(f"\nFatal error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
