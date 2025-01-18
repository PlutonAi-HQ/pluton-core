from fastapi import FastAPI, HTTPException, Depends, Request, Response
from pydantic import BaseModel, Field
from app.controllers.agent import AgentController
import uvicorn
from fastapi.responses import StreamingResponse
from config import settings
from app.middleware.limiter import RedisRateLimiterMiddleware
from app.middleware.redis import get_redis_client
from typing import Optional

app = FastAPI()

# Add the rate limiting middleware
app.add_middleware(
    RedisRateLimiterMiddleware,
    redis_client=get_redis_client(),
    window=settings.RATE_LIMIT_WINDOW,
    limit=settings.RATE_LIMIT_MAX_REQUESTS,
)


@app.middleware("http")
async def cors_handler(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Origin"] = settings.origins
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
    if request.method == "OPTIONS":
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Origin"] = settings.origins
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
        return Response(status_code=200)
    return response


PREFIX = "/api"


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


@app.get(f"{PREFIX}/healthz")
def healthz():
    try:
        return {"message": "OK"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{PREFIX}/agent/history")
def agent_history(request: AgentHistoryRequest):
    try:
        agent_controller = AgentController()
        return agent_controller.get_agent_history(request.session_id, request.user_id)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.post(f"{PREFIX}/agent/call")
def agent_call(request: AgentCallRequest):
    try:

        def event_generator():
            agent_controller = AgentController()
            aggregated_response = ""
            response = agent_controller.call_agent(
                request.message, request.session_id, request.images, request.user_id
            )
            for chunk in response:
                aggregated_response += chunk.content
                yield f"event: token\ndata: {chunk.content}\n\n"
            yield f"event: end\ndata: {aggregated_response}\n\n"

        return StreamingResponse(event_generator(), media_type="text/event-stream")
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=3456)
