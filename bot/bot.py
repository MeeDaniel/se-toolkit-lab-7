#!/usr/bin/env python3
"""
Telegram bot entry point with --test mode.

Usage:
    uv run bot.py --test "/start"    # Test mode: prints response to stdout
    uv run bot.py                    # Normal mode: connects to Telegram
"""

import argparse
import logging
import sys
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent))

from handlers import (
    handle_start,
    handle_help,
    handle_health,
    handle_labs,
    handle_scores,
)
from config import load_config

# Set up logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
)
logger = logging.getLogger(__name__)


def main():
    parser = argparse.ArgumentParser(description="LMS Telegram Bot")
    parser.add_argument(
        "--test",
        type=str,
        metavar="INPUT",
        help="Test mode: pass a command like '/start' and see the response",
    )
    args = parser.parse_args()

    if args.test:
        # Test mode: call handlers directly
        command = args.test.strip()
        
        if command == "/start":
            response = handle_start()
        elif command == "/help":
            response = handle_help()
        elif command == "/health":
            response = handle_health()
        elif command == "/labs":
            response = handle_labs()
        elif command.startswith("/scores"):
            parts = command.split(maxsplit=1)
            arg = parts[1] if len(parts) > 1 else ""
            response = handle_scores(arg)
        else:
            response = f"Unknown command: {command}"
        
        print(response)
        sys.exit(0)

    # Normal mode: Telegram bot startup
    try:
        from telegram import Update
        from telegram.ext import (
            Application,
            CommandHandler,
            ContextTypes,
        )
    except ImportError:
        logger.error("python-telegram-bot not installed. Run: uv sync")
        sys.exit(1)

    config = load_config()
    
    if not config.bot_token:
        logger.error("BOT_TOKEN not set in .env.bot.secret")
        sys.exit(1)

    logger.info("Starting Telegram bot...")

    async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        response = handle_start()
        await update.message.reply_text(response)

    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        response = handle_help()
        await update.message.reply_text(response)

    async def health_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /health command."""
        response = handle_health()
        await update.message.reply_text(response)

    async def labs_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /labs command."""
        response = handle_labs()
        await update.message.reply_text(response)

    async def scores_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /scores command."""
        arg = " ".join(context.args) if context.args else ""
        response = handle_scores(arg)
        await update.message.reply_text(response)

    # Build application
    application = Application.builder().token(config.bot_token).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("health", health_command))
    application.add_handler(CommandHandler("labs", labs_command))
    application.add_handler(CommandHandler("scores", scores_command))

    # Start polling
    logger.info("Bot started. Polling for messages...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
