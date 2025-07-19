from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from database import Base
from .base import TimestampMixin
import enum

class ReferralStatus(enum.Enum):
    PENDING = "pending"
    COMPLETED = "completed"
    EXPIRED = "expired"
    CANCELED = "canceled"

class Referral(Base, TimestampMixin):
    """User referral tracking"""
    __tablename__ = "referrals"

    id = Column(Integer, primary_key=True, index=True)
    referrer_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    referred_id = Column(Integer, ForeignKey("users.id"), nullable=True, index=True)
    
    # Referral details
    referral_code = Column(String(20), nullable=False, index=True)
    status = Column(SQLEnum(ReferralStatus), default=ReferralStatus.PENDING, nullable=False)
    
    # Completion tracking
    referred_email = Column(String(255), nullable=True)
    registration_completed = Column(Boolean, default=False)
    profile_completed = Column(Boolean, default=False)
    first_payment_made = Column(Boolean, default=False)
    
    # Rewards
    referrer_reward_amount = Column(Integer, default=0)  # In cents
    referred_reward_amount = Column(Integer, default=0)  # In cents
    reward_paid = Column(Boolean, default=False)
    reward_paid_at = Column(DateTime(timezone=True), nullable=True)
    
    # Tracking
    click_count = Column(Integer, default=0)
    last_clicked = Column(DateTime(timezone=True), nullable=True)
    source = Column(String(50), nullable=True)  # email, social, direct, etc.
    
    # Relationships
    referrer = relationship("User", foreign_keys=[referrer_id], back_populates="referrals_made")
    referred = relationship("User", foreign_keys=[referred_id], back_populates="referral_received")

    def __repr__(self):
        return f"<Referral(id={self.id}, referrer_id={self.referrer_id}, code='{self.referral_code}', status='{self.status.value}')>"