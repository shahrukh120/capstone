"""Simple in-memory rate limiter for API endpoints.

Uses a sliding window approach per IP address.
"""
from __future__ import annotations

import time
import logging
from collections import defaultdict
from typing import Dict, List, Tuple

logger = logging.getLogger(__name__)


class RateLimiter:
    """Token-bucket-style rate limiter with per-IP tracking."""

    def __init__(self, requests_per_minute: int = 30, burst_limit: int = 10):
        self.rpm = requests_per_minute
        self.burst = burst_limit
        self.window = 60.0  # 1 minute window
        self._requests: Dict[str, List[float]] = defaultdict(list)

    def is_allowed(self, client_ip: str) -> Tuple[bool, dict]:
        """Check if a request from client_ip is allowed.

        Returns (allowed, info_dict).
        """
        now = time.time()
        window_start = now - self.window

        # Clean old entries
        self._requests[client_ip] = [
            t for t in self._requests[client_ip] if t > window_start
        ]

        recent = self._requests[client_ip]
        count = len(recent)

        # Check burst (requests in last 2 seconds)
        burst_window = now - 2.0
        burst_count = sum(1 for t in recent if t > burst_window)

        info = {
            "requests_in_window": count,
            "limit": self.rpm,
            "remaining": max(0, self.rpm - count),
            "burst_count": burst_count,
        }

        if burst_count >= self.burst:
            logger.warning(f"Burst limit hit for {client_ip}: {burst_count} in 2s")
            return False, info

        if count >= self.rpm:
            logger.warning(f"Rate limit hit for {client_ip}: {count}/{self.rpm} per minute")
            return False, info

        # Allow and record
        self._requests[client_ip].append(now)
        return True, info

    def cleanup(self):
        """Remove expired entries (call periodically)."""
        now = time.time()
        window_start = now - self.window
        expired_keys = []
        for ip, timestamps in self._requests.items():
            self._requests[ip] = [t for t in timestamps if t > window_start]
            if not self._requests[ip]:
                expired_keys.append(ip)
        for ip in expired_keys:
            del self._requests[ip]


# ── Pre-configured limiters ─────────────────────────────────────────
# General API: 30 requests/min, burst of 10
api_limiter = RateLimiter(requests_per_minute=30, burst_limit=10)

# LLM-heavy endpoints: 10 requests/min (these are expensive)
llm_limiter = RateLimiter(requests_per_minute=10, burst_limit=5)

# Upload: 5 per minute
upload_limiter = RateLimiter(requests_per_minute=5, burst_limit=3)
