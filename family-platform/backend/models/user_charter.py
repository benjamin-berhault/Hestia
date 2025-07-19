from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean, String, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

class CharterStatus(enum.Enum):
    DRAFT = "draft"
    PENDING_REVIEW = "pending_review"
    UNDER_NEGOTIATION = "under_negotiation"
    AGREED = "agreed"
    SIGNED = "signed"
    ACTIVE = "active"
    AMENDED = "amended"
    TERMINATED = "terminated"

class UserCharter(Base):
    __tablename__ = "user_charters"

    id = Column(Integer, primary_key=True, index=True)
    template_id = Column(Integer, ForeignKey("charter_templates.id"), nullable=True)
    
    # Users involved
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)  # Primary creator
    partner_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Partner (can be null if draft)
    
    # Charter content
    title = Column(String(200), nullable=False)
    charter_content = Column(Text, nullable=False)  # JSON structure with actual agreement content
    version = Column(Integer, default=1, nullable=False)
    
    # Status and approvals
    status = Column(SQLEnum(CharterStatus), default=CharterStatus.DRAFT, nullable=False)
    user_agreed = Column(Boolean, default=False, nullable=False)
    user_agreed_at = Column(DateTime(timezone=True), nullable=True)
    partner_agreed = Column(Boolean, default=False, nullable=False)
    partner_agreed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Digital signatures
    user_signature = Column(Text, nullable=True)  # Digital signature data
    partner_signature = Column(Text, nullable=True)
    
    # Amendment tracking
    previous_version_id = Column(Integer, ForeignKey("user_charters.id"), nullable=True)
    amendment_reason = Column(Text, nullable=True)
    
    # Dates
    effective_date = Column(DateTime(timezone=True), nullable=True)
    expiration_date = Column(DateTime(timezone=True), nullable=True)
    terminated_date = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    is_private = Column(Boolean, default=True, nullable=False)  # Not stored permanently on platform
    export_requested = Column(Boolean, default=False, nullable=False)
    exported_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    template = relationship("CharterTemplate", back_populates="user_charters")
    user = relationship("User", foreign_keys=[user_id], back_populates="charters")
    previous_version = relationship("UserCharter", remote_side=[id])

    def __repr__(self):
        return f"<UserCharter(id={self.id}, user_id={self.user_id}, partner_user_id={self.partner_user_id}, status='{self.status.value}', version={self.version})>"

    @property
    def is_fully_signed(self):
        """Check if both parties have signed the charter"""
        return self.user_agreed and self.partner_agreed and self.status == CharterStatus.SIGNED