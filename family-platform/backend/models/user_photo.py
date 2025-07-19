from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from .base import TimestampMixin
import enum

class PhotoStatus(enum.Enum):
    PENDING = "pending"
    APPROVED = "approved"
    REJECTED = "rejected"
    FLAGGED = "flagged"
    PROCESSING = "processing"

class UserPhoto(Base, TimestampMixin):
    __tablename__ = "user_photos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # MinIO object information
    object_name = Column(String(255), nullable=False, unique=True)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    
    # Photo metadata
    is_primary = Column(Boolean, default=False, nullable=False)
    status = Column(SQLEnum(PhotoStatus), default=PhotoStatus.PENDING, nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    
    # Image analysis
    width = Column(Integer, nullable=True)
    height = Column(Integer, nullable=True)
    dominant_colors = Column(JSON, nullable=True)
    brightness_score = Column(Float, nullable=True)
    quality_score = Column(Float, nullable=True)
    
    # AI moderation
    ai_moderation_score = Column(Float, nullable=True)  # 0.0 to 1.0
    ai_flags = Column(JSON, nullable=True)  # Array of detected issues
    nudity_confidence = Column(Float, nullable=True)
    violence_confidence = Column(Float, nullable=True)
    
    # Face detection
    faces_detected = Column(Integer, default=0, nullable=False)
    face_confidence = Column(Float, nullable=True)
    estimated_age = Column(Integer, nullable=True)
    estimated_gender = Column(String(20), nullable=True)
    
    # Manual review
    reviewed_by_admin_id = Column(Integer, nullable=True)
    reviewed_at = Column(DateTime(timezone=True), nullable=True)
    rejection_reason = Column(Text, nullable=True)
    review_notes = Column(Text, nullable=True)
    
    # Usage statistics
    view_count = Column(Integer, default=0, nullable=False)
    last_viewed = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="photos")

    def __repr__(self):
        return f"<UserPhoto(id={self.id}, user_id={self.user_id}, object_name='{self.object_name}', status='{self.status.value}')>"
        
    def is_approved(self) -> bool:
        """Check if photo is approved for display"""
        return self.status == PhotoStatus.APPROVED
    
    def needs_review(self) -> bool:
        """Check if photo needs manual review"""
        return self.status in [PhotoStatus.PENDING, PhotoStatus.FLAGGED]