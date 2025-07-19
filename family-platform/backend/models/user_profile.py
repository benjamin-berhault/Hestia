from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Float, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

class Gender(enum.Enum):
    MALE = "male"
    FEMALE = "female"
    NON_BINARY = "non_binary"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class EducationLevel(enum.Enum):
    HIGH_SCHOOL = "high_school"
    SOME_COLLEGE = "some_college"
    BACHELORS = "bachelors"
    MASTERS = "masters"
    DOCTORATE = "doctorate"
    TRADE_SCHOOL = "trade_school"
    OTHER = "other"

class ReligiousView(enum.Enum):
    CHRISTIAN = "christian"
    CATHOLIC = "catholic"
    JEWISH = "jewish"
    MUSLIM = "muslim"
    BUDDHIST = "buddhist"
    HINDU = "hindu"
    SPIRITUAL = "spiritual"
    AGNOSTIC = "agnostic"
    ATHEIST = "atheist"
    OTHER = "other"
    PREFER_NOT_TO_SAY = "prefer_not_to_say"

class ParentingPhilosophy(enum.Enum):
    TRADITIONAL = "traditional"
    PROGRESSIVE = "progressive"
    ATTACHMENT = "attachment"
    AUTHORITATIVE = "authoritative"
    PERMISSIVE = "permissive"
    MONTESSORI = "montessori"
    WALDORF = "waldorf"
    HOMESCHOOL = "homeschool"
    OTHER = "other"

class UserProfile(Base):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Basic Demographics
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(SQLEnum(Gender), nullable=False)
    location_city = Column(String(100), nullable=False)
    location_state = Column(String(50), nullable=False)
    location_country = Column(String(50), default="United States", nullable=False)
    latitude = Column(Float, nullable=True)  # For distance calculations
    longitude = Column(Float, nullable=True)
    
    # Education and Career
    education_level = Column(SQLEnum(EducationLevel), nullable=False)
    occupation = Column(String(100), nullable=False)
    employer = Column(String(100), nullable=True)
    annual_income_range = Column(String(50), nullable=True)  # e.g., "50000-75000"
    
    # Physical Characteristics
    height_inches = Column(Integer, nullable=True)
    body_type = Column(String(50), nullable=True)
    ethnicity = Column(String(100), nullable=True)
    
    # Lifestyle and Values
    religious_views = Column(SQLEnum(ReligiousView), nullable=False)
    political_views = Column(String(50), nullable=True)
    smoking = Column(String(20), nullable=True)  # never, occasionally, regularly, trying_to_quit
    drinking = Column(String(20), nullable=True)  # never, occasionally, socially, regularly
    exercise_frequency = Column(String(20), nullable=True)  # daily, weekly, occasionally, never
    
    # Family and Relationship Goals
    wants_children = Column(String(20), nullable=False)  # definitely, probably, unsure, probably_not, definitely_not
    children_timeline = Column(String(20), nullable=False)  # within_1_year, 1_3_years, 3_5_years, 5_plus_years
    desired_children_count = Column(String(20), nullable=False)  # 1, 2, 3, 4_plus, open
    has_children = Column(String(20), default="no", nullable=False)  # no, yes_joint_custody, yes_full_custody
    parenting_philosophy = Column(SQLEnum(ParentingPhilosophy), nullable=True)
    relationship_timeline = Column(String(30), nullable=False)  # serious_immediately, 6_months, 1_year, 2_years
    living_arrangement_preference = Column(String(50), nullable=False)  # separate_until_marriage, move_in_1_year, move_in_soon
    
    # Profile Content
    bio = Column(Text, nullable=False)
    family_vision = Column(Text, nullable=False)
    looking_for = Column(Text, nullable=False)
    deal_breakers = Column(Text, nullable=True)
    interests = Column(Text, nullable=True)  # JSON array of interests
    
    # Profile Completion and Status
    profile_completion_percentage = Column(Integer, default=0, nullable=False)
    is_profile_approved = Column(Boolean, default=False, nullable=False)
    profile_approved_at = Column(DateTime(timezone=True), nullable=True)
    is_visible = Column(Boolean, default=True, nullable=False)
    last_active = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, name='{self.first_name} {self.last_name}')>"
    
    @property
    def age(self):
        """Calculate age from date of birth"""
        from datetime import datetime
        today = datetime.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    @property
    def full_name(self):
        """Get full name"""
        return f"{self.first_name} {self.last_name}"