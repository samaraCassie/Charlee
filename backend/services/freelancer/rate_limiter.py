"""RN10: Rate Limiting Service for External APIs.

Implements rate limiting for freelance platform APIs using:
- Leaky bucket algorithm with Redis sorted sets
- Per-platform rate limits (Upwork: 100 req/hour, Freelancer: 200 req/hour)
- Automatic retry with exponential backoff

This service prevents API quota exhaustion and temporary bans from platforms.
"""

import logging
import time
import uuid
from typing import Any, Callable, Optional, TypedDict

logger = logging.getLogger(__name__)


# TypedDict for rate limit status
class RateLimitStatus(TypedDict, total=False):
    """Rate limit status information.

    Attributes:
        current_requests: Number of requests made in current window
        max_requests: Maximum requests allowed in window
        remaining: Number of remaining requests
        reset_time: Unix timestamp when window resets
        window_seconds: Size of rate limit window in seconds
    """

    current_requests: int
    max_requests: int
    remaining: int
    reset_time: Optional[float]
    window_seconds: int


class RateLimitExceeded(Exception):
    """
    Exception raised when rate limit is exceeded.

    Attributes:
        wait_time: Seconds to wait before next request is allowed
    """

    def __init__(self, message: str, wait_time: float) -> None:
        """
        Initialize exception.

        Args:
            message: Human-readable error message
            wait_time: Seconds to wait before retrying
        """
        self.wait_time = wait_time
        super().__init__(message)


