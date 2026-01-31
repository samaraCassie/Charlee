"""RN13: LGPD Compliance Service.

Provides LGPD-compliant data protection for client personal information:
- Encryption of PII (client names, emails)
- Data retention management (5-year limit)
- Automatic anonymization after retention period
- Data portability support

LGPD (Lei Geral de Proteção de Dados) is Brazil's data protection law,
similar to GDPR. This service ensures compliance with key requirements:
- Encryption at rest for personal data
- Right to data portability (export)
- Right to erasure (deletion)
- Automatic data retention limits
"""

import logging
import os
from datetime import date, datetime, timedelta, timezone
from typing import Any, List, Optional, TypedDict

from cryptography.fernet import Fernet
from pydantic import BaseModel, Field
from sqlalchemy.orm import Session

from database.models import FreelanceOpportunity

logger = logging.getLogger(__name__)


# Pydantic Models for Validation
class OpportunityPIIData(BaseModel):
    """Opportunity data with PII fields for encryption/decryption.

    Attributes:
        client_name: Client name (PII - requires encryption)
        external_id: External platform ID (may contain PII)
        additional_pii: Any other PII fields as key-value pairs
    """

    client_name: Optional[str] = Field(None, max_length=200)
    external_id: Optional[str] = Field(None, max_length=100)
    additional_pii: Optional[dict[str, str]] = Field(default_factory=dict)


# TypedDicts for Return Types
class DataRetentionStatus(TypedDict, total=False):
    """Data retention status information.

    Attributes:
        opportunity_id: ID of the opportunity
        status: Current status (active, anonymized)
        retention_until: Date when data will be anonymized (ISO format)
        days_until_deletion: Days remaining until anonymization
        anonymized_at: When data was anonymized (ISO format)
        note: Additional status information
        error: Error message if status check failed
    """

    opportunity_id: int
    status: str
    retention_until: Optional[str]
    days_until_deletion: Optional[int]
    anonymized_at: Optional[str]
    note: Optional[str]
    error: Optional[str]


class CleanupStats(TypedDict):
    """Statistics from data cleanup operation.

    Attributes:
        anonymized_count: Number of opportunities anonymized
        error_count: Number of errors encountered
        total_processed: Total opportunities processed
    """

    anonymized_count: int
    error_count: int
    total_processed: int


class UserDataExport(TypedDict):
    """Exported user data for LGPD portability.

    Attributes:
        user_id: User ID
        export_date: Export timestamp (ISO format)
        opportunities: List of opportunity data dictionaries
    """

    user_id: int
    export_date: str
    opportunities: List[dict[str, Any]]


class DeletionStats(TypedDict):
    """Statistics from user data deletion.

    Attributes:
        deleted_opportunities: Number of opportunities deleted
    """

    deleted_opportunities: int


