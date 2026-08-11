"""
LLM client abstraction (Dependency Inversion).

EnhancedSCMChatbot depends on this interface rather than importing and
constructing the Groq SDK directly, so the LLM provider can be swapped
or mocked in tests without touching business logic in enhanced_chatbot.py.
"""

from abc import ABC, abstractmethod
from typing import Dict, Iterator, List


class LLMClient(ABC):
    """Abstract interface for a chat-completion LLM client."""

    @abstractmethod
    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        """Return a single completed response string."""
        raise NotImplementedError

    @abstractmethod
    def complete_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Iterator[str]:
        """Yield the response incrementally as text chunks."""
        raise NotImplementedError


class GroqClient(LLMClient):
    """Groq-backed implementation of LLMClient."""

    def __init__(self, api_key: str, model: str = "llama-3.3-70b-versatile"):
        from groq import Groq

        self._client = Groq(api_key=api_key)
        self.model = model

    def complete(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> str:
        response = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
        )
        return response.choices[0].message.content

    def complete_stream(
        self,
        messages: List[Dict[str, str]],
        temperature: float = 0.3,
        max_tokens: int = 1024,
    ) -> Iterator[str]:
        stream = self._client.chat.completions.create(
            model=self.model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=True,
        )
        for chunk in stream:
            delta = chunk.choices[0].delta.content
            if delta:
                yield delta
