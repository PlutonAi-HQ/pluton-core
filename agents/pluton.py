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


from phi.model.openai import OpenAIChat
from phi.model.aws.claude import Claude
from uuid import uuid4
from app.services.wallet import WalletService
from app.database.client import get_db
from sqlalchemy.orm import Session
from prompt_engineering.pluton import PlutonPrompt
from pydantic import BaseModel
from typing import List, Any, Optional
from prompt_engineering.base import BasePrompt
from pydantic import ConfigDict


class PlutonAgent(BaseModel):
    user_id: str | None = None
    session_id: str | None = None
    agent: Agent | None = None
    tools: Optional[List[Any]] = None
    prompt: Optional[BasePrompt] = PlutonPrompt()
    storage: Optional[PgAgentStorage] = None
    db: Session = next(get_db())
    wallet_address: str | None = None

    model_config = ConfigDict(
        arbitrary_types_allowed=True, populate_by_name=True, extra="allow"
    )

    def get_wallet_address(self):
        if self.user_id:
            wallet = WalletService(self.db).get_wallet_by_user_id(self.user_id)
            if wallet:
                self.wallet_address = wallet.public_key
        return self.wallet_address

    def get_tools(self):
        if self.tools is None:
            self.tools = [
                search,
                analyze_image,
                get_tokens_information,
                JupiterTool(),
            ]
        return self.tools

    def get_agent(self):
        return Agent(
            tools=self.get_tools(),
            storage=self.get_storage(),
            description=self.prompt.description,
            instructions=self.prompt.instructions,
            system_prompt=self.prompt.system_prompt,
            user_id=self.user_id,
            session_id=self.session_id,
            markdown=True,
            read_chat_history=True,
            num_history_responses=5,
            add_chat_history_to_messages=True,
            debug_mode=True,
            add_datetime_to_instructions=True,
            read_tool_call_history=True,
            additional_context=f"You own the wallet with address: {self.get_wallet_address()}",
            context={
                "user_id": self.user_id,
                "session_id": self.session_id,
            },
        )

    def get_storage(self):
        if self.storage is None:
            self.storage = PgAgentStorage(
                table_name="agent_sessions",
                db_url=settings.POSTGRES_URL,
            )
        return self.storage

    def run(self, message: str, stream: bool = True):
        agent = self.get_agent()
        return agent.run(message, stream=stream)


if __name__ == "__main__":
    user_id = "50c96bb8-359e-4adf-bec7-4532895b2bbb"
    session_id = str(uuid4())
    pluton = PlutonAgent(user_id=user_id, session_id=session_id)
    while True:
        message = input("Enter a message: ")
        logger.info(pluton.run(message, stream=False).content)
