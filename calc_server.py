from mcp.server.session import ServerSession
from mcp.server.fastmcp import FastMCP

#Create an MCP Server
mcp = FastMCP("Calculator Demo")

# Add an addition tool
@mcp.tool()
def add(a: int, b: int) -> int:
    """ Add two numbers """
    return a + b

# Add a subtraction tool
@mcp.tool()
def subtract(a: int, b: int) -> int:
    """ Subtract two numbers """
    return a - b

# Add a multiplication tool
@mcp.tool()
def multiply(a: int, b: int) -> int:
    """ Multiply two numbers """
    return a * b

# Add a division tool
@mcp.tool()
def divide(a: int, b: int) -> float:
    """ Divide two numbers """
    if b == 0:
        return float("inf")  # Handle division by zero
    return a / b

# Add a dynamic greeting resource
@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    """ Greet a person by name """
    return f"Hello, {name}!"

if __name__ == "__main__":
    # Run the server
    mcp.run()