class PIIEncryption:
    """
    Encryption service for Personally Identifiable Information (PII).

    Uses Fernet (symmetric encryption with AES-128) for encrypting client data
    at rest in the database. This ensures compliance with LGPD requirements
    for data protection.

    Attributes:
        cipher: Fernet cipher instance for encryption/decryption

    Examples:
        >>> encryption = PIIEncryption()
        >>> encrypted = encryption.encrypt("John Doe")
        >>> decrypted = encryption.decrypt(encrypted)
        >>> assert decrypted == "John Doe"

    Security Notes:
        - ENCRYPTION_KEY must be set in environment variables
        - Key should be generated with: Fernet.generate_key()
        - Store key securely (not in code or version control)
        - Rotate keys periodically in production
    """

    def __init__(self, encryption_key: Optional[str] = None) -> None:
        """
        Initialize PII encryption service.

        Args:
            encryption_key: Optional encryption key (base64-encoded).
                          If not provided, reads from ENCRYPTION_KEY env var.

        Raises:
            ValueError: If encryption_key not provided and ENCRYPTION_KEY env var not set

        Examples:
            >>> # Using environment variable (recommended)
            >>> encryption = PIIEncryption()
            >>> # Using explicit key (for testing)
            >>> test_key = Fernet.generate_key().decode()
            >>> encryption = PIIEncryption(encryption_key=test_key)
        """
        if encryption_key:
            key = encryption_key.encode()
        else:
            key_str = os.getenv("ENCRYPTION_KEY")
            if not key_str:
                # CRITICAL SECURITY FIX: Never generate fallback keys
                # This violates SECURITY_STANDARDS.md section "Secrets Management"
                raise ValueError(
                    "ENCRYPTION_KEY environment variable is required for LGPD compliance. "
                    "Generate with: python -c 'from cryptography.fernet import Fernet; "
                    "print(Fernet.generate_key().decode())'"
                )
            key = key_str.encode()

        self.cipher = Fernet(key)

    def encrypt(self, data: Optional[str]) -> Optional[str]:
        """
        Encrypt PII data.

        Uses Fernet symmetric encryption (AES-128 in CBC mode) with
        automatic IV generation for each encryption operation.

        Args:
            data: Plain text data to encrypt

        Returns:
            Encrypted data (base64 string) or None if input is None

        Raises:
            Exception: If encryption fails (propagated from Fernet)

        Examples:
            >>> encryption = PIIEncryption()
            >>> encrypted = encryption.encrypt("sensitive data")
            >>> assert encrypted is not None
            >>> assert encrypted != "sensitive data"
        """
        if not data:
            return None

        try:
            encrypted_bytes = self.cipher.encrypt(data.encode())
            return encrypted_bytes.decode()
        except Exception as e:
            logger.error(
                "Error encrypting data",
                extra={"error_type": type(e).__name__, "error": str(e)},
                exc_info=True,
            )
            raise

    def decrypt(self, encrypted_data: Optional[str]) -> Optional[str]:
        """
        Decrypt PII data.

        Args:
            encrypted_data: Encrypted data (base64 string)

        Returns:
            Plain text data or None if input is None or decryption fails

        Raises:
            No exceptions raised - returns None on decryption errors

        Examples:
            >>> encryption = PIIEncryption()
            >>> encrypted = encryption.encrypt("test data")
            >>> decrypted = encryption.decrypt(encrypted)
            >>> assert decrypted == "test data"
        """
        if not encrypted_data:
            return None

        try:
            decrypted_bytes = self.cipher.decrypt(encrypted_data.encode())
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(
                "Error decrypting data - possible key mismatch or corrupted data",
                extra={"error_type": type(e).__name__, "error": str(e)},
                exc_info=True,
            )
            # Return None on decryption error (key mismatch, corrupted data, etc.)
            # This is fail-safe behavior to avoid breaking the application
            return None

    def encrypt_dict(self, data: dict[str, Any], fields: List[str]) -> dict[str, Any]:
        """
        Encrypt specified fields in a dictionary.

        Creates a shallow copy of the dictionary and encrypts only
        the specified fields, leaving other fields unchanged.

        Args:
            data: Dictionary with data
            fields: List of field names to encrypt

        Returns:
            Dictionary with encrypted fields (new dict, original unchanged)

        Examples:
            >>> encryption = PIIEncryption()
            >>> data = {"client_name": "John Doe", "budget": 5000}
            >>> encrypted = encryption.encrypt_dict(data, ["client_name"])
            >>> assert encrypted["client_name"] != "John Doe"
            >>> assert encrypted["budget"] == 5000
        """
        encrypted_data = data.copy()

        for field in fields:
            if field in encrypted_data and encrypted_data[field]:
                encrypted_data[field] = self.encrypt(str(encrypted_data[field]))

        return encrypted_data

    def decrypt_dict(self, data: dict[str, Any], fields: List[str]) -> dict[str, Any]:
        """
        Decrypt specified fields in a dictionary.

        Creates a shallow copy of the dictionary and decrypts only
        the specified fields, leaving other fields unchanged.

        Args:
            data: Dictionary with encrypted data
            fields: List of field names to decrypt

        Returns:
            Dictionary with decrypted fields (new dict, original unchanged)

        Examples:
            >>> encryption = PIIEncryption()
            >>> data = {"client_name": "John Doe", "budget": 5000}
            >>> encrypted = encryption.encrypt_dict(data, ["client_name"])
            >>> decrypted = encryption.decrypt_dict(encrypted, ["client_name"])
            >>> assert decrypted["client_name"] == "John Doe"
        """
        decrypted_data = data.copy()

        for field in fields:
            if field in decrypted_data and decrypted_data[field]:
                decrypted_data[field] = self.decrypt(decrypted_data[field])

        return decrypted_data


