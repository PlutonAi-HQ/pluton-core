from langchain_google_genai import ChatGoogleGenerativeAI
import os
from config import settings
from constants import image_analysis_system_prompt
from typing import List

from phi.tools import Toolkit
from phi.utils.log import logger
os.environ["GOOGLE_API_KEY"] = settings.GEMINI_API_KEY
model =  ChatGoogleGenerativeAI(
    model="gemini-1.5-flash",
    temperature=0.3,
    max_tokens=8192)
class ImageAnalyzer(Toolkit):
    def __init__(self):
            super().__init__(name = "Image_Analyzer")
            self.register(self.image_analyzer)
    def image_analyzer(urls: list[str], query: str):
        """
        This agent is useful for analyzing images to extract features, identify objects, and provide a detailed description of the image. It is also useful for providing investment strategies related to the identified elements.

        Args:
            urls (list[str]): List of URLs to images for analysis.
            query (str): Query string to guide the analysis.

        Returns:
            str: Result of the image analysis.
        """
        try:
            import ast
            user_message_content = []
            user_message_content.append({'type': 'text', 'text': query})
            urls = ast.literal_eval(urls) if type(urls) != type([]) else urls
            for url in urls:
                user_message_content.append({"type": "image_url", "image_url": {"url": url}})
            messages = [{
                            "role": "system",
                            "content": image_analysis_system_prompt
                        },
                        
                        {
                            "role": "user",
                            "content": user_message_content
                        }
                    ]
            response = model.invoke(messages).content
            return response
        except Exception as e:
                return {"status": "error", "message": str(e)}
        