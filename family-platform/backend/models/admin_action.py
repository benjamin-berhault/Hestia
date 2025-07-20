from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

class AdminActionType(enum.Enum):
    USER_SUSPENDED = "user_suspended"
    USER_BANNED = "user_banned"
    USER_REINSTATED = "user_reinstated"
    PROFILE_APPROVED = "profile_approved"
    PROFILE_REJECTED = "profile_rejected"
    PHOTO_APPROVED = "photo_approved"
    PHOTO_REJECTED = "photo_rejected"
    CONTENT_REMOVED = "content_removed"
    REPORT_RESOLVED = "report_resolved"
    REPORT_DISMISSED = "report_dismissed"
    WARNING_SENT = "warning_sent"
    ACCOUNT_VERIFIED = "account_verified"
    CHARTER_TEMPLATE_CREATED = "charter_template_created"
    CHARTER_TEMPLATE_MODIFIED = "charter_template_modified"
    SYSTEM_SETTINGS_CHANGED = "system_settings_changed"
    BULK_ACTION_PERFORMED = "bulk_action_performed"

class AdminAction(Base):
    __tablename__ = "admin_actions"

    id = Column(Integer, primary_key=True, index=True)
    admin_user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    
    # Action details
    action_type = Column(SQLEnum(AdminActionType), nullable=False)
    description = Column(Text, nullable=False)
    reason = Column(Text, nullable=True)
    
    # Context references
    report_id = Column(Integer, ForeignKey("reports.id"), nullable=True)
    affected_content_type = Column(String(50), nullable=True)  # profile, photo, message, etc.
    affected_content_id = Column(Integer, nullable=True)
    
    # Action metadata
    ip_address = Column(String(45), nullable=True)  # IPv6 compatible
    user_agent = Column(String(500), nullable=True)
    additional_data = Column(Text, nullable=True)  # JSON for any extra data
    
    # Duration (for temporary actions like suspensions)
    duration_hours = Column(Integer, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    def __repr__(self):
        return f"<AdminAction(id={self.id}, admin_user_id={self.admin_user_id}, target_user_id={self.target_user_id}, action_type='{self.action_type.value}')>"