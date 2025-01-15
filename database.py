from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from models import Base, UserModel
import os
from dotenv import load_dotenv

load_dotenv()


class PostgresDAO:
    def __init__(self):
        self.database_url = os.getenv("POSTGRES_URL")
        self.engine = create_engine(self.database_url)
        self.SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )
        Base.metadata.create_all(bind=self.engine)

    def drop_users_table(self):
        """Drop users table"""
        UserModel.__table__.drop(self.engine)
        # Tạo lại bảng users
        UserModel.__table__.create(self.engine)

    def __enter__(self) -> Session:
        self.session = self.SessionLocal()
        return self.session

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.session.close()

    def save_user(
        self,
        chat_id: int,
        username: str,
        first_name: str,
        seed_phrase: str | None = None,
        private_key: str | None = None,
        public_key: str | None = None,
    ):
        """Save new user"""
        with self.SessionLocal() as session:
            user = UserModel(
                chat_id=chat_id,
                username=username,
                first_name=first_name,
                seed_phrase=seed_phrase,
                private_key=private_key,
                public_key=public_key,
            )
            session.add(user)
            session.commit()
            return user

    def get_user_by_id(self, chat_id: int):
        """Get user by chat_id"""
        with self.SessionLocal() as session:
            return session.query(UserModel).filter(UserModel.chat_id == chat_id).first()

    def upsert_user(self, chat_id: int, **kwargs):
        """Update user if exists, otherwise create new user"""
        user = self.get_user_by_id(chat_id)
        if user:
            self.update_user(chat_id, **kwargs)
        else:
            self.save_user(
                chat_id, username=kwargs["username"], first_name=kwargs["first_name"]
            )

    def update_user(self, chat_id: int, **kwargs):
        """Update user
        Args:
            chat_id: The chat ID of the user
            **kwargs: The key-value pairs to update
        Returns:
            None
        Example:
            update_user(chat_id=123, seed_phrase="new seed phrase")
        """
        with self.SessionLocal() as session:
            session.query(UserModel).filter(UserModel.chat_id == chat_id).update(kwargs)
            session.commit()

    def get_user_by_chat_id(self, chat_id: int):
        """Get user by chat_id"""
        with self.SessionLocal() as session:
            return session.query(UserModel).filter(UserModel.chat_id == chat_id).first()

    def get_all_users(self):
        """Lấy danh sách tất cả users"""
        with self.SessionLocal() as session:
            return session.query(UserModel).all()

    def get_wallet_secret(self, chat_id: int):
        """Get wallet secret"""
        with self.SessionLocal() as session:
            return session.query(UserModel).filter(UserModel.chat_id == chat_id).first()
