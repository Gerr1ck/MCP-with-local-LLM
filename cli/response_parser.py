"""
Response parser implementation for extracting and parsing LLM responses.
"""

import re
import json
from typing import List, Dict, Any
from .interfaces import ResponseParserInterface


class RegexResponseParser(ResponseParserInterface):
    """Parses responses using regex patterns to extract content."""
    
    def __init__(self, begin_marker: str = r"\[BEGIN\]:", end_marker: str = r"\[END\]"):
        self.content_pattern = re.compile(
            f"{begin_marker}\\s*(.*?){end_marker}", 
            re.DOTALL
        )
    
    def extract_content(self, raw_response: str) -> str:
        """Extract content between BEGIN and END markers."""
        match = self.content_pattern.search(raw_response)
        if match:
            return match.group(1).strip()
        # If markers not found, return empty string to avoid returning raw output
        return ""
    
    def parse_tool_calls(self, response: str) -> List[Dict[str, Any]]:
        """Parse tool calls from JSON response."""
        try:
            # Clean up the response
            response = self._clean_json_response(response)
            
            # Parse JSON
            parsed = json.loads(response)
            
            # Normalize to list format
            return self._normalize_tool_calls(parsed)
            
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            print(f"Failed to parse tool selection response: {e}")
            print(f"Response was: {response}")
            return []
    
    def _clean_json_response(self, response: str) -> str:
        """Clean up JSON response by removing markdown code blocks."""
        response = response.strip()
        
        # Remove markdown code blocks if present
        if response.startswith('```json'):
            response = response[7:]
        if response.startswith('```'):
            response = response[3:]
        if response.endswith('```'):
            response = response[:-3]
        
        return response.strip()
    
    def _normalize_tool_calls(self, parsed: Any) -> List[Dict[str, Any]]:
        """Normalize parsed JSON to consistent tool call format."""
        if isinstance(parsed, list):
            return parsed
        elif isinstance(parsed, dict):
            # Check for standard format: {"tool": "name", "arguments": {...}}
            if "tool" in parsed and "arguments" in parsed:
                return [parsed]
            # Handle nested format
            elif "tool" in parsed and parsed["tool"] == "function" and "arguments" in parsed:
                args = parsed["arguments"]
                if "function" in args and "arguments" in args:
                    tool_name = args["function"]
                    tool_args = args["arguments"]
                    return [{"tool": tool_name, "arguments": tool_args}]
            # Fallback: return as single item list
            return [parsed]
        else:
            return []