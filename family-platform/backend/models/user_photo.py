from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class UserPhoto(Base):
    __tablename__ = "user_photos"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # MinIO object information
    object_name = Column(String(255), nullable=False, unique=True)
    original_filename = Column(String(255), nullable=False)
    content_type = Column(String(50), nullable=False)
    file_size = Column(Integer, nullable=False)  # in bytes
    
    # Photo metadata
    is_primary = Column(Boolean, default=False, nullable=False)
    is_approved = Column(Boolean, default=False, nullable=False)
    approved_at = Column(DateTime(timezone=True), nullable=True)
    display_order = Column(Integer, default=0, nullable=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user = relationship("User", back_populates="photos")

    def __repr__(self):
        return f"<UserPhoto(id={self.id}, user_id={self.user_id}, object_name='{self.object_name}', is_primary={self.is_primary})>"