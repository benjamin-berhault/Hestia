from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON
from sqlalchemy.orm import relationship
from database import Base
from .base import TimestampMixin
import enum

class PaymentStatus(enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELED = "canceled"
    REFUNDED = "refunded"

class PaymentMethod(enum.Enum):
    CREDIT_CARD = "credit_card"
    DEBIT_CARD = "debit_card"
    PAYPAL = "paypal"
    APPLE_PAY = "apple_pay"
    GOOGLE_PAY = "google_pay"
    BANK_TRANSFER = "bank_transfer"

class Payment(Base, TimestampMixin):
    """Payment transactions"""
    __tablename__ = "payments"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Payment details
    amount = Column(Integer, nullable=False)  # Amount in cents
    currency = Column(String(3), default="USD", nullable=False)
    description = Column(Text, nullable=True)
    
    # Status and processing
    status = Column(SQLEnum(PaymentStatus), default=PaymentStatus.PENDING, nullable=False)
    payment_method = Column(SQLEnum(PaymentMethod), nullable=False)
    
    # External payment processor
    stripe_payment_intent_id = Column(String(100), nullable=True)
    stripe_customer_id = Column(String(100), nullable=True)
    external_transaction_id = Column(String(100), nullable=True)
    
    # Subscription related
    subscription_id = Column(Integer, nullable=True)
    subscription_period_start = Column(DateTime(timezone=True), nullable=True)
    subscription_period_end = Column(DateTime(timezone=True), nullable=True)
    
    # Billing details
    billing_address = Column(JSON, nullable=True)
    tax_amount = Column(Integer, default=0)  # In cents
    discount_amount = Column(Integer, default=0)  # In cents
    
    # Processing details
    processed_at = Column(DateTime(timezone=True), nullable=True)
    failure_reason = Column(Text, nullable=True)
    refund_amount = Column(Integer, default=0)  # In cents
    refunded_at = Column(DateTime(timezone=True), nullable=True)
    
    # Metadata
    metadata = Column(JSON, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="payments")

    def __repr__(self):
        return f"<Payment(id={self.id}, user_id={self.user_id}, amount=${self.amount/100:.2f}, status='{self.status.value}')>"

class PaymentCard(Base, TimestampMixin):
    """Stored payment methods for users"""
    __tablename__ = "payment_cards"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Card details (PCI compliant - stored at Stripe)
    stripe_payment_method_id = Column(String(100), nullable=False)
    card_brand = Column(String(20), nullable=True)  # visa, mastercard, etc.
    last_four = Column(String(4), nullable=True)
    exp_month = Column(Integer, nullable=True)
    exp_year = Column(Integer, nullable=True)
    
    # Settings
    is_default = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    
    # Usage tracking
    last_used = Column(DateTime(timezone=True), nullable=True)
    usage_count = Column(Integer, default=0)

    def __repr__(self):
        return f"<PaymentCard(id={self.id}, user_id={self.user_id}, brand='{self.card_brand}', last_four='****{self.last_four}')>"