from sqlalchemy import Column, Integer, String, Text, Boolean, DateTime, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

class ChapterTemplateCategory(enum.Enum):
    FINANCIAL = "financial"
    PARENTING = "parenting"
    LIVING_ARRANGEMENTS = "living_arrangements"
    CONFLICT_RESOLUTION = "conflict_resolution"
    RELATIONSHIP_BOUNDARIES = "relationship_boundaries"
    FUTURE_PLANNING = "future_planning"
    HEALTH_DECISIONS = "health_decisions"
    CAREER_SUPPORT = "career_support"
    FAMILY_TRADITIONS = "family_traditions"
    COMPREHENSIVE = "comprehensive"

class CharterTemplate(Base):
    __tablename__ = "charter_templates"

    id = Column(Integer, primary_key=True, index=True)
    
    # Template information
    name = Column(String(200), nullable=False)
    description = Column(Text, nullable=False)
    category = Column(SQLEnum(ChapterTemplateCategory), nullable=False)
    
    # Template content
    template_content = Column(Text, nullable=False)  # JSON structure with sections and fields
    version = Column(String(20), default="1.0", nullable=False)
    
    # Usage and availability
    is_active = Column(Boolean, default=True, nullable=False)
    is_default = Column(Boolean, default=False, nullable=False)
    usage_count = Column(Integer, default=0, nullable=False)
    
    # Metadata
    created_by_admin = Column(Boolean, default=True, nullable=False)
    tags = Column(Text, nullable=True)  # JSON array of tags for searching
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user_charters = relationship("UserCharter", back_populates="template")

    def __repr__(self):
        return f"<CharterTemplate(id={self.id}, name='{self.name}', category='{self.category.value}', usage_count={self.usage_count})>"