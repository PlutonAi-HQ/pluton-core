from agent_call import call_agent


class AgentController:
    def __init__(self):
        pass

    def call_agent(
        self, message: str, session_id: str, images: list[str] = [], user_id: str = None
    ):
        return call_agent(message, session_id, images, user_id, stream=True)
