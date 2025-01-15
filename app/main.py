from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from app.controllers.agent import AgentController
import uvicorn
from fastapi.responses import StreamingResponse
from fastapi import Request, Response
from config import settings

app = FastAPI()
print(settings.origins)


@app.middleware("http")
async def cors_handler(request: Request, call_next):
    response: Response = await call_next(request)
    response.headers["Access-Control-Allow-Credentials"] = "true"
    response.headers["Access-Control-Allow-Origin"] = settings.origins
    response.headers["Access-Control-Allow-Methods"] = "*"
    response.headers["Access-Control-Allow-Headers"] = "*"
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


@app.get(f"{PREFIX}/healthz")
def healthz():
    return {"message": "OK"}


@app.options(f"{PREFIX}/agent/call")
def agent_call_options():
    return {"message": "OK"}


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
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=3456)
