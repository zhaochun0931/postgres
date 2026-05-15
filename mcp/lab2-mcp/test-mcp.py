import asyncio
import json
import ollama
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# --- CONFIGURATION ---
MODEL = "llama3.1" 
DB_URL = "postgresql://user:password@localhost:5432/dev_db"
MCP_PATH = "/opt/homebrew/bin/mcp-server-postgres"

async def main():
    # Setup the connection parameters to launch the MCP server as a subprocess
    server_params = StdioServerParameters(command=MCP_PATH, args=[DB_URL])

    print("🔌 Booting up local MCP Server...")
    
    # Open the standard input/output bridge to the MCP server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the MCP connection
            await session.initialize()
            
            print("✅ MCP Bridge Connected!")
            print(f"🧠 AI Model ({MODEL}) is ready to analyze your data.")
            print("💡 Type 'exit' or 'quit' to close the session.\n")
            
            # --- THE "ANALYST" SYSTEM PROMPT ---
            chat_history = [
                {
                    'role': 'system', 
                    'content': (
                        "You are an expert PostgreSQL Data Analyst. "
                        "You are connected to a database via an MCP server. "
                        "When the user asks a question about their data, you MUST use the 'query' tool to fetch the answer. "
                        "Never use placeholder text like 'your_database_name' in your SQL. "
                        "Always assume the 'public' schema."
                    )
                }
            ]
            
            # Fetch the available tools dynamically from the MCP server (just 'query' for Postgres)
            tools = [{
                'type': 'function',
                'function': {
                    'name': 'query',
                    'description': 'Execute a read-only SQL SELECT query against the database.',
                    'parameters': {
                        'type': 'object',
                        'properties': {'sql': {'type': 'string'}},
                        'required': ['sql']
                    }
                }
            }]

            # --- THE INTERACTIVE LOOP ---
            while True:
                try:
                    user_input = input("👤 You: ")
                    
                    if user_input.lower() in ['exit', 'quit']:
                        print("👋 Ending session. Goodbye!")
                        break
                        
                    if not user_input.strip():
                        continue

                    chat_history.append({'role': 'user', 'content': user_input})

                    # Step 1: Ask Ollama what to do
                    response = ollama.chat(
                        model=MODEL,
                        messages=chat_history,
                        tools=tools
                    )

                    # --- ROBUST PARSING (Markdown-Proof) ---
                    sql_to_run = None
                    ai_message = response.message.content
                    
                    if response.message.tool_calls:
                        sql_to_run = response.message.tool_calls[0].function.arguments.get('sql')
                    elif ai_message:
                        clean_text = ai_message.strip()
                        
                        # Clean markdown formatting safely using standard indentation
                        if clean_text.startswith("```json"):
                            clean_text = clean_text[7:]
                        elif clean_text.startswith("```"):
                            clean_text = clean_text[3:]
                            
                        if clean_text.endswith("```"):
                            clean_text = clean_text[:-3]
                            
                        clean_text = clean_text.strip()
                        
                        try:
                            parsed = json.loads(clean_text)
                            if 'arguments' in parsed and 'sql' in parsed['arguments']:
                                sql_to_run = parsed['arguments']['sql']
                            elif 'parameters' in parsed and 'sql' in parsed['parameters']:
                                sql_to_run = parsed['parameters']['sql']
                            elif 'sql' in parsed: 
                                sql_to_run = parsed['sql']
                        except json.JSONDecodeError:
                            pass 

                    # --- MCP TOOL EXECUTION ---
                    if sql_to_run:
                        # Clean up the SQL string before sending
                        sql_to_run = sql_to_run.strip().rstrip(';').strip().rstrip('.')
                        print(f"⚙️  MCP Executing SQL: {sql_to_run}")
                        
                        try:
                            # Send the tool call to the MCP server
                            result = await session.call_tool("query", {"sql": sql_to_run})
                            data = result.content[0].text
                            print(f"📊 MCP Returned Data: {data}")
                            
                            # Feed the data back to the AI quietly
                            chat_history.append({
                                'role': 'system', 
                                'content': f"BACKGROUND EVENT - SQL EXECUTED: {sql_to_run}\nDATABASE RESULT: {data}\nSummarize this data for the user."
                            })
                            
                            # Step 2: Get the final conversational answer
                            final_response = ollama.chat(
                                model=MODEL,
                                messages=chat_history
                            )
                            
                            print(f"🤖 AI: {final_response.message.content}\n")
                            chat_history.append({'role': 'assistant', 'content': final_response.message.content})
                            
                        except Exception as e:
                            print(f"❌ MCP Server Error: {e}\n")
                            chat_history.append({
                                'role': 'system', 
                                'content': f"BACKGROUND EVENT - SQL FAILED: {sql_to_run}\nERROR: {e}\nExplain this error to the user."
                            })
                            
                            # Let the AI explain the failure
                            error_response = ollama.chat(model=MODEL, messages=chat_history)
                            print(f"🤖 AI: {error_response.message.content}\n")
                            chat_history.append({'role': 'assistant', 'content': error_response.message.content})
                    else:
                        # If the AI just wants to chat normally without running SQL
                        print(f"🤖 AI: {ai_message}\n")
                        chat_history.append({'role': 'assistant', 'content': ai_message})

                except KeyboardInterrupt:
                    print("\n👋 Session interrupted. Goodbye!")
                    break
                except Exception as e:
                    print(f"\n❌ System Error: {e}")

if __name__ == "__main__":
    # Run the async loop
    asyncio.run(main())
