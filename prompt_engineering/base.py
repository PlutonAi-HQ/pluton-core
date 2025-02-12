from pydantic import BaseModel
from typing import List, Optional


class BasePrompt(BaseModel):
    description: Optional[str] = None
    instructions: Optional[List[str]] = None
    system_prompt: Optional[str] = None

    def __str__(self):
        return f"{self.description}\n{self.instructions}"
