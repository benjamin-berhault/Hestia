from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey, Enum as SQLEnum, Float, Boolean, JSON
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from sqlalchemy.ext.hybrid import hybrid_property
from database import Base
from .base import TimestampMixin, GeoLocationMixin
import enum
from datetime import datetime
from typing import Optional

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

class UserProfile(Base, TimestampMixin, GeoLocationMixin):
    __tablename__ = "user_profiles"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    
    # Basic Demographics
    first_name = Column(String(100), nullable=False)
    last_name = Column(String(100), nullable=False)
    date_of_birth = Column(DateTime, nullable=False)
    gender = Column(SQLEnum(Gender), nullable=False)
    
    # Education and Career
    education_level = Column(SQLEnum(EducationLevel), nullable=False)
    occupation = Column(String(100), nullable=False)
    employer = Column(String(100), nullable=True)
    annual_income_range = Column(String(50), nullable=True)  # e.g., "50000-75000"
    career_ambitions = Column(Text, nullable=True)
    
    # Physical Characteristics
    height_inches = Column(Integer, nullable=True)
    body_type = Column(String(50), nullable=True)
    ethnicity = Column(String(100), nullable=True)
    hair_color = Column(String(30), nullable=True)
    eye_color = Column(String(30), nullable=True)
    
    # Lifestyle and Values
    religious_views = Column(SQLEnum(ReligiousView), nullable=False)
    political_views = Column(String(50), nullable=True)
    smoking = Column(String(20), nullable=True)  # never, occasionally, regularly, trying_to_quit
    drinking = Column(String(20), nullable=True)  # never, occasionally, socially, regularly
    exercise_frequency = Column(String(20), nullable=True)  # daily, weekly, occasionally, never
    diet_preferences = Column(String(50), nullable=True)  # omnivore, vegetarian, vegan, etc.
    
    # Family and Relationship Goals
    wants_children = Column(String(20), nullable=False)  # definitely, probably, unsure, probably_not, definitely_not
    children_timeline = Column(String(20), nullable=False)  # within_1_year, 1_3_years, 3_5_years, 5_plus_years
    desired_children_count = Column(String(20), nullable=False)  # 1, 2, 3, 4_plus, open
    has_children = Column(String(20), default="no", nullable=False)  # no, yes_joint_custody, yes_full_custody
    children_details = Column(JSON, nullable=True)  # Ages, genders, custody details
    parenting_philosophy = Column(SQLEnum(ParentingPhilosophy), nullable=True)
    relationship_timeline = Column(String(30), nullable=False)  # serious_immediately, 6_months, 1_year, 2_years
    living_arrangement_preference = Column(String(50), nullable=False)  # separate_until_marriage, move_in_1_year, move_in_soon
    
    # Profile Content
    bio = Column(Text, nullable=False)
    family_vision = Column(Text, nullable=False)
    looking_for = Column(Text, nullable=False)
    deal_breakers = Column(Text, nullable=True)
    interests = Column(JSON, nullable=True)  # Array of interests/hobbies
    languages_spoken = Column(JSON, nullable=True)  # Array of languages
    
    # Personality and Lifestyle
    personality_traits = Column(JSON, nullable=True)  # Big 5 traits from assessment
    communication_style = Column(String(50), nullable=True)
    conflict_resolution_style = Column(String(50), nullable=True)
    love_languages = Column(JSON, nullable=True)  # Array of love languages
    
    # Travel and Adventure
    travel_frequency = Column(String(20), nullable=True)
    favorite_destinations = Column(JSON, nullable=True)
    adventure_level = Column(String(20), nullable=True)  # low, moderate, high
    
    # Financial and Living
    financial_philosophy = Column(String(50), nullable=True)
    homeownership_status = Column(String(20), nullable=True)  # own, rent, family, other
    pet_preferences = Column(JSON, nullable=True)  # Pets owned/wanted
    
    # Profile Completion and Status
    profile_completion_percentage = Column(Integer, default=0, nullable=False)
    is_profile_approved = Column(Boolean, default=False, nullable=False)
    profile_approved_at = Column(DateTime(timezone=True), nullable=True)
    is_visible = Column(Boolean, default=True, nullable=False)
    last_active = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Privacy settings
    show_age = Column(Boolean, default=True, nullable=False)
    show_location = Column(Boolean, default=True, nullable=False)
    show_last_seen = Column(Boolean, default=True, nullable=False)
    
    # Verification status
    identity_verified = Column(Boolean, default=False, nullable=False)
    employment_verified = Column(Boolean, default=False, nullable=False)
    education_verified = Column(Boolean, default=False, nullable=False)
    
    # SEO and Discovery
    search_keywords = Column(Text, nullable=True)  # For internal search optimization
    
    # Relationships
    user = relationship("User", back_populates="profile")

    def __repr__(self):
        return f"<UserProfile(id={self.id}, user_id={self.user_id}, name='{self.first_name} {self.last_name}')>"
    
    @hybrid_property
    def age(self) -> Optional[int]:
        """Calculate age from date of birth"""
        if not self.date_of_birth:
            return None
        today = datetime.today()
        return today.year - self.date_of_birth.year - ((today.month, today.day) < (self.date_of_birth.month, self.date_of_birth.day))
    
    @hybrid_property
    def full_name(self) -> str:
        """Get full name"""
        return f"{self.first_name} {self.last_name}"
    
    @hybrid_property
    def display_age(self) -> str:
        """Get display-friendly age"""
        age = self.age
        if not age:
            return "Age not provided"
        if not self.show_age:
            return "Age hidden"
        return str(age)
    
    def calculate_completion_percentage(self) -> int:
        """Calculate profile completion percentage"""
        total_fields = 25  # Total important fields
        completed = 0
        
        # Required fields (5 points each)
        required_fields = [
            self.first_name, self.last_name, self.date_of_birth, 
            self.gender, self.education_level, self.occupation,
            self.religious_views, self.wants_children, self.children_timeline,
            self.desired_children_count, self.relationship_timeline,
            self.living_arrangement_preference, self.bio, self.family_vision,
            self.looking_for
        ]
        
        for field in required_fields:
            if field:
                completed += 1
        
        # Optional but important fields (weighted)
        if self.height_inches:
            completed += 0.5
        if self.interests:
            completed += 0.5
        if self.deal_breakers:
            completed += 0.5
        if self.personality_traits:
            completed += 0.5
        if self.annual_income_range:
            completed += 0.5
        if self.parenting_philosophy:
            completed += 0.5
        if self.political_views:
            completed += 0.3
        if self.smoking:
            completed += 0.3
        if self.drinking:
            completed += 0.3
        if self.exercise_frequency:
            completed += 0.3
        
        percentage = min(int((completed / total_fields) * 100), 100)
        self.profile_completion_percentage = percentage
        return percentage
    
    def get_age_range(self) -> str:
        """Get age range for display"""
        age = self.age
        if not age:
            return "Unknown"
        
        if age < 25:
            return "18-24"
        elif age < 30:
            return "25-29"
        elif age < 35:
            return "30-34"
        elif age < 40:
            return "35-39"
        elif age < 45:
            return "40-44"
        elif age < 50:
            return "45-49"
        elif age < 55:
            return "50-54"
        elif age < 60:
            return "55-59"
        else:
            return "60+"
    
    def get_family_readiness_score(self) -> float:
        """Calculate family readiness score based on profile data"""
        score = 0.0
        factors = 0
        
        # Timeline urgency
        if self.children_timeline == "within_1_year":
            score += 1.0
        elif self.children_timeline == "1_3_years":
            score += 0.8
        elif self.children_timeline == "3_5_years":
            score += 0.6
        else:
            score += 0.3
        factors += 1
        
        # Relationship commitment
        if self.relationship_timeline in ["serious_immediately", "6_months"]:
            score += 1.0
        elif self.relationship_timeline == "1_year":
            score += 0.7
        else:
            score += 0.4
        factors += 1
        
        # Children certainty
        if self.wants_children == "definitely":
            score += 1.0
        elif self.wants_children == "probably":
            score += 0.7
        else:
            score += 0.3
        factors += 1
        
        # Profile completion
        completion = self.profile_completion_percentage / 100
        score += completion
        factors += 1
        
        return score / factors if factors > 0 else 0.5