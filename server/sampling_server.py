from mcp.server.fastmcp import Context, FastMCP
from mcp.server.session import ServerSession
from mcp.types import SamplingMessage, TextContent

#Create an MCP Server
mcp = FastMCP("Sampling Demo")


# Add a tool that generates a poem using LLM sampling
@mcp.tool()
async def useSampling(ctx: Context[ServerSession, None]) -> str:
    
    prompt = f"Describe three use cases where MCP Sampling can be applied on an embedded device."

    result = await ctx.session.create_message(
        messages=[
            SamplingMessage(
                role="user",
                content=TextContent(type="text", text=prompt),
            )
        ],
        max_tokens=100,
    )

    if result.content.type == "text":
        return result.content.text
    return str(result.content)

if __name__ == "__main__":
    # Run the server
    print("MCP Server is running on port 5000")
    mcp.run()
    
