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
from tools.token import TopTrending
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
    web_searcher = Agent(
        provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-flash-latest"),
        name="Web Searcher",
        role="Searches the web for information on a topic",
        tools=[DuckDuckGo()],
        add_datetime_to_instructions=True,
    )

    image_analyzer = Agent(
        provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-flash-latest"),
        name="Image Analyzer",
        role="Analyzes the image",
        add_datetime_to_instructions = True,
        tools = [ImageAnalyzer()],
        description="Useful for analyzing images to extract features, identify objects, and provide insights based on visual content, including a detailed description of the image and investment strategies related to the identified elements."  # Cập nhật mô tả theo cấu trúc mới
    )
    
    
    coin_suggestor = Agent(
        provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-flash-latest"),
        name="Coin Suggestor",  
        role="Recommends cryptocurrencies ", 
        add_datetime_to_instructions=True,
        tools=[TopTrending()] 
        description="Useful for suggesting trending cryptocurrencies based on market analysis, user preferences, and investment opportunities."  
    )


    fennik_team = Agent(
        provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-flash-latest"),
        name="Fennik Team",
        team=[web_searcher, image_analyzer, coin_suggestor],
        instructions=[
            "First, search the web for what the user is asking about.",
            "If the user asks about a wallet, ask the wallet agent to get information about the wallet. If the wallet is not generated, generate a new wallet.",
            "Before calling wallet agent, you must warn the user about the risk of revealing their wallet information and ask for their consent to proceed.",
            "If the user provides an image, analyze the image and provide a summary of the image.",
            "If the user asks about a trade, call the trader agent to trade on the market.",
            "Finally, provide a thoughtful and engaging summary. Not include any tool calls",
            "Response could include emojis.",
        ],
        show_tool_calls=False,
        markdown=True,
        storage=storage,
        read_chat_history=True,
        session_id=session_id,
        num_history_responses=5,
        add_chat_history_to_messages=True,
        user_id=user_id,
        debug_mode=True,
        add_datetime_to_instructions = True
        system_prompt = [
            "You are PlutonAI, an intelligent virtual assistant with the ability to search for information on the web, analyze images, and provide cryptocurrency suggestions.",
            "You have the capability to interact with users to understand their requests and provide accurate and helpful information.",
            "You can analyze the content of images to provide detailed information and summaries about the objects within the image.",
            "Based on the analysis of images, you can also suggest investment strategies related to the identified elements.",
            "You can also suggest trending cryptocurrencies based on market analysis and user preferences.",
            "Always ensure that you warn users about the risks associated with wallet information and request their consent before taking any actions.",
            "Finally, provide engaging and friendly responses, which may include emojis.",
        ]
    )

    return fennik_team.run(message=message, images=images, stream=stream)
