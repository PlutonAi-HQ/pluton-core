from app.dto import LoginRequest, SignupRequest
from sqlalchemy.orm import Session
from app.services.user import UserService
from fastapi import HTTPException
from datetime import datetime, timedelta
import jwt
from config import settings
from app.services.wallet import WalletService
from app.dto import SocialCallbackRequest
from app.services.referral import ReferralService


class AuthController:
    def __init__(self, db: Session):
        self.db = db

    def login(self, body: LoginRequest):
        user_service = UserService(self.db)
        user = user_service.get_user_by_email(body.email)
        if not user:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        if not user.password == body.password:
            raise HTTPException(status_code=401, detail="Invalid username or password")
        # TODO: Generate JWT token
        token = jwt.encode(
            {"sub": str(user.id), "exp": datetime.now() + timedelta(hours=1)},
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )
        refresh_token = jwt.encode(
            {"sub": str(user.id), "exp": datetime.now() + timedelta(days=7)},
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )
        # TODO: Return JWT token
        return {
            "message": "Login successful",
            "access_token": token,
            "refresh_token": refresh_token,
        }

    def signup(self, body: SignupRequest):
        user_service = UserService(self.db)
        user = user_service.get_user_by_email(body.email)
        if user:
            raise HTTPException(status_code=401, detail="User already exists")
        body.avatar = (
            body.avatar
            or f"https://avatar.iran.liara.run/username?username={body.username}"
        )
        user = user_service.create_user(body)
        # Create wallet
        wallet_service = WalletService(self.db)
        wallet = wallet_service.create_wallet(user.id)

        return {
            "message": "Signup successful",
            "wallet": {
                "public_key": wallet.public_key,
            },
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "avatar": user.avatar,
            },
        }

    def callback_social(self, body: SocialCallbackRequest):
        # TODO: Check to if user exists
        user_service = UserService(self.db)
        user = user_service.get_user_by_email(body.email)
        # TODO: If not, create user
        body.avatar = (
            body.avatar
            or f"https://avatar.iran.liara.run/username?username={body.username}"
        )
        if not user:
            user = user_service.create_user(body)
            # TODO: Create wallet
            wallet_service = WalletService(self.db)
            wallet = wallet_service.create_wallet(user.id)
            print("CREATE REFERRAL NOT EXISTS")
        # If exists, get wallet info
        else:
            # User exists, get wallet info
            print(user)
            wallet_service = WalletService(self.db)
            wallet = wallet_service.get_wallet_by_user_id(user.id)
        referral_service = ReferralService(self.db)
        referral = referral_service.get_referral_by_user_id(user.id)
        # TODO: Generate JWT token
        token = jwt.encode(
            {"sub": str(user.id), "exp": datetime.now() + timedelta(hours=1)},
            settings.JWT_SECRET,
            algorithm=settings.JWT_ALGORITHM,
        )
        # TODO: Return all data
        return {
            "message": "Social callback successful",
            "access_token": token,
            "wallet": {
                "public_key": wallet.public_key,
            },
            "user": {
                "id": user.id,
                "email": user.email,
                "username": user.username,
                "avatar": user.avatar,
            },
            "referral": {
                "code": referral.referral_code,
                "total_used": referral.total_used,
            },
        }
