"""Resolves the primary trading pair for TETSUO token."""

import requests
from typing import Optional, Dict, Any


class PairResolver:
    """Finds the best trading pair for a token on Dexscreener."""

    def __init__(self, timeout: int = 5):
        """
        Initialize resolver.

        Args:
            timeout: Request timeout in seconds
        """
        self.timeout = timeout
        self.base_url = "https://api.dexscreener.com/latest/dex/tokens"

    def resolve_best_pair(self, mint_address: str, dex: str = "raydium") -> Optional[Dict[str, Any]]:
        """
        Find the trading pair with highest liquidity for a token.

        Args:
            mint_address: Token mint address
            dex: Preferred DEX name (e.g., "raydium")

        Returns:
            Dict with pair info or None if not found:
            {
                "pair_address": str,
                "dex_id": str,
                "base_token": str,
                "quote_token": str,
                "liquidity_usd": float,
                "price_usd": float
            }
        """
        try:
            url = f"{self.base_url}/{mint_address}"
            response = requests.get(url, timeout=self.timeout)
            response.raise_for_status()

            data = response.json()
            pairs = data.get("pairs", [])

            if not pairs:
                return None

            # Filter by preferred DEX if specified
            preferred_pairs = [p for p in pairs if p.get("dexId", "").lower() == dex.lower()]
            search_pool = preferred_pairs if preferred_pairs else pairs

            # Find pair with max liquidity
            best_pair = max(
                search_pool,
                key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0),
                default=None
            )

            if not best_pair:
                return None

            # Extract relevant info
            liquidity = best_pair.get("liquidity", {})

            return {
                "pair_address": best_pair.get("pairAddress", ""),
                "dex_id": best_pair.get("dexId", ""),
                "base_token": best_pair.get("baseToken", {}).get("symbol", ""),
                "quote_token": best_pair.get("quoteToken", {}).get("symbol", ""),
                "liquidity_usd": float(liquidity.get("usd", 0) or 0),
                "price_usd": float(best_pair.get("priceUsd", 0) or 0)
            }

        except requests.RequestException as e:
            print(f"Error resolving pair: {e}")
            return None
        except (ValueError, KeyError) as e:
            print(f"Error parsing pair data: {e}")
            return None

    def format_pair_info(self, pair_info: Dict[str, Any]) -> str:
        """
        Format pair info for display.

        Args:
            pair_info: Pair information dict

        Returns:
            Formatted string
        """
        if not pair_info:
            return "No pair found"

        return (
            f"Pair: {pair_info['base_token']}/{pair_info['quote_token']}\n"
            f"DEX: {pair_info['dex_id']}\n"
            f"Address: {pair_info['pair_address']}\n"
            f"Liquidity: ${pair_info['liquidity_usd']:,.2f}\n"
            f"Price: ${pair_info['price_usd']:.8f}"
        )


def main():
    """CLI tool to resolve and display the best trading pair."""
    import sys

    if len(sys.argv) < 2:
        print("Usage: python pair_resolver.py <MINT_ADDRESS> [DEX]")
        print("Example: python pair_resolver.py 8i51XNNpGaKaj4G4nDdmQh95v4FKAxw8mhtaRoKd9tE8 raydium")
        sys.exit(1)

    mint = sys.argv[1]
    dex = sys.argv[2] if len(sys.argv) > 2 else "raydium"

    print(f"Resolving best {dex.upper()} pair for {mint}...\n")

    resolver = PairResolver()
    pair_info = resolver.resolve_best_pair(mint, dex)

    if pair_info:
        print(resolver.format_pair_info(pair_info))
        print(f"\n✓ Use this pair address in config.yaml: {pair_info['pair_address']}")
    else:
        print("✗ Could not find a suitable trading pair")
        sys.exit(1)


if __name__ == "__main__":
    main()
