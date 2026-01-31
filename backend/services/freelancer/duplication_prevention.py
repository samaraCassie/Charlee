"""RN09: Project Duplication Prevention Service.

Prevents duplicate analysis of projects across platforms using:
- Similarity matching (title, client, budget)
- Distributed locks with Redis
- Timeout management

This service helps avoid:
- Processing the same project from multiple platforms
- Race conditions between concurrent workers
- Wasting API quota on duplicate analysis
"""

import hashlib
import logging
import uuid
from datetime import datetime, timedelta, timezone
from typing import Any, Optional, TypedDict

from pydantic import BaseModel, Field, validator
from sqlalchemy import text
from sqlalchemy.orm import Session

from database.models import FreelanceOpportunity

logger = logging.getLogger(__name__)


# Pydantic Models for Validation
class ProjectData(BaseModel):
    """Project data for duplication detection.

    Attributes:
        title: Project title (required)
        description: Project description
        client_name: Client name for matching
        budget: Project budget in USD
        external_id: External platform ID (e.g., Upwork job ID)
    """

    title: str = Field(..., min_length=1, max_length=300)
    description: Optional[str] = None
    client_name: Optional[str] = Field(None, max_length=200)
    budget: Optional[float] = Field(None, gt=0)
    external_id: Optional[str] = Field(None, max_length=100)

    @validator("title", "client_name")
    def strip_whitespace(cls, v: Optional[str]) -> Optional[str]:
        """Strip leading/trailing whitespace from text fields."""
        return v.strip() if v else v


# TypedDicts for Return Types
class DuplicateCheckResult(TypedDict, total=False):
    """Result of duplicate check operation.

    Attributes:
        is_duplicate: Whether duplicate was found
        original_id: ID of original project if duplicate
        original_title: Title of original project if duplicate
        reason: Explanation of why flagged as duplicate
        error: Error message if check failed
    """

    is_duplicate: bool
    original_id: Optional[int]
    original_title: Optional[str]
    reason: Optional[str]
    error: Optional[str]


