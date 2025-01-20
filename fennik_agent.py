import sys
sys.path.append(".")
from phi.agent import Agent
from phi.tools.hackernews import HackerNews
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k
from phi.model.google import Gemini
import os
from dotenv import load_dotenv
from phi.storage.agent.postgres import PgAgentStorage
import typer
from tools.image_analyzer import ImageAnalyzer
from tools.token import TokenTrending
from config import settings
from rich import print
from logging import getLogger, INFO, basicConfig
from constants import image_analysis_system_prompt
basicConfig(level=INFO)
logger = getLogger(__name__)

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
    logger.info(f"Sessions: {sessions}")

    if session_id:
        session = next((s for s in sessions if s.session_id == session_id), None)
        if session is None:
            logger.info(f"No session found for {session_id} and user {user_id}")
            return history
        for run in session.memory.get("runs"):
            user_message = run.get("message").get("content")
            agent_message = run.get("response").get("content")
            result = [
                {
                    "role": "user",
                    "content": user_message,
                    "session_id": session.session_id,
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
                agent_message = run.get("response").get("content")
                history.extend(
                    [
                        {
                            "role": "user",
                            "content": user_message,
                            "session_id": session_id,
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
):
    fennik_team = Agent(
        provider=Gemini(
            api_key=settings.GEMINI_API_KEY, 
            id="gemini-1.5-flash-latest"),
        name="Fennik Team",
        description= """You are PlutonAI, an intelligent virtual assistant with the ability to search for information on the web, analyze images, and provide cryptocurrency suggestions.

You have the capability to interact with users to understand their requests and provide accurate and helpful information.

You can analyze the content of images to provide detailed information and summaries about the objects within the image.

Based on the analysis of images, you can also suggest investment strategies related to the identified elements.

You can also suggest trending cryptocurrencies based on market analysis and user preferences.

Always ensure that you warn users about the risks associated with wallet information and request their consent before taking any actions.

Finally, provide engaging and friendly responses, which may include emojis.""",
        instructions=[
            "Carefully read and analyze questions to understand user requirements ",
            "Search for relevant information from reliable sources",
            "Create detailed, accurate and easy-to-understand answers",
            "Ask clarifying questions if the query is unclear",
            "Double check answers to ensure complete and accurate information",
            "If the user asks about a wallet, ask the wallet agent to get information about the wallet. If the wallet is not generated, generate a new wallet.",
            "Before calling wallet agent, you must warn the user about the risk of revealing their wallet information and ask for their consent to proceed.",
            "If the user provides an image, analyze the image and provide a summary of the image.",
            "If the user asks about a trade, call the trader agent to trade on the market.",
            "Finally, provide a thoughtful and engaging summary. Not include any tool calls",
            "Response could include emojis.",
        ],
        tools=[DuckDuckGo(), ImageAnalyzer(), TokenTrending()],
        show_tool_calls=True,
        markdown=True,
        storage=storage,
        read_chat_history=True,
        session_id=session_id,
        num_history_responses=5,
        add_chat_history_to_messages=True,
        user_id=user_id,
        debug_mode=True,
        prevent_hallucinations = True,
        add_datetime_to_instructions = True,
        read_tool_call_history = True
        )

    # image_analyzer = Agent(
    #     provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-flash-latest"),
    #     name="Image Analyzer",
    #     role="Analyzes the image",
    #     add_datetime_to_instructions=True,
    #     tools=[ImageAnalyzer()],
    #     description="This agent is useful for analyzing images to extract features, identify objects, and provide a detailed description of the image. It is also useful for providing investment strategies related to the identified elements."  # Updated description according to the new structure
    # )
    
    
    # coin_suggestor = Agent(
    #     provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-flash-latest"),
    #     name="Coin Suggestor",  
    #     role="Coin recommender", 
    #     add_datetime_to_instructions=True,
    #     tools=[TokenTrending()],
    #     description="This agent is useful for suggesting trending cryptocurrencies."  
    # )


    # fennik_team = Agent(
    #     provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-flash-latest", system_prompt = "You are PlutonAI."),
    #     name="Fennik Team",
    #     team=[web_searcher, image_analyzer, coin_suggestor],
    #     instructions=[
    #         "First, search the web for what the user is asking about.",
    #         "If the user asks about a wallet, ask the wallet agent to get information about the wallet. If the wallet is not generated, generate a new wallet.",
    #         "Before calling wallet agent, you must warn the user about the risk of revealing their wallet information and ask for their consent to proceed.",
    #         "If the user provides an image, analyze the image and provide a summary of the image.",
    #         "If the user asks about a trade, call the trader agent to trade on the market.",
    #         "Finally, provide a thoughtful and engaging summary. Not include any tool calls",
    #         "Response could include emojis.",
    #     ],
    #     show_tool_calls=True,
    #     markdown=True,
    #     storage=storage,
    #     read_chat_history=True,
    #     session_id=session_id,
    #     num_history_responses=5,
    #     add_chat_history_to_messages=True,
    #     user_id=user_id,
    #     debug_mode=True,
    #     add_datetime_to_instructions = True
    #      )

    return fennik_team.run(message=message, images=images, stream=stream)

if __name__ == "__main__":
    # Chạy hàm call_agent với các tham số mẫu
    user_id = "phuctinh"
    session_id = "2"
    while True:
        message = input("Nhập message:     ")
        if message in ['q', 'exit']:
            break
        response = call_agent(message=message, session_id=session_id, user_id = user_id)
        print(response)  # In ra phản hồi từ hàm call_agent
    