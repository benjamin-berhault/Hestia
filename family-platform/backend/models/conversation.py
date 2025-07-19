from sqlalchemy import Column, Integer, DateTime, ForeignKey, Boolean, String
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base

class Conversation(Base):
    __tablename__ = "conversations"

    id = Column(Integer, primary_key=True, index=True)
    user1_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    user2_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    match_id = Column(Integer, ForeignKey("matches.id"), nullable=False)
    
    # Conversation status
    is_active = Column(Boolean, default=True, nullable=False)
    is_blocked_by_user1 = Column(Boolean, default=False, nullable=False)
    is_blocked_by_user2 = Column(Boolean, default=False, nullable=False)
    
    # Message tracking
    last_message_at = Column(DateTime(timezone=True), nullable=True)
    last_message_by_user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    message_count = Column(Integer, default=0, nullable=False)
    
    # Read status
    user1_last_read = Column(DateTime(timezone=True), nullable=True)
    user2_last_read = Column(DateTime(timezone=True), nullable=True)
    user1_unread_count = Column(Integer, default=0, nullable=False)
    user2_unread_count = Column(Integer, default=0, nullable=False)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    user1 = relationship("User", foreign_keys=[user1_id], back_populates="sent_conversations")
    user2 = relationship("User", foreign_keys=[user2_id], back_populates="received_conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Conversation(id={self.id}, user1_id={self.user1_id}, user2_id={self.user2_id}, is_active={self.is_active})>"

    def get_unread_count_for_user(self, user_id: int) -> int:
        """Get unread message count for a specific user"""
        if user_id == self.user1_id:
            return self.user1_unread_count
        elif user_id == self.user2_id:
            return self.user2_unread_count
        else:
            return 0

    def is_blocked_for_user(self, user_id: int) -> bool:
        """Check if conversation is blocked for a specific user"""
        if user_id == self.user1_id:
            return self.is_blocked_by_user2
        elif user_id == self.user2_id:
            return self.is_blocked_by_user1
        else:
            return False