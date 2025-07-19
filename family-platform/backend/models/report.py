from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Boolean, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

class ReportType(enum.Enum):
    INAPPROPRIATE_PHOTOS = "inappropriate_photos"
    FAKE_PROFILE = "fake_profile"
    HARASSMENT = "harassment"
    INAPPROPRIATE_MESSAGES = "inappropriate_messages"
    SPAM = "spam"
    UNDERAGE = "underage"
    VIOLENT_CONTENT = "violent_content"
    HATE_SPEECH = "hate_speech"
    SCAM = "scam"
    OTHER = "other"

class ReportStatus(enum.Enum):
    PENDING = "pending"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    DISMISSED = "dismissed"
    ESCALATED = "escalated"

class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    reporter_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    reported_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Report details
    report_type = Column(SQLEnum(ReportType), nullable=False)
    description = Column(Text, nullable=False)
    evidence_urls = Column(Text, nullable=True)  # JSON array of URLs/object names
    
    # Context information
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=True)
    message_id = Column(Integer, ForeignKey("messages.id"), nullable=True)
    photo_id = Column(Integer, ForeignKey("user_photos.id"), nullable=True)
    
    # Moderation
    status = Column(SQLEnum(ReportStatus), default=ReportStatus.PENDING, nullable=False)
    priority = Column(String(20), default="normal", nullable=False)  # low, normal, high, urgent
    
    # Review process
    reviewed_by_admin_id = Column(Integer, nullable=True)  # Reference to admin user
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    action_taken = Column(String(100), nullable=True)  # warning_sent, user_suspended, content_removed, etc.
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    reporter = relationship("User", foreign_keys=[reporter_id], back_populates="reports_made")
    reported_user = relationship("User", foreign_keys=[reported_user_id], back_populates="reports_received")

    def __repr__(self):
        return f"<Report(id={self.id}, reporter_id={self.reporter_id}, reported_user_id={self.reported_user_id}, type='{self.report_type.value}', status='{self.status.value}')>"