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
from fastapi import Depends, Query
from app.dto import UpdateTitleRequest

logger = logging.getLogger(__name__)

router = APIRouter(tags=["agent"])


@router.get("/agent/history")
def agent_history(
    session_id: str = Query(default=""),
    limit: int = Query(default=10),
    offset: int = Query(default=0),
    user: User = Depends(verify_token),
):
    try:
        agent_controller = AgentController(str(user.id), session_id)
        return agent_controller.get_agent_history(limit, offset)
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
            agent_controller = AgentController(str(user.id), body.session_id)
            aggregated_response = ""
            response = agent_controller.call_agent(body.message, body.images)
            for chunk in response:
                aggregated_response += chunk.content
                yield f"event: token\ndata: {chunk.content}\n\n"
            yield f"event: end\ndata: {aggregated_response}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/agent/history/{session_id}/title")
def agent_title(
    session_id: str,
    body: UpdateTitleRequest,
    user: User = Depends(verify_token),
):
    try:
        agent_controller = AgentController(str(user.id), session_id)
        return agent_controller.edit_title(body.title)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.delete("/agent/history/{session_id}")
def agent_delete(
    session_id: str,
    user: User = Depends(verify_token),
):
    try:
        agent_controller = AgentController(str(user.id), session_id)
        return agent_controller.delete_session()
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
