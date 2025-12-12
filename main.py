from mcp.server.fastmcp import FastMCP
from mcp.types import TextContent, Tool
import os
import uvicorn

# Initialize FastMCP with JSON response enabled
mcp = FastMCP("Koyeb OpenAI Apps SDK Demo", json_response=True)

# Read the HTML widget file
with open("public/todo-widget.html", "r") as f:
    todo_html = f.read()

# In-memory todo storage
todos = []
next_id = 1

# Register the UI widget as a resource
@mcp.resource("ui://widget/todo.html")
def get_todo_widget() -> str:
    return todo_html

# Define a tool to add a todo
@mcp.tool()
def add_todo(title: str) -> str:
    """Creates a todo item with the given title.
    
    Args:
        title: The title of the todo item
    """
    global next_id
    
    title = title.strip()
    if not title:
        return "Missing title."
    
    todo = {"id": f"todo-{next_id}", "title": title, "completed": False}
    next_id += 1
    todos.append(todo)
    
    return f'Added "{todo["title"]}".'

# Define a tool to complete a todo
@mcp.tool()
def complete_todo(id: str) -> str:
    """Marks a todo as done by id.
    
    Args:
        id: The ID of the todo to complete
    """
    if not id:
        return "Missing todo id."
    
    todo = next((task for task in todos if task["id"] == id), None)
    if not todo:
        return f"Todo {id} was not found."
    
    for task in todos:
        if task["id"] == id:
            task["completed"] = True
    
    return f'Completed "{todo["title]}".'

# Create the FastMCP app
app = mcp.streamable_http_app()

port = int(os.environ.get("PORT", 8080))
print(f"Listening on port {port}")

uvicorn.run(app, host="0.0.0.0", port=port)
