from phi.agent import Agent
from phi.tools.hackernews import HackerNews
from phi.tools.duckduckgo import DuckDuckGo
from phi.tools.newspaper4k import Newspaper4k
from phi.model.google import Gemini
import os
from dotenv import load_dotenv
from phi.storage.agent.postgres import PgAgentStorage
import typer
from tools.wallet import get_wallet_secret, generate_wallet
from tools.trade import faucet
from config import settings

db_url = settings.POSTGRES_URL
storage = PgAgentStorage(
    # store sessions in the ai.sessions table
    table_name="agent_sessions",
    # db_url: Postgres database URL
    db_url=db_url,
)


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

    wallet_agent = Agent(
        provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-flash-latest"),
        name="Wallet Agent",
        role="Do everything related to the wallet. Cannot generate wallet and cannot get wallet secret at the same time.",
        additional_context="The chat_id will be the session_id: {}".format(session_id),
        tools=[get_wallet_secret, generate_wallet],
    )
    image_analyzer = Agent(
        provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-flash-latest"),
        name="Image Analyzer",
        role="Analyzes the image",
    )

    trader = Agent(
        provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-flash-latest"),
        name="Trader",
        role="Trades on the market. Swaps tokens, buys and sells tokens. Faucets, airdrops tokens.",
        additional_context=" The chat_id will be the session_id: {}".format(session_id),
        tools=[faucet],
    )

    fennik_team = Agent(
        provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-flash-latest"),
        name="Fennik Team",
        team=[web_searcher, wallet_agent, image_analyzer, trader],
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
    )

    return fennik_team.run(message=message, images=images, stream=stream)
