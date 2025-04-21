import logging
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    ContextTypes,
    CommandHandler,
    MessageHandler,
    ConversationHandler,
    CallbackQueryHandler,
    filters,
)
from database.models import ProjectModel
from utils.helpers import extract_contact_info, extract_project_info, handle_file_upload

BASIC_INFO, BRIEF_FILE, ADDITIONAL_BRIEF, CONTACT_INFO = range(4) # define conversation states

logger = logging.getLogger(__name__)

async def new_project(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ Start the project submission process """

    user = update.effective_user
    logger.info(f"User {user.id} started new project submission")

    await update.message.reply_text(
        "Let's get started with your new project! 🚀\n\n"
        "Please provide the basic information using this format:\n"
        "/basicinfo [Project Name] - [Brief Summary]\n\n"
        "For example: /basicinfo Marketing Website - Need a new responsive website for our marketing campaign"
    )

    # init a new project in user_data
    context.user_data['current_project'] = ProjectModel.create_project(
        user_id=user.id,
        username=user.username
    )

    return BASIC_INFO


async def basic_info(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ Handle the basic project information """

    user_id = update.effective_user.id
    text = update.message.text
    logger.info(f"User {user_id} submitted basic project info")

    if not text.startswith('/basicinfo'):
        await update.message.reply_text(
            "Please use the /basicinfo command followed by your project name and summary."
        )
        return BASIC_INFO

    # extract project info
    project_info = text[len('/basicinfo'):].strip()
    if not project_info:
        await update.message.reply_text(
            "Please provide project name and summary after the /basicinfo command."
        )
        return BASIC_INFO

    try:
        project_name, project_summary = extract_project_info(project_info) # process the info

        # save to user data
        context.user_data['current_project']['name'] = project_name
        context.user_data['current_project']['summary'] = project_summary

        await update.message.reply_text(
            f"Great! I've recorded the following information:\n\n"
            f"Project Name: {project_name}\n"
            f"Summary: {project_summary}\n\n"
            f"Now, please upload any brief documents or files using the /brieffile command. "
            f"You can upload files directly after typing /brieffile."
        )
        return BRIEF_FILE
    except Exception as e:
        logger.error(f"Error processing basic info: {e}")
        await update.message.reply_text(
            "Something went wrong. Please try again with the format:\n"
            "/basicinfo [Project Name] - [Brief Summary]"
        )
        return BASIC_INFO


async def brief_file(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle brief document upload."""
    user_id = update.effective_user.id

    # Check if this is the command or a file upload
    if update.message.text and update.message.text.startswith('/brieffile'):
        logger.info(f"User {user_id} initiated file upload")
        await update.message.reply_text(
            "Please upload your brief file now. You can send documents, images, or other files."
        )
        return BRIEF_FILE

    # Handle file uploads
    if update.message.document or update.message.photo:
        logger.info(f"User {user_id} uploaded a file")

        # Process the file upload using file_handlers module
        from handlers.file_handlers import process_file_upload, validate_file

        # First inform user that we're processing their file
        processing_message = await update.message.reply_text("Processing your file...")

        # Process and validate the file
        file_metadata = await process_file_upload(update, context)

        if not file_metadata:
            await processing_message.edit_text(
                "Sorry, there was an error processing your file. Please try again."
            )
            return BRIEF_FILE

        if 'error' in file_metadata:
            if file_metadata['error'] == 'file_too_large':
                max_mb = file_metadata['max_size'] / (1024 * 1024)
                await processing_message.edit_text(
                    f"Your file is too large. Maximum allowed size is {max_mb:.1f} MB. Please upload a smaller file."
                )
                return BRIEF_FILE
            else:
                await processing_message.edit_text(
                    "Sorry, there was an error with your file. Please try again."
                )
                return BRIEF_FILE

        # validate the file
        validation = await validate_file(file_metadata)
        if not validation['valid']:
            issues = ', '.join(validation['issues'])
            await processing_message.edit_text(
                f"Your file could not be validated ({issues}). Please try again with a different file."
            )
            # Clean up invalid file
            from handlers.file_handlers import delete_file
            if 'local_path' in file_metadata:
                await delete_file(file_metadata['local_path'])
            return BRIEF_FILE

        # file is valid, update processing message
        await processing_message.edit_text(f"File '{file_metadata['name']}' received successfully!")

        # add file info to project
        if 'files' not in context.user_data['current_project']:
            context.user_data['current_project']['files'] = []

        context.user_data['current_project']['files'].append(file_metadata)

        # ask if they want to add more files
        keyboard = [
            [
                InlineKeyboardButton("Yes, add more files", callback_data='more_files'),
                InlineKeyboardButton("No, continue", callback_data='no_more_files'),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)

        await update.message.reply_text(
            f"Would you like to add more files?",
            reply_markup=reply_markup
        )
        return ADDITIONAL_BRIEF

    await update.message.reply_text(
        "I'm expecting a file upload. Please upload your brief document or use /skipadditionalbrief to skip."
    )
    return BRIEF_FILE


async def additional_brief_callback(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ Handle button callbacks for additional brief files """

    query = update.callback_query
    user_id = update.effective_user.id
    await query.answer()

    if query.data == 'more_files':
        logger.info(f"User {user_id} wants to add more files")
        await query.edit_message_text(
            "Please upload your next file, or use /skipadditionalbrief when you're done."
        )
        return BRIEF_FILE
    else:  # no more files
        logger.info(f"User {user_id} finished adding files")
        await query.edit_message_text(
            "Great! Now, let's get your contact information using the /getintouch command."
        )
        return CONTACT_INFO


async def skip_additional_brief(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ Skip additional brief uploads """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} skipped additional files")

    await update.message.reply_text(
        "Skipping additional files. Now, let's get your contact information.\n\n"
        "Please use the /getintouch command followed by your email and phone number like this:\n"
        "/getintouch email@example.com - 123-456-7890"
    )
    return CONTACT_INFO


async def get_into_touch(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle contact information."""
    user_id = update.effective_user.id
    text = update.message.text
    logger.info(f"User {user_id} submitted contact info")

    if not text.startswith('/getintouch'):
        await update.message.reply_text(
            "Please use the /getintouch command followed by your email and phone number."
        )
        return CONTACT_INFO

    # Extract contact info
    contact_info = text[len('/getintouch'):].strip()
    if not contact_info:
        await update.message.reply_text(
            "Please provide your contact information after the /getintouch command.\n"
            "Format: /getintouch email@example.com - 123-456-7890"
        )
        return CONTACT_INFO

    try:
        # process the contact info
        email, phone = extract_contact_info(contact_info)

        # save to user data
        context.user_data['current_project']['contact'] = {
            'email': email,
            'phone': phone,
            'submitted_at': datetime.utcnow().isoformat()
        }

        # save the project to the database
        project_id = ProjectModel.save_project(context.user_data['current_project'])

        await update.message.reply_text(
            f"Thank you for submitting your project information! 🎉\n\n"
            f"Your project has been registered with ID: {context.user_data['current_project']['project_id']}\n\n"
            f"We've recorded the following contact details:\n"
            f"Email: {email}\n"
            f"Phone: {phone}\n\n"
            f"Our team will connect with you shortly to discuss your project requirements in detail."
            f"If you have any questions in the meantime, feel free to reach out."
        )

        # Clear user data
        context.user_data.clear()

        return ConversationHandler.END
    except Exception as e:
        logger.error(f"Error processing contact info: {e}")
        await update.message.reply_text(
            "Something went wrong. Please try again with the format:\n"
            "/getintouch email@example.com - 123-456-7890"
        )
        return CONTACT_INFO


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """ Cancel the conversation """
    user_id = update.effective_user.id
    logger.info(f"User {user_id} canceled project submission")

    await update.message.reply_text(
        "Project submission canceled. You can start again anytime with /newproject."
    )
    context.user_data.clear()
    return ConversationHandler.END


def register_project_handlers(application: Application) -> None:
    """ Register project-related handlers """
    # add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('newproject', new_project)],
        states={
            BASIC_INFO: [
                CommandHandler('basicinfo', basic_info),
                MessageHandler(filters.TEXT & ~filters.COMMAND, basic_info)
            ],
            BRIEF_FILE: [
                CommandHandler('brieffile', brief_file),
                CommandHandler('skipadditionalbrief', skip_additional_brief),
                MessageHandler(filters.Document.ALL | filters.PHOTO, brief_file)
            ],
            ADDITIONAL_BRIEF: [
                CallbackQueryHandler(additional_brief_callback),
                CommandHandler('skipadditionalbrief', skip_additional_brief),
                MessageHandler(filters.Document.ALL | filters.PHOTO, brief_file)
            ],
            CONTACT_INFO: [
                CommandHandler('getintouch', get_into_touch),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_into_touch)
            ],
        },
        fallbacks=[CommandHandler('cancel', cancel)]
    )
    application.add_handler(conv_handler)
    logger.info("Project handlers registered")