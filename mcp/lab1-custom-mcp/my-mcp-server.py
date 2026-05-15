import asyncio
import json
import psycopg2
from psycopg2.extras import RealDictCursor
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import Tool, TextContent

# --- SERVER CONFIGURATION ---
DB_URL = "postgresql://user:password@localhost:5432/dev_db"

# Initialize our custom MCP Server
app = Server("postgres-god-mode-server")

@app.list_tools()
async def list_tools() -> list[Tool]:
    """Tells the MCP Client what tools this server has available."""
    return [
        Tool(
            name="query",
            description="Execute ANY SQL command on the database, including CREATE, INSERT, DROP, and SELECT.",
            inputSchema={
                "type": "object",
                "properties": {
                    "sql": {"type": "string"}
                },
                "required": ["sql"]
            }
        )
    ]

@app.call_tool()
async def call_tool(name: str, arguments: dict) -> list[TextContent]:
    """Handles the execution when the client uses the tool."""
    if name != "query":
        raise ValueError(f"Unknown tool: {name}")
        
    sql = arguments.get("sql")
    
    try:
        # Connect to Postgres with Autocommit ON (This enables WRITE/CREATE)
        conn = psycopg2.connect(DB_URL)
        conn.autocommit = True 
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        cursor.execute(sql)
        
        # If it's a SELECT query, grab the data
        if cursor.description:
            rows = cursor.fetchall()
            result = json.dumps(rows, default=str)
        else:
            # If it's a CREATE/INSERT, report success
            result = "Command executed successfully (no data returned)."
            
        cursor.close()
        conn.close()
        
        # Return the data back through the MCP protocol
        return [TextContent(type="text", text=result)]
        
    except Exception as e:
        return [TextContent(type="text", text=f"Database Error: {str(e)}")]

async def main():
    # Run the server using standard input/output (this is how MCP bridges communicate)
    async with stdio_server() as (read_stream, write_stream):
        await app.run(read_stream, write_stream, app.create_initialization_options())

if __name__ == "__main__":
    asyncio.run(main())