class LGPDDataRetention:
    """
    LGPD data retention management service.

    Handles automatic data cleanup and anonymization according to LGPD
    requirements. LGPD requires that personal data be kept only for
    as long as necessary for the purpose it was collected.

    For freelance opportunities, we retain data for 5 years after project
    completion (standard for financial/tax records in Brazil), then
    automatically anonymize PII while keeping non-identifying analytics data.

    Attributes:
        db: SQLAlchemy database session
        RETENTION_YEARS: Number of years to retain data (5 years default)

    Examples:
        >>> retention = LGPDDataRetention(db)
        >>> # Set retention date when project completes
        >>> retention.set_retention_date(opp_id, completion_date)
        >>> # Run cleanup job (scheduled daily)
        >>> stats = retention.cleanup_expired_data()
        >>> print(f"Anonymized {stats['anonymized_count']} records")
    """

    # LGPD retention period (5 years after project completion)
    # This aligns with Brazilian tax record retention requirements
    RETENTION_YEARS: int = 5

    def __init__(self, db: Session) -> None:
        """
        Initialize data retention service.

        Args:
            db: SQLAlchemy database session

        Examples:
            >>> from database.session import get_db
            >>> db = next(get_db())
            >>> retention = LGPDDataRetention(db)
        """
        self.db = db

    def set_retention_date(self, opportunity_id: int, completion_date: date) -> bool:
        """
        Set data retention expiration date for an opportunity.

        Should be called when a project is completed or rejected to
        start the retention countdown timer.

        Args:
            opportunity_id: Opportunity ID
            completion_date: Project completion date

        Returns:
            True if set successfully, False on error

        Raises:
            No exceptions raised - returns False on errors

        Examples:
            >>> retention = LGPDDataRetention(db)
            >>> from datetime import date
            >>> success = retention.set_retention_date(123, date.today())
            >>> assert success is True
        """
        try:
            opportunity = (
                self.db.query(FreelanceOpportunity)
                .filter(FreelanceOpportunity.id == opportunity_id)
                .first()
            )

            if not opportunity:
                logger.error(
                    "Cannot set retention date - opportunity not found",
                    extra={"opportunity_id": opportunity_id},
                )
                return False

            # Set retention date (5 years from completion)
            retention_date = completion_date + timedelta(days=self.RETENTION_YEARS * 365)

            # Store retention date in extracted_context JSON field
            # TODO: Consider adding dedicated data_retention_until column in future
            if not opportunity.extracted_context:
                opportunity.extracted_context = {}

            opportunity.extracted_context["data_retention_until"] = retention_date.isoformat()
            opportunity.updated_at = datetime.now(timezone.utc)

            self.db.commit()

            logger.info(
                "Set data retention date",
                extra={
                    "opportunity_id": opportunity_id,
                    "completion_date": completion_date.isoformat(),
                    "retention_until": retention_date.isoformat(),
                    "retention_years": self.RETENTION_YEARS,
                },
            )
            return True

        except Exception as e:
            logger.error(
                "Error setting retention date",
                extra={
                    "opportunity_id": opportunity_id,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            self.db.rollback()
            return False

    def cleanup_expired_data(self) -> CleanupStats:
        """
        Anonymize data for opportunities past retention period.

        This should be run as a scheduled job (e.g., daily cron job or
        Celery task). Finds all opportunities with expired retention dates
        and anonymizes their PII while keeping non-identifying data for
        analytics and ML model training.

        Returns:
            Statistics about cleanup operation (anonymized count, errors, total)

        Raises:
            No exceptions raised - returns error stats on failure

        Examples:
            >>> retention = LGPDDataRetention(db)
            >>> stats = retention.cleanup_expired_data()
            >>> print(f"Anonymized: {stats['anonymized_count']}")
            >>> print(f"Errors: {stats['error_count']}")
            >>> print(f"Total processed: {stats['total_processed']}")
        """
        try:
            today = date.today()
            anonymized_count = 0
            error_count = 0

            # Find opportunities past retention period
            # Only process completed/rejected/expired opportunities
            opportunities = (
                self.db.query(FreelanceOpportunity)
                .filter(FreelanceOpportunity.status.in_(["completed", "rejected", "expired"]))
                .all()
            )

            total_candidates = len(opportunities)

            for opp in opportunities:
                try:
                    # Check if retention date exists and has passed
                    if opp.extracted_context and "data_retention_until" in opp.extracted_context:
                        retention_date_str = opp.extracted_context["data_retention_until"]
                        retention_date = date.fromisoformat(retention_date_str)

                        if retention_date <= today:
                            # Anonymize the opportunity
                            self._anonymize_opportunity(opp)
                            anonymized_count += 1

                except Exception as e:
                    logger.error(
                        "Error processing opportunity for anonymization",
                        extra={
                            "opportunity_id": opp.id,
                            "error_type": type(e).__name__,
                            "error": str(e),
                        },
                        exc_info=True,
                    )
                    error_count += 1
                    continue

            self.db.commit()

            logger.info(
                "LGPD data cleanup completed",
                extra={
                    "anonymized_count": anonymized_count,
                    "error_count": error_count,
                    "total_candidates": total_candidates,
                },
            )

            return CleanupStats(
                anonymized_count=anonymized_count,
                error_count=error_count,
                total_processed=total_candidates,
            )

        except Exception as e:
            logger.error(
                "Error in cleanup_expired_data",
                extra={"error_type": type(e).__name__, "error": str(e)},
                exc_info=True,
            )
            self.db.rollback()
            return CleanupStats(anonymized_count=0, error_count=1, total_processed=0)

    def _anonymize_opportunity(self, opportunity: FreelanceOpportunity) -> None:
        """
        Anonymize PII in an opportunity.

        Removes all personally identifiable information while keeping
        non-identifying data for analytics (budget, complexity, category, etc.).

        This complies with LGPD's requirement to minimize data retention
        while allowing legitimate business purposes (ML training, analytics).

        Args:
            opportunity: Opportunity model instance to anonymize

        Returns:
            None - modifies opportunity in place

        Examples:
            >>> # Called internally by cleanup_expired_data()
            >>> retention._anonymize_opportunity(opportunity)
        """
        # Remove PII fields
        opportunity.client_name = None
        opportunity.external_id = None  # Platform-specific ID may be PII

        # Mark as anonymized with timestamp
        if not opportunity.extracted_context:
            opportunity.extracted_context = {}

        opportunity.extracted_context["anonymized"] = True
        opportunity.extracted_context["anonymized_at"] = datetime.now(timezone.utc).isoformat()

        # Keep non-PII data for learning (complexity, category, outcomes, budget ranges, etc.)
        # This is LGPD-compliant as long as data cannot identify individuals
        # Examples of safe data: project category, complexity score, budget range,
        # success/failure outcome, general location (country-level)

        logger.info(
            "Anonymized opportunity PII data",
            extra={
                "opportunity_id": opportunity.id,
                "anonymized_at": opportunity.extracted_context["anonymized_at"],
            },
        )

    def export_user_data(self, user_id: int) -> UserDataExport:
        """
        Export all data for a user (LGPD data portability right).

        LGPD Article 18, Section II grants users the right to obtain
        a copy of all their personal data in a structured, commonly used format.

        Args:
            user_id: User ID to export data for

        Returns:
            Dictionary with all user data including opportunities

        Raises:
            Exception: If database query fails (propagated)

        Examples:
            >>> retention = LGPDDataRetention(db)
            >>> export = retention.export_user_data(user_id=1)
            >>> print(f"Found {len(export['opportunities'])} opportunities")
            >>> # Save to JSON file for user download
            >>> import json
            >>> with open('user_data.json', 'w') as f:
            ...     json.dump(export, f, indent=2)
        """
        try:
            opportunities = (
                self.db.query(FreelanceOpportunity)
                .filter(FreelanceOpportunity.user_id == user_id)
                .all()
            )

            exported_data: UserDataExport = {
                "user_id": user_id,
                "export_date": datetime.now(timezone.utc).isoformat(),
                "opportunities": [],
            }

            for opp in opportunities:
                opp_data = {
                    "id": opp.id,
                    "title": opp.title,
                    "description": opp.description,
                    "client_name": opp.client_name,
                    "client_rating": opp.client_rating,
                    "client_country": opp.client_country,
                    "budget": opp.client_budget,
                    "currency": opp.client_currency,
                    "status": opp.status,
                    "collected_at": opp.collected_at.isoformat() if opp.collected_at else None,
                    "analyzed_at": opp.analyzed_at.isoformat() if opp.analyzed_at else None,
                }

                exported_data["opportunities"].append(opp_data)

            logger.info(
                "Exported user data for LGPD portability",
                extra={
                    "user_id": user_id,
                    "opportunity_count": len(opportunities),
                    "export_date": exported_data["export_date"],
                },
            )

            return exported_data

        except Exception as e:
            logger.error(
                "Error exporting user data",
                extra={"user_id": user_id, "error_type": type(e).__name__, "error": str(e)},
                exc_info=True,
            )
            raise

    def delete_user_data(self, user_id: int) -> DeletionStats:
        """
        Delete all user data (LGPD right to erasure).

        LGPD Article 18, Section VI grants users the right to request
        deletion of their personal data. This operation is IRREVERSIBLE.

        WARNING: Use with extreme caution. This permanently deletes all
        user opportunities and cannot be undone.

        Args:
            user_id: User ID to delete all data for

        Returns:
            Statistics about deletion operation

        Raises:
            Exception: If database operation fails (propagated after rollback)

        Examples:
            >>> retention = LGPDDataRetention(db)
            >>> # Confirm with user before executing!
            >>> stats = retention.delete_user_data(user_id=1)
            >>> print(f"Deleted {stats['deleted_opportunities']} opportunities")
        """
        try:
            # Count opportunities before deletion for statistics
            count = (
                self.db.query(FreelanceOpportunity)
                .filter(FreelanceOpportunity.user_id == user_id)
                .count()
            )

            # Delete all opportunities for this user
            self.db.query(FreelanceOpportunity).filter(
                FreelanceOpportunity.user_id == user_id
            ).delete()

            self.db.commit()

            logger.warning(
                "DELETED all user data per LGPD right to erasure",
                extra={
                    "user_id": user_id,
                    "deleted_opportunities": count,
                    "operation": "IRREVERSIBLE_DATA_DELETION",
                },
            )

            return DeletionStats(deleted_opportunities=count)

        except Exception as e:
            logger.error(
                "Error deleting user data",
                extra={"user_id": user_id, "error_type": type(e).__name__, "error": str(e)},
                exc_info=True,
            )
            self.db.rollback()
            raise


class LGPDCompliance:
    """
    Main LGPD compliance service combining encryption and retention.

    Provides a unified interface for all LGPD compliance operations:
    - PII encryption/decryption
    - Data retention management
    - Data portability (export)
    - Right to erasure (deletion)

    This is the recommended service to use for LGPD compliance rather than
    using PIIEncryption or LGPDDataRetention directly.

    Attributes:
        encryption: PIIEncryption service instance
        retention: LGPDDataRetention service instance
        db: SQLAlchemy database session

    Examples:
        >>> lgpd = LGPDCompliance(db)
        >>> # Encrypt opportunity data before saving
        >>> encrypted = lgpd.encrypt_opportunity_pii(opp_data)
        >>> # Get retention status
        >>> status = lgpd.get_retention_status(opp_id)
        >>> # Export user data
        >>> export = lgpd.retention.export_user_data(user_id)
    """

    def __init__(self, db: Session, encryption_key: Optional[str] = None) -> None:
        """
        Initialize LGPD compliance service.

        Args:
            db: SQLAlchemy database session
            encryption_key: Optional encryption key (reads from env if not provided)

        Raises:
            ValueError: If encryption_key not provided and ENCRYPTION_KEY env var not set

        Examples:
            >>> from database.session import get_db
            >>> db = next(get_db())
            >>> lgpd = LGPDCompliance(db)
        """
        self.encryption = PIIEncryption(encryption_key)
        self.retention = LGPDDataRetention(db)
        self.db = db

    def encrypt_opportunity_pii(self, opportunity_data: dict[str, Any]) -> dict[str, Any]:
        """
        Encrypt PII fields in opportunity data before saving to database.

        Args:
            opportunity_data: Opportunity data dictionary

        Returns:
            Opportunity data with encrypted PII fields

        Examples:
            >>> lgpd = LGPDCompliance(db)
            >>> opp_data = {"title": "Django Dev", "client_name": "John Doe", "budget": 5000}
            >>> encrypted = lgpd.encrypt_opportunity_pii(opp_data)
            >>> assert encrypted["client_name"] != "John Doe"
            >>> assert encrypted["budget"] == 5000
        """
        pii_fields = ["client_name"]  # Add more fields as needed (e.g., client_email)

        return self.encryption.encrypt_dict(opportunity_data, pii_fields)

    def decrypt_opportunity_pii(self, opportunity_data: dict[str, Any]) -> dict[str, Any]:
        """
        Decrypt PII fields in opportunity data after reading from database.

        Args:
            opportunity_data: Opportunity data with encrypted PII

        Returns:
            Opportunity data with decrypted PII fields

        Examples:
            >>> lgpd = LGPDCompliance(db)
            >>> decrypted = lgpd.decrypt_opportunity_pii(encrypted_opp_data)
            >>> assert decrypted["client_name"] == "John Doe"
        """
        pii_fields = ["client_name"]  # Must match encrypt_opportunity_pii fields

        return self.encryption.decrypt_dict(opportunity_data, pii_fields)

    def ensure_consent(self, user_id: int, opportunity_id: int) -> bool:
        """
        Ensure user has consented to data processing (LGPD requirement).

        LGPD Article 7 requires explicit consent for data processing.
        For MVP, we assume consent is given when user creates an account
        and accepts terms of service.

        In production, this should check a proper consent records table
        with timestamps and consent scope.

        Args:
            user_id: User ID
            opportunity_id: Opportunity ID

        Returns:
            True if consent exists, False otherwise

        Examples:
            >>> lgpd = LGPDCompliance(db)
            >>> has_consent = lgpd.ensure_consent(user_id=1, opportunity_id=123)
            >>> if not has_consent:
            ...     raise ValueError("User has not consented to data processing")
        """
        # TODO: In production, check consent records table
        # For MVP, assume consent is given when user creates account
        # and accepts terms of service
        return True

    def get_retention_status(self, opportunity_id: int) -> DataRetentionStatus:
        """
        Get data retention status for an opportunity.

        Shows when data will be anonymized and how many days remain.

        Args:
            opportunity_id: Opportunity ID

        Returns:
            Retention status information dictionary

        Examples:
            >>> lgpd = LGPDCompliance(db)
            >>> status = lgpd.get_retention_status(123)
            >>> if status['status'] == 'active':
            ...     print(f"Data retained until {status['retention_until']}")
            ...     print(f"Days remaining: {status['days_until_deletion']}")
            >>> elif status['status'] == 'anonymized':
            ...     print(f"Data anonymized at {status['anonymized_at']}")
        """
        try:
            opportunity = (
                self.db.query(FreelanceOpportunity)
                .filter(FreelanceOpportunity.id == opportunity_id)
                .first()
            )

            if not opportunity:
                return DataRetentionStatus(
                    opportunity_id=opportunity_id, status="error", error="Opportunity not found"
                )

            # Check if already anonymized
            is_anonymized = opportunity.extracted_context and opportunity.extracted_context.get(
                "anonymized", False
            )

            if is_anonymized:
                return DataRetentionStatus(
                    opportunity_id=opportunity_id,
                    status="anonymized",
                    anonymized_at=opportunity.extracted_context.get("anonymized_at"),
                )

            # Check retention date
            retention_date = None
            if (
                opportunity.extracted_context
                and "data_retention_until" in opportunity.extracted_context
            ):
                retention_date_str = opportunity.extracted_context["data_retention_until"]
                retention_date = date.fromisoformat(retention_date_str)

            if retention_date:
                days_until_deletion = (retention_date - date.today()).days

                return DataRetentionStatus(
                    opportunity_id=opportunity_id,
                    status="active",
                    retention_until=retention_date.isoformat(),
                    days_until_deletion=max(0, days_until_deletion),
                )

            # No retention date set (project not completed yet)
            return DataRetentionStatus(
                opportunity_id=opportunity_id,
                status="active",
                retention_until=None,
                note="Retention date not set (project not completed)",
            )

        except Exception as e:
            logger.error(
                "Error getting retention status",
                extra={
                    "opportunity_id": opportunity_id,
                    "error_type": type(e).__name__,
                    "error": str(e),
                },
                exc_info=True,
            )
            return DataRetentionStatus(opportunity_id=opportunity_id, status="error", error=str(e))
