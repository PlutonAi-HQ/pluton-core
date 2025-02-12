from agents.pluton import PlutonAgent
from log import logger
from app.core.response import ResponseHandler, StatusCode, ResponseCode
from app.dto import ChatHistoryDTO, Message
from app.models.chat_history import AgentSession
from app.database.client import get_db


class AgentService:
    def __init__(self, user_id: str, session_id: str):
        self.agent_service = PlutonAgent(user_id=user_id, session_id=session_id)
        self.agent = self.agent_service.get_agent()
        self.storage = self.agent_service.get_storage()
        self.db = next(get_db())
        self.user_id = user_id
        self.session_id = session_id

    def run(self, message: str, images: list[str] = []):
        query = message + " " + "\n".join(images)
        return self.agent.run(query, stream=True)

    def get_history(self, limit: int, offset: int):
        session_id = self.agent_service.session_id
        user_id = self.agent_service.user_id
        logger.info(f"[HISTORY] - user_id: {user_id}, session_id: {session_id}")

        sessions = self.storage.get_all_sessions(user_id=user_id)
        if not sessions:
            return []

        if session_id:
            logger.info(f"[GET_HISTORY] - session_id: {session_id}")
            session = self._get_session(sessions, session_id)
            if not session:
                logger.info(f"No session found for {session_id} and user {user_id}")
                return ResponseHandler.error(
                    code=ResponseCode.CONVERSATION_NOT_FOUND,
                    status_code=StatusCode.NOT_FOUND,
                )
            return self._create_chat_history_dto(session)

        logger.info(
            f"[GET_HISTORY] - all sessions with offset: {offset}, limit: {limit}"
        )
        # Apply offset and limit before processing sessions
        paginated_sessions = sessions[offset : offset + limit]
        return [
            dto
            for session in paginated_sessions
            if (dto := self._create_chat_history_dto(session)) is not None
        ]

    def _create_chat_history_dto(self, session) -> ChatHistoryDTO:
        history, created_at = self._extract_history(session.memory.get("runs", []))
        if not history:
            return None

        title = (
            session.user_data.get("title", history[0].content)
            if session.user_data
            else history[0].content
        )
        return ChatHistoryDTO(
            title=title,
            data=history,
            created_at=created_at,
            session_id=session.session_id,
        )

    def _extract_history(self, runs: list[dict]):
        history: list[Message] = []
        for run in runs:
            user_message = run.get("message").get("content")
            created_at = run.get("message").get("created_at")
            images_message = [
                message.get("images") for message in run.get("response").get("messages")
            ][0]
            agent_message = run.get("response").get("content")
            result = [
                Message(role="user", content=user_message, images=images_message),
                Message(role="assistant", content=agent_message),
            ]
            history.extend(result)
        return history, created_at

    def _get_session(self, sessions: list, session_id: str) -> AgentSession:
        return next((s for s in sessions if s.session_id == session_id), None)

    def edit_title(self, title: str):
        user_id = self.agent_service.user_id
        session_id = self.agent_service.session_id
        logger.info(f"[EDIT_TITLE] - user_id: {user_id}, session_id: {session_id}")
        try:
            sessions = self.storage.get_all_sessions(user_id=user_id)
            session = self._get_session(sessions, session_id)
            logger.info(f"[EDIT_TITLE] - session: {session}")
            if not session:
                return ResponseHandler.error(
                    code=ResponseCode.CONVERSATION_NOT_FOUND,
                    status_code=StatusCode.NOT_FOUND,
                )
            if session.user_data is None:
                session.user_data = {}
            session.user_data["title"] = title
            self.storage.upsert(session)
            return ResponseHandler.success(
                status_code=StatusCode.OK,
            )
        except Exception as e:
            logger.error(f"Error editing title: {e}")
            return ResponseHandler.error(
                code=ResponseCode.INTERNAL_ERROR,
                status_code=StatusCode.INTERNAL_SERVER_ERROR,
            )

    def delete_session(self):
        self.storage.delete_session(self.session_id)
        return ResponseHandler.success(
            code=ResponseCode.SUCCESS,
            status_code=StatusCode.OK,
        )
