from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Float
from sqlalchemy.orm import relationship
from sqlalchemy import func
from app.database.client import Base


class Wallet(Base):
    __tablename__ = "wallets"
    id = Column(Integer, primary_key=True, index=True)
    balance = Column(Float, default=0.0)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    user = relationship("User", back_populates="wallets")
    public_key = Column(String, nullable=True)
    private_key = Column(String, nullable=True)
    seed_phrase = Column(String, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<Wallet(id={self.id}, balance={self.balance}, user_id={self.user_id})>"
