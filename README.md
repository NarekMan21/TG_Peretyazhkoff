# Telegram Bot for Furniture Reupholstery Leads

Telegram bot + lightweight admin panel for collecting, reviewing, and managing furniture reupholstery requests.

This is a real business automation project for a furniture reupholstery workflow: lead collection, photo intake, manager notifications, request storage, and admin review.

## Problem

Furniture reupholstery requests usually arrive through messy channels: calls, messages, photos, addresses, comments, and incomplete customer details.

Without a structured intake flow, managers spend extra time asking the same questions, collecting photos, finding phone numbers, and transferring requests into a working process.

## Solution

This bot guides a customer through a structured Telegram flow, collects the required data, saves the request, and forwards it to a manager chat. A lightweight admin panel allows the team to review requests and basic stats.

## Main flow

```text
Customer opens Telegram bot
   ↓
Selects furniture type
   ↓
Uploads 1–10 photos
   ↓
Shares district / location
   ↓
Shares phone number
   ↓
Request is saved in SQLite
   ↓
Manager receives structured lead in Telegram
   ↓
Admin panel can review requests and stats
```

## What it does

- Collects lead data through a guided Telegram flow
- Supports 1–10 furniture photos per request
- Normalizes phone numbers before saving
- Sends completed requests to a manager chat in Telegram
- Stores requests in SQLite
- Provides a web admin panel for browsing requests and stats
- Can publish content/case posts to a Telegram channel

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

## Security notes

- Do **not** commit real bot tokens or private chat IDs
- Keep secrets only in `.env` or deployment platform secrets
- If a token was ever exposed publicly, revoke it in BotFather and issue a new one
- Use anonymized screenshots for portfolio/demo purposes

## Why this project matters

This project demonstrates practical automation for a real service business.

It shows:

- structured lead collection
- customer-facing Telegram automation
- manager notifications
- request storage
- admin panel thinking
- business workflow understanding

## Next improvements

- [ ] Add screenshots of bot flow
- [ ] Add admin panel screenshots
- [ ] Add anonymized example request
- [ ] Add deployment instructions
- [ ] Add simple analytics section
- [ ] Add request status workflow
- [ ] Add CRM/export integration notes

## Screenshots

Add screenshots in `docs/images/` and embed them like this:

```md
![Bot flow](docs/images/bot-flow.png)
![Admin panel](docs/images/admin-panel.png)
```

## Target portfolio roles

This project supports positioning for:

- AI Automation Engineer
- Internal Tools Developer
- Business Automation Consultant
- Technical Product Engineer
- Telegram / workflow automation developer
