from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
from .user_profile import Gender, EducationLevel, ReligiousView, ParentingPhilosophy
import enum

class ImportanceLevel(enum.Enum):
    NOT_IMPORTANT = "not_important"
    SOMEWHAT_IMPORTANT = "somewhat_important"
    IMPORTANT = "important"
    VERY_IMPORTANT = "very_important"
    DEAL_BREAKER = "deal_breaker"

class UserPreferences(Base):
    __tablename__ = "user_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Age preferences
    min_age = Column(Integer, nullable=False)
    max_age = Column(Integer, nullable=False)
    age_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.IMPORTANT, nullable=False)
    
    # Location preferences
    max_distance_miles = Column(Integer, default=50, nullable=False)
    location_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.IMPORTANT, nullable=False)
    willing_to_relocate = Column(Boolean, default=False, nullable=False)
    
    # Demographics
    preferred_genders = Column(String(100), nullable=True)  # JSON array of Gender enums
    gender_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.VERY_IMPORTANT, nullable=False)
    
    # Education and Career
    min_education_level = Column(SQLEnum(EducationLevel), nullable=True)
    education_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.SOMEWHAT_IMPORTANT, nullable=False)
    career_ambition_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.SOMEWHAT_IMPORTANT, nullable=False)
    
    # Physical preferences
    min_height_inches = Column(Integer, nullable=True)
    max_height_inches = Column(Integer, nullable=True)
    height_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.NOT_IMPORTANT, nullable=False)
    body_type_preferences = Column(String(200), nullable=True)  # JSON array
    physical_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.NOT_IMPORTANT, nullable=False)
    
    # Lifestyle and Values
    religious_preferences = Column(String(200), nullable=True)  # JSON array of ReligiousView enums
    religious_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.IMPORTANT, nullable=False)
    political_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.SOMEWHAT_IMPORTANT, nullable=False)
    smoking_preference = Column(String(50), nullable=True)  # never, occasionally, doesn't_matter
    smoking_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.IMPORTANT, nullable=False)
    drinking_preference = Column(String(50), nullable=True)  # never, socially, doesn't_matter
    drinking_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.SOMEWHAT_IMPORTANT, nullable=False)
    
    # Family and Relationship
    children_timeline_preference = Column(String(50), nullable=True)  # JSON array of timelines
    children_timeline_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.VERY_IMPORTANT, nullable=False)
    children_count_preference = Column(String(50), nullable=True)  # JSON array of counts
    children_count_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.IMPORTANT, nullable=False)
    parenting_philosophy_preferences = Column(String(200), nullable=True)  # JSON array
    parenting_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.IMPORTANT, nullable=False)
    has_children_preference = Column(String(50), nullable=True)  # no_children, open_to_children, doesn't_matter
    has_children_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.IMPORTANT, nullable=False)
    
    # Relationship Timeline
    relationship_timeline_preference = Column(String(50), nullable=True)  # JSON array
    relationship_timeline_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.VERY_IMPORTANT, nullable=False)
    living_arrangement_preference = Column(String(100), nullable=True)  # JSON array
    living_arrangement_importance = Column(SQLEnum(ImportanceLevel), default=ImportanceLevel.IMPORTANT, nullable=False)
    
    # Matching settings
    show_me_to_others = Column(Boolean, default=True, nullable=False)
    only_show_verified_profiles = Column(Boolean, default=False, nullable=False)
    auto_like_compatible_profiles = Column(Boolean, default=False, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="preferences")

    def __repr__(self):
        return f"<UserPreferences(id={self.id}, user_id={self.user_id}, age_range={self.min_age}-{self.max_age})>"