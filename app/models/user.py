from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database.client import Base
from sqlalchemy import func
import uuid


class User(Base):
    __tablename__ = "users"
    id = Column(String, primary_key=True, index=True, default=lambda: str(uuid.uuid4()))
    email = Column(String, unique=True, index=True)
    username = Column(String, index=True)
    password = Column(String, nullable=True)
    avatar = Column(
        String, default="https://avatar.iran.liara.run/public", nullable=True
    )
    files = relationship(
        "File", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    wallets = relationship(
        "Wallet", back_populates="user", cascade="all, delete-orphan", lazy="select"
    )
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

    def __repr__(self):
        return f"<User(id={self.id}, email={self.email}, username={self.username})>"
