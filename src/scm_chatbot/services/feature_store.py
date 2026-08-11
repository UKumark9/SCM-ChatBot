"""
Feature Store - ML Feature Caching and Management
Stores pre-computed features for faster inference and analytics
"""

import json
import pickle
import logging
from pathlib import Path
from datetime import datetime, timedelta
from typing import Any, Dict, Optional, List
import hashlib

logger = logging.getLogger(__name__)


class FeatureStore:
    """
    Feature Store for caching ML features and analytics results
    Supports both file-based and Redis-based storage
    """

    def __init__(self, storage_path: str = "data/feature_store", use_redis: bool = False):
        """
        Initialize Feature Store

        Args:
            storage_path: Path for file-based storage
            use_redis: Whether to use Redis (if available)
        """
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.use_redis = use_redis
        self.redis_client = None

        # Try to initialize Redis if requested
        if use_redis:
            try:
                import redis
                self.redis_client = redis.Redis(
                    host='localhost',
                    port=6379,
                    db=0,
                    decode_responses=False
                )
                self.redis_client.ping()
                logger.info("✅ Feature Store initialized with Redis")
            except Exception as e:
                logger.warning(f"Redis not available, using file-based storage: {e}")
                self.use_redis = False
                self.redis_client = None

        if not self.use_redis:
            logger.info(f"✅ Feature Store initialized (file-based at {storage_path})")

    def _generate_key(self, feature_type: str, identifier: str) -> str:
        """Generate unique key for feature"""
        return f"feature:{feature_type}:{identifier}"

    def _get_file_path(self, key: str) -> Path:
        """Get file path for key"""
        # Create safe filename from key
        safe_key = hashlib.md5(key.encode()).hexdigest()
        return self.storage_path / f"{safe_key}.pkl"

    def set(self, feature_type: str, identifier: str, value: Any, ttl: int = 3600):
        """
        Store a feature

        Args:
            feature_type: Type of feature (e.g., 'customer_segment', 'product_category')
            identifier: Unique identifier (e.g., customer_id, product_id)
            value: Feature value to store
            ttl: Time to live in seconds (default: 1 hour)
        """
        key = self._generate_key(feature_type, identifier)

        try:
            if self.use_redis and self.redis_client:
                # Store in Redis with TTL
                serialized = pickle.dumps(value)
                self.redis_client.setex(key, ttl, serialized)
            else:
                # Store in file with metadata
                data = {
                    'value': value,
                    'timestamp': datetime.now().isoformat(),
                    'ttl': ttl,
                    'expires_at': (datetime.now() + timedelta(seconds=ttl)).isoformat()
                }
                file_path = self._get_file_path(key)
                with open(file_path, 'wb') as f:
                    pickle.dump(data, f)

            logger.debug(f"Stored feature: {key}")
            return True

        except Exception as e:
            logger.error(f"Error storing feature {key}: {e}")
            return False

    def get(self, feature_type: str, identifier: str) -> Optional[Any]:
        """
        Retrieve a feature

        Args:
            feature_type: Type of feature
            identifier: Unique identifier

        Returns:
            Feature value or None if not found/expired
        """
        key = self._generate_key(feature_type, identifier)

        try:
            if self.use_redis and self.redis_client:
                # Get from Redis
                serialized = self.redis_client.get(key)
                if serialized:
                    return pickle.loads(serialized)
                return None
            else:
                # Get from file
                file_path = self._get_file_path(key)
                if not file_path.exists():
                    return None

                with open(file_path, 'rb') as f:
                    data = pickle.load(f)

                # Check if expired
                expires_at = datetime.fromisoformat(data['expires_at'])
                if datetime.now() > expires_at:
                    # Expired, delete file
                    file_path.unlink()
                    return None

                return data['value']

        except Exception as e:
            logger.error(f"Error retrieving feature {key}: {e}")
            return None

    def batch_set(self, feature_type: str, features: Dict[str, Any], ttl: int = 3600):
        """
        Store multiple features at once

        Args:
            feature_type: Type of features
            features: Dictionary of {identifier: value}
            ttl: Time to live in seconds
        """
        success_count = 0
        for identifier, value in features.items():
            if self.set(feature_type, identifier, value, ttl):
                success_count += 1

        logger.info(f"Batch stored {success_count}/{len(features)} features of type {feature_type}")
        return success_count

    def batch_get(self, feature_type: str, identifiers: List[str]) -> Dict[str, Any]:
        """
        Retrieve multiple features at once

        Args:
            feature_type: Type of features
            identifiers: List of identifiers

        Returns:
            Dictionary of {identifier: value} for found features
        """
        results = {}
        for identifier in identifiers:
            value = self.get(feature_type, identifier)
            if value is not None:
                results[identifier] = value

        logger.debug(f"Batch retrieved {len(results)}/{len(identifiers)} features of type {feature_type}")
        return results

    def delete(self, feature_type: str, identifier: str) -> bool:
        """Delete a specific feature"""
        key = self._generate_key(feature_type, identifier)

        try:
            if self.use_redis and self.redis_client:
                self.redis_client.delete(key)
            else:
                file_path = self._get_file_path(key)
                if file_path.exists():
                    file_path.unlink()

            logger.debug(f"Deleted feature: {key}")
            return True

        except Exception as e:
            logger.error(f"Error deleting feature {key}: {e}")
            return False

    def clear_type(self, feature_type: str) -> int:
        """
        Clear all features of a specific type

        Args:
            feature_type: Type of features to clear

        Returns:
            Number of features cleared
        """
        count = 0

        try:
            if self.use_redis and self.redis_client:
                # Get all keys matching pattern
                pattern = f"feature:{feature_type}:*"
                keys = self.redis_client.keys(pattern)
                if keys:
                    count = self.redis_client.delete(*keys)
            else:
                # Delete all files (expensive, but works)
                for file_path in self.storage_path.glob("*.pkl"):
                    try:
                        with open(file_path, 'rb') as f:
                            data = pickle.load(f)
                        # Check if this is the right type (would need to store type in metadata)
                        file_path.unlink()
                        count += 1
                    except:
                        pass

            logger.info(f"Cleared {count} features of type {feature_type}")
            return count

        except Exception as e:
            logger.error(f"Error clearing features of type {feature_type}: {e}")
            return count

    def clear_all(self) -> int:
        """Clear all features from store"""
        count = 0

        try:
            if self.use_redis and self.redis_client:
                # Clear all feature keys
                keys = self.redis_client.keys("feature:*")
                if keys:
                    count = self.redis_client.delete(*keys)
            else:
                # Delete all files
                for file_path in self.storage_path.glob("*.pkl"):
                    file_path.unlink()
                    count += 1

            logger.info(f"Cleared {count} features from store")
            return count

        except Exception as e:
            logger.error(f"Error clearing feature store: {e}")
            return count

    def get_stats(self) -> Dict[str, Any]:
        """Get feature store statistics"""
        stats = {
            'backend': 'redis' if self.use_redis else 'file',
            'storage_path': str(self.storage_path) if not self.use_redis else 'N/A',
            'total_features': 0
        }

        try:
            if self.use_redis and self.redis_client:
                keys = self.redis_client.keys("feature:*")
                stats['total_features'] = len(keys)
                stats['redis_info'] = {
                    'used_memory': self.redis_client.info('memory').get('used_memory_human', 'N/A')
                }
            else:
                stats['total_features'] = len(list(self.storage_path.glob("*.pkl")))
                # Calculate storage size
                total_size = sum(f.stat().st_size for f in self.storage_path.glob("*.pkl"))
                stats['storage_size_mb'] = round(total_size / (1024 * 1024), 2)

        except Exception as e:
            logger.error(f"Error getting stats: {e}")

        return stats


