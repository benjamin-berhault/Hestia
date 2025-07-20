from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, ForeignKey, Enum as SQLEnum, JSON, Float
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base
from .base import TimestampMixin, AuditMixin
import enum
from datetime import datetime, timedelta
from typing import Dict, List, Optional

class DevelopmentCategory(enum.Enum):
    FITNESS = "fitness"
    PRACTICAL_SKILLS = "practical_skills"
    SOCIAL = "social"
    FINANCIAL = "financial"
    INTELLECTUAL = "intellectual"
    EMOTIONAL = "emotional"
    CAREER = "career"
    LIFESTYLE = "lifestyle"

class GoalDifficulty(enum.Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"
    EXPERT = "expert"

class ChallengeType(enum.Enum):
    DAILY = "daily"
    WEEKLY = "weekly"
    MONTHLY = "monthly"
    MILESTONE = "milestone"

class AchievementStatus(enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    VERIFIED = "verified"
    EXPIRED = "expired"

class MentorshipStatus(enum.Enum):
    PENDING = "pending"
    ACTIVE = "active"
    COMPLETED = "completed"
    PAUSED = "paused"
    ENDED = "ended"

class PersonalDevelopmentGoal(Base, TimestampMixin):
    """User's personal development goals and targets"""
    __tablename__ = "personal_development_goals"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Goal details
    category = Column(SQLEnum(DevelopmentCategory), nullable=False)
    difficulty = Column(SQLEnum(GoalDifficulty), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    target_description = Column(Text, nullable=False)
    
    # Timeline
    start_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    target_date = Column(DateTime(timezone=True), nullable=False)
    completed_date = Column(DateTime(timezone=True), nullable=True)
    
    # Progress tracking
    status = Column(SQLEnum(AchievementStatus), default=AchievementStatus.NOT_STARTED, nullable=False)
    progress_percentage = Column(Integer, default=0, nullable=False)
    current_value = Column(Float, nullable=True)  # Current metric value
    target_value = Column(Float, nullable=True)   # Target metric value
    unit = Column(String(50), nullable=True)      # Unit of measurement
    
    # Documentation
    progress_notes = Column(JSON, default=list)  # Array of progress updates
    before_photos = Column(JSON, default=list)   # MinIO object names
    progress_photos = Column(JSON, default=list) # Progress documentation
    after_photos = Column(JSON, default=list)    # Completion photos
    skill_demonstrations = Column(JSON, default=list) # Video/photo proofs
    
    # Gamification
    points_earned = Column(Integer, default=0, nullable=False)
    badges_earned = Column(JSON, default=list)   # Badge IDs earned
    is_public = Column(Boolean, default=True, nullable=False)
    featured = Column(Boolean, default=False, nullable=False)
    
    # Community
    mentor_feedback = Column(Text, nullable=True)
    peer_encouragements = Column(Integer, default=0, nullable=False)
    success_story = Column(Text, nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="development_goals")
    skill_challenges = relationship("SkillChallenge", back_populates="related_goal")

    def __repr__(self):
        return f"<PersonalDevelopmentGoal(id={self.id}, user_id={self.user_id}, title='{self.title}', status='{self.status.value}')>"

    def calculate_progress(self) -> int:
        """Calculate progress percentage based on current vs target values"""
        if self.target_value and self.current_value is not None:
            progress = min((self.current_value / self.target_value) * 100, 100)
            self.progress_percentage = int(progress)
            return self.progress_percentage
        return self.progress_percentage

    def add_progress_update(self, description: str, photos: List[str] = None, value: float = None):
        """Add a progress update with optional photos and metrics"""
        update = {
            "date": datetime.utcnow().isoformat(),
            "description": description,
            "photos": photos or [],
            "value": value,
            "progress_percentage": self.progress_percentage
        }
        
        if not self.progress_notes:
            self.progress_notes = []
        self.progress_notes.append(update)
        
        if value is not None:
            self.current_value = value
            self.calculate_progress()

class SkillChallenge(Base, TimestampMixin):
    """Monthly/weekly skill challenges for personal development"""
    __tablename__ = "skill_challenges"

    id = Column(Integer, primary_key=True, index=True)
    
    # Challenge details
    category = Column(SQLEnum(DevelopmentCategory), nullable=False)
    difficulty = Column(SQLEnum(GoalDifficulty), nullable=False)
    challenge_type = Column(SQLEnum(ChallengeType), nullable=False)
    title = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    instructions = Column(Text, nullable=False)
    
    # Requirements
    success_criteria = Column(JSON, nullable=False)  # What constitutes success
    required_evidence = Column(JSON, nullable=False) # Photos, videos, documents needed
    minimum_effort_days = Column(Integer, default=1, nullable=False)
    
    # Timeline
    start_date = Column(DateTime(timezone=True), nullable=False)
    end_date = Column(DateTime(timezone=True), nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Gamification
    base_points = Column(Integer, nullable=False)
    bonus_points = Column(Integer, default=0, nullable=False)
    badge_reward = Column(String(100), nullable=True)
    
    # Community features
    max_participants = Column(Integer, nullable=True)
    current_participants = Column(Integer, default=0, nullable=False)
    is_group_challenge = Column(Boolean, default=False, nullable=False)
    
    # Content
    example_submissions = Column(JSON, default=list)  # Examples of good submissions
    tips_and_tricks = Column(Text, nullable=True)
    related_resources = Column(JSON, default=list)    # Helpful links/resources
    
    # Tracking
    related_goal_id = Column(Integer, ForeignKey("personal_development_goals.id"), nullable=True)
    created_by_admin = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    related_goal = relationship("PersonalDevelopmentGoal", back_populates="skill_challenges")
    participations = relationship("ChallengeParticipation", back_populates="challenge")

    def __repr__(self):
        return f"<SkillChallenge(id={self.id}, title='{self.title}', category='{self.category.value}')>"

    def is_currently_active(self) -> bool:
        """Check if challenge is currently active"""
        now = datetime.utcnow()
        return self.is_active and self.start_date <= now <= self.end_date

    def can_participate(self, user) -> bool:
        """Check if user can participate in this challenge"""
        if not self.is_currently_active():
            return False
        
        # Check if user already participating
        existing = ChallengeParticipation.query.filter_by(
            user_id=user.id, 
            challenge_id=self.id
        ).first()
        
        if existing:
            return False
        
        # Check max participants
        if self.max_participants and self.current_participants >= self.max_participants:
            return False
        
        return True

class ChallengeParticipation(Base, TimestampMixin):
    """User participation in skill challenges"""
    __tablename__ = "challenge_participations"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    challenge_id = Column(Integer, ForeignKey("skill_challenges.id"), nullable=False, index=True)
    
    # Participation details
    started_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    completed_date = Column(DateTime(timezone=True), nullable=True)
    status = Column(SQLEnum(AchievementStatus), default=AchievementStatus.IN_PROGRESS, nullable=False)
    
    # Submission
    submission_text = Column(Text, nullable=True)
    submission_photos = Column(JSON, default=list)   # Evidence photos
    submission_videos = Column(JSON, default=list)   # Evidence videos
    submission_documents = Column(JSON, default=list) # Additional documents
    
    # Progress tracking
    daily_checkins = Column(JSON, default=list)      # Daily progress updates
    effort_days_completed = Column(Integer, default=0, nullable=False)
    progress_percentage = Column(Integer, default=0, nullable=False)
    
    # Review and scoring
    reviewed_by_admin = Column(Boolean, default=False, nullable=False)
    admin_feedback = Column(Text, nullable=True)
    peer_votes = Column(Integer, default=0, nullable=False)
    quality_score = Column(Float, nullable=True)     # 0.0 to 1.0
    
    # Rewards
    points_earned = Column(Integer, default=0, nullable=False)
    badge_earned = Column(String(100), nullable=True)
    featured = Column(Boolean, default=False, nullable=False)
    
    # Community recognition
    encouragements_received = Column(Integer, default=0, nullable=False)
    mentor_comments = Column(JSON, default=list)
    
    # Relationships
    user = relationship("User", back_populates="challenge_participations")
    challenge = relationship("SkillChallenge", back_populates="participations")

    def __repr__(self):
        return f"<ChallengeParticipation(id={self.id}, user_id={self.user_id}, challenge_id={self.challenge_id}, status='{self.status.value}')>"

    def add_daily_checkin(self, description: str, photos: List[str] = None):
        """Add a daily check-in update"""
        checkin = {
            "date": datetime.utcnow().isoformat(),
            "description": description,
            "photos": photos or []
        }
        
        if not self.daily_checkins:
            self.daily_checkins = []
        self.daily_checkins.append(checkin)
        self.effort_days_completed += 1

class MentorshipPair(Base, TimestampMixin):
    """Mentorship relationships between users"""
    __tablename__ = "mentorship_pairs"

    id = Column(Integer, primary_key=True, index=True)
    mentor_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    mentee_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Relationship details
    status = Column(SQLEnum(MentorshipStatus), default=MentorshipStatus.PENDING, nullable=False)
    focus_areas = Column(JSON, nullable=False)        # Areas mentor will help with
    goals = Column(Text, nullable=False)              # Mentorship goals
    
    # Timeline
    started_date = Column(DateTime(timezone=True), nullable=True)
    planned_duration_weeks = Column(Integer, default=12, nullable=False)
    ended_date = Column(DateTime(timezone=True), nullable=True)
    
    # Communication
    last_contact_date = Column(DateTime(timezone=True), nullable=True)
    total_sessions = Column(Integer, default=0, nullable=False)
    planned_sessions_per_week = Column(Integer, default=1, nullable=False)
    
    # Progress tracking
    mentee_progress_rating = Column(Integer, nullable=True)  # 1-5 scale
    mentor_satisfaction = Column(Integer, nullable=True)     # 1-5 scale
    mentee_satisfaction = Column(Integer, nullable=True)     # 1-5 scale
    
    # Feedback
    mentor_notes = Column(Text, nullable=True)
    mentee_feedback = Column(Text, nullable=True)
    success_stories = Column(Text, nullable=True)
    
    # Matching criteria
    preferred_communication = Column(String(50), nullable=True)  # video, voice, text
    meeting_frequency = Column(String(50), nullable=True)        # weekly, biweekly, monthly
    timezone_preference = Column(String(50), nullable=True)
    
    # Relationships
    mentor = relationship("User", foreign_keys=[mentor_id], back_populates="mentoring_relationships")
    mentee = relationship("User", foreign_keys=[mentee_id], back_populates="mentee_relationships")

    def __repr__(self):
        return f"<MentorshipPair(id={self.id}, mentor_id={self.mentor_id}, mentee_id={self.mentee_id}, status='{self.status.value}')>"

class AchievementBadge(Base, TimestampMixin):
    """Achievement badges for user accomplishments"""
    __tablename__ = "achievement_badges"

    id = Column(Integer, primary_key=True, index=True)
    
    # Badge details
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(DevelopmentCategory), nullable=False)
    difficulty = Column(SQLEnum(GoalDifficulty), nullable=False)
    
    # Visual
    icon_url = Column(String(500), nullable=False)
    color_scheme = Column(String(50), nullable=False)
    
    # Requirements
    requirements = Column(JSON, nullable=False)       # What's needed to earn it
    points_required = Column(Integer, nullable=True)
    challenges_required = Column(Integer, nullable=True)
    time_period_days = Column(Integer, nullable=True)
    
    # Gamification
    points_reward = Column(Integer, nullable=False)
    is_rare = Column(Boolean, default=False, nullable=False)
    is_active = Column(Boolean, default=True, nullable=False)
    
    # Stats
    total_earned = Column(Integer, default=0, nullable=False)
    
    # Relationships
    user_badges = relationship("UserBadge", back_populates="badge")

    def __repr__(self):
        return f"<AchievementBadge(id={self.id}, name='{self.name}', category='{self.category.value}')>"

class UserBadge(Base, TimestampMixin):
    """User's earned badges"""
    __tablename__ = "user_badges"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    badge_id = Column(Integer, ForeignKey("achievement_badges.id"), nullable=False, index=True)
    
    # Earning details
    earned_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    points_earned = Column(Integer, nullable=False)
    evidence_data = Column(JSON, nullable=True)       # How they earned it
    
    # Display
    is_featured = Column(Boolean, default=False, nullable=False)
    is_public = Column(Boolean, default=True, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="badges")
    badge = relationship("AchievementBadge", back_populates="user_badges")

    def __repr__(self):
        return f"<UserBadge(id={self.id}, user_id={self.user_id}, badge_id={self.badge_id})>"

class PeerSupportGroup(Base, TimestampMixin):
    """Brotherhood circles for peer support"""
    __tablename__ = "peer_support_groups"

    id = Column(Integer, primary_key=True, index=True)
    
    # Group details
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    focus_category = Column(SQLEnum(DevelopmentCategory), nullable=True)
    group_type = Column(String(50), nullable=False)   # beginner, intermediate, advanced, mixed
    
    # Settings
    max_members = Column(Integer, default=8, nullable=False)
    current_members = Column(Integer, default=0, nullable=False)
    is_private = Column(Boolean, default=False, nullable=False)
    requires_approval = Column(Boolean, default=True, nullable=False)
    
    # Management
    created_by_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    moderator_ids = Column(JSON, default=list)        # User IDs who can moderate
    
    # Activity
    last_activity = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    total_posts = Column(Integer, default=0, nullable=False)
    weekly_check_ins = Column(Boolean, default=True, nullable=False)
    
    # Goals
    group_goals = Column(JSON, default=list)          # Shared group goals
    success_stories = Column(JSON, default=list)      # Member success stories
    
    # Relationships
    created_by = relationship("User", foreign_keys=[created_by_id])
    memberships = relationship("GroupMembership", back_populates="group")

    def __repr__(self):
        return f"<PeerSupportGroup(id={self.id}, name='{self.name}', members={self.current_members})>"

class GroupMembership(Base, TimestampMixin):
    """User membership in peer support groups"""
    __tablename__ = "group_memberships"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    group_id = Column(Integer, ForeignKey("peer_support_groups.id"), nullable=False, index=True)
    
    # Membership details
    joined_date = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    status = Column(String(20), default="active", nullable=False)  # active, inactive, removed
    role = Column(String(20), default="member", nullable=False)    # member, moderator, leader
    
    # Participation
    last_activity = Column(DateTime(timezone=True), nullable=True)
    posts_count = Column(Integer, default=0, nullable=False)
    encouragements_given = Column(Integer, default=0, nullable=False)
    check_ins_completed = Column(Integer, default=0, nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="group_memberships")
    group = relationship("PeerSupportGroup", back_populates="memberships")

    def __repr__(self):
        return f"<GroupMembership(id={self.id}, user_id={self.user_id}, group_id={self.group_id}, role='{self.role}')>"

class FeedbackRequest(Base, TimestampMixin):
    """Anonymous feedback requests from users"""
    __tablename__ = "feedback_requests"

    id = Column(Integer, primary_key=True, index=True)
    requesting_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Request details
    feedback_type = Column(String(50), nullable=False)  # profile, photos, messaging, general
    specific_area = Column(String(100), nullable=True)   # What specific aspect needs feedback
    description = Column(Text, nullable=False)
    
    # Content to review
    profile_snapshot = Column(JSON, nullable=True)       # Profile data at time of request
    photo_urls = Column(JSON, default=list)              # Photos to review
    message_examples = Column(JSON, default=list)        # Message examples
    
    # Settings
    anonymous_feedback = Column(Boolean, default=True, nullable=False)
    feedback_from_women = Column(Boolean, default=True, nullable=False)
    feedback_from_men = Column(Boolean, default=True, nullable=False)
    max_responses = Column(Integer, default=5, nullable=False)
    
    # Status
    is_active = Column(Boolean, default=True, nullable=False)
    expires_at = Column(DateTime(timezone=True), nullable=False)
    responses_received = Column(Integer, default=0, nullable=False)
    
    # Relationships
    requesting_user = relationship("User", back_populates="feedback_requests")
    feedback_responses = relationship("FeedbackResponse", back_populates="request")

    def __repr__(self):
        return f"<FeedbackRequest(id={self.id}, user_id={self.requesting_user_id}, type='{self.feedback_type}')>"

class FeedbackResponse(Base, TimestampMixin):
    """Anonymous feedback responses"""
    __tablename__ = "feedback_responses"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("feedback_requests.id"), nullable=False, index=True)
    responding_user_id = Column(Integer, ForeignKey("users.id"), nullable=False, index=True)
    
    # Response content
    overall_rating = Column(Integer, nullable=False)     # 1-5 scale
    specific_feedback = Column(Text, nullable=False)
    suggestions = Column(Text, nullable=True)
    
    # Ratings breakdown
    profile_rating = Column(Integer, nullable=True)      # 1-5 scale
    photos_rating = Column(Integer, nullable=True)       # 1-5 scale
    messaging_rating = Column(Integer, nullable=True)    # 1-5 scale
    
    # Feedback details
    positive_aspects = Column(JSON, default=list)        # What's working well
    improvement_areas = Column(JSON, default=list)       # What needs work
    red_flags = Column(JSON, default=list)              # Warning signs
    
    # Quality control
    is_constructive = Column(Boolean, default=True, nullable=False)
    helpful_votes = Column(Integer, default=0, nullable=False)
    reported_count = Column(Integer, default=0, nullable=False)
    
    # Relationships
    request = relationship("FeedbackRequest", back_populates="feedback_responses")
    responding_user = relationship("User", back_populates="feedback_responses")

    def __repr__(self):
        return f"<FeedbackResponse(id={self.id}, request_id={self.request_id}, rating={self.overall_rating})>"