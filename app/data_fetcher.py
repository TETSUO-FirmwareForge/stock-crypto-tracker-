"""Data fetcher with multi-source fallback for TETSUO token."""

import json
import time
import requests
from pathlib import Path
from typing import Optional, Dict, Any
from datetime import datetime


class TokenData:
    """Normalized token data structure."""

    def __init__(
        self,
        price_usd: float,
        change_24h_pct: Optional[float],
        volume_24h_usd: Optional[float],
        liquidity_usd: Optional[float],
        fdv_usd: Optional[float],
        source: str,
        updated_at_epoch: int
    ):
        self.price_usd = price_usd
        self.change_24h_pct = change_24h_pct
        self.volume_24h_usd = volume_24h_usd
        self.liquidity_usd = liquidity_usd
        self.fdv_usd = fdv_usd
        self.source = source
        self.updated_at_epoch = updated_at_epoch

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "price_usd": self.price_usd,
            "change_24h_pct": self.change_24h_pct,
            "volume_24h_usd": self.volume_24h_usd,
            "liquidity_usd": self.liquidity_usd,
            "fdv_usd": self.fdv_usd,
            "source": self.source,
            "updated_at_epoch": self.updated_at_epoch
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TokenData":
        """Create from dictionary."""
        return cls(
            price_usd=data["price_usd"],
            change_24h_pct=data.get("change_24h_pct"),
            volume_24h_usd=data.get("volume_24h_usd"),
            liquidity_usd=data.get("liquidity_usd"),
            fdv_usd=data.get("fdv_usd"),
            source=data["source"],
            updated_at_epoch=data["updated_at_epoch"]
        )

    def age_seconds(self) -> int:
        """Get age of data in seconds."""
        return int(time.time()) - self.updated_at_epoch

    def __repr__(self) -> str:
        return (
            f"TokenData(price=${self.price_usd:.8f}, "
            f"change_24h={self.change_24h_pct}%, "
            f"source={self.source}, "
            f"age={self.age_seconds()}s)"
        )


