from fastapi import FastAPI, HTTPException, Depends, Request, Response
from pydantic import BaseModel, Field
from app.controllers.agent import AgentController
from app.controllers.wallet import WalletController
import uvicorn
from fastapi.responses import StreamingResponse
from config import settings
from app.middleware.limiter import RedisRateLimiterMiddleware
from app.middleware.redis import get_redis_client
from app.routes.agent import router as agent_router
from app.routes.wallet import router as wallet_router
from fastapi.responses import JSONResponse

app = FastAPI()


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
        return Response(headers=response.headers, status_code=204)
    return response


PREFIX = "/api"

app.include_router(agent_router, prefix=PREFIX)
app.include_router(wallet_router, prefix=PREFIX)


@app.get(f"{PREFIX}/healthz")
def healthz():
    try:
        return {"message": "OK"}
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.exception_handler(HTTPException)
def http_exception_handler(request: Request, exc: HTTPException):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=3456)
