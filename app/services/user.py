from sqlalchemy.orm import Session
from app.models.user import User
from app.models.referral import Referral
from app.dto import UserRequestDTO
from app.core.exceptions import AppException, ErrorCode
from sqlalchemy.exc import IntegrityError
import hashlib


def ref_generator(input_string):
    hash_object = hashlib.sha256(input_string.encode())
    full_hash = hash_object.hexdigest()
    short_hash = full_hash[:6]
    return short_hash


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserRequestDTO) -> User:
        try:
            user_model = User(**user.model_dump())
            ref_model = Referral(owner=user_model)
            user_model.ref_code = ref_model.referral_code
            self.db.add(ref_model)
            self.db.add(user_model)
            self.db.commit()
            return user_model
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

    def get_user_by_username(self, username: str) -> User:
        return self.db.query(User).filter(User.username == username).first()

    def get_user_by_email(self, email: str) -> User:
        return self.db.query(User).filter(User.email == email).first()

    def get_user_by_id(self, id: int) -> User:
        return self.db.query(User).filter(User.id == id).first()
