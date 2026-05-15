import os
import asyncio
import json
import ollama
from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters

# --- CONFIGURATION ---
MODEL = "llama3.1"
DB_URL = "postgresql://user:password@localhost:5432/dev_db"

# Point the MCP client to run your custom python server!
CUSTOM_SERVER_PATH = os.path.abspath("my-mcp-server.py")

async def main():
    # Setup the connection parameters to launch our custom MCP server as a subprocess
    server_params = StdioServerParameters(command="python3", args=[CUSTOM_SERVER_PATH])

    print("🔌 Booting up Custom MCP Server in GOD MODE...")

    # Open the standard input/output bridge to the MCP server
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # Initialize the MCP connection
            await session.initialize()

            print("✅ MCP Bridge Connected!")
            print(f"🧠 AI Model ({MODEL}) is ready to modify your database.")
            print("💡 Type 'exit' or 'quit' to close the session.\n")

            # --- THE "ADMIN" SYSTEM PROMPT ---
            chat_history = [
                {
                    'role': 'system',
                    'content': (
                        "You are an expert PostgreSQL Database Administrator. "
                        "You are connected to a database via a custom MCP server. "
                        "You have FULL WRITE ACCESS. You are permitted to CREATE, INSERT, UPDATE, and DROP tables. "
                        "When the user asks you to alter the database, you MUST use the 'query' tool to execute the SQL immediately. "
                        "CRITICAL RULES:\n"
                        "1. When creating tables, always use 'DROP TABLE IF EXISTS table_name;' first or use 'CREATE TABLE IF NOT EXISTS' to avoid conflicts.\n"
                        "2. If asked to do multiple things (e.g., create a table, insert data, AND fetch it), combine ALL SQL statements into a SINGLE string separated by semicolons (;) and run them in ONE tool call.\n"
                        "3. Never use placeholder text like 'your_database_name'. Always assume the 'public' schema."
                    )
                }
            ]

            # Tell the AI about the tool and explicitly state it has full access
            tools = [{
                'type': 'function',
                'function': {
                    'name': 'query',
                    'description': 'Execute ANY SQL command against the database (CREATE, INSERT, UPDATE, DROP, SELECT, etc.)',
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

                    # --- ROBUST PARSING (Chatty-AI Proof) ---
                    sql_to_run = None
                    ai_message = response.message.content

                    if response.message.tool_calls:
                        # Scenario A: AI correctly used the strict tool-calling API
                        sql_to_run = response.message.tool_calls[0].function.arguments.get('sql')
                        
                    elif ai_message:
                        # Scenario B: AI printed raw JSON mixed with conversational text
                        # Extract JSON block by finding the first '{' and last '}'
                        start_idx = ai_message.find('{')
                        end_idx = ai_message.rfind('}')
                        
                        if start_idx != -1 and end_idx != -1 and end_idx > start_idx:
                            json_str = ai_message[start_idx:end_idx+1]
                            try:
                                parsed = json.loads(json_str)
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
                                'content': f"BACKGROUND EVENT - SQL EXECUTED: {sql_to_run}\nDATABASE RESULT: {data}\nSummarize this outcome for the user."
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
