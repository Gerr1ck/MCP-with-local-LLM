from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client
import asyncio
import os
import sys

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'cli')))

# llm
from call_llm import LLMClient


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

    def convert_to_llm_tool(self, tool):
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

    def choose_mcp_tools(self, prompt, functions):
        
        response = self.llm_client.choose_mcp_tools(prompt, functions)
        print("LLM response: ", response)
        functions_to_call = []

        if response:
            for tool_call in response:
                print("TOOL: ", tool_call)
                # Access the new simplified format: {"function": "name", "arguments": {...}}
                name = tool_call.get("function", "")
                args = tool_call.get("arguments", {})
                
                if name:  # Only add if we have a valid tool name
                    functions_to_call.append({ "name": name, "args": args })

        return functions_to_call

    async def run(self):
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    print("📡 Connecting to MCP server...")

                    await session.initialize()

                    print("✅ Connected to MCP server successfully!")

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
                        functions.append(self.convert_to_llm_tool(tool))

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

                    print("\n✨ Client operations completed successfully!")

        except Exception as e:
            import traceback

            print(f"❌ Error running MCP client: {e}")
            traceback.print_exc()
            raise


async def main():
    client = MCPClient()
    await client.run()


if __name__ == "__main__":
    asyncio.run(main())
