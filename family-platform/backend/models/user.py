from sqlalchemy import Boolean, Column, Integer, String, DateTime, Enum as SQLEnum, Float, Text, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from database import Base
from .base import TimestampMixin, SoftDeleteMixin, GeoLocationMixin
import enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class UserStatus(enum.Enum):
    PENDING_VERIFICATION = "pending_verification"
    ACTIVE = "active"
    SUSPENDED = "suspended"
    BANNED = "banned"
    DELETED = "deleted"
    INCOMPLETE_PROFILE = "incomplete_profile"
    PREMIUM = "premium"

class UserRole(enum.Enum):
    USER = "user"
    MODERATOR = "moderator"
    ADMIN = "admin"
    SUPER_ADMIN = "super_admin"

class SubscriptionPlan(enum.Enum):
    FREE = "free"
    PREMIUM_MONTHLY = "premium_monthly"
    PREMIUM_ANNUAL = "premium_annual"
    LIFETIME = "lifetime"

class User(Base, TimestampMixin, SoftDeleteMixin, GeoLocationMixin):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    
    # Authentication
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    phone_number = Column(String(20), unique=True, index=True, nullable=True)
    
    # Verification
    is_email_verified = Column(Boolean, default=False)
    is_phone_verified = Column(Boolean, default=False)
    is_id_verified = Column(Boolean, default=False)
    is_background_checked = Column(Boolean, default=False)
    
    # Verification tokens
    email_verification_token = Column(String(255), nullable=True)
    phone_verification_token = Column(String(10), nullable=True)
    password_reset_token = Column(String(255), nullable=True)
    phone_verification_expires = Column(DateTime(timezone=True), nullable=True)
    password_reset_expires = Column(DateTime(timezone=True), nullable=True)
    
    # User status and role
    status = Column(SQLEnum(UserStatus), default=UserStatus.PENDING_VERIFICATION, nullable=False)
    role = Column(SQLEnum(UserRole), default=UserRole.USER, nullable=False)
    
    # Activity tracking
    last_login = Column(DateTime(timezone=True), nullable=True)
    last_seen = Column(DateTime(timezone=True), nullable=True)
    login_count = Column(Integer, default=0, nullable=False)
    
    # Profile completion
    profile_completion_percentage = Column(Integer, default=0, nullable=False)
    onboarding_completed = Column(Boolean, default=False, nullable=False)
    onboarding_step = Column(String(50), default="registration", nullable=False)
    
    # Subscription and billing
    subscription_plan = Column(SQLEnum(SubscriptionPlan), default=SubscriptionPlan.FREE, nullable=False)
    subscription_expires = Column(DateTime(timezone=True), nullable=True)
    stripe_customer_id = Column(String(100), nullable=True)
    
    # Platform engagement
    daily_matches_used = Column(Integer, default=0, nullable=False)
    daily_messages_sent = Column(Integer, default=0, nullable=False)
    last_daily_reset = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Safety and moderation
    warning_count = Column(Integer, default=0, nullable=False)
    suspension_count = Column(Integer, default=0, nullable=False)
    last_warning_date = Column(DateTime(timezone=True), nullable=True)
    suspension_expires = Column(DateTime(timezone=True), nullable=True)
    
    # Privacy settings
    privacy_settings = Column(JSON, default=lambda: {
        "show_online_status": True,
        "allow_messages_from": "matches_only",  # all, matches_only, premium_only
        "show_distance": True,
        "show_last_seen": True,
        "profile_visibility": "public"  # public, members_only, hidden
    })
    
    # Communication preferences
    notification_preferences = Column(JSON, default=lambda: {
        "email_notifications": True,
        "sms_notifications": False,
        "push_notifications": True,
        "match_notifications": True,
        "message_notifications": True,
        "marketing_emails": False
    })
    
    # Analytics and AI
    personality_scores = Column(JSON, nullable=True)  # Big 5 personality traits
    compatibility_weights = Column(JSON, nullable=True)  # Custom matching weights
    ai_insights = Column(JSON, nullable=True)  # AI-generated insights
    
    # Referral system
    referral_code = Column(String(20), unique=True, nullable=True)
    referred_by_id = Column(Integer, nullable=True)
    referral_earnings = Column(Integer, default=0, nullable=False)  # In cents
    
    # Device and security
    device_tokens = Column(JSON, default=list)  # For push notifications
    two_factor_enabled = Column(Boolean, default=False, nullable=False)
    two_factor_secret = Column(String(32), nullable=True)
    trusted_devices = Column(JSON, default=list)
    
    # Relationships
    profile = relationship("UserProfile", back_populates="user", uselist=False, cascade="all, delete-orphan")
    photos = relationship("UserPhoto", back_populates="user", cascade="all, delete-orphan")
    preferences = relationship("UserPreferences", back_populates="user", uselist=False, cascade="all, delete-orphan")
    
    # Matching and communication
    sent_matches = relationship("Match", foreign_keys="[Match.sender_id]", back_populates="sender", cascade="all, delete-orphan")
    received_matches = relationship("Match", foreign_keys="[Match.receiver_id]", back_populates="receiver", cascade="all, delete-orphan")
    sent_conversations = relationship("Conversation", foreign_keys="[Conversation.user1_id]", back_populates="user1", cascade="all, delete-orphan")
    received_conversations = relationship("Conversation", foreign_keys="[Conversation.user2_id]", back_populates="user2", cascade="all, delete-orphan")
    messages = relationship("Message", back_populates="sender", cascade="all, delete-orphan")
    
    # Charter system
    charters = relationship("UserCharter", back_populates="user", cascade="all, delete-orphan")
    
    # Safety and moderation
    reports_made = relationship("Report", foreign_keys="[Report.reporter_id]", back_populates="reporter")
    reports_received = relationship("Report", foreign_keys="[Report.reported_user_id]", back_populates="reported_user")
    safety_alerts = relationship("SafetyAlert", back_populates="user", cascade="all, delete-orphan")
    
    # Business features
    payments = relationship("Payment", back_populates="user", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="user", cascade="all, delete-orphan")
    activities = relationship("UserActivity", back_populates="user", cascade="all, delete-orphan")
    support_tickets = relationship("SupportTicket", back_populates="user", cascade="all, delete-orphan")
    
    # Referrals
    referrals_made = relationship("Referral", foreign_keys="[Referral.referrer_id]", back_populates="referrer")
    referral_received = relationship("Referral", foreign_keys="[Referral.referred_id]", back_populates="referred", uselist=False)

    def __repr__(self):
        return f"<User(id={self.id}, email='{self.email}', status='{self.status.value}')>"

    @hybrid_property
    def is_premium(self) -> bool:
        """Check if user has active premium subscription"""
        if self.subscription_plan == SubscriptionPlan.FREE:
            return False
        if self.subscription_plan == SubscriptionPlan.LIFETIME:
            return True
        return self.subscription_expires and self.subscription_expires > datetime.utcnow()

    @hybrid_property
    def is_online(self) -> bool:
        """Check if user is currently online (seen within 5 minutes)"""
        if not self.last_seen:
            return False
        return (datetime.utcnow() - self.last_seen) < timedelta(minutes=5)

    @hybrid_property
    def age(self) -> Optional[int]:
        """Get user age from profile"""
        if self.profile and self.profile.date_of_birth:
            today = datetime.today()
            birth_date = self.profile.date_of_birth
            return today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
        return None

    def reset_daily_limits(self):
        """Reset daily usage limits"""
        today = datetime.utcnow().date()
        last_reset = self.last_daily_reset.date() if self.last_daily_reset else None
        
        if last_reset != today:
            self.daily_matches_used = 0
            self.daily_messages_sent = 0
            self.last_daily_reset = datetime.utcnow()

    def can_send_match(self) -> bool:
        """Check if user can send more matches today"""
        self.reset_daily_limits()
        max_matches = 50 if self.is_premium else 10
        return self.daily_matches_used < max_matches

    def can_send_message(self) -> bool:
        """Check if user can send more messages today"""
        if self.is_premium:
            return True
        self.reset_daily_limits()
        return self.daily_messages_sent < 20  # Free tier limit

    def update_last_seen(self):
        """Update last seen timestamp"""
        self.last_seen = datetime.utcnow()

    def increment_login_count(self):
        """Increment login count and update last login"""
        self.login_count += 1
        self.last_login = datetime.utcnow()
        self.update_last_seen()

    def add_warning(self, reason: str = None):
        """Add a warning to the user"""
        self.warning_count += 1
        self.last_warning_date = datetime.utcnow()
        
        # Auto-suspend after 3 warnings
        if self.warning_count >= 3:
            self.suspend(days=7, reason="Multiple warnings")

    def suspend(self, days: int = 7, reason: str = None):
        """Suspend user for specified number of days"""
        self.status = UserStatus.SUSPENDED
        self.suspension_count += 1
        self.suspension_expires = datetime.utcnow() + timedelta(days=days)

    def lift_suspension(self):
        """Remove suspension"""
        if self.status == UserStatus.SUSPENDED:
            self.status = UserStatus.ACTIVE
            self.suspension_expires = None

    def ban(self, reason: str = None):
        """Permanently ban user"""
        self.status = UserStatus.BANNED
        self.suspension_expires = None

    def calculate_profile_completion(self) -> int:
        """Calculate profile completion percentage"""
        completion = 0
        total_steps = 10
        
        # Basic info (2 points)
        if self.email and self.is_email_verified:
            completion += 2
        
        # Profile data (3 points)
        if self.profile:
            if self.profile.first_name and self.profile.last_name:
                completion += 1
            if self.profile.bio and len(self.profile.bio) >= 100:
                completion += 1
            if self.profile.family_vision and len(self.profile.family_vision) >= 50:
                completion += 1
        
        # Photos (2 points)
        approved_photos = len([p for p in self.photos if p.is_approved])
        if approved_photos >= 1:
            completion += 1
        if approved_photos >= 3:
            completion += 1
        
        # Preferences (2 points)
        if self.preferences:
            completion += 2
        
        # Verification (1 point)
        if self.is_id_verified or self.is_phone_verified:
            completion += 1
        
        percentage = int((completion / total_steps) * 100)
        self.profile_completion_percentage = percentage
        return percentage

class Subscription(Base, TimestampMixin):
    """User subscription tracking"""
    __tablename__ = "subscriptions"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False, index=True)
    plan = Column(SQLEnum(SubscriptionPlan), nullable=False)
    status = Column(String(20), nullable=False)  # active, canceled, expired
    
    # Billing
    stripe_subscription_id = Column(String(100), nullable=True)
    current_period_start = Column(DateTime(timezone=True), nullable=False)
    current_period_end = Column(DateTime(timezone=True), nullable=False)
    canceled_at = Column(DateTime(timezone=True), nullable=True)
    
    # Features
    features = Column(JSON, default=lambda: {
        "unlimited_matches": False,
        "unlimited_messages": False,
        "priority_support": False,
        "advanced_filters": False,
        "read_receipts": False,
        "video_calls": False
    })

    def __repr__(self):
        return f"<Subscription(id={self.id}, user_id={self.user_id}, plan='{self.plan.value}', status='{self.status}')>"