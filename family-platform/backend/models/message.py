from sqlalchemy import Column, Integer, Text, DateTime, ForeignKey, Boolean, String, Enum as SQLEnum
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

class MessageType(enum.Enum):
    TEXT = "text"
    PHOTO = "photo"
    SYSTEM = "system"  # System messages like "User joined conversation"

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Message content
    message_type = Column(SQLEnum(MessageType), default=MessageType.TEXT, nullable=False)
    content = Column(Text, nullable=False)  # Text content or MinIO object name for photos
    encrypted_content = Column(Text, nullable=True)  # Encrypted version of content
    
    # Message metadata
    is_edited = Column(Boolean, default=False, nullable=False)
    edited_at = Column(DateTime(timezone=True), nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)
    deleted_at = Column(DateTime(timezone=True), nullable=True)
    
    # Read status
    is_read = Column(Boolean, default=False, nullable=False)
    read_at = Column(DateTime(timezone=True), nullable=True)
    
    # Moderation
    is_flagged = Column(Boolean, default=False, nullable=False)
    flagged_reason = Column(String(100), nullable=True)
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    sender = relationship("User", back_populates="messages")

    def __repr__(self):
        content_preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<Message(id={self.id}, conversation_id={self.conversation_id}, sender_id={self.sender_id}, type='{self.message_type.value}', content='{content_preview}')>"