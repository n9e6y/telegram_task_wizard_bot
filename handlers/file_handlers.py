import os
import logging
from typing import Dict, Any, Optional, BinaryIO
from telegram import Update, File
from telegram.ext import ContextTypes

logger = logging.getLogger(__name__)

# Configure file storage
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', 'uploads')
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 10 * 1024 * 1024))  # 10MB default

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


async def download_file(file: File, destination: str) -> bool:
    """ Download a file from Telegram to local storage """
    try:
        os.makedirs(os.path.dirname(destination), exist_ok=True) # directory exists?

        # Download the file
        await file.download_to_drive(destination)
        logger.info(f"File downloaded to {destination}")
        return True
    except Exception as e:
        logger.error(f"Error downloading file: {e}")
        return False


async def process_file_upload(update: Update, context: ContextTypes.DEFAULT_TYPE) -> Optional[Dict[str, Any]]:
    """ Process an uploaded file and store it """
    try:
        # get the user ID for folder organization
        user_id = update.effective_user.id
        project_id = context.user_data.get('current_project', {}).get('project_id', 'unknown')

        # extract file info based on file type
        if update.message.document:
            file = update.message.document
            file_type = 'document'
            file_name = file.file_name if hasattr(file, 'file_name') else f"document_{file.file_id}"
            mime_type = file.mime_type if hasattr(file, 'mime_type') else 'application/octet-stream'
        elif update.message.photo:
            photos = update.message.photo
            file = photos[-1]  # get photo
            file_type = 'photo'
            file_name = f"photo_{file.file_id}.jpg"
            mime_type = 'image/jpeg'
        else:
            logger.warning(f"Unsupported file type from user {user_id}")
            return None

        # check file size
        file_size = file.file_size if hasattr(file, 'file_size') else 0
        if file_size > MAX_FILE_SIZE:
            logger.warning(f"File too large: {file_size} bytes (max: {MAX_FILE_SIZE})")
            return {
                'error': 'file_too_large',
                'max_size': MAX_FILE_SIZE,
                'file_size': file_size
            }

        # prepare file metadata
        file_metadata = {
            'file_id': file.file_id,
            'name': file_name,
            'mime_type': mime_type,
            'size': file_size,
            'type': file_type,
            'uploaded_by': user_id
        }

        # create folder structure: uploads/user_id/project_id/
        save_dir = os.path.join(UPLOAD_FOLDER, str(user_id), project_id)
        os.makedirs(save_dir, exist_ok=True)

        # download path
        local_path = os.path.join(save_dir, file_name)

        # check if file with same name exists
        if os.path.exists(local_path):
            # add timestamp to avoid overwriting
            base, ext = os.path.splitext(file_name)
            timestamp = int(datetime.now().timestamp())
            file_name = f"{base}_{timestamp}{ext}"
            local_path = os.path.join(save_dir, file_name)

        #get the file from Telegram
        telegram_file = await file.get_file()

        # download and save the file
        if await download_file(telegram_file, local_path):
            file_metadata['local_path'] = local_path
            file_metadata['download_success'] = True
            logger.info(f"File {file_name} successfully saved to {local_path}")
        else:
            file_metadata['download_success'] = False
            logger.error(f"Failed to download file {file_name}")

        return file_metadata

    except Exception as e:
        logger.error(f"Error processing file upload: {e}")
        return None


async def validate_file(file_metadata: Dict[str, Any]) -> Dict[str, Any]:
    """ Validate file for security and appropriateness """

    # Initialize validation result
    validation = {
        'valid': True,
        'issues': []
    }

    # check if file was downloaded successfully
    if not file_metadata.get('download_success', False):
        validation['valid'] = False
        validation['issues'].append('download_failed')
        return validation

    # check file size again (local file may differ from reported size)
    try:
        local_path = file_metadata.get('local_path')
        if local_path and os.path.exists(local_path):
            actual_size = os.path.getsize(local_path)
            if actual_size > MAX_FILE_SIZE:
                validation['valid'] = False
                validation['issues'].append('file_too_large')
        else:
            validation['valid'] = False
            validation['issues'].append('file_not_found')
    except Exception as e:
        logger.error(f"Error validating file: {e}")
        validation['valid'] = False
        validation['issues'].append('validation_error')

    # TODO: add more validation steps as needed:
    # - Virus scanning
    # - File type verification
    # - Content analysis

    return validation


async def delete_file(file_path: str) -> bool:
    """ Delete a file from storage """
    try:
        if os.path.exists(file_path):
            os.remove(file_path)
            logger.info(f"File deleted: {file_path}")
            return True
        else:
            logger.warning(f"File not found for deletion: {file_path}")
            return False
    except Exception as e:
        logger.error(f"Error deleting file {file_path}: {e}")
        return False