# ZIBELINO Telegram Bot

Commercial Telegram bot for the ZIBELINO accessories brand. The bot introduces the brand through short visual cards, sends marketplace links, shows current promotions, links to social media, and helps users select a device to generate personalized marketplace search links.

## Technology Stack

- Python 3.12+
- aiogram 3.x
- python-dotenv
- pytest for simple unit tests

No database, Redis, webhooks, Docker, external APIs, or marketplace API integrations are used.

## Installation

```bash
cd project
python3.12 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Create `.env` from the example:

```bash
cp .env.example .env
```

Example `.env`:

```env
BOT_TOKEN=1234567890:replace_with_your_telegram_bot_token
MEDIA_DIR=media
```

Place brand card images into `media/`:

- `media/start.jpg` — brand welcome card
- `media/shops.jpg` — catalog and marketplace card
- `media/promo.jpg` — promotion card
- `media/socials.jpg` — social media card

If an image is missing, the bot sends the text and buttons without crashing.

## Run

```bash
python bot.py
```

The bot runs in polling mode only.

## Tests

```bash
pytest
```

## Project Structure

```text
project/
├── bot.py
├── config.py
├── handlers.py
├── texts.py
├── keyboards.py
├── devices.py
├── services/
│   └── marketplace.py
├── media/
│   ├── start.jpg
│   ├── shops.jpg
│   ├── promo.jpg
│   └── socials.jpg
├── tests/
│   └── test_marketplace.py
├── .env.example
├── requirements.txt
└── README.md
```

## Notes

- Device selection uses aiogram FSM states: `choosing_brand`, `choosing_model`, `device_selected`.
- Current device data is kept in FSM memory as `{"brand": "...", "model": "..."}`.
- Marketplace links are generated locally with `urllib.parse.quote_plus`.
- Unsupported user text returns the user to the main menu.
- Menu navigation keeps the chat clean: the previous bot screen is deleted after a new screen is sent.
