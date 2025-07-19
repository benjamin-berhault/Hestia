from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Float, JSON, BigInteger
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from .base import TimestampMixin
import enum

class UserActivity(Base, TimestampMixin):
    """Track detailed user activities for analytics"""
    __tablename__ = "user_activities"

    id = Column(BigInteger, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Activity details
    activity_type = Column(String(50), nullable=False, index=True)  # login, profile_view, match_sent, etc.
    activity_data = Column(JSON, nullable=True)
    
    # Context
    session_id = Column(String(100), nullable=True)
    ip_address = Column(String(45), nullable=True)
    user_agent = Column(Text, nullable=True)
    referrer = Column(String(500), nullable=True)
    
    # Location data
    country = Column(String(50), nullable=True)
    region = Column(String(50), nullable=True)
    city = Column(String(100), nullable=True)
    
    # Device info
    device_type = Column(String(20), nullable=True)  # mobile, desktop, tablet
    os = Column(String(50), nullable=True)
    browser = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="activities")

    def __repr__(self):
        return f"<UserActivity(id={self.id}, user_id={self.user_id}, type='{self.activity_type}')>"

class MatchAnalytics(Base, TimestampMixin):
    """Track match success rates and patterns"""
    __tablename__ = "match_analytics"

    id = Column(Integer, primary_key=True, index=True)
    
    # Match details
    sender_id = Column(Integer, nullable=False, index=True)
    receiver_id = Column(Integer, nullable=False, index=True)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=True)
    
    # Compatibility scores
    algorithm_score = Column(Float, nullable=False)
    actual_outcome = Column(String(20), nullable=True)  # accepted, declined, ignored
    response_time_hours = Column(Integer, nullable=True)
    
    # Feature importance
    age_factor = Column(Float, nullable=True)
    location_factor = Column(Float, nullable=True)
    education_factor = Column(Float, nullable=True)
    family_goals_factor = Column(Float, nullable=True)
    religious_factor = Column(Float, nullable=True)
    lifestyle_factor = Column(Float, nullable=True)
    
    # Conversation outcome
    conversation_started = Column(Boolean, default=False)
    messages_exchanged = Column(Integer, default=0)
    conversation_lasted_hours = Column(Integer, nullable=True)
    relationship_outcome = Column(String(20), nullable=True)  # ongoing, ended, charter_created

    def __repr__(self):
        return f"<MatchAnalytics(id={self.id}, sender_id={self.sender_id}, receiver_id={self.receiver_id}, score={self.algorithm_score})>"

class PlatformMetrics(Base, TimestampMixin):
    """Daily platform-wide metrics"""
    __tablename__ = "platform_metrics"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    
    # User metrics
    total_users = Column(Integer, default=0)
    active_users_daily = Column(Integer, default=0)
    new_registrations = Column(Integer, default=0)
    verified_users = Column(Integer, default=0)
    premium_users = Column(Integer, default=0)
    
    # Profile metrics
    completed_profiles = Column(Integer, default=0)
    profiles_with_photos = Column(Integer, default=0)
    approved_photos = Column(Integer, default=0)
    
    # Matching metrics
    matches_sent = Column(Integer, default=0)
    matches_accepted = Column(Integer, default=0)
    match_acceptance_rate = Column(Float, default=0.0)
    mutual_matches = Column(Integer, default=0)
    
    # Communication metrics
    conversations_started = Column(Integer, default=0)
    messages_sent = Column(Integer, default=0)
    average_conversation_length = Column(Float, default=0.0)
    
    # Charter metrics
    charters_created = Column(Integer, default=0)
    charters_signed = Column(Integer, default=0)
    
    # Safety metrics
    reports_submitted = Column(Integer, default=0)
    accounts_suspended = Column(Integer, default=0)
    content_moderated = Column(Integer, default=0)
    
    # Business metrics
    revenue_daily = Column(Integer, default=0)  # in cents
    subscription_upgrades = Column(Integer, default=0)
    subscription_cancellations = Column(Integer, default=0)
    
    # Engagement metrics
    average_session_duration = Column(Float, default=0.0)
    page_views = Column(Integer, default=0)
    unique_visitors = Column(Integer, default=0)

    def __repr__(self):
        return f"<PlatformMetrics(id={self.id}, date='{self.date.date()}', active_users={self.active_users_daily})>"

class FeatureUsage(Base, TimestampMixin):
    """Track usage of specific platform features"""
    __tablename__ = "feature_usage"

    id = Column(Integer, primary_key=True, index=True)
    date = Column(DateTime(timezone=True), nullable=False, index=True)
    feature_name = Column(String(100), nullable=False, index=True)
    
    # Usage metrics
    total_uses = Column(Integer, default=0)
    unique_users = Column(Integer, default=0)
    premium_users = Column(Integer, default=0)
    
    # Performance metrics
    average_response_time = Column(Float, nullable=True)
    error_rate = Column(Float, default=0.0)
    
    # User feedback
    positive_feedback = Column(Integer, default=0)
    negative_feedback = Column(Integer, default=0)

    def __repr__(self):
        return f"<FeatureUsage(id={self.id}, feature='{self.feature_name}', uses={self.total_uses})>"