class DataFetcher:
    """Multi-source token data fetcher with automatic fallback."""

    def __init__(self, config):
        """
        Initialize data fetcher.

        Args:
            config: Config instance
        """
        self.config = config
        self.timeout = config.request_timeout
        self.max_retries = config.max_retries
        self.cache_path = Path(config.cache_path)

        # Ensure cache directory exists
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    def fetch(self) -> Optional[TokenData]:
        """
        Fetch token data using fallback ladder.

        Returns:
            TokenData or None if all sources fail
        """
        fallback_order = self.config.get("fallback.order", [])

        for source_name in fallback_order:
            try:
                print(f"Trying {source_name}...")

                if source_name == "dexscreener_pair":
                    data = self._fetch_dexscreener_pair()
                elif source_name == "dexscreener_token":
                    data = self._fetch_dexscreener_token()
                elif source_name == "birdeye":
                    data = self._fetch_birdeye()
                elif source_name == "geckoterminal":
                    data = self._fetch_geckoterminal()
                else:
                    print(f"Unknown source: {source_name}")
                    continue

                if data:
                    print(f"✓ Success from {source_name}")
                    self._save_cache(data)
                    return data

            except Exception as e:
                print(f"✗ {source_name} failed: {e}")
                continue

        print("✗ All sources failed")
        return None

    def fetch_with_cache(self) -> tuple[Optional[TokenData], int]:
        """
        Fetch data with cache fallback.

        Returns:
            (TokenData or None, stale_seconds)
            If fresh data: (data, 0)
            If cached data: (data, age_in_seconds)
            If no data: (None, 0)
        """
        # Try fresh fetch
        fresh_data = self.fetch()
        if fresh_data:
            return (fresh_data, 0)

        # Fall back to cache
        cached_data = self._load_cache()
        if cached_data:
            stale_for = cached_data.age_seconds()
            print(f"Using cached data (stale for {stale_for}s)")
            return (cached_data, stale_for)

        return (None, 0)

    def _fetch_dexscreener_pair(self) -> Optional[TokenData]:
        """Fetch from Dexscreener pair endpoint."""
        pair_address = self.config.primary_pair
        if not pair_address:
            print("No pair address configured")
            return None

        url = self.config.get("sources.dexscreener_pair").replace("{PAIR}", pair_address)

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                pair = data.get("pair")
                if not pair:
                    return None

                # Check staleness
                price_usd = float(pair.get("priceUsd", 0))
                if price_usd == 0:
                    return None

                # Parse fields
                price_change = pair.get("priceChange", {})
                volume = pair.get("volume", {})
                liquidity = pair.get("liquidity", {})

                return TokenData(
                    price_usd=price_usd,
                    change_24h_pct=self._safe_float(price_change.get("h24")),
                    volume_24h_usd=self._safe_float(volume.get("h24")),
                    liquidity_usd=self._safe_float(liquidity.get("usd")),
                    fdv_usd=self._safe_float(pair.get("fdv")),
                    source="dexscreener_pair",
                    updated_at_epoch=int(time.time())
                )

            except requests.RequestException as e:
                if attempt < self.max_retries:
                    time.sleep(0.5 * (2 ** attempt))  # Exponential backoff
                    continue
                raise

        return None

    def _fetch_dexscreener_token(self) -> Optional[TokenData]:
        """Fetch from Dexscreener token endpoint."""
        mint = self.config.token_mint
        url = self.config.get("sources.dexscreener_token").replace("{MINT}", mint)

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                pairs = data.get("pairs", [])
                if not pairs:
                    return None

                # Pick pair with max liquidity
                best_pair = max(
                    pairs,
                    key=lambda p: float(p.get("liquidity", {}).get("usd", 0) or 0),
                    default=None
                )

                if not best_pair:
                    return None

                price_usd = float(best_pair.get("priceUsd", 0))
                if price_usd == 0:
                    return None

                price_change = best_pair.get("priceChange", {})
                volume = best_pair.get("volume", {})
                liquidity = best_pair.get("liquidity", {})

                return TokenData(
                    price_usd=price_usd,
                    change_24h_pct=self._safe_float(price_change.get("h24")),
                    volume_24h_usd=self._safe_float(volume.get("h24")),
                    liquidity_usd=self._safe_float(liquidity.get("usd")),
                    fdv_usd=self._safe_float(best_pair.get("fdv")),
                    source="dexscreener_token",
                    updated_at_epoch=int(time.time())
                )

            except requests.RequestException as e:
                if attempt < self.max_retries:
                    time.sleep(0.5 * (2 ** attempt))
                    continue
                raise

        return None

    def _fetch_birdeye(self) -> Optional[TokenData]:
        """Fetch from Birdeye API."""
        api_key = self.config.birdeye_api_key
        if not api_key:
            print("Birdeye API key not configured")
            return None

        mint = self.config.token_mint
        url = self.config.get("sources.birdeye").replace("{MINT}", mint)
        headers = {"x-api-key": api_key}

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(url, headers=headers, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                # Birdeye returns price directly
                price_data = data.get("data", {})
                price_usd = self._safe_float(price_data.get("value"))

                if not price_usd or price_usd == 0:
                    return None

                # Note: Birdeye price endpoint may not include 24h stats
                # Mark as limited data
                return TokenData(
                    price_usd=price_usd,
                    change_24h_pct=None,  # Not available in basic endpoint
                    volume_24h_usd=None,
                    liquidity_usd=None,
                    fdv_usd=None,
                    source="birdeye",
                    updated_at_epoch=int(time.time())
                )

            except requests.RequestException as e:
                if attempt < self.max_retries:
                    time.sleep(0.5 * (2 ** attempt))
                    continue
                raise

        return None

    def _fetch_geckoterminal(self) -> Optional[TokenData]:
        """Fetch from GeckoTerminal API."""
        mint = self.config.token_mint
        url = self.config.get("sources.geckoterminal").replace("{MINT}", mint)

        for attempt in range(self.max_retries + 1):
            try:
                response = requests.get(url, timeout=self.timeout)
                response.raise_for_status()
                data = response.json()

                token_data = data.get("data", {})
                attributes = token_data.get("attributes", {})

                price_usd = self._safe_float(attributes.get("price_usd"))
                if not price_usd or price_usd == 0:
                    return None

                return TokenData(
                    price_usd=price_usd,
                    change_24h_pct=self._safe_float(
                        attributes.get("price_change_percentage", {}).get("24h")
                    ),
                    volume_24h_usd=self._safe_float(attributes.get("volume_usd", {}).get("h24")),
                    liquidity_usd=None,  # May be in relationships, not parsing for now
                    fdv_usd=self._safe_float(attributes.get("fdv_usd")),
                    source="geckoterminal",
                    updated_at_epoch=int(time.time())
                )

            except requests.RequestException as e:
                if attempt < self.max_retries:
                    time.sleep(0.5 * (2 ** attempt))
                    continue
                raise

        return None

    def _safe_float(self, value) -> Optional[float]:
        """Safely convert value to float."""
        if value is None:
            return None
        try:
            result = float(value)
            return result if result != 0 else None
        except (ValueError, TypeError):
            return None

    def _save_cache(self, data: TokenData):
        """Save data to cache file."""
        try:
            with open(self.cache_path, 'w') as f:
                json.dump(data.to_dict(), f, indent=2)
        except Exception as e:
            print(f"Failed to save cache: {e}")

    def _load_cache(self) -> Optional[TokenData]:
        """Load data from cache file."""
        try:
            if not self.cache_path.exists():
                return None

            with open(self.cache_path, 'r') as f:
                data = json.load(f)

            return TokenData.from_dict(data)

        except Exception as e:
            print(f"Failed to load cache: {e}")
            return None


def main():
    """CLI tool to test data fetcher."""
    import sys
    sys.path.insert(0, str(Path(__file__).parent.parent))

    from app.config import Config

    print("Testing data fetcher...\n")

    config = Config()
    fetcher = DataFetcher(config)

    # Test fresh fetch
    print("=== Fresh Fetch ===")
    data = fetcher.fetch()

    if data:
        print(f"\n{data}")
        print(f"\nFull data:")
        for key, value in data.to_dict().items():
            print(f"  {key}: {value}")
    else:
        print("Failed to fetch data")

    # Test cache
    print("\n=== Cache Test ===")
    cached_data, stale_for = fetcher.fetch_with_cache()
    if cached_data:
        print(f"Cached data (stale for {stale_for}s): {cached_data}")
    else:
        print("No cached data available")


if __name__ == "__main__":
    main()
