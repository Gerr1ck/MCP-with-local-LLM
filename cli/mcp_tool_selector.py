"""
MCP tool selector implementation for orchestrating tool selection logic.
"""

from typing import List, Dict, Any
from .interfaces import ExecutorInterface, PromptBuilderInterface, ResponseParserInterface, ToolFormatterInterface


class MCPToolSelector:
    """Orchestrates the tool selection process using LLM."""
    
    def __init__(self, 
                 executor: ExecutorInterface,
                 prompt_builder: PromptBuilderInterface, 
                 response_parser: ResponseParserInterface,
                 tool_formatter: ToolFormatterInterface):
        self.executor = executor
        self.prompt_builder = prompt_builder
        self.response_parser = response_parser
        self.tool_formatter = tool_formatter
    
    def select_tools(self, user_request: str, available_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Select appropriate tools for a user request using LLM.
        
        Args:
            user_request: The user's request/query
            available_tools: List of available MCP tools with their descriptions and schemas
            
        Returns:
            List of tools that should be called with their arguments
        """
        if not available_tools:
            return []
        
        try:            
            # Build prompt for tool selection
            prompt = self.prompt_builder.build_tool_selection_prompt(user_request, available_tools)
            
            # Execute and get raw response
            raw_response = self.executor.execute(prompt)
            
            # Extract content from raw response
            content = self.response_parser.extract_content(raw_response)
            
            # Parse tool calls from content
            return self.response_parser.parse_tool_calls(content)
            
        except Exception as e:
            print(f"Error in tool selection: {e}")
            return []