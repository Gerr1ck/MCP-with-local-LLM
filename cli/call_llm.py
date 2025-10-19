import re
import subprocess
import json
from typing import Optional, List, Dict, Any


class LLMClient:
    """Simple wrapper to call a local LLM executable.

    Usage contract (minimal):
    - Inputs: user_message (either full tagged message or plain user content)
    - Output: stdout returned by the executable (string)
    - Errors: raises FileNotFoundError if executable missing; RuntimeError on non-zero exit
    """

    def __init__(self, exe_path: str = "./genie_bundle/genie-t2t-run.exe", config_file: str = "genie_bundle/genie_config.json", cwd: Optional[str] = None):
        self.exe_path = exe_path
        self.config_file = config_file
        # If you need to run with a specific working directory, pass cwd (e.g. "genie_bundle")
        self.cwd = cwd
        
    def build_prompt(self, user_message: str) -> str:
        """Return a full prompt string. 
        """
        return (
            "<|system|>\nYou are a helpful assistant. Be helpful but brief.<|end|>\n"
            f"<|user|>{user_message}\n<|end|>\n"
            "<|assistant|>\n"
        )

    def ask(self, prompt: str) -> str:
        """Send the prompt to the executable and return stdout."""

        print("Calling LLM with prompt:")
        print(prompt)

        command = [
            self.exe_path,
            "-c",
            self.config_file,
            "-p",
            prompt,
        ]

        try:
            result = subprocess.run(
                command,
                capture_output=True,
                text=True,
                check=True,
                cwd=self.cwd,
            )

            stdout_text = result.stdout

            # Look for the content between '[BEGIN]:' and '[END]'
            m = re.search(r"\[BEGIN\]:\s*(.*?)\[END\]", stdout_text, re.DOTALL)
            if m:
                # Return trimmed inner text
                return m.group(1).strip()

            # If markers not found, return empty string to avoid returning the whole stdout.
            return ""

        except FileNotFoundError:
            raise FileNotFoundError(f"Executable not found at {self.exe_path}")

        except subprocess.CalledProcessError as e:
            # Even in failure, try to extract the marked response from stdout if present
            stdout_text = e.stdout or ""
            m = re.search(r"\[BEGIN\]:\s*(.*?)\[END\]", stdout_text, re.DOTALL)
            if m:
                return m.group(1).strip()

            raise RuntimeError(f"Command failed with exit code {e.returncode}\nstdout:\n{e.stdout}\nstderr:\n{e.stderr}")

    def choose_mcp_tools(self, user_request: str, available_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ask the LLM to choose which MCP server tools are needed for a given user request.
        
        Args:
            user_request: The user's request/query
            available_tools: List of available MCP tools with their descriptions and schemas
            
        Returns:
            List of tools that should be called with their arguments
        """
        if not available_tools:
            return []
        
        """tools_description = self._format_tools_for_llm(available_tools)"""
        prompt = self._build_tool_selection_prompt(user_request, available_tools)
        
        try:
            response = self.ask(prompt)
            return self._parse_tool_selection_response(response)
        except Exception as e:
            print(f"Error in tool selection: {e}")
            return []
    
    def _format_tools_for_llm(self, tools: List[Dict[str, Any]]) -> str:
        """Format available tools into a readable description for the LLM."""
        tools_text = "Available tools:\n"
        
        for i, tool in enumerate(tools, 1):
            name = tool.get('name', 'Unknown')
            description = tool.get('description', 'No description')
            
            # Extract parameters if available
            input_schema = tool.get('inputSchema', {})
            properties = input_schema.get('properties', {})
            
            params_text = ""
            if properties:
                param_list = []
                for param_name, param_info in properties.items():
                    param_type = param_info.get('type', 'unknown')
                    param_desc = param_info.get('description', '')
                    param_list.append(f"{param_name} ({param_type}): {param_desc}")
                params_text = f"\n  Parameters: {', '.join(param_list)}"
            
            tools_text += f"{i}. {name}: {description}{params_text}\n"
        
        return tools_text
    
    def _build_tool_selection_prompt(self, user_request: str, tools_description: str) -> str:
        """Build a prompt asking the LLM to select appropriate tools."""
        return (
            "<|system|>\nYou are an AI assistant that helps select the right tools for a user's request.\n"
            "Given a user request and a list of available tools from the MCP Server, you need to:\n\n"
            "1. Analyze the user's request\n"
            "2. Select the appropriate tool(s) that can fulfill the request\n"
            "3. Provide the necessary arguments for each selected tool\n"
            "4. Respond ONLY in valid JSON with the following schema:\n\n"
            "{{\n"
            '  "tool": "<tool_name>",\n'
            '  "arguments": {{ ... }}\n'
            "}}\n\n"
            "If no tools are needed, respond with an empty array: []\n\n"
            "<|end|>\n"
            
            f"<|user|>User request: {user_request}\n\n"
            f"Available Tools at MCP Server: {tools_description}\n\n"
            "Please select the appropriate tools and provide the arguments needed to fulfill this request.\n"
            "<|end|>\n"
            "<|assistant|>\n"
        )
    
    def _parse_tool_selection_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse the LLM response to extract tool calls in the expected format."""
        try:
            # Strip whitespace
            response = response.strip()
            
            # Remove markdown code blocks if present
            if response.startswith('```json'):
                response = response[7:]  # Remove ```json
            if response.startswith('```'):
                response = response[3:]  # Remove ```
            if response.endswith('```'):
                response = response[:-3]  # Remove ending ```
            
            response = response.strip()
            
            # Try to parse as JSON
            parsed = json.loads(response)
            
            # Handle different response formats
            if isinstance(parsed, list):
                # Already a list, return as is
                return parsed
            elif isinstance(parsed, dict):
                # Single tool call, convert to list
                # Check if it's in the expected format: {"tool": "name", "arguments": {...}}
                if "tool" in parsed and "arguments" in parsed:
                    return [parsed]
                # Handle the nested format from your example
                elif "tool" in parsed and parsed["tool"] == "function" and "arguments" in parsed:
                    args = parsed["arguments"]
                    if "function" in args and "arguments" in args:
                        # Extract the actual tool name and arguments
                        tool_name = args["function"]
                        tool_args = args["arguments"]
                        return [{"tool": tool_name, "arguments": tool_args}]
                # Fallback: return as single item list
                return [parsed]
            else:
                return []
            
        except (json.JSONDecodeError, AttributeError, KeyError) as e:
            print(f"Failed to parse tool selection response: {e}")
            print(f"Response was: {response}")
            return []
    
    

if __name__ == "__main__":
    client = LLMClient()

    # Example: pass either the full tagged prompt or just the plain user content.
    example_prompt = "Whats the capital of Switzerland?"

    print("Running example prompt...")
    try:
        prompt = client.build_prompt(example_prompt)
        response = client.ask(example_prompt)
        print("\n--- Response ---")
        print(response)
    except Exception as exc:
        print("Error:", exc)
