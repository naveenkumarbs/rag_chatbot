import httpx
import re

from app.core.config import settings
from app.rag.providers.base import LLMProvider

class OllamaLLMProvider(LLMProvider):

    def __init__(self):
        self.base_url = settings.ollama_base_url.rstrip("/")
        self.model = settings.ollama_chat_model

    def generate(
        self,
        prompt: str
    ) -> str:

        timeout = httpx.Timeout(
            connect=10.0,
            read=300.0,
            write=30.0,
            pool=10.0
        )
        
        response = httpx.post(
            f"{self.base_url}/api/chat",
            json={
                "model": self.model,
                "messages": [
                    {
                        "role": "user",
                        "content": prompt + "\n\n/no_think"
                    }
                ],
                "stream": False,
                "think": False,
                "keep_alive": "10m",
                "options": {
                    "num_predict": 300
                }
            },
            timeout=timeout
        )


        response.raise_for_status()

        data = response.json()

        content = (
            data
            .get("message",{})
            .get("content","")
            .strip()
        )

        # Remove Qwen-style reasoning blocks
        # <think> ... </think> blocks

        content = re.sub(
            r"<think>.*?</think>",
            "",
            content,
            flags=re.DOTALL | re.IGNORECASE
        ).strip()

        # some Qwen/ollama combinations return reasoning text
        # followed only by </think>. In that case keep only
        # the content after the closing tag.
        if "</think>" in content:
            content = content.split("</think>")[-1].strip()

        if not content:
            raise RuntimeError(
                f"Ollama returned empty content. Raw response: {data}"
            )

        return content