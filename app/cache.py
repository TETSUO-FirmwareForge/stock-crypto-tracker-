"""
Cache module for storing token data
"""

import json
import os
from datetime import datetime
from typing import Optional
from pathlib import Path


class Cache:
    """Simple cache for token data."""

    def __init__(self, config):
        """Initialize cache with config."""
        self.config = config
        self.cache_path = Path(config.get('cache.path', './data/last_snapshot.json'))
        self.cache_path.parent.mkdir(parents=True, exist_ok=True)

    def save(self, data):
        """Save token data to cache."""
        if data is None:
            return

        try:
            cache_data = {
                'timestamp': datetime.now().isoformat(),
                'data': {
                    'price_usd': data.price_usd,
                    'change_24h_pct': data.change_24h_pct,
                    'volume_24h_usd': data.volume_24h_usd,
                    'liquidity_usd': data.liquidity_usd,
                    'fdv_usd': data.fdv_usd if hasattr(data, 'fdv_usd') else None,
                    'source': data.source,
                    'updated_at_epoch': data.updated_at_epoch
                }
            }

            with open(self.cache_path, 'w') as f:
                json.dump(cache_data, f, indent=2)

        except Exception as e:
            print(f"Error saving cache: {e}")

    def load(self):
        """Load token data from cache."""
        if not self.cache_path.exists():
            return None

        try:
            with open(self.cache_path, 'r') as f:
                cache_data = json.load(f)

            # Convert to TokenData object
            from app.data_fetcher import TokenData

            data = cache_data.get('data', {})
            return TokenData(
                price_usd=data.get('price_usd', 0),
                change_24h_pct=data.get('change_24h_pct'),
                volume_24h_usd=data.get('volume_24h_usd'),
                liquidity_usd=data.get('liquidity_usd'),
                fdv_usd=data.get('fdv_usd'),
                source=data.get('source', 'cache'),
                updated_at_epoch=data.get('updated_at_epoch', 0)
            )

        except Exception as e:
            print(f"Error loading cache: {e}")
            return None

    def clear(self):
        """Clear the cache."""
        if self.cache_path.exists():
            try:
                os.remove(self.cache_path)
            except Exception as e:
                print(f"Error clearing cache: {e}")

    def get_age(self) -> Optional[int]:
        """Get cache age in seconds."""
        if not self.cache_path.exists():
            return None

        try:
            stat = os.stat(self.cache_path)
            age = int(datetime.now().timestamp() - stat.st_mtime)
            return age
        except Exception:
            return None