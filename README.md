# FoxVPN Telegram Bot

A Telegram bot built with aiogram that provides VPN service information and management through an interactive menu.

## Features

- Welcome message with VPN service description
- Interactive menu with the following options:
  - 💎 Тарифы (Tariffs)
  - 🔑 Мои ключи (My Keys)
  - ⚙️ Мой аккаунт (My Account)
  - 📚 Инструкция (Instructions)
  - 🆘 Помощь (Help)
  - 🤝 Партнерам (For Partners)

## Setup

1. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

2. **Create environment file:**
   - Copy `env_example.txt` to `.env`
   - Add your bot token from [@BotFather](https://t.me/botfather)

3. **Run the bot:**
   ```bash
   python bot.py
   ```

## Bot Commands

- `/start` - Shows the welcome message and main menu

## Project Structure

- `bot.py` - Main bot logic and handlers
- `config.py` - Configuration and environment variables
- `requirements.txt` - Python dependencies
- `env_example.txt` - Example environment file

## Requirements

- Python 3.8+
- aiogram 3.4.1
- python-dotenv 1.0.0

## Getting a Bot Token

1. Message [@BotFather](https://t.me/botfather) on Telegram
2. Use `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token and add it to your `.env` file