class PlatformRateLimiter:
    """
    Rate limiter for external platform APIs.

    Uses Redis sorted sets to implement sliding window rate limiting.
    This is more accurate than fixed-window and more memory-efficient
    than token bucket.

    Platform limits:
        - Upwork: 100 requests/hour
        - Freelancer.com: 200 requests/hour
        - Fiverr: 150 requests/hour (estimated)
        - Default: 100 requests/hour (conservative)

    Attributes:
        redis: Redis client for storing request timestamps
        platform: Platform name (lowercase)
        max_requests: Maximum requests allowed per window
        window_seconds: Rate limit window size (3600 = 1 hour)

    Examples:
        >>> from redis import Redis
        >>> redis_client = Redis(host='localhost', port=6379)
        >>> limiter = PlatformRateLimiter(redis_client, platform='upwork')
        >>> try:
        ...     limiter.can_make_request(user_id=1)
        ...     response = api.get_projects()
        ... except RateLimitExceeded as e:
        ...     print(f"Rate limited. Wait {e.wait_time}s")
    """

    # Platform-specific rate limits (requests per hour)
    RATE_LIMITS: dict[str, int] = {
        "upwork": 100,  # Upwork: 100 requests/hour
        "freelancer": 200,  # Freelancer.com: 200 requests/hour
        "fiverr": 150,  # Fiverr: 150 requests/hour (estimated)
        "default": 100,  # Default conservative limit
    }

    def __init__(self, redis_client: Any, platform: str = "default") -> None:
        """
        Initialize rate limiter.

        Args:
            redis_client: Redis client for storing request timestamps
            platform: Platform name (upwork, freelancer, fiverr, etc.)

        Examples:
            >>> limiter = PlatformRateLimiter(redis, platform='upwork')
            >>> print(f"Max requests: {limiter.max_requests}/hour")
        """
        self.redis = redis_client
        self.platform = platform.lower()
        self.max_requests = self.RATE_LIMITS.get(self.platform, self.RATE_LIMITS["default"])
        self.window_seconds = 3600  # 1 hour window

    def can_make_request(self, user_id: Optional[int] = None) -> bool:
        """
        Check if a request can be made without violating rate limit.

        Uses sliding window algorithm:
        1. Remove requests older than window
        2. Count requests in current window
        3. Check if under limit
        4. Register new request

        Args:
            user_id: Optional user ID for per-user rate limiting
                    If None, uses global platform limit

        Returns:
            True if request is allowed

        Raises:
            RateLimitExceeded: If rate limit would be exceeded (includes wait_time)

        Examples:
            >>> limiter = PlatformRateLimiter(redis, 'upwork')
            >>> try:
            ...     if limiter.can_make_request(user_id=1):
            ...         response = make_api_call()
            ... except RateLimitExceeded as e:
            ...     print(f"Wait {e.wait_time:.0f}s")
        """
        key = self._get_key(user_id)
        now = time.time()

        try:
            # Remove requests older than the window
            self.redis.zremrangebyscore(key, 0, now - self.window_seconds)

            # Count current requests in window
            current_requests = self.redis.zcard(key)

            if current_requests >= self.max_requests:
                # Get oldest request to calculate wait time
                oldest = self.redis.zrange(key, 0, 0, withscores=True)
                if oldest:
                    oldest_timestamp = oldest[0][1]
                    wait_time = (oldest_timestamp + self.window_seconds) - now

                    logger.warning(
                        "Rate limit exceeded",
                        extra={
                            "platform": self.platform,
                            "user_id": user_id,
                            "current_requests": current_requests,
                            "max_requests": self.max_requests,
                            "wait_time": wait_time,
                        },
                    )

                    raise RateLimitExceeded(
                        f"Rate limit exceeded for {self.platform}. "
                        f"Wait {wait_time:.0f}s before next request.",
                        wait_time,
                    )

            # Register new request
            request_id = str(uuid.uuid4())
            self.redis.zadd(key, {request_id: now})

            # Set expiration on the key (cleanup)
            self.redis.expire(key, self.window_seconds + 60)

            logger.debug(
                "Rate limit check passed",
                extra={
                    "platform": self.platform,
                    "user_id": user_id,
                    "current_requests": current_requests + 1,
                    "max_requests": self.max_requests,
                },
            )
            return True

        except RateLimitExceeded:
            raise
        except Exception as e:
            logger.error(
                "Error checking rate limit",
                extra={
                    "platform": self.platform,
                    "user_id": user_id,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            # On Redis error, allow request (fail open to avoid blocking)
            return True

    def get_remaining_requests(self, user_id: Optional[int] = None) -> int:
        """
        Get number of remaining requests in current window.

        Args:
            user_id: Optional user ID for per-user limits

        Returns:
            Number of remaining requests (0 if at limit)

        Examples:
            >>> limiter = PlatformRateLimiter(redis, 'upwork')
            >>> remaining = limiter.get_remaining_requests(user_id=1)
            >>> print(f"Can make {remaining} more requests")
        """
        key = self._get_key(user_id)
        now = time.time()

        try:
            # Remove old requests
            self.redis.zremrangebyscore(key, 0, now - self.window_seconds)

            # Count current
            current_requests = self.redis.zcard(key)
            remaining = max(0, self.max_requests - current_requests)

            return remaining

        except Exception as e:
            logger.error(
                "Error getting remaining requests",
                extra={
                    "platform": self.platform,
                    "user_id": user_id,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            return self.max_requests  # Assume full quota on error

    def get_reset_time(self, user_id: Optional[int] = None) -> Optional[float]:
        """
        Get timestamp when rate limit will reset.

        Returns the time when the oldest request in the window will expire,
        freeing up one request slot.

        Args:
            user_id: Optional user ID for per-user limits

        Returns:
            Unix timestamp when oldest request expires, or None if no requests

        Examples:
            >>> limiter = PlatformRateLimiter(redis, 'upwork')
            >>> reset = limiter.get_reset_time(user_id=1)
            >>> if reset:
            ...     wait = reset - time.time()
            ...     print(f"Resets in {wait:.0f}s")
        """
        key = self._get_key(user_id)

        try:
            # Get oldest request
            oldest = self.redis.zrange(key, 0, 0, withscores=True)
            if oldest:
                oldest_timestamp = oldest[0][1]
                reset_time = oldest_timestamp + self.window_seconds
                return reset_time

            return None

        except Exception as e:
            logger.error(
                "Error getting reset time",
                extra={
                    "platform": self.platform,
                    "user_id": user_id,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            return None

    def get_status(self, user_id: Optional[int] = None) -> RateLimitStatus:
        """
        Get complete rate limit status.

        Args:
            user_id: Optional user ID for per-user limits

        Returns:
            Dictionary with rate limit status information

        Examples:
            >>> status = limiter.get_status(user_id=1)
            >>> print(f"Using {status['current_requests']}/{status['max_requests']} requests")
            >>> print(f"Remaining: {status['remaining']}")
        """
        key = self._get_key(user_id)
        now = time.time()

        try:
            # Remove old requests
            self.redis.zremrangebyscore(key, 0, now - self.window_seconds)

            # Get current count
            current_requests = self.redis.zcard(key)
            remaining = max(0, self.max_requests - current_requests)

            # Get reset time
            reset_time = self.get_reset_time(user_id)

            return RateLimitStatus(
                current_requests=current_requests,
                max_requests=self.max_requests,
                remaining=remaining,
                reset_time=reset_time,
                window_seconds=self.window_seconds,
            )

        except Exception as e:
            logger.error(
                "Error getting rate limit status",
                extra={
                    "platform": self.platform,
                    "user_id": user_id,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            # Return safe defaults on error
            return RateLimitStatus(
                current_requests=0,
                max_requests=self.max_requests,
                remaining=self.max_requests,
                reset_time=None,
                window_seconds=self.window_seconds,
            )

    def _get_key(self, user_id: Optional[int] = None) -> str:
        """
        Get Redis key for rate limiting.

        Args:
            user_id: Optional user ID for per-user limits

        Returns:
            Redis key string (e.g., "ratelimit:upwork:user:1")

        Examples:
            >>> limiter._get_key(user_id=1)
            'ratelimit:upwork:user:1'
            >>> limiter._get_key()
            'ratelimit:upwork:global'
        """
        if user_id:
            return f"ratelimit:{self.platform}:user:{user_id}"
        else:
            return f"ratelimit:{self.platform}:global"

    def reset(self, user_id: Optional[int] = None) -> bool:
        """
        Reset rate limit counter (for testing/admin use).

        WARNING: This clears all request history for the specified user/global.
        Use only for testing or admin override.

        Args:
            user_id: Optional user ID to reset (None = global)

        Returns:
            True if reset successfully, False on error

        Examples:
            >>> limiter.reset(user_id=1)  # Reset for specific user
            True
            >>> limiter.reset()  # Reset global counter
            True
        """
        key = self._get_key(user_id)

        try:
            self.redis.delete(key)
            logger.info(
                "Rate limit counter reset",
                extra={"platform": self.platform, "user_id": user_id},
            )
            return True

        except Exception as e:
            logger.error(
                "Error resetting rate limit",
                extra={
                    "platform": self.platform,
                    "user_id": user_id,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            return False


class RetryWithBackoff:
    """
    Retry mechanism with exponential backoff for rate-limited APIs.

    Implements intelligent retry strategy:
    - For RateLimitExceeded: waits exact time + 1s buffer
    - For other errors: exponential backoff (1s, 2s, 4s, ...)

    Attributes:
        max_retries: Maximum number of retry attempts
        base_delay: Base delay for exponential backoff (seconds)
        max_delay: Maximum delay cap (seconds)

    Examples:
        >>> retry = RetryWithBackoff(max_retries=3, base_delay=1.0)
        >>> result = retry.execute(lambda: api.get_projects())
    """

    def __init__(
        self,
        max_retries: int = 3,
        base_delay: float = 1.0,
        max_delay: float = 60.0,
    ) -> None:
        """
        Initialize retry mechanism.

        Args:
            max_retries: Maximum number of retry attempts (default: 3)
            base_delay: Base delay in seconds for exponential backoff (default: 1.0)
            max_delay: Maximum delay cap in seconds (default: 60.0)

        Examples:
            >>> retry = RetryWithBackoff(max_retries=5, base_delay=2.0)
            >>> # Will retry up to 5 times with delays: 2s, 4s, 8s, 16s, 32s
        """
        self.max_retries = max_retries
        self.base_delay = base_delay
        self.max_delay = max_delay

    def execute(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """
        Execute function with retry and exponential backoff.

        Strategy:
        - RateLimitExceeded: waits for e.wait_time + 1s buffer
        - Other exceptions: exponential backoff (base_delay * 2^attempt)
        - All delays capped at max_delay

        Args:
            func: Function to execute
            *args: Positional arguments for func
            **kwargs: Keyword arguments for func

        Returns:
            Result from successful function execution

        Raises:
            Last exception if all retries exhausted

        Examples:
            >>> retry = RetryWithBackoff(max_retries=3)
            >>> def fetch_projects():
            ...     return api.get_projects()
            >>> result = retry.execute(fetch_projects)
        """
        last_exception: Optional[Exception] = None

        for attempt in range(self.max_retries + 1):
            try:
                return func(*args, **kwargs)

            except RateLimitExceeded as e:
                last_exception = e

                if attempt >= self.max_retries:
                    logger.error(
                        "Max retries exceeded - rate limit",
                        extra={"max_retries": self.max_retries, "wait_time": e.wait_time},
                    )
                    raise

                # Wait for the exact time specified by rate limiter + 1s buffer
                wait_time = min(e.wait_time + 1, self.max_delay)
                logger.warning(
                    "Rate limit exceeded - retrying",
                    extra={
                        "wait_time": wait_time,
                        "attempt": attempt + 1,
                        "max_attempts": self.max_retries + 1,
                    },
                )
                time.sleep(wait_time)

            except Exception as e:
                last_exception = e

                if attempt >= self.max_retries:
                    logger.error(
                        "Max retries exceeded - error",
                        extra={
                            "max_retries": self.max_retries,
                            "error_type": type(e).__name__,
                            "error": str(e),
                        },
                    )
                    raise

                # Exponential backoff for other errors
                delay = min(self.base_delay * (2**attempt), self.max_delay)
                logger.warning(
                    "Request failed - retrying with exponential backoff",
                    extra={
                        "error_type": type(e).__name__,
                        "error": str(e),
                        "delay": delay,
                        "attempt": attempt + 1,
                        "max_attempts": self.max_retries + 1,
                    },
                )
                time.sleep(delay)

        # Should never reach here, but just in case
        if last_exception:
            raise last_exception
        raise RuntimeError("Retry loop exited without result or exception")


class UpworkRateLimiter(PlatformRateLimiter):
    """
    Specialized rate limiter for Upwork API.

    Rate limit: 100 requests per hour

    Examples:
        >>> limiter = UpworkRateLimiter(redis)
        >>> limiter.can_make_request(user_id=1)
    """

    def __init__(self, redis_client: Any) -> None:
        """
        Initialize Upwork rate limiter.

        Args:
            redis_client: Redis client for storing request timestamps
        """
        super().__init__(redis_client, platform="upwork")


class FreelancerRateLimiter(PlatformRateLimiter):
    """
    Specialized rate limiter for Freelancer.com API.

    Rate limit: 200 requests per hour

    Examples:
        >>> limiter = FreelancerRateLimiter(redis)
        >>> limiter.can_make_request(user_id=1)
    """

    def __init__(self, redis_client: Any) -> None:
        """
        Initialize Freelancer.com rate limiter.

        Args:
            redis_client: Redis client for storing request timestamps
        """
        super().__init__(redis_client, platform="freelancer")


def create_rate_limiter(redis_client: Any, platform: str) -> PlatformRateLimiter:
    """
    Factory function to create appropriate rate limiter.

    Args:
        redis_client: Redis client for storing request timestamps
        platform: Platform name (upwork, freelancer, fiverr, etc.)

    Returns:
        Platform-specific rate limiter instance

    Examples:
        >>> limiter = create_rate_limiter(redis, 'upwork')
        >>> isinstance(limiter, UpworkRateLimiter)
        True
        >>> limiter = create_rate_limiter(redis, 'unknown')
        >>> isinstance(limiter, PlatformRateLimiter)
        True
    """
    platform_lower = platform.lower()

    if platform_lower == "upwork":
        return UpworkRateLimiter(redis_client)
    elif platform_lower in ["freelancer", "freelancer.com"]:
        return FreelancerRateLimiter(redis_client)
    else:
        # Return generic limiter for unknown platforms
        return PlatformRateLimiter(redis_client, platform)
