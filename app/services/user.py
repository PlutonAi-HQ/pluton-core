from sqlalchemy.orm import Session
from app.models.user import User
from app.dto import UserRequestDTO
from app.core.exceptions import AppException, ErrorCode
from sqlalchemy.exc import IntegrityError


class UserService:
    def __init__(self, db: Session):
        self.db = db

    def create_user(self, user: UserRequestDTO) -> User:
        try:
            user_model = User(**user.model_dump())
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
