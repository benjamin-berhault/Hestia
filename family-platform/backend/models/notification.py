from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from database import Base
from .base import TimestampMixin
import enum

class NotificationType(enum.Enum):
    MATCH_RECEIVED = "match_received"
    MATCH_ACCEPTED = "match_accepted"
    MESSAGE_RECEIVED = "message_received"
    PROFILE_VIEW = "profile_view"
    PHOTO_APPROVED = "photo_approved"
    PHOTO_REJECTED = "photo_rejected"
    SUBSCRIPTION_EXPIRING = "subscription_expiring"
    SECURITY_ALERT = "security_alert"
    SYSTEM_ANNOUNCEMENT = "system_announcement"
    CHARTER_INVITATION = "charter_invitation"
    CHARTER_SIGNED = "charter_signed"
    VIDEO_CALL_REQUEST = "video_call_request"
    SAFETY_WARNING = "safety_warning"
    REFERRAL_BONUS = "referral_bonus"

class Notification(Base, TimestampMixin):
    __tablename__ = "notifications"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Notification details
    type = Column(SQLEnum(NotificationType), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Status
    is_read = Column(Boolean, default=False, nullable=False)
    is_sent = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Delivery channels
    sent_via_email = Column(Boolean, default=False, nullable=False)
    sent_via_sms = Column(Boolean, default=False, nullable=False)
    sent_via_push = Column(Boolean, default=False, nullable=False)
    
    # Context data
    action_url = Column(String(500), nullable=True)
    related_user_id = Column(Integer, nullable=True)
    metadata = Column(JSON, nullable=True)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="notifications")

    def __repr__(self):
        return f"<Notification(id={self.id}, user_id={self.user_id}, type='{self.type.value}', is_read={self.is_read})>"