from phi.agent import Agent
from phi.tools.hackernews import HackerNews
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k
from phi.model.google import Gemini
import os
from dotenv import load_dotenv
from phi.storage.agent.postgres import PgAgentStorage
import typer
from tools.image_analyzer import analyze_image
from tools.token import get_tokens_information
from tools.search import search
from config import settings
from rich import print
from logging import getLogger, INFO, basicConfig
from constants import image_analysis_system_prompt
from log import logger
from rich.console import Console
from rich.json import JSON
from tools.jupiter import JupiterTool
from phi.model.azure import AzureOpenAIChat

console = Console()
from phi.model.openai import OpenAIChat
from phi.model.aws.claude import Claude
from uuid import uuid4
from app.services.wallet import WalletService
from app.database.client import get_db
from sqlalchemy.orm import Session

db_url = settings.POSTGRES_URL
storage = PgAgentStorage(
    # store sessions in the ai.sessions table
    table_name="agent_sessions",
    # db_url: Postgres database URL
    db_url=db_url,
)


def get_history(user_id: str, session_id: str = None):
    logger.info(f"Getting history for session {session_id} and user {user_id}")
    sessions = storage.get_all_sessions(user_id=user_id)
    history = []
    if session_id:
        session = next((s for s in sessions if s.session_id == session_id), None)
        if session is None:
            logger.info(f"No session found for {session_id} and user {user_id}")
            return history
        for run in session.memory.get("runs"):
            user_message = run.get("message").get("content")
            created_at = run.get("message").get("created_at")
            images_message = [
                message.get("images")
                for message in run.get("response").get("messages")
                if message.get("role") == "user"
            ][0]
            agent_message = run.get("response").get("content")
            result = [
                {
                    "role": "user",
                    "content": user_message,
                    "images": images_message,
                    "session_id": session.session_id,
                    "created_at": created_at,
                },
                {
                    "role": "assistant",
                    "content": agent_message,
                    "session_id": session.session_id,
                },
            ]
            history.extend(result)
        return history
    else:
        all_sessions = []
        for session in sessions:
            history = []
            session_id = session.session_id
            for run in session.memory.get("runs"):
                user_message = run.get("message").get("content")
                created_at = run.get("message").get("created_at")
                agent_message = run.get("response").get("content")
                history.extend(
                    [
                        {
                            "role": "user",
                            "content": user_message,
                            "session_id": session_id,
                            "created_at": created_at,
                        },
                        {
                            "role": "assistant",
                            "content": agent_message,
                            "session_id": session_id,
                        },
                    ]
                )
            all_sessions.append(history)
        return all_sessions


def call_agent(
    message: str,
    session_id: str,
    images: list[str] = [],
    user_id: str = None,
    stream: bool = False,
    db: Session = None,
):
    if db is None:
        db = next(get_db())

    tools = [
        search,
        analyze_image,
        get_tokens_information,
        JupiterTool(),
    ]
    #     azure_model = AzureOpenAIChat(
    #     id="gpt-4o-mini",
    #     api_key="60faaa4f139c4047b60657b4d2393efc",
    #     azure_endpoint="https://aitoolvbi.openai.azure.com/",
    #     azure_deployment="gpt-4o-mini",
    # )
    multi_agent_team = Agent(
        name="Multi Agent Team",
        tools=tools,
        model=OpenAIChat(id="gpt-4o-mini", temperature=0.3, max_tokens=16000),
        description="""You are PlutonAI, an expert in analyzing images and charts,... etc""",
        instructions=[
            "Carefully read and analyze questions to understand user requirements ",
            "Consider whether it is necessary to use tools to fulfill the user's request. If so, determine which tools to use and execute them to obtain output.",
            "Use search tools to search the web for accurate and up-to-date information before answering user questions that require providing knowledge",
            "If the user asks about a wallet, ask the wallet agent to get information about the wallet. If the wallet is not generated, generate a new wallet.",
            "Before calling wallet agent, you must warn the user about the risk of revealing their wallet information and ask for their consent to proceed.",
            "If the user sends an image link or requests image analysis, use tool analyze image to analyze image and provide a analysis.",
            "If the user asks about a trade, call the trader agent to trade on the market.",
            "If the user asks about coins, tokens, or crypto trends, use the suggest tokens tool to provide a brief summary of the coin.",
            "Finally, provide a thoughtful and engaging summary. Not include any tool calls",
            "Response could include emojis.",
            "Before execute any tool, notify the user your action",
            "Ask clarifying questions if the query is unclear",
            "Double check answers to ensure complete and accurate information",
            # "You can ONLY use the tools following:  ",
            # f"{tools}",
            "Return your response in MARKDOWN format.",
        ],
        # show_tool_calls=True,
        markdown=True,
        storage=storage,
        read_chat_history=True,
        session_id=session_id,
        num_history_responses=5,
        add_chat_history_to_messages=True,
        user_id=user_id,
        debug_mode=True,
        add_datetime_to_instructions=True,
        read_tool_call_history=True,
        additional_context=f"You own the wallet with address: {WalletService(db).get_wallet_by_user_id(user_id) if user_id else None}",
        context={
            "user_id": user_id,
            "session_id": session_id,
        },
    )
    # multi_agent_team.print_response(message=message + " " + "\n".join(images), stream=stream, markdown = True)
    return multi_agent_team.run(
        message=message + " " + "\n".join(images), stream=stream
    )


if __name__ == "__main__":
    # Chạy hàm call_agent với các tham số mẫu
    user_id = "50c96bb8-359e-4adf-bec7-4532895b2bbb"
    session_id = str(uuid4())
    while True:
        message = input("Nhập message:     ")
        if message in ["q", "exit"]:
            break
        response = call_agent(
            message=message, session_id=session_id, user_id=user_id, stream=True
        )
        aggregated_response = ""
        for chunk in response:
            aggregated_response += chunk.content
        print(aggregated_response)
