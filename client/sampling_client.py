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


class SamplingClient(MCPClient):
    """
    Specialized MCP Client for the sampling use case.
    Implements specific workflows for sampling operations.
    """
    
    async def run(self):
        """
        Run the sampling client workflow.
        This includes demonstrating LLM sampling capabilities.
        """
        try:
            async with stdio_client(self.server_params) as (read, write):
                async with ClientSession(read, write) as session:
                    # ============== SERVER CONNECTION ==============
                    print(f"\n{'='*60}")
                    print("CONNECTING TO MCP SERVER")
                    print(f"{'='*60}")

                    # Initialize with sampling capability enabled
                    await self.initialize_session(session, enable_sampling=True)
                    print("Connected to MCP server successfully!\n")

                    # ============== DIRECT TOOL CALL (useSampling) ==============
                    print(f"\n{'='*60}")
                    print("DIRECT TOOL CALL (useSampling)")
                    print(f"{'='*60}")
                    result = await self.call_tool(session, "useSampling", {})
                    print(f"  Result: {result.content}")

        except Exception as e:
            import traceback

            print(f"Error running MCP client: {e}")
            traceback.print_exc()
            raise


async def main():
    """Run the sampling client."""
    # Get the path to the sampling server
    server_script = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'server', 'sampling_server.py'))

    # Initialize the sampling client with the server script
    client = SamplingClient(server_script)
    
    # Run the calculator workflow
    await client.run()


if __name__ == "__main__":
    asyncio.run(main())