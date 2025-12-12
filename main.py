from mcp.server.fastmcp import FastMCP
import mcp.types as types
import os
import uvicorn
from pydantic import BaseModel, Field

# Initialize FastMCP with stateless HTTP mode
mcp = FastMCP("Koyeb OpenAI Apps SDK Demo", stateless_http=True)

# Read the HTML widget file
with open("public/todo-widget.html", "r") as f:
    todo_html = f.read()

TEMPLATE_URI = "ui://widget/todo.html"
MIME_TYPE = "text/html+skybridge"

# In-memory todo storage
todos = []
next_id = 1

class TodoPayload(BaseModel):
    tasks: list = Field(default_factory=list)
    message: str = Field(default="")

# Register the UI widget as a resource
@mcp.resource(TEMPLATE_URI, "Todo widget", mime_type=MIME_TYPE)
def get_todo_widget() -> str:
    return todo_html

def tool_meta(tool_name: str):
    return {
        "openai/outputTemplate": TEMPLATE_URI,
        "openai/toolInvocation/invoking": f"Running {tool_name}",
        "openai/toolInvocation/invoked": f"{tool_name} completed",
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    }

# Define a tool to add a todo
@mcp.tool()
def add_todo(title: str = Field(..., description="The title of the todo item")) -> types.CallToolResult:
    """Creates a todo item with the given title."""
    global next_id
    
    title = title.strip()
    if not title:
        payload = TodoPayload(tasks=todos, message="Missing title.")
        return types.CallToolResult(
            content=[types.TextContent(type="text", text="Missing title.")],
            structuredContent=payload.model_dump(mode="json"),
            _meta=tool_meta("add_todo"),
            isError=True,
        )
    
    todo = {"id": f"todo-{next_id}", "title": title, "completed": False}
    next_id += 1
    todos.append(todo)
    
    payload = TodoPayload(tasks=todos, message=f'Added "{todo["title"]}".')
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=f'Added "{todo["title]}".')],
        structuredContent=payload.model_dump(mode="json"),
        _meta=tool_meta("add_todo"),
        isError=False,
    )

# Define a tool to complete a todo  
@mcp.tool()
def complete_todo(todo_id: str = Field(..., description="The ID of the todo to complete")) -> types.CallToolResult:
    """Marks a todo as done by id."""
    
    if not todo_id:
        payload = TodoPayload(tasks=todos, message="Missing todo id.")
        return types.CallToolResult(
            content=[types.TextContent(type="text", text="Missing todo id.")],
            structuredContent=payload.model_dump(mode="json"),
            _meta=tool_meta("complete_todo"),
            isError=True,
        )
    
    todo = next((task for task in todos if task["id"] == todo_id), None)
    if not todo:
        payload = TodoPayload(tasks=todos, message=f"Todo {todo_id} was not found.")
        return types.CallToolResult(
            content=[types.TextContent(type="text", text=f"Todo {todo_id} was not found.")],
            structuredContent=payload.model_dump(mode="json"),
            _meta=tool_meta("complete_todo"),
            isError=True,
        )
    
    for task in todos:
        if task["id"] == todo_id:
            task["completed"] = True
    
    payload = TodoPayload(tasks=todos, message=f'Completed "{todo["title"]}".')
    return types.CallToolResult(
        content=[types.TextContent(type="text", text=f'Completed "{todo["title"]}".')],
        structuredContent=payload.model_dump(mode="json"),
        _meta=tool_meta("complete_todo"),
        isError=False,
    )

# Create the FastMCP app
app = mcp.fastapi

port = int(os.environ.get("PORT", 8080))
print(f"Listening on port {port}")

uvicorn.run(app, host="0.0.0.0", port=port)
