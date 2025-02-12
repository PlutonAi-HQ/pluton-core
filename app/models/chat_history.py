from datetime import datetime
from sqlalchemy import Column, Integer, String, DateTime, ForeignKey, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from app.database.client import Base
import uuid
from sqlalchemy import JSON, BigInteger, text


class AgentSession(Base):
    __tablename__ = "agent_sessions"

    # Primary Key
    session_id = Column(String, primary_key=True)
    # Foreign Keys and Relationships
    agent_id = Column(String)
    user_id = Column(String)

    # JSON Data Fields
    memory = Column(JSON)
    agent_data = Column(JSON)
    session_data = Column(JSON)
    user_data = Column(JSON)

    # Timestamps
    created_at = Column(
        BigInteger, server_default=text("(extract(epoch from now()))::bigint")
    )
    updated_at = Column(
        BigInteger, server_onupdate=text("(extract(epoch from now()))::bigint")
    )

    class Config:
        orm_mode = True
