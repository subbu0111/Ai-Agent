import asyncio
import logging
import os
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from openai import OpenAI
import json
import sqlite3
from duckduckgo_search import DDGS

# Load environment variables
load_dotenv()

TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
MODEL = os.getenv('MODEL', 'x-ai/grok-4.1-fast')

SYSTEM_PROMPT = """You are a highly intelligent personal AI agent powered by Grok. Think step-by-step before responding. 

CRITICAL: For ANY news, current events, weather, stocks, sports scores, facts that change over time, or real-time data, ALWAYS use web_search FIRST. Never rely on your training data or guess dates/prices/events. Summarize top recent results concisely.

Use tools when needed for current information (web_search) or calculations (calculator). Be helpful, concise, accurate, and proactive."""

if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
    raise ValueError("Missing TELEGRAM_TOKEN or OPENROUTER_API_KEY in .env")

# OpenRouter OpenAI-compatible client
client = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=OPENROUTER_API_KEY,
)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_db():
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS histories
                 (user_id TEXT PRIMARY KEY, history TEXT)''')
    conn.commit()
    conn.close()

def get_history(user_id):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("SELECT history FROM histories WHERE user_id=?", (user_id,))
    row = c.fetchone()
    conn.close()
    if row:
        return json.loads(row[0])
    return [{"role": "system", "content": SYSTEM_PROMPT}]

def save_history(user_id, history):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("INSERT OR REPLACE INTO histories (user_id, history) VALUES (?, ?)", 
              (user_id, json.dumps(history)))
    conn.commit()
    conn.close()

def clear_history(user_id):
    conn = sqlite3.connect('chat_history.db')
    c = conn.cursor()
    c.execute("DELETE FROM histories WHERE user_id=?", (user_id,))
    conn.commit()
    conn.close()

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text('Hi! Super intelligent AI agent powered by Grok here! Chat away. Use /clear to reset history. I can web search and calculate math!')

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    history = get_history(user_id)
    history.append({"role": "user", "content": update.message.text})
    if len(history) > 50:
        history = history[-40:]

    tools = [
        {
            "type": "function",
            "function": {
                "name": "web_search",
                "description": "Get the LATEST web search results (prioritizes recent news/content). ALWAYS use for news, current events, weather, stocks, sports, real-time facts. Input specific query.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "query": {
                            "type": "string",
                            "description": "Search query"
                        }
                    },
                    "required": ["query"]
                }
            }
        },
        {
            "type": "function",
            "function": {
                "name": "calculator",
                "description": "Evaluate mathematical expressions. Supports +, -, *, /, **, %, parentheses.",
                "parameters": {
                    "type": "object",
                    "properties": {
                        "expression": {
                            "type": "string",
                            "description": "Math expression like '2+3*4' or '16**0.5'"
                        }
                    },
                    "required": ["expression"]
                }
            }
        }
    ]

    max_retries = 3

    max_retries = 3
    ai_msg = None
    temp_history = history.copy()
    for attempt in range(max_retries):
        try:
            response = client.chat.completions.create(
                model=MODEL,
                messages=temp_history,
                tools=tools,
                tool_choice="auto",
                max_tokens=1500,
                temperature=0.7,
            )
            message = response.choices[0].message
            if message.tool_calls:
                temp_history.append(message)
                for tool_call in message.tool_calls:
                    function_name = tool_call.function.name
                    function_args = json.loads(tool_call.function.arguments)
                    if function_name == "web_search":
                        ddgs = DDGS()
                        results = ddgs.text(function_args["query"], max_results=5, timeliness="d")
                        tool_response = "\n\n".join([f"• {r.get('title', '')}: {r.get('body', '')}" for r in results])
                    elif function_name == "calculator":
                        expression = function_args["expression"]
                        try:
                            result = eval(expression, {"__builtins__": {}})
                            tool_response = f"Result: {result}"
                        except Exception as calc_err:
                            tool_response = f"Calc error: {str(calc_err)}. Use simple math."
                    else:
                        tool_response = "Unknown tool"
                    tool_response_msg = {
                        "role": "tool",
                        "tool_call_id": tool_call.id,
                        "name": function_name,
                        "content": tool_response,
                    }
                    temp_history.append(tool_response_msg)
                continue  # Loop back to call model again with tool results
            else:
                ai_msg = message.content
                break
        except Exception as e:
            logger.error(f"Attempt {attempt + 1} error: {e}")
            if attempt == max_retries - 1:
                ai_msg = "Sorry, I encountered an error after several retries. Please try again."
                break

    if ai_msg:
        history.append({"role": "assistant", "content": ai_msg})
        save_history(user_id, history)
        await update.message.reply_text(ai_msg)

async def clear(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    user_id = str(update.effective_user.id)
    clear_history(user_id)
    await update.message.reply_text('Chat history cleared! Fresh start.')

def main() -> None:
    init_db()
    app = Application.builder().token(TELEGRAM_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("clear", clear))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
