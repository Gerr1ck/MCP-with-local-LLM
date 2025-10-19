from typing import Optional, List, Dict, Any
from .cli_executor import CLIExecutor
from .prompt_builder import ChatPromptBuilder
from .response_parser import RegexResponseParser
from .tool_formatter import MCPToolFormatter
from .mcp_tool_selector import MCPToolSelector
from .interfaces import ExecutorInterface, PromptBuilderInterface, ResponseParserInterface, ToolFormatterInterface


class LLMClient:
    """Facade for LLM communication that coordinates multiple specialized components."""

    def __init__(self, 
                 exe_path: str = "./genie_bundle/genie-t2t-run.exe", 
                 config_file: str = "genie_bundle/genie_config.json", 
                 cwd: Optional[str] = None,
                 executor: Optional[ExecutorInterface] = None,
                 prompt_builder: Optional[PromptBuilderInterface] = None,
                 response_parser: Optional[ResponseParserInterface] = None,
                 tool_formatter: Optional[ToolFormatterInterface] = None):
        
        # Initialize components with dependency injection capability
        self.executor = executor or CLIExecutor(exe_path, config_file, cwd)
        self.prompt_builder = prompt_builder or ChatPromptBuilder()
        self.response_parser = response_parser or RegexResponseParser()
        self.tool_formatter = tool_formatter or MCPToolFormatter()
        
        # Initialize tool selector with all components
        self.tool_selector = MCPToolSelector(
            self.executor,
            self.prompt_builder,
            self.response_parser,
            self.tool_formatter
        )
        
    def build_prompt(self, user_message: str) -> str:
        """Build a chat prompt from user message."""
        return self.prompt_builder.build_chat_prompt(user_message)

    def ask(self, prompt: str) -> str:
        """Send the prompt to the LLM and return extracted response."""
        raw_response = self.executor.execute(prompt)
        return self.response_parser.extract_content(raw_response)

    def choose_mcp_tools(self, user_request: str, available_tools: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Ask the LLM to choose which MCP server tools are needed for a given user request.
        
        Args:
            user_request: The user's request/query
            available_tools: List of available MCP tools with their descriptions and schemas
            
        Returns:
            List of tools that should be called with their arguments
        """
        return self.tool_selector.select_tools(user_request, available_tools)
    
    

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
