from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.client import Base
from sqlalchemy import func
import uuid


class Referral(Base):
    __tablename__ = "referrals"
    referral_code = Column(String, index=True, primary_key=True, default=lambda: str(uuid.uuid4()))
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    total_used = Column(Integer, server_default="0")
    owner_id = Column(String, ForeignKey("users.id"))
    owner = relationship("User", back_populates="referral")

    def __repr__(self):
        return f"<Referral(referral_code={self.referral_code}, created_at={self.created_at}, total_used={self.total_used})>"
        