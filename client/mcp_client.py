from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import os
import sys

# Add the parent directory to sys.path so we can import from cli package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# llm
from cli.call_llm import LLMClient
from cli.tool_formatter import MCPToolFormatter


class MCPClient:
    """
    Generic MCP Client for connecting to MCP servers.
    
    This is a base client that provides core functionality for:
    - Connecting to MCP servers
    - Listing and reading resources
    - Listing available tools
    - Calling tools on the server
    - Using LLM to select tools based on prompts
    
    Subclasses can override methods or the run() method to implement
    specific use case workflows.
    """
    
    def __init__(self, server_script_path):
        """
        Initialize the MCP Client.
        
        Args:
            server_script_path: Absolute path to the MCP server script
        """
        print(f"\n{'='*60}")
        print(f"MCP Client Configuration")
        print(f"{'='*60}")
        print(f"Server script: {server_script_path}")

        self.server_params = StdioServerParameters(
            command=sys.executable,
            args=[server_script_path],
            env=None,
        )

        self.llm_client = LLMClient()
        self.tool_formatter = MCPToolFormatter()

    def choose_mcp_tools(self, prompt, functions):
        """
        Use LLM to choose which tools to call based on the prompt.
        
        Args:
            prompt: The user's prompt
            functions: Available functions/tools
            
        Returns:
            List of functions to call with their arguments
        """
        response = self.llm_client.choose_mcp_tools(prompt, functions)
        print(f"\nLLM Response: {response}")
        
        functions_to_call = []
        if response:
            for tool_call in response:
                # Handle the nested JSON structure: {"tool": "function", "arguments": {"function": "add", "arguments": {...}}}
                if tool_call.get("tool") == "function":
                    args_section = tool_call.get("arguments", {})
                    function_name = args_section.get("function", "")
                    function_args = args_section.get("arguments", {})
                    
                    if function_name:  # Only add if we have a valid tool name
                        functions_to_call.append({"name": function_name, "args": function_args})
        
        return functions_to_call

    async def list_resources(self, session):
        """
        List all available resources from the server.
        
        Args:
            session: The MCP session
            
        Returns:
            List of resources
        """
        resources = await session.list_resources()
        return resources

    async def list_resource_templates(self, session):
        """
        List all available resource templates from the server.
        
        Args:
            session: The MCP session
            
        Returns:
            List of resource templates
        """
        resource_templates = await session.list_resource_templates()
        return resource_templates

    async def list_tools(self, session):
        """
        List all available tools from the server.
        
        Args:
            session: The MCP session
            
        Returns:
            List of function definitions converted to LLM tools
        """
        tools = await session.list_tools()
        functions = []
        for tool in tools.tools:
            functions.append(self.tool_formatter.convert_to_llm_tool(tool))
        return functions, tools

    async def read_resource(self, session, resource_uri):
        """
        Read a resource from the server.
        
        Args:
            session: The MCP session
            resource_uri: The URI of the resource to read
            
        Returns:
            Tuple of (content, mime_type)
        """
        content, mime_type = await session.read_resource(resource_uri)
        return content, mime_type

    async def call_tool(self, session, tool_name, arguments):
        """
        Call a tool on the server.
        
        Args:
            session: The MCP session
            tool_name: Name of the tool to call
            arguments: Arguments to pass to the tool
            
        Returns:
            The result of the tool call
        """
        result = await session.call_tool(tool_name, arguments=arguments)
        return result

    async def run(self):
        """
        Main entry point for the MCP client.
        Override this method in subclasses to implement specific workflows.
        
        Raises:
            NotImplementedError: This base class doesn't implement a specific workflow
        """
        raise NotImplementedError("Subclasses must implement the run() method")
