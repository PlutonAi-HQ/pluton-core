from fastapi import APIRouter, Request
from app.controllers.wallet import WalletController
from app.middleware.decorator import rate_limit
from config import settings

router = APIRouter()


@router.post("/wallet/generate")
@rate_limit(
    max_requests=settings.RATE_LIMIT_MAX_REQUESTS + 100,
    window=settings.RATE_LIMIT_WINDOW,
)
def generate_wallet(request: Request):
    return WalletController.generate_wallet()
