import logging
from telegram.ext import Application
from config import TELEGRAM_TOKEN
from utils.logger import setup_logger
from handlers.start_handler import register_start_handlers
from handlers.project_handlers import register_project_handlers

logger = setup_logger(__name__) # set up logging


def main() -> None:
    """Initialize and start the bot"""

    logger.info("Starting bot...")

    # create the Application
    application = Application.builder().token(TELEGRAM_TOKEN).build()

    # register all handlers
    register_start_handlers(application)
    register_project_handlers(application)

    # start the bot
    logger.info("Bot started, polling for updates...")
    application.run_polling()


if __name__ == '__main__':
    main()