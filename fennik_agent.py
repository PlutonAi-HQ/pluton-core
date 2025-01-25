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
from tools.jupiter import swap_token, limit_order, cancel_all_orders

console = Console()

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
    print(sessions)
    if session_id:
        session = next((s for s in sessions if s.session_id == session_id), None)
        if session is None:
            logger.info(f"No session found for {session_id} and user {user_id}")
            return history
        for run in session.memory.get("runs"):
            user_message = run.get("message").get("content")
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
    tools = [
            search,
            analyze_image,
            get_tokens_information,
            swap_token,
            limit_order,
            cancel_all_orders,
        ]
    print("toools:    \n", tools)
    search_agent = Agent(provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-pro"),
        name="Web Search Agent",
        role = "You are PlutonAI, Search the web for accurate and up-to-date information",
        instruction =[
        "Always include sources and citations",
        "Verify information from multiple sources when possible",
        "Present information in a clear, structured format",
    ],
    tools = [search],
    show_tool_calls=True,
    markdown=True,
    storage=storage,
    tool_choice = 'auto',
    read_chat_history=True,
    session_id=session_id,
    num_history_responses=5,
    add_chat_history_to_messages=True,
    user_id=user_id,
    debug_mode=True,
    add_datetime_to_instructions=True,
    read_tool_call_history=True,
    monitoring=True)
    
    analyze_image_agent = Agent(provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-pro"),
        name="Image Analysis Agent",
        role = "You are PlutonAI, an expert in analyzing images and charts related to cryptocurrency and blockchain.",
        instruction = [
        "Thoroughly examine images and charts to identify key elements and features.",
        "Provide detailed descriptions of the content of images, including relevant context or implications.",
        "Identify and describe key technical indicators, price patterns, market trends, and network metrics for charts.",
        "Interpret the data using appropriate analytical techniques and frameworks.",
        "Offer well-reasoned insights, predictions, and trading/investment recommendations based on the analysis.",
        "Ensure the analysis is data-driven, objective, and tailored to the user's needs.",
        "Maintain a friendly, helpful, and professional tone throughout interactions."
    ],
    tools = [analyze_image],
    tool_choice = 'auto',
    show_tool_calls=True,
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
    monitoring=True)
    

    # Tạo agent cho tool `get_tokens_information`
    tokens_agent = Agent(
        provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-pro"),
        name="Tokens Trend Agent",
        role="You are PlutonAI, an expert in providing recommendations for trending tokens.",
        instruction=[
            "Provide information and recommendations about trending tokens.",
            "Include market data, recent performance, and news related to these tokens.",
            "Suggest tokens that are currently popular and have potential for growth.",
        ],
        tools=[get_tokens_information],
        show_tool_calls=True,
        markdown=True,
        tool_choice = 'auto',
        storage=storage,
        read_chat_history=True,
        session_id=session_id,
        num_history_responses=5,
        add_chat_history_to_messages=True,
        user_id=user_id,
        debug_mode=True,
        add_datetime_to_instructions=True,
        read_tool_call_history=True,
        monitoring=True
    )

    # Tạo agent cho tool `swap_token`
    swap_agent = Agent(
        provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-pro"),
        name="Token Swap Agent",
        role="You are PlutonAI, an expert in swapping tokens.",
        instruction=[
            "Assist users in swapping tokens efficiently.",
            "Provide information about swap rates and fees.",
            "Ensure the process is secure and user-friendly.",
        ],
        tools=[swap_token],
        show_tool_calls=True,
        markdown=True,   
        tool_choice = 'auto',
        storage=storage,
        read_chat_history=True,
        session_id=session_id,
        num_history_responses=5,
        add_chat_history_to_messages=True,
        user_id=user_id,
        debug_mode=True,
        add_datetime_to_instructions=True,
        read_tool_call_history=True,
        monitoring=True
    )

    # Tạo agent cho tool `limit_order`
    limit_order_agent = Agent(
        provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-pro"),
        name="Limit Order Agent",
        role="You are PlutonAI, an expert in placing limit orders.",
        instruction=[
            "Help users place limit orders on the market.",
            "Provide guidance on setting order parameters.",
            "Ensure users understand the risks involved.",
        ],
        tools=[limit_order],
        show_tool_calls=True,
        markdown=True,
        tool_choice = 'auto',
        storage=storage,
        read_chat_history=True,
        session_id=session_id,
        num_history_responses=5,
        add_chat_history_to_messages=True,
        user_id=user_id,
        debug_mode=True,
        add_datetime_to_instructions=True,
        read_tool_call_history=True,
        monitoring=True
    )

    # Tạo agent cho tool `cancel_all_orders`
    cancel_orders_agent = Agent(
        provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-pro"),
        name="Cancel All Orders Agent",
        role="You are PlutonAI, an expert in canceling orders.",
        instruction=[
            "Assist users in canceling all their active orders.",
            "Provide confirmation and details of canceled orders.",
            "Ensure the process is clear and straightforward.",
        ],
        tools=[cancel_all_orders],
        show_tool_calls=True,
        tool_choice = 'auto',
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
        monitoring=True
    )
    
    # print("TEAM:     \n", [search_agent, analyze_image_agent, tokens_agent, swap_agent, limit_order_agent, cancel_orders_agent])
    multi_agent_team = Agent(
        name="Multi Agent Team",
        # team=[search_agent, analyze_image_agent, tokens_agent, swap_agent, limit_order_agent, cancel_orders_agent],
        tools = tools,
        provider=Gemini(api_key=settings.GEMINI_API_KEY, id="gemini-1.5-pro"),
        description="""You are PlutonAI.""",
        instructions=[
            "Carefully read and analyze questions to understand user requirements ",
            "Consider whether it is necessary to use tools to fulfill the user's request. If so, determine which tools to use and execute them to obtain output.",
            "Use `search` tools to search the web for accurate and up-to-date information before answering user questions that require providing knowledge or real-time information.",
            "If the user asks about a wallet, ask the wallet agent to get information about the wallet. If the wallet is not generated, generate a new wallet.",
            "Before calling wallet agent, you must warn the user about the risk of revealing their wallet information and ask for their consent to proceed.",
            "If the user sends an image link or requests image analysis, use tool `analyze_image` to analyze image and provide a analysis.",
            "If the user asks about a trade, call the trader agent to trade on the market.",
            "If the user asks about a coin, use the `get_tokens_information` tool to provide a brief summary of the coin.",
            "Finally, provide a thoughtful and engaging summary. Not include any tool calls",
            "Response could include emojis.",
            "Before execute any tool, notify the user your action",
            "Create detailed, accurate and easy-to-understand answers",
            "Ask clarifying questions if the query is unclear",
            "Double check answers to ensure complete and accurate information",
            "Do not provide tool names, function names, or disclaimers in the response",
            "You can ONLY use the tools following:  ",
            f"{tools}"
        ],
        show_tool_calls=True,
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
        add_context=True
    )

    return multi_agent_team.run(message=message + " " + "\n".join(images), stream=stream)


if __name__ == "__main__":
    # Chạy hàm call_agent với các tham số mẫu
    user_id = "phuctinh"
    session_id = "aaaaâaaâ"
    while True:
        message = input("Nhập message:     ")
        if message in ["q", "exit"]:
            break
        response = call_agent(message=message, session_id=session_id, user_id=user_id)
        print(response)  # In ra phản hồi từ hàm call_agent
    