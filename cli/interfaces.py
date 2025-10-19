"""
Abstract interfaces for LLM client components.
These interfaces define contracts for different responsibilities.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional


class ExecutorInterface(ABC):
    """Interface for executing commands and getting responses."""
    
    @abstractmethod
    def execute(self, prompt: str) -> str:
        """Execute a command with the given prompt and return raw output."""
        pass


class PromptBuilderInterface(ABC):
    """Interface for building various types of prompts."""
    
    @abstractmethod
    def build_chat_prompt(self, user_message: str) -> str:
        """Build a chat prompt from user message."""
        pass
    
    @abstractmethod
    def build_tool_selection_prompt(self, user_request: str, tools_description: str) -> str:
        """Build a prompt for tool selection."""
        pass


class ResponseParserInterface(ABC):
    """Interface for parsing responses from LLM."""
    
    @abstractmethod
    def extract_content(self, raw_response: str) -> str:
        """Extract clean content from raw response."""
        pass
    
    @abstractmethod
    def parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """Parse tool calls from LLM response."""
        pass


class ToolFormatterInterface(ABC):
    """Interface for formatting tool descriptions."""
    
    @abstractmethod
    def format_tools(self, tools: List[Dict[str, Any]]) -> str:
        """Format tools into readable description."""
        pass