from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from database import Base
from .base import TimestampMixin
import enum

class TicketStatus(enum.Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    WAITING_FOR_CUSTOMER = "waiting_for_customer"
    RESOLVED = "resolved"
    CLOSED = "closed"

class TicketCategory(enum.Enum):
    TECHNICAL_ISSUE = "technical_issue"
    ACCOUNT_PROBLEM = "account_problem"
    BILLING_QUESTION = "billing_question"
    SAFETY_CONCERN = "safety_concern"
    FEATURE_REQUEST = "feature_request"
    GENERAL_INQUIRY = "general_inquiry"
    BUG_REPORT = "bug_report"
    HARASSMENT_REPORT = "harassment_report"
    VERIFICATION_ISSUE = "verification_issue"

class SupportTicket(Base, TimestampMixin):
    """Customer support tickets"""
    __tablename__ = "support_tickets"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Ticket details
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(TicketCategory), nullable=False)
    priority = Column(String(20), default="normal", nullable=False)  # low, normal, high, urgent
    
    # Status tracking
    status = Column(SQLEnum(TicketStatus), default=TicketStatus.OPEN, nullable=False)
    assigned_to_admin_id = Column(Integer, nullable=True)
    
    # Communication
    last_response_by = Column(String(20), nullable=True)  # customer, admin
    last_response_at = Column(DateTime(timezone=True), nullable=True)
    customer_satisfaction_rating = Column(Integer, nullable=True)  # 1-5 stars
    
    # Resolution
    resolved_at = Column(DateTime(timezone=True), nullable=True)
    resolution_notes = Column(Text, nullable=True)
    
    # Metadata
    attachments = Column(JSON, nullable=True)  # MinIO object names
    tags = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="support_tickets")

    def __repr__(self):
        return f"<SupportTicket(id={self.id}, user_id={self.user_id}, category='{self.category.value}', status='{self.status.value}')>"