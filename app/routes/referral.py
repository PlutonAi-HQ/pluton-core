from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.dto import UseRefCodeRequest
from app.controllers.referral import ReferralController
from app.database import get_db

router = APIRouter()


@router.post("/ref/use")
def use_ref(body: UseRefCodeRequest, db: Session = Depends(get_db)):
    ref_controller = ReferralController(db)
    return ref_controller.use_ref(body)


