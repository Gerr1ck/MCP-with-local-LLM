"""
Calculator Client for MCP
This script demonstrates the calculator use case with the MCP client.
It connects to a calculation server and performs various operations.
"""
import asyncio
import os
import sys
from mcp.client.stdio import stdio_client
from mcp import ClientSession

# Add the parent directory to sys.path so we can import from cli package
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from mcp_client import MCPClient


class CalculatorClient(MCPClient):
    """
    Specialized MCP Client for the calculator use case.
    Implements specific workflows for calculator operations.
    """
    
    async def run(self):
        """
        Run the calculator client workflow.
        This includes demonstrating all calculator operations.
        """
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
                    resources = await self.list_resources(session)
                    for resource in resources:
                        print(f"  • {resource}")

                    # ============== RESOURCE TEMPLATES ==============
                    print(f"\n{'='*60}")
                    print("RESOURCE TEMPLATES")
                    print(f"{'='*60}")
                    resource_templates = await self.list_resource_templates(session)
                    for template in resource_templates:
                        print(f"  • {template}")

                    # ============== TOOLS ==============
                    print(f"\n{'='*60}")
                    print("AVAILABLE TOOLS")
                    print(f"{'='*60}")
                    functions, tools = await self.list_tools(session)
                    for tool in tools.tools:
                        print(f"\n  Tool: {tool.name}")
                        print(f"  Input Schema: {tool.inputSchema['properties']}")

                    # ============== READ RESOURCE ==============
                    print(f"\n{'='*60}")
                    print("READING RESOURCE")
                    print(f"{'='*60}")
                    content, mime_type = await self.read_resource(session, "greeting://hello")
                    print(f"  Content: {content}")
                    print(f"  MIME Type: {mime_type}")

                    # ============== DIRECT TOOL CALL ==============
                    print(f"\n{'='*60}")
                    print("DIRECT TOOL CALL (add 1 + 7)")
                    print(f"{'='*60}")
                    result = await self.call_tool(session, "add", {"a": 1, "b": 7})
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
                        result = await self.call_tool(session, f["name"], f["args"])
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
    """Run the calculator client."""
    # Get the path to the calculator server
    server_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server', 'calc_server.py'))
    
    # Initialize the calculator client with the server script
    client = CalculatorClient(server_script)
    
    # Run the calculator workflow
    await client.run()


if __name__ == "__main__":
    asyncio.run(main())