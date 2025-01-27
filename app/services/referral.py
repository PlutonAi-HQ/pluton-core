from sqlalchemy.orm import Session
from app.models.referral import Referral
from app.models.user import User
from app.core.exceptions import AppException, ErrorCode
from sqlalchemy.exc import IntegrityError


class ReferralService:
    def __init__(self, db: Session):
        self.db = db
    def create_referral(self, username, referral_code) -> Referral:
        try:
            referral_model = Referral(referral_code=referral_code)
            self.db.add(referral_model)
            self.db.commit()
            return referral_model
        except IntegrityError as e:
            self.db.rollback()
            raise e
        except Exception as e:
            self.db.rollback()
            raise AppException(
                error_code=ErrorCode.INTERNAL_ERROR,
                message="An unexpected error occurred",
                status_code=500,
                extra={"original_error": str(e)},
            )
    def get_all_referrals(self):
        return self.db.query(Referral).all()

    def use_ref_code(self, user_id: str, ref_code: str):
        user = self.db.query(User).filter_by(id=user_id).first()
        if(user):
            if user.used_ref_code!='':
                return 403
        else:
            return 402    
        
        ref = self.db.query(Referral).filter_by(referral_code=ref_code).first()
        if ref:
            user.used_ref_code = ref_code
            ref.total_used += 1
            self.db.commit()
            return 200
        return 405
