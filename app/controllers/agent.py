from agent_call import call_agent, get_history


class AgentController:
    def __init__(self):
        pass

    def call_agent(
        self, message: str, session_id: str, images: list[str] = [], user_id: str = None
    ):
        return call_agent(message, session_id, images, user_id, stream=True)

    def get_agent_history(self, user_id: str, session_id: str = None):
        return get_history(user_id, session_id)
