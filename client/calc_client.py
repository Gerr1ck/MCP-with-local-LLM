from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
import asyncio
import os
import sys

# Add the parent directory to sys.path so we can import from cli package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# llm
from cli.call_llm import LLMClient
from cli.tool_formatter import MCPToolFormatter

class MCPClient:
    def __init__(self):
        # Use the working example server from ../server/calc_server.py
        server_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server', 'calc_server.py'))
        
        print(f"Using server script at: {server_script}")

        self.server_params = StdioServerParameters(
            command=sys.executable,  # Use the same python interpreter that's running this client
            args=[server_script],  # Absolute path to server script
            env=None,  # Optional environment variables
        )

        self.llm_client = LLMClient()
        self.tool_formatter = MCPToolFormatter()

    def choose_mcp_tools(self, prompt, functions):
        
        response = self.llm_client.choose_mcp_tools(prompt, functions)
        print("LLM response: ", response)
        
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

    async def run(self):
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    print("Connecting to MCP server...")

                    await session.initialize()

                    print("Connected to MCP server successfully!")

                    # List available resources
                    resources = await session.list_resources()
                    print("LISTING RESOURCES")
                    for resource in resources:
                        print("Resource: ", resource)

                    # List available resources templates
                    resource_templates = await session.list_resource_templates()
                    print("LISTING RESOURCE TEMPLATES")
                    for template in resource_templates:
                        print("Template: ", template)

                    # List available tools
                    tools = await session.list_tools()
                    print("LISTING TOOLS")
                    functions = []
                    for tool in tools.tools:
                        print("Tool: ", tool.name)
                        print("Tool: ", tool.inputSchema["properties"])
                        functions.append(self.tool_formatter.convert_to_llm_tool(tool))

                    # Read a resource
                    print("READING RESOURCE")
                    content, mime_type = await session.read_resource("greeting://hello")
                    print(f"Content: {content}, MIME Type: {mime_type}")

                    # Call a tool
                    print("CALL TOOL")
                    result = await session.call_tool("add", arguments={"a": 1, "b": 7})
                    print(result.content)

                    # Use LLM to decide what tools to call
                    print("USING LLM TO DECIDE WHAT TOOLS TO CALL")
                    prompt = "Add 2 to 20"
                    # ask LLM what tools to all, if any
                    functions_to_call = self.choose_mcp_tools(prompt, functions)

                    # call suggested functions
                    for f in functions_to_call:
                        result = await session.call_tool(f["name"], arguments=f["args"])
                        print("LLM result: ", result.content)

                    print("\n Client operations completed successfully!")

        except Exception as e:
            import traceback

            print(f"Error running MCP client: {e}")
            traceback.print_exc()
            raise


async def main():
    client = MCPClient()
    await client.run()


if __name__ == "__main__":
    asyncio.run(main())