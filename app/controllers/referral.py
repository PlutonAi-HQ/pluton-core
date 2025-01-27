from app.dto import UseRefCodeRequest
from sqlalchemy.orm import Session
from app.services.referral import ReferralService
from fastapi import HTTPException
import jwt
from config import settings


class ReferralController:
    def __init__(self, db: Session):
        self.db = db

    def use_ref(self, body: UseRefCodeRequest):
        user_id=None
        try:
            payload = jwt.decode(body.access_token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])
            user_id = payload.get("sub")
            if user_id is None:
                raise HTTPException(status_code=401, detail="Invalid token")
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token has expired")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")

        referralService = ReferralService(self.db)
        res = referralService.use_ref_code(user_id, body.ref_code)
            
        if(res == 403):
            raise HTTPException(status_code=403, detail="This account is already used a referral code")
        if(res == 402):
            raise HTTPException(status_code=402, detail="This account does not exist")
        if(res == 405):
            raise HTTPException(status_code=405, detail="The referral code does not exist")
        return {
                "message": "Referral code used successfully"
            }
