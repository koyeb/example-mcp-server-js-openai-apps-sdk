from mcp.server.fastmcp import FastMCP
import mcp.types as types
import os
import uvicorn
from pydantic import BaseModel, Field, ValidationError, AnyUrl
from typing import Any, Dict, List

# Initialize FastMCP with stateless HTTP
mcp = FastMCP(name="koyeb-todo", stateless_http=True)

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

class TodoInput(BaseModel):
    title: str = Field(..., description="The title of the todo item")

class CompleteTodoInput(BaseModel):
    todo_id: str = Field(..., alias="todoId", description="The ID of the todo to complete")

def tool_meta():
    return {
        "openai/outputTemplate": TEMPLATE_URI,
        "openai/toolInvocation/invoking": "Managing todos",
        "openai/toolInvocation/invoked": "Todo updated",
        "openai/widgetAccessible": True,
        "openai/resultCanProduceWidget": True,
    }

# Register tools
@mcp._mcp_server.list_tools()
async def _list_tools() -> List[types.Tool]:
    return [
        types.Tool(
            name="add_todo",
            title="Add Todo",
            description="Creates a todo item with the given title",
            inputSchema={
                "type": "object",
                "properties": {
                    "title": {
                        "type": "string",
                        "description": "The title of the todo item",
                    }
                },
                "required": ["title"],
            },
            _meta=tool_meta(),
        ),
        types.Tool(
            name="complete_todo",
            title="Complete Todo",
            description="Marks a todo as done by id",
            inputSchema={
                "type": "object",
                "properties": {
                    "todoId": {
                        "type": "string",
                        "description": "The ID of the todo to complete",
                    }
                },
                "required": ["todoId"],
            },
            _meta=tool_meta(),
        ),
    ]

# Register resources
@mcp._mcp_server.list_resources()
async def _list_resources() -> List[types.Resource]:
    return [
        types.Resource(
            name="Todo Widget",
            title="Todo Widget",
            uri=AnyUrl(TEMPLATE_URI),
            description="Todo widget markup",
            mimeType=MIME_TYPE,
            _meta=tool_meta(),
        )
    ]

# Handle resource reading
async def _handle_read_resource(req: types.ReadResourceRequest) -> types.ServerResult:
    if str(req.params.uri) != TEMPLATE_URI:
        return types.ServerResult(
            types.ReadResourceResult(
                contents=[],
                _meta={"error": f"Unknown resource: {req.params.uri}"},
            )
        )

    contents = [
        types.TextResourceContents(
            uri=AnyUrl(TEMPLATE_URI),
            mimeType=MIME_TYPE,
            text=todo_html,
            _meta=tool_meta(),
        )
    ]

    return types.ServerResult(types.ReadResourceResult(contents=contents))

# Handle tool calls
async def _call_tool_request(req: types.CallToolRequest) -> types.ServerResult:
    global next_id
    
    tool_name = req.params.name
    arguments = req.params.arguments or {}
    
    if tool_name == "add_todo":
        try:
            title = arguments.get("title", "").strip()
            if not title:
                payload = TodoPayload(tasks=todos, message="Missing title.")
                return types.ServerResult(
                    types.CallToolResult(
                        content=[types.TextContent(type="text", text="Missing title.")],
                        structuredContent=payload.model_dump(mode="json"),
                        _meta=tool_meta(),
                        isError=True,
                    )
                )
            
            todo = {"id": f"todo-{next_id}", "title": title, "completed": False}
            next_id += 1
            todos.append(todo)
            
            message = f'Added "{todo["title"]}".'
            payload = TodoPayload(tasks=todos, message=message)
            return types.ServerResult(
                types.CallToolResult(
                    content=[types.TextContent(type="text", text=message)],
                    structuredContent=payload.model_dump(mode="json"),
                    _meta=tool_meta(),
                    isError=False,
                )
            )
        except Exception as e:
            return types.ServerResult(
                types.CallToolResult(
                    content=[types.TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True,
                )
            )
    
    elif tool_name == "complete_todo":
        try:
            todo_id = arguments.get("todoId", "")
            if not todo_id:
                payload = TodoPayload(tasks=todos, message="Missing todo id.")
                return types.ServerResult(
                    types.CallToolResult(
                        content=[types.TextContent(type="text", text="Missing todo id.")],
                        structuredContent=payload.model_dump(mode="json"),
                        _meta=tool_meta(),
                        isError=True,
                    )
                )
            
            todo = next((task for task in todos if task["id"] == todo_id), None)
            if not todo:
                payload = TodoPayload(tasks=todos, message=f"Todo {todo_id} was not found.")
                return types.ServerResult(
                    types.CallToolResult(
                        content=[types.TextContent(type="text", text=f"Todo {todo_id} was not found.")],
                        structuredContent=payload.model_dump(mode="json"),
                        _meta=tool_meta(),
                        isError=True,
                    )
                )
            
            for task in todos:
                if task["id"] == todo_id:
                    task["completed"] = True
            
            message = f'Completed "{todo["title"]}".'
            payload = TodoPayload(tasks=todos, message=message)
            return types.ServerResult(
                types.CallToolResult(
                    content=[types.TextContent(type="text", text=message)],
                    structuredContent=payload.model_dump(mode="json"),
                    _meta=tool_meta(),
                    isError=False,
                )
            )
        except Exception as e:
            return types.ServerResult(
                types.CallToolResult(
                    content=[types.TextContent(type="text", text=f"Error: {str(e)}")],
                    isError=True,
                )
            )
    
    else:
        return types.ServerResult(
            types.CallToolResult(
                content=[types.TextContent(type="text", text=f"Unknown tool: {tool_name}")],
                isError=True,
            )
        )

# Register custom handlers
mcp._mcp_server.request_handlers[types.CallToolRequest] = _call_tool_request
mcp._mcp_server.request_handlers[types.ReadResourceRequest] = _handle_read_resource

# Create the FastMCP app
app = mcp.streamable_http_app()

# Add CORS middleware
try:
    from starlette.middleware.cors import CORSMiddleware

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False,
    )
except Exception:
    pass

port = int(os.environ.get("PORT", 8080))

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=port)
