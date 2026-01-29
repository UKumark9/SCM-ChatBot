"""
Utility Functions for SCM Chatbot
Includes logging, authentication, and helper functions
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
from datetime import datetime, timedelta
from typing import Dict, Optional
import hashlib
import secrets

try:
    import jwt
except ImportError:
    logging.warning("PyJWT not installed")


def setup_logging(config: Dict) -> logging.Logger:
    """Setup logging configuration"""
    log_file = Path(config['file'])
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger('scm_chatbot')
    logger.setLevel(config['level'])
    
    # Create formatters
    formatter = logging.Formatter(config['format'])
    
    # File handler with rotation
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=config['max_bytes'],
        backupCount=config['backup_count']
    )
    file_handler.setLevel(config['level'])
    file_handler.setFormatter(formatter)
    
    # Console handler
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config['level'])
    console_handler.setFormatter(formatter)
    
    # Add handlers
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)
    
    return logger


class AuthenticationManager:
    """Manages user authentication and authorization"""
    
    def __init__(self, secret_key: str, algorithm: str = "HS256", 
                 token_expire_minutes: int = 60):
        self.secret_key = secret_key
        self.algorithm = algorithm
        self.token_expire_minutes = token_expire_minutes
        self.users_db = {}  # Simple in-memory user store
    
    def hash_password(self, password: str) -> str:
        """Hash a password"""
        return hashlib.sha256(password.encode()).hexdigest()
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password"""
        return self.hash_password(plain_password) == hashed_password
    
    def create_user(self, username: str, password: str, role: str = "user") -> bool:
        """Create a new user"""
        if username in self.users_db:
            return False
        
        self.users_db[username] = {
            "username": username,
            "password": self.hash_password(password),
            "role": role,
            "created_at": datetime.now().isoformat()
        }
        return True
    
    def authenticate_user(self, username: str, password: str) -> Optional[Dict]:
        """Authenticate a user"""
        user = self.users_db.get(username)
        if not user:
            return None
        
        if not self.verify_password(password, user['password']):
            return None
        
        return user
    
    def create_access_token(self, data: Dict) -> str:
        """Create a JWT access token"""
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(minutes=self.token_expire_minutes)
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, self.secret_key, algorithm=self.algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str) -> Optional[Dict]:
        """Verify a JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            return payload
        except jwt.ExpiredSignatureError:
            return None
        except jwt.JWTError:
            return None


class PerformanceMonitor:
    """Monitor system performance metrics"""
    
    def __init__(self):
        self.query_times = []
        self.query_count = 0
        self.error_count = 0
        self.start_time = datetime.now()
    
    def record_query_time(self, duration: float):
        """Record query response time"""
        self.query_times.append(duration)
        self.query_count += 1
    
    def record_error(self):
        """Record an error occurrence"""
        self.error_count += 1
    
    def get_metrics(self) -> Dict:
        """Get performance metrics"""
        uptime = (datetime.now() - self.start_time).total_seconds()
        
        return {
            "total_queries": self.query_count,
            "total_errors": self.error_count,
            "average_response_time": sum(self.query_times) / len(self.query_times) if self.query_times else 0,
            "min_response_time": min(self.query_times) if self.query_times else 0,
            "max_response_time": max(self.query_times) if self.query_times else 0,
            "uptime_seconds": uptime,
            "queries_per_minute": (self.query_count / uptime) * 60 if uptime > 0 else 0,
            "error_rate": (self.error_count / self.query_count * 100) if self.query_count > 0 else 0
        }
    
    def reset_metrics(self):
        """Reset all metrics"""
        self.query_times = []
        self.query_count = 0
        self.error_count = 0
        self.start_time = datetime.now()


def format_number(num: float, decimals: int = 2) -> str:
    """Format a number with commas and decimals"""
    return f"{num:,.{decimals}f}"


def format_percentage(num: float, decimals: int = 2) -> str:
    """Format a number as percentage"""
    return f"{num:.{decimals}f}%"


def format_currency(amount: float, currency: str = "USD") -> str:
    """Format amount as currency"""
    symbols = {"USD": "$", "EUR": "€", "GBP": "£", "BRL": "R$"}
    symbol = symbols.get(currency, "$")
    return f"{symbol}{amount:,.2f}"


def truncate_text(text: str, max_length: int = 100) -> str:
    """Truncate text to max length"""
    if len(text) <= max_length:
        return text
    return text[:max_length-3] + "..."


def validate_query(query: str) -> tuple[bool, str]:
    """Validate user query"""
    if not query or not query.strip():
        return False, "Query cannot be empty"
    
    if len(query) > 1000:
        return False, "Query is too long (max 1000 characters)"
    
    # Check for potential injection attacks
    dangerous_patterns = ["<script>", "javascript:", "DROP TABLE", "DELETE FROM"]
    query_lower = query.lower()
    
    for pattern in dangerous_patterns:
        if pattern.lower() in query_lower:
            return False, "Query contains potentially dangerous content"
    
    return True, "Valid"


class CacheManager:
    """Simple cache manager for query results"""
    
    def __init__(self, ttl: int = 3600):
        self.cache = {}
        self.ttl = ttl  # Time to live in seconds
    
    def get(self, key: str) -> Optional[any]:
        """Get cached value"""
        if key in self.cache:
            entry = self.cache[key]
            if datetime.now() - entry['timestamp'] < timedelta(seconds=self.ttl):
                return entry['value']
            else:
                del self.cache[key]
        return None
    
    def set(self, key: str, value: any):
        """Set cached value"""
        self.cache[key] = {
            'value': value,
            'timestamp': datetime.now()
        }
    
    def clear(self):
        """Clear all cache"""
        self.cache = {}
    
    def get_stats(self) -> Dict:
        """Get cache statistics"""
        return {
            "total_entries": len(self.cache),
            "cache_size_bytes": sum(len(str(v['value'])) for v in self.cache.values())
        }
