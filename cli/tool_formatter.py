"""
Tool formatter implementation for formatting MCP tool descriptions.
"""

from typing import List, Dict, Any
from .interfaces import ToolFormatterInterface


class MCPToolFormatter(ToolFormatterInterface):
    """Formats MCP tools into human-readable descriptions."""
    
    def format_tools(self, tools: List[Dict[str, Any]]) -> str:
        """Format available tools into a readable description for the LLM."""
        if not tools:
            return "No tools available."
        
        tools_text = "Available tools:\n"
        
        for i, tool in enumerate(tools, 1):
            name = tool.get('name', 'Unknown')
            description = tool.get('description', 'No description')
            
            # Extract parameters if available
            params_text = self._format_parameters(tool)
            
            tools_text += f"{i}. {name}: {description}{params_text}\n"
        
        return tools_text
    
    def _format_parameters(self, tool: Dict[str, Any]) -> str:
        """Format tool parameters into readable text."""
        input_schema = tool.get('inputSchema', {})
        properties = input_schema.get('properties', {})
        
        if not properties:
            return ""
        
        param_list = []
        for param_name, param_info in properties.items():
            param_type = param_info.get('type', 'unknown')
            param_desc = param_info.get('description', '')
            param_list.append(f"{param_name} ({param_type}): {param_desc}")
        
        return f"\n  Parameters: {', '.join(param_list)}"
    
    def convert_to_llm_tool(self, tool: Any) -> Dict[str, Any]:
        """Convert MCP tool to LLM-compatible tool schema (OpenAI function format)."""
        tool_schema = {
            "type": "function",
            "function": {
                "name": tool.name,
                "description": tool.description,
                "type": "function",
                "parameters": {
                    "type": "object",
                    "properties": tool.inputSchema["properties"]
                }
            }
        }
        return tool_schema