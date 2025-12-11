from mcp.server.fastmcp import FastMCP
from starlette.middleware.cors import CORSMiddleware
import os
import uvicorn

mcp = FastMCP("Demo", json_response=True)

@mcp.tool()
def add(a: int, b: int) -> int:
    return a + b

@mcp.resource("greeting://{name}")
def get_greeting(name: str) -> str:
    return f"Hello, {name}!"

@mcp.prompt()
def greet_user(name: str, style="friendly") -> str:
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }
    return f"{styles.get(style, styles['friendly'])} for someone named {name}."

# Create a basic tool that counts the number of a a specific letter in a string
@mcp.tool()
def count_letter(text: str, letter: str) -> int:
    return text.lower().count(letter.lower())

# Create ASGI app using FastMCP's streamable_http_app() method
app = mcp.streamable_http_app()

# Add CORS middleware for browser based clients
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "OPTIONS"],
    allow_headers=["*"],
    expose_headers=["mcp-session-id", "mcp-protocol-version"],
    max_age=86400,
)

# Debug: Print registered routes
print("Registered routes:")
for route in app.routes:
    print(f"  {route}")

# Start the server
port = int(os.environ.get("PORT", 8080))
print(f"Listening on port {port}")

uvicorn.run(app, host="0.0.0.0", port=port)
