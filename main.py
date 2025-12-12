from mcp.server.fastmcp import FastMCP
from starlette.middleware.trustedhost import TrustedHostMiddleware
import os
import uvicorn

# Initialize FastMCP with JSON response enabled
mcp = FastMCP("Koyeb OpenAI Apps SDK Demo", json_response=True)

# Read the HTML widget file
with open("public/widget.html", "r") as f:
    widget_html = f.read()

# Register the UI widget as a resource
@mcp.resource("ui://widget/demo.html")
def get_widget() -> str:
    return widget_html

# Define a tool that generates a greeting message
@mcp.tool()
def greet_user(name: str, style="friendly") -> str:
    """Generate a greeting for a user in different styles.
    
    Args:
        name: The person's name
        style: The style of greeting (friendly, formal, or casual)
    """
    styles = {
        "friendly": f"Hello, {name}! It's wonderful to meet you!",
        "formal": f"Good day, {name}. It is a pleasure to make your acquaintance.",
        "casual": f"Hey {name}! What's up?",
    }
    return styles.get(style, styles['friendly'])

# Define a tool that counts occurrences of a letter in a given text
@mcp.tool()
def count_letter(text: str, letter: str) -> int:
    """Count how many times a specific letter appears in text.
    
    Args:
        text: The text to search in
        letter: The letter to count (case-insensitive)
    """
    return text.lower().count(letter.lower())

# Create the FastMCP app
app = mcp.streamable_http_app()

port = int(os.environ.get("PORT", 8000))
print(f"Listening on port {port}")

uvicorn.run(
    app, 
    host="0.0.0.0", 
    port=port,
    proxy_headers=True,
    forwarded_allow_ips="*",
    server_header=False,
    date_header=False
)
