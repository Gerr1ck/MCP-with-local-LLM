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
        
        print(f"\n{'='*60}")
        print(f"MCP Client Configuration")
        print(f"{'='*60}")
        print(f"Server script: {server_script}")

        self.server_params = StdioServerParameters(
            command=sys.executable,  # Use the same python interpreter that's running this client
            args=[server_script],  # Absolute path to server script
            env=None,  # Optional environment variables
        )

        self.llm_client = LLMClient()
        self.tool_formatter = MCPToolFormatter()

    def choose_mcp_tools(self, prompt, functions):
        
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

    async def run(self):
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # ============== SERVER CONNECTION ==============
                    print(f"\n{'='*60}")
                    print("CONNECTING TO MCP SERVER")
                    print(f"{'='*60}")

                    await session.initialize()
                    print("Connected to MCP server successfully!\n")

                    # ============== RESOURCES ==============
                    print(f"\n{'='*60}")
                    print("AVAILABLE RESOURCES")
                    print(f"{'='*60}")
                    resources = await session.list_resources()
                    for resource in resources:
                        print(f"  • {resource}")

                    # ============== RESOURCE TEMPLATES ==============
                    print(f"\n{'='*60}")
                    print("RESOURCE TEMPLATES")
                    print(f"{'='*60}")
                    resource_templates = await session.list_resource_templates()
                    for template in resource_templates:
                        print(f"  • {template}")

                    # ============== TOOLS ==============
                    print(f"\n{'='*60}")
                    print("AVAILABLE TOOLS")
                    print(f"{'='*60}")
                    tools = await session.list_tools()
                    functions = []
                    for tool in tools.tools:
                        print(f"\n  Tool: {tool.name}")
                        print(f"  Input Schema: {tool.inputSchema['properties']}")
                        functions.append(self.tool_formatter.convert_to_llm_tool(tool))

                    # ============== READ RESOURCE ==============
                    print(f"\n{'='*60}")
                    print("READING RESOURCE")
                    print(f"{'='*60}")
                    content, mime_type = await session.read_resource("greeting://hello")
                    print(f"  Content: {content}")
                    print(f"  MIME Type: {mime_type}")

                    # ============== DIRECT TOOL CALL ==============
                    print(f"\n{'='*60}")
                    print("DIRECT TOOL CALL (add 1 + 7)")
                    print(f"{'='*60}")
                    result = await session.call_tool("add", arguments={"a": 1, "b": 7})
                    print(f"  Result: {result.content}")

                    # ============== LLM-DRIVEN TOOL CALLS ==============
                    print(f"\n{'='*60}")
                    print("LLM-DRIVEN TOOL SELECTION")
                    print(f"{'='*60}")
                    prompt = "Add 2 to 20"
                    print(f"  Prompt: '{prompt}'")
                    functions_to_call = self.choose_mcp_tools(prompt, functions)

                    print(f"\n  Calling suggested tools:")
                    for f in functions_to_call:
                        result = await session.call_tool(f["name"], arguments=f["args"])
                        print(f"    → {f['name']}({f['args']}) = {result.content}")

                    # ============== COMPLETION ==============
                    print(f"\n{'='*60}")
                    print("CLIENT OPERATIONS COMPLETED SUCCESSFULLY!")
                    print(f"{'='*60}\n")

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