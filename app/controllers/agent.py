from app.services.agent import AgentService


class AgentController:
    def __init__(self, user_id: str, session_id: str):
        self.agent_service = AgentService(user_id, session_id)

    def call_agent(self, message: str, images: list[str] = []):
        return self.agent_service.run(message, images)

    def get_agent_history(self, limit: int = 10, offset: int = 0):
        return self.agent_service.get_history(limit, offset)
