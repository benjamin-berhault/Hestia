from sqlalchemy import Column, Integer, DateTime, ForeignKey, Enum as SQLEnum, Float, Text
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from database import Base
import enum

class MatchStatus(enum.Enum):
    PENDING = "pending"          # One user liked, waiting for response
    MATCHED = "matched"          # Both users liked each other
    DECLINED = "declined"        # One user declined the match
    EXPIRED = "expired"          # Match request expired
    BLOCKED = "blocked"          # One user blocked the other
    UNMATCHED = "unmatched"      # Previously matched, then unmatched

class Match(Base):
    __tablename__ = "matches"

    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    receiver_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    
    # Match details
    status = Column(SQLEnum(MatchStatus), default=MatchStatus.PENDING, nullable=False)
    compatibility_score = Column(Float, nullable=False)  # 0.0 to 1.0
    compatibility_breakdown = Column(Text, nullable=True)  # JSON object with detailed scoring
    
    # Interaction tracking
    sender_liked_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    receiver_responded_at = Column(DateTime(timezone=True), nullable=True)
    matched_at = Column(DateTime(timezone=True), nullable=True)
    last_interaction = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    
    # Expiration
    expires_at = Column(DateTime(timezone=True), nullable=True)  # When pending match expires
    
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    
    # Relationships
    sender = relationship("User", foreign_keys=[sender_id], back_populates="sent_matches")
    receiver = relationship("User", foreign_keys=[receiver_id], back_populates="received_matches")

    def __repr__(self):
        return f"<Match(id={self.id}, sender_id={self.sender_id}, receiver_id={self.receiver_id}, status='{self.status.value}', score={self.compatibility_score})>"

    @property
    def is_mutual(self):
        """Check if this is a mutual match"""
        return self.status == MatchStatus.MATCHED