"""
Prompt builder implementation for various prompt types.
"""

from .interfaces import PromptBuilderInterface


class ChatPromptBuilder(PromptBuilderInterface):
    """Builds prompts in chat format with system/user/assistant tags."""
    
    def __init__(self, system_message: str = "You are an ultra-concise, factual assistant. Answer the user's request directly and avoid any unnecessary elaboration, conversational padding, or self-reference."):
        self.system_message = system_message
    
    def build_chat_prompt(self, user_message: str) -> str:
        """Build a chat prompt with proper formatting."""
        return (
            f"<|system|>\n{self.system_message}<|end|>\n"
            f"<|user|>{user_message}\n<|end|>\n"
            "<|assistant|>\n"
        )
    
    def build_tool_selection_prompt(self, user_request: str, tools_description: str) -> str:
        """Build a prompt for tool selection with specific instructions."""
        system_prompt = (
            "You are an AI assistant that helps select the right tools for a user's request.\n"
            "Given a user request and a list of available tools from the MCP Server, you need to:\n\n"
            "1. Analyze the user's request\n"
            "2. Select the appropriate tool(s) that can fulfill the request\n"
            "3. Provide the necessary arguments for each selected tool\n"
            "4. Respond ONLY in valid JSON with the following schema:\n\n"
            "{\n"
            '  "tool": "<tool_name>",\n'
            '  "arguments": { ... }\n'
            "}\n\n"
            "If no tools are needed, respond with an empty array: []"
        )
        
        user_prompt = (
            f"User request: {user_request}\n\n"
            f"Available Tools at MCP Server: {tools_description}\n\n"
            "Please select the appropriate tools and provide the arguments needed to fulfill this request."
        )
        
        return (
            f"<|system|>\n{system_prompt}<|end|>\n"
            f"<|user|>{user_prompt}\n<|end|>\n"
            "<|assistant|>\n"
        )