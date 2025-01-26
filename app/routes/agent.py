from fastapi import APIRouter, Request
from app.dto import AgentHistoryRequest, AgentCallRequest
from app.controllers.agent import AgentController
from fastapi.responses import StreamingResponse
from fastapi.exceptions import HTTPException
from app.middleware.decorator import rate_limit
from config import settings
from fastapi import File, UploadFile
from storage.aws_s3 import S3Storage
from typing import List
import logging
from uuid import uuid4
from config import settings
from app.middleware.auth import verify_token
from app.models import User
from fastapi import Depends
from sqlalchemy.orm import Session
from app.database import get_db

logger = logging.getLogger(__name__)

router = APIRouter()


@router.post("/agent/history")
def agent_history(
    request: Request,
    body: AgentHistoryRequest,
    user: User = Depends(verify_token),
):
    try:
        agent_controller = AgentController()
        return agent_controller.get_agent_history(body.session_id, str(user.id))
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post(
    "/agent/call",
)
@rate_limit(
    max_requests=settings.RATE_LIMIT_MAX_REQUESTS, window=settings.RATE_LIMIT_WINDOW
)
def agent_call(
    request: Request,
    body: AgentCallRequest,
    user: User = Depends(verify_token),
):
    try:

        def event_generator():
            agent_controller = AgentController()
            aggregated_response = ""
            response = agent_controller.call_agent(
                body.message, body.session_id, body.images, str(user.id)
            )
            is_tool = False
            for chunk in response:
                if chunk.content == "\nRunning:" and count == 0:
                    is_tool = True
                if is_tool and chunk.content == "\n\n":
                    is_tool = False
                    count = 1
                if not is_tool and count == 1:
                    aggregated_response += chunk.content
                    yield f"event: token\ndata: {chunk.content}\n\n"
            yield f"event: end\ndata: {aggregated_response}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
