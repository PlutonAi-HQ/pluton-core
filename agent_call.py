import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fennik_agent import call_agent as caller, get_history as history
from tools.format_markdown import format_telegram_markdown


def call_agent(
    message: str,
    session_id: str,
    images: list[str] = [],
    user_id: str = None,
    stream: bool = False,
):
    response = caller(
        message=message,
        session_id=session_id,
        images=images,
        user_id=user_id,
        stream=stream,
    )
    print(response)
    return response


def get_history(session_id: str, user_id: str):
    return history(session_id, user_id)
