from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON, Float
from sqlalchemy.orm import relationship
from database import Base
from .base import TimestampMixin, AuditMixin
import enum

class AlertSeverity(enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class VerificationStatus(enum.Enum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    APPROVED = "approved"
    REJECTED = "rejected"
    EXPIRED = "expired"

class SafetyAlert(Base, TimestampMixin):
    """Safety alerts for users"""
    __tablename__ = "safety_alerts"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # suspicious_activity, location_change, etc.
    severity = Column(SQLEnum(AlertSeverity), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    
    # Context
    trigger_data = Column(JSON, nullable=True)
    ip_address = Column(String(45), nullable=True)
    device_info = Column(JSON, nullable=True)
    location_data = Column(JSON, nullable=True)
    
    # Status
    is_acknowledged = Column(Boolean, default=False)
    acknowledged_at = Column(DateTime(timezone=True), nullable=True)
    is_resolved = Column(Boolean, default=False)
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    
    # Actions taken
    actions_taken = Column(JSON, nullable=True)
    requires_user_action = Column(Boolean, default=False)
    
    # Relationships
    user = relationship("User", back_populates="safety_alerts")

    def __repr__(self):
        return f"<SafetyAlert(id={self.id}, user_id={self.user_id}, type='{self.alert_type}', severity='{self.severity.value}')>"

class VerificationRequest(Base, TimestampMixin, AuditMixin):
    """ID and background verification requests"""
    __tablename__ = "verification_requests"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Verification type
    verification_type = Column(String(50), nullable=False)  # id_verification, background_check, phone_verification
    status = Column(SQLEnum(VerificationStatus), default=VerificationStatus.PENDING, nullable=False)
    
    # Submitted documents/data
    submitted_data = Column(JSON, nullable=True)  # Document URLs, phone numbers, etc.
    document_urls = Column(JSON, nullable=True)  # MinIO object names
    
    # Verification results
    verification_score = Column(Float, nullable=True)  # 0.0 to 1.0
    verification_details = Column(JSON, nullable=True)
    rejection_reason = Column(Text, nullable=True)
    
    # Third-party integration
    external_verification_id = Column(String(100), nullable=True)
    provider = Column(String(50), nullable=True)  # jumio, veriff, checkr, etc.
    provider_response = Column(JSON, nullable=True)
    
    # Processing
    processed_by_admin_id = Column(Integer, nullable=True)
    processed_at = Column(DateTime(timezone=True), nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Audit trail
    review_notes = Column(Text, nullable=True)
    manual_review_required = Column(Boolean, default=False)

    def __repr__(self):
        return f"<VerificationRequest(id={self.id}, user_id={self.user_id}, type='{self.verification_type}', status='{self.status.value}')>"

class BackgroundCheck(Base, TimestampMixin):
    """Background check results"""
    __tablename__ = "background_checks"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    verification_request_id = Column(Integer, ForeignKey("verification_requests.id"), nullable=True)
    
    # Check details
    provider = Column(String(50), nullable=False)  # checkr, sterling, etc.
    external_check_id = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False)
    
    # Results
    overall_result = Column(String(20), nullable=True)  # clear, consider, suspended
    criminal_history = Column(JSON, nullable=True)
    sex_offender_check = Column(JSON, nullable=True)
    identity_verification = Column(JSON, nullable=True)
    
    # Detailed results
    federal_criminal = Column(String(20), nullable=True)
    state_criminal = Column(String(20), nullable=True)
    county_criminal = Column(String(20), nullable=True)
    global_watchlist = Column(String(20), nullable=True)
    
    # Report data
    report_url = Column(String(500), nullable=True)
    raw_report = Column(JSON, nullable=True)
    
    # Platform decision
    platform_decision = Column(String(20), nullable=True)  # approved, rejected, manual_review
    decision_reason = Column(Text, nullable=True)
    reviewed_by_admin_id = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)

    def __repr__(self):
        return f"<BackgroundCheck(id={self.id}, user_id={self.user_id}, result='{self.overall_result}')>"

class ContentModeration(Base, TimestampMixin):
    """Content moderation results"""
    __tablename__ = "content_moderation"

    id = Column(Integer, primary_key=True, index=True)
    
    # Content details
    content_type = Column(String(50), nullable=False)  # photo, message, profile_text, etc.
    content_id = Column(Integer, nullable=False)  # ID of the content being moderated
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Moderation method
    moderation_type = Column(String(20), nullable=False)  # automatic, manual, reported
    ai_model_used = Column(String(50), nullable=True)
    
    # Results
    is_approved = Column(Boolean, nullable=True)
    confidence_score = Column(Float, nullable=True)  # 0.0 to 1.0
    flags_detected = Column(JSON, nullable=True)  # List of detected issues
    
    # Categories flagged
    inappropriate_content = Column(Boolean, default=False)
    nudity_detected = Column(Boolean, default=False)
    violence_detected = Column(Boolean, default=False)
    hate_speech_detected = Column(Boolean, default=False)
    spam_detected = Column(Boolean, default=False)
    
    # Manual review
    requires_human_review = Column(Boolean, default=False)
    reviewed_by_admin_id = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Actions taken
    action_taken = Column(String(50), nullable=True)  # approved, rejected, user_warned, etc.
    user_notified = Column(Boolean, default=False)

    def __repr__(self):
        return f"<ContentModeration(id={self.id}, type='{self.content_type}', approved={self.is_approved})>"

class TrustScore(Base, TimestampMixin):
    """User trust score calculation"""
    __tablename__ = "trust_scores"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, unique=True, index=True)
    
    # Overall score
    trust_score = Column(Float, nullable=False, default=0.5)  # 0.0 to 1.0
    
    # Component scores
    verification_score = Column(Float, default=0.0)  # Email, phone, ID verification
    activity_score = Column(Float, default=0.5)  # Regular, consistent activity
    community_score = Column(Float, default=0.5)  # Reports, warnings, etc.
    profile_quality_score = Column(Float, default=0.0)  # Completeness, photo quality
    
    # Factors
    days_since_registration = Column(Integer, default=0)
    login_frequency = Column(Float, default=0.0)
    profile_completion_rate = Column(Float, default=0.0)
    positive_interactions = Column(Integer, default=0)
    negative_reports = Column(Integer, default=0)
    
    # Last calculation
    last_calculated = Column(DateTime(timezone=True), nullable=False)
    calculation_version = Column(String(10), default="1.0")

    def __repr__(self):
        return f"<TrustScore(user_id={self.user_id}, score={self.trust_score})>"