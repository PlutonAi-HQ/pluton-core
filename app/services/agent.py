from agents.pluton import PlutonAgent
from log import logger
from app.core.response import ResponseHandler
from app.core.error_handlers import ErrorCode


class AgentService:
    def __init__(self, user_id: str, session_id: str):
        self.agent_service = PlutonAgent(user_id=user_id, session_id=session_id)
        self.agent = self.agent_service.get_agent()
        self.storage = self.agent_service.get_storage()

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
                    message="No session found",
                    code=ErrorCode.CONVERSATION_NOT_FOUND.value,
                )
            return self._create_chat_history_dto(session, user_id)

        logger.info(
            f"[GET_HISTORY] - all sessions with offset: {offset}, limit: {limit}"
        )
        # Apply offset and limit before processing sessions
        paginated_sessions = sessions[offset : offset + limit]
        return [
            dto
            for session in paginated_sessions
            if (dto := self._create_chat_history_dto(session, user_id)) is not None
        ]
