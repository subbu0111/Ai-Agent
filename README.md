# AI Agent Bot connect via Telegram 

## Setup
1. Copy `.env.example` to `.env` and fill in:
   - `TELEGRAM_TOKEN`: Your bot token from @BotFather
   - `OPENROUTER_API_KEY`: Your OpenRouter API key
   - `MODEL`: e.g., `x-ai/grok-4.1-fast`

2. Install deps: `pip install -r requirements.txt`

3. Run: `python bot.py`

## Features
- Stateful conversations per user
- Powered by Grok via OpenRouter
- Handles text messages, /start command
- In-memory history (add Redis for persistence/prod)

## Customization
- Edit system prompt in `bot.py`
- Add tools/function calling via OpenAI client
- Deploy to VPS/Heroku for 24/7

Bot ready! Message your bot on Telegram to test.

## GitHub and Railway deployment
1. Initialize git locally and commit the project.
2. Create a GitHub repository and push this folder to it.
3. On Railway, create a new project and connect the GitHub repository.
4. Configure the Railway service as a worker process using `python bot.py`.
5. Add the required environment variables in Railway: `TELEGRAM_TOKEN`, `OPENROUTER_API_KEY`, and `MODEL`.

## Notes
- Keep `.env` local and do not commit it.
- The `Procfile` and `runtime.txt` were added for Railway-style deployment.
