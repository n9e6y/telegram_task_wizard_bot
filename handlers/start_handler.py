import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

logger = logging.getLogger(__name__)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Send a welcome message when the command /start is issued """
    user = update.effective_user
    logger.info(f"User {user.id} started the bot")

    await update.message.reply_text(
        f"Hello {user.first_name}! 👋\n\n"
        f"I'm your project assistant. I'll help you submit your project information.\n\n"
        f"Use /newproject to start submitting a new project."
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """ Send a message when the command /help is issued """
    logger.info(f"User {update.effective_user.id} requested help")

    help_text = (
        "🤖 *Project Assistant Bot Help* 🤖\n\n"
        "*Available Commands:*\n"
        "/start - Start the bot\n"
        "/help - Show this help message\n"
        "/newproject - Begin submitting a new project\n"
        "/basicinfo - Provide project name and summary\n"
        "/brieffile - Upload project brief documents\n"
        "/skipadditionalbrief - Skip uploading additional files\n"
        "/getintouch - Provide your contact information\n"
        "/cancel - Cancel the current submission process\n\n"
        "To submit a new project, follow these steps:\n"
        "1. Use /newproject to start\n"
        "2. Provide basic info with /basicinfo\n"
        "3. Upload files with /brieffile\n"
        "4. Provide contact details with /getintouch"
    )
    await update.message.reply_text(help_text, parse_mode='Markdown')


def register_start_handlers(application: Application) -> None:
    """ Register basic command handlers """
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CommandHandler('help', help_command))

    logger.info("Basic command handlers registered")