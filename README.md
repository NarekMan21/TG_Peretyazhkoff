# Telegram bot for furniture reupholstery leads

Telegram bot + lightweight admin panel for collecting, reviewing, and managing furniture reupholstery requests.

## What it does
- Collects lead data through a guided Telegram flow
- Supports 1–10 furniture photos per request
- Normalizes phone numbers before saving
- Sends completed requests to a manager chat in Telegram
- Stores requests in SQLite
- Provides a web admin panel for browsing requests and stats
- Can publish content/case posts to a Telegram channel

## Main flow
1. User starts the bot
2. Selects furniture type
3. Uploads photos
4. Shares district / location
5. Shares phone number
6. Request is stored and forwarded to the manager

## Stack
- Python
- aiogram
- SQLite
- Telegram Bot API
- Web admin panel

## Setup
Create a `.env` file in the bot directory:

```env
BOT_TOKEN=your_bot_token
MANAGER_CHAT_ID=your_manager_chat_id
CHANNEL_ID=@your_channel_username
ADMIN_PORT=5000
DB_PATH=bot.db
```

## Run locally
```bash
pip install -r requirements.txt
python main.py
```

## Notes
- Do **not** commit real bot tokens or private chat IDs
- Keep secrets only in `.env` or your deployment platform secrets
- If a token was ever exposed publicly, revoke it in BotFather and issue a new one

## Screenshots
Add 1-3 screenshots in `docs/images/` and embed them like this:

```md
![Overview](docs/images/overview.png)
![Dashboard](docs/images/dashboard.png)
```

