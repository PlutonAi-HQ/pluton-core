from typing import Optional
from pydantic import BaseModel, Field


class AgentCallRequest(BaseModel):
    message: str = Field(
        ...,
        description="The message to send to the agent",
        example="Hello, how are you?",
    )
    session_id: str = Field(..., description="The session id", example="s-1234567890")
    images: list[str] = Field([], description="The images to send to the agent")
    user_id: str = Field(None, description="The user id", example="u-1234567890")


class AgentHistoryRequest(BaseModel):
    session_id: Optional[str] = Field(
        None, description="The session id", example="s-1234567890"
    )
    user_id: str = Field(None, description="The user id", example="u-1234567890")