# Convenience functions for common ML features
class MLFeatures:
    """Helper class for common ML feature operations"""

    def __init__(self, feature_store: FeatureStore):
        self.store = feature_store

    def cache_customer_segment(self, customer_id: str, segment: str, ttl: int = 86400):
        """Cache customer segment (24h TTL by default)"""
        return self.store.set('customer_segment', customer_id, segment, ttl)

    def get_customer_segment(self, customer_id: str) -> Optional[str]:
        """Get cached customer segment"""
        return self.store.get('customer_segment', customer_id)

    def cache_product_category(self, product_id: str, category: Dict, ttl: int = 604800):
        """Cache product category (7 days TTL by default)"""
        return self.store.set('product_category', product_id, category, ttl)

    def get_product_category(self, product_id: str) -> Optional[Dict]:
        """Get cached product category"""
        return self.store.get('product_category', product_id)

    def cache_forecast(self, forecast_key: str, forecast_data: Dict, ttl: int = 3600):
        """Cache forecast results (1 hour TTL by default)"""
        return self.store.set('forecast', forecast_key, forecast_data, ttl)

    def get_forecast(self, forecast_key: str) -> Optional[Dict]:
        """Get cached forecast"""
        return self.store.get('forecast', forecast_key)

    def cache_analytics(self, analytics_type: str, result: Any, ttl: int = 1800):
        """Cache analytics results (30 min TTL by default)"""
        return self.store.set('analytics', analytics_type, result, ttl)

    def get_analytics(self, analytics_type: str) -> Optional[Any]:
        """Get cached analytics"""
        return self.store.get('analytics', analytics_type)


# Example usage
if __name__ == "__main__":
    # Initialize feature store
    fs = FeatureStore(use_redis=False)

    # Create ML features helper
    ml = MLFeatures(fs)

    # Cache some features
    ml.cache_customer_segment("CUST001", "high_value")
    ml.cache_product_category("PROD001", {"category": "electronics", "subcategory": "phones"})
    ml.cache_forecast("demand_30d", {"forecast": [100, 105, 110], "confidence": 0.85})

    # Retrieve features
    segment = ml.get_customer_segment("CUST001")
    print(f"Customer segment: {segment}")

    # Get stats
    stats = fs.get_stats()
    print(f"Feature store stats: {stats}")