class ProjectDuplicationPrevention:
    """
    Prevents duplicate analysis of projects across platforms.

    Uses similarity matching and distributed locking to avoid:
    - Processing same project from multiple platforms
    - Race conditions between concurrent workers
    - Wasting API quota on duplicates

    Attributes:
        db: Database session for querying existing projects
        redis: Redis client for distributed locking
        SIMILARITY_THRESHOLD: Minimum similarity score for duplicate (0.85 = 85%)
        BUDGET_VARIANCE_THRESHOLD: Maximum budget difference allowed (0.15 = 15%)
        LOOKBACK_DAYS: Number of days to check for duplicates (7 days)

    Examples:
        >>> duplication = ProjectDuplicationPrevention(db, redis)
        >>> project = ProjectData(
        ...     title="Django Developer Needed",
        ...     client_name="TechCorp",
        ...     budget=5000.0
        ... )
        >>> result = duplication.detect_duplicate(project, user_id=1)
        >>> if result['is_duplicate']:
        ...     print(f"Duplicate of project #{result['original_id']}")
    """

    SIMILARITY_THRESHOLD: float = 0.85  # 85% similarity = duplicate
    BUDGET_VARIANCE_THRESHOLD: float = 0.15  # 15% budget difference allowed
    LOOKBACK_DAYS: int = 7  # Check last 7 days for duplicates

    def __init__(self, db: Session, redis_client: Any) -> None:
        """
        Initialize duplication prevention service.

        Args:
            db: SQLAlchemy database session
            redis_client: Redis client for distributed locking

        Examples:
            >>> from redis import Redis
            >>> redis_client = Redis(host='localhost', port=6379)
            >>> service = ProjectDuplicationPrevention(db, redis_client)
        """
        self.db = db
        self.redis = redis_client

    def detect_duplicate(self, new_project: ProjectData, user_id: int) -> DuplicateCheckResult:
        """
        Detect if a project is a duplicate using similarity matching.

        Checks recent projects (last 7 days) for duplicates based on:
        - Same external ID across platforms
        - Same client + similar title (85% threshold)
        - Similar budget (within 15% variance)

        Args:
            new_project: Project data to check for duplicates
            user_id: User ID for multi-tenancy isolation

        Returns:
            Dictionary with:
                - is_duplicate (bool): Whether duplicate was found
                - original_id (int, optional): ID of original project if duplicate
                - original_title (str, optional): Title of original project
                - reason (str, optional): Why it was flagged as duplicate
                - error (str, optional): Error message if check failed

        Raises:
            No exceptions raised - returns error in dict on failure

        Examples:
            >>> project = ProjectData(
            ...     title="Build Django API",
            ...     description="Need experienced Django dev",
            ...     client_name="TechCorp",
            ...     budget=5000.0,
            ...     external_id="upwork_12345"
            ... )
            >>> result = service.detect_duplicate(project, user_id=1)
            >>> if result['is_duplicate']:
            ...     print(f"Duplicate of project #{result['original_id']}")
            ...     print(f"Reason: {result['reason']}")
        """
        try:
            # Get recent similar projects
            cutoff_date = datetime.now(timezone.utc) - timedelta(days=self.LOOKBACK_DAYS)

            query = text("""
                SELECT id, title, client_name, client_budget, external_id
                FROM freelance_opportunities
                WHERE user_id = :user_id
                    AND collected_at >= :cutoff_date
                ORDER BY collected_at DESC
                LIMIT 50
            """)

            result = self.db.execute(
                query,
                {"user_id": user_id, "cutoff_date": cutoff_date},
            )

            similar_projects = result.fetchall()

            # Check each candidate for duplication
            for candidate in similar_projects:
                is_duplicate = self._is_duplicate_project(new_project, candidate)

                if is_duplicate:
                    logger.info(
                        "Duplicate project detected",
                        extra={
                            "new_project_title": new_project.title,
                            "original_project_id": candidate.id,
                            "original_project_title": candidate.title,
                            "user_id": user_id,
                        },
                    )
                    return DuplicateCheckResult(
                        is_duplicate=True,
                        original_id=candidate.id,
                        original_title=candidate.title,
                        reason="Similar title, client, and budget detected",
                    )

            return DuplicateCheckResult(is_duplicate=False)

        except Exception as e:
            logger.error(
                "Error detecting duplicates",
                extra={"user_id": user_id, "error_type": type(e).__name__, "error": str(e)},
                exc_info=True,
            )
            # On error, assume not duplicate (fail open to avoid blocking valid projects)
            return DuplicateCheckResult(is_duplicate=False, error=str(e))

    def _is_duplicate_project(self, new_project: ProjectData, candidate: Any) -> bool:
        """
        Check if two projects are duplicates.

        Uses multiple heuristics:
        1. Same external ID (definitive match)
        2. Same client (prerequisite)
        3. High title similarity (>= 85%)
        4. Similar budget (within 15% variance)

        Args:
            new_project: New project data (Pydantic model)
            candidate: Existing project from database (SQLAlchemy row)

        Returns:
            True if projects are duplicates, False otherwise

        Examples:
            >>> new = ProjectData(title="Django Developer", client_name="TechCorp", budget=5000)
            >>> # candidate is DB row with same fields
            >>> is_dup = service._is_duplicate_project(new, candidate)
        """
        # 1. Check if same external ID (across different platforms)
        if new_project.external_id and candidate.external_id == new_project.external_id:
            return True

        # 2. Check client matching
        same_client = self._is_same_client(new_project, candidate)
        if not same_client:
            return False  # Different clients can't be duplicates

        # 3. Check title similarity
        title_similarity = self._text_similarity(new_project.title, candidate.title or "")
        if title_similarity < self.SIMILARITY_THRESHOLD:
            return False

        # 4. Check budget similarity (if both have budgets)
        if new_project.budget and candidate.client_budget:
            if candidate.client_budget > 0:
                budget_variance = (
                    abs(new_project.budget - candidate.client_budget) / candidate.client_budget
                )
                if budget_variance > self.BUDGET_VARIANCE_THRESHOLD:
                    return False
        elif new_project.budget or candidate.client_budget:
            # One has budget, other doesn't - likely different projects
            return False

        # All checks passed - this is a duplicate
        return True

    def _is_same_client(self, new_project: ProjectData, candidate: Any) -> bool:
        """
        Check if two projects are from the same client.

        Uses fuzzy matching to handle variations in client names.

        Args:
            new_project: New project data
            candidate: Existing project from database

        Returns:
            True if same client, False otherwise

        Examples:
            >>> new = ProjectData(title="Test", client_name="TechCorp Inc")
            >>> # Returns True even if candidate.client_name is "TechCorp"
        """
        new_client = (new_project.client_name or "").strip().lower()
        candidate_client = (candidate.client_name or "").strip().lower()

        if not new_client or not candidate_client:
            return False

        # Exact match
        if new_client == candidate_client:
            return True

        # Fuzzy match (simple substring)
        if new_client in candidate_client or candidate_client in new_client:
            return True

        return False

    def _text_similarity(self, text1: str, text2: str) -> float:
        """
        Calculate text similarity using character-level n-grams.

        Uses Jaccard similarity with 3-character n-grams (trigrams).
        This is more robust than simple string matching for:
        - Typos
        - Minor variations
        - Word order differences

        Args:
            text1: First text to compare
            text2: Second text to compare

        Returns:
            Similarity score from 0.0 (completely different) to 1.0 (identical)

        Examples:
            >>> service._text_similarity("Django Developer", "Django Developer")
            1.0
            >>> service._text_similarity("Django Developer", "Python Developer")
            0.45  # Approximate - shares some trigrams
            >>> service._text_similarity("Django", "React")
            0.0
        """
        if not text1 or not text2:
            return 0.0

        # Normalize
        text1 = text1.lower().strip()
        text2 = text2.lower().strip()

        if text1 == text2:
            return 1.0

        # Character 3-grams (trigrams)
        def get_ngrams(text: str, n: int = 3) -> set[str]:
            return {text[i : i + n] for i in range(len(text) - n + 1)}

        ngrams1 = get_ngrams(text1)
        ngrams2 = get_ngrams(text2)

        if not ngrams1 or not ngrams2:
            return 0.0

        # Jaccard similarity: |intersection| / |union|
        intersection = ngrams1.intersection(ngrams2)
        union = ngrams1.union(ngrams2)

        return len(intersection) / len(union) if union else 0.0

    def acquire_processing_lock(self, project_id: int, timeout: int = 300) -> Optional[str]:
        """
        Acquire distributed lock for processing a project.

        Prevents race conditions when multiple workers try to process
        the same project simultaneously (e.g., from different platforms).

        Uses Redis SET NX EX for atomic lock acquisition.

        Args:
            project_id: Project ID to lock
            timeout: Lock timeout in seconds (default: 5 minutes)

        Returns:
            Lock token (UUID) if acquired successfully, None if lock already held

        Raises:
            No exceptions raised - returns None on Redis errors

        Examples:
            >>> lock_token = service.acquire_processing_lock(project_id=123, timeout=300)
            >>> if lock_token:
            ...     try:
            ...         # Process project
            ...         process_project(123)
            ...     finally:
            ...         service.release_processing_lock(123, lock_token)
            ... else:
            ...     print("Project is being processed by another worker")
        """
        try:
            lock_key = f"processing:project:{project_id}"
            lock_token = str(uuid.uuid4())

            # Try to acquire lock (SET NX EX - atomic operation)
            acquired = self.redis.set(lock_key, lock_token, nx=True, ex=timeout)

            if acquired:
                logger.info(
                    "Acquired processing lock",
                    extra={
                        "project_id": project_id,
                        "lock_token": lock_token[:8],  # Log first 8 chars only
                        "timeout": timeout,
                    },
                )
                return lock_token
            else:
                logger.warning(
                    "Failed to acquire processing lock - already locked",
                    extra={"project_id": project_id},
                )
                return None

        except Exception as e:
            logger.error(
                "Error acquiring processing lock",
                extra={"project_id": project_id, "error_type": type(e).__name__, "error": str(e)},
                exc_info=True,
            )
            return None

    def release_processing_lock(self, project_id: int, lock_token: str) -> bool:
        """
        Release processing lock.

        Only releases the lock if the provided token matches (prevents
        releasing someone else's lock).

        Uses Lua script for atomic check-and-delete operation.

        Args:
            project_id: Project ID that was locked
            lock_token: Token returned from acquire_processing_lock

        Returns:
            True if released successfully, False if token didn't match or error

        Raises:
            No exceptions raised - returns False on errors

        Examples:
            >>> lock_token = service.acquire_processing_lock(123)
            >>> # ... process project ...
            >>> released = service.release_processing_lock(123, lock_token)
            >>> assert released is True
        """
        try:
            lock_key = f"processing:project:{project_id}"

            # Only release if we own the lock (prevent releasing someone else's lock)
            lua_script = """
            if redis.call("get", KEYS[1]) == ARGV[1] then
                return redis.call("del", KEYS[1])
            else
                return 0
            end
            """

            result = self.redis.eval(lua_script, 1, lock_key, lock_token)

            if result:
                logger.info(
                    "Released processing lock",
                    extra={"project_id": project_id, "lock_token": lock_token[:8]},
                )
                return True
            else:
                logger.warning(
                    "Could not release processing lock - not owner",
                    extra={"project_id": project_id},
                )
                return False

        except Exception as e:
            logger.error(
                "Error releasing processing lock",
                extra={"project_id": project_id, "error_type": type(e).__name__, "error": str(e)},
                exc_info=True,
            )
            return False

    def get_project_hash(self, project_data: ProjectData) -> str:
        """
        Generate hash for project to use as deduplication key.

        Creates a consistent SHA256 hash from key identifying fields.
        Useful for quick duplicate checks without full similarity matching.

        Args:
            project_data: Project data to hash

        Returns:
            SHA256 hash (hex string, 64 characters)

        Examples:
            >>> project = ProjectData(title="Django Dev", client_name="TechCorp", budget=5000)
            >>> hash1 = service.get_project_hash(project)
            >>> hash2 = service.get_project_hash(project)
            >>> assert hash1 == hash2  # Same input = same hash
        """
        # Create consistent hash from key fields
        hash_input = "|".join(
            [
                project_data.title.lower(),
                (project_data.client_name or "").lower(),
                str(project_data.budget or ""),
                project_data.external_id or "",
            ]
        )

        return hashlib.sha256(hash_input.encode()).hexdigest()

    def mark_as_duplicate(self, project_id: int, original_project_id: int, reason: str) -> bool:
        """
        Mark a project as duplicate in database.

        Updates the project status to 'rejected' and records the reason.

        Args:
            project_id: ID of duplicate project to mark
            original_project_id: ID of original project
            reason: Human-readable reason for marking as duplicate

        Returns:
            True if marked successfully, False on error

        Raises:
            No exceptions raised - commits or rolls back transaction internally

        Examples:
            >>> success = service.mark_as_duplicate(
            ...     project_id=456,
            ...     original_project_id=123,
            ...     reason="Same client and title"
            ... )
            >>> if success:
            ...     print("Project marked as duplicate")
        """
        try:
            project = (
                self.db.query(FreelanceOpportunity)
                .filter(FreelanceOpportunity.id == project_id)
                .first()
            )

            if not project:
                logger.error(
                    "Cannot mark as duplicate - project not found",
                    extra={"project_id": project_id},
                )
                return False

            # Update project status
            project.status = "rejected"
            project.final_decision = "rejected"
            project.decision_reason = f"Duplicate of project #{original_project_id}: {reason}"
            project.recommendation = "reject"
            project.recommendation_reason = "Duplicate project detected"

            self.db.commit()

            logger.info(
                "Marked project as duplicate",
                extra={
                    "duplicate_project_id": project_id,
                    "original_project_id": original_project_id,
                    "reason": reason,
                },
            )
            return True

        except Exception as e:
            logger.error(
                "Error marking project as duplicate",
                extra={
                    "project_id": project_id,
                    "original_project_id": original_project_id,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            self.db.rollback()
            return False
