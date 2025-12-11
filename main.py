from mcp.server.fastmcp import FastMCP
import os
import uvicorn

mcp = FastMCP("Koyeb OpenAI Apps SDK Demo", json_response=True)

# Define a prompt that generates a greeting message
@mcp.prompt()
def greet_user(name: str, style="friendly") -> str:
    styles = {
        "friendly": "Please write a warm, friendly greeting",
        "formal": "Please write a formal, professional greeting",
        "casual": "Please write a casual, relaxed greeting",
    }
    return f"{styles.get(style, styles['friendly'])} for someone named {name}."

# Define a tool that counts occurrences of a letter in a given text
@mcp.tool()
def count_letter(text: str, letter: str) -> int:
    return text.lower().count(letter.lower())

# Create the FastMCP app
app = mcp.streamable_http_app()

port = int(os.environ.get("PORT", 8080))
print(f"Listening on port {port}")

uvicorn.run(app, host="0.0.0.0", port=port)
