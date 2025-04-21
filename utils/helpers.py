import logging
from typing import Tuple, Dict, Any
from telegram import Update

logger = logging.getLogger(__name__)


def extract_project_info(project_info: str) -> Tuple[str, str]:
    """ Extract project name and summary from input string """
    if ' - ' in project_info:
        project_name, project_summary = project_info.split(' - ', 1)
    else:
        project_name = project_info
        project_summary = "No summary provided"

    return project_name.strip(), project_summary.strip()


def extract_contact_info(contact_info: str) -> Tuple[str, str]:
    """ Extract email and phone from input string """
    if ' - ' in contact_info:
        email, phone = contact_info.split(' - ', 1)
    else:
        email = contact_info
        phone = "Not provided"

    return email.strip(), phone.strip()


def handle_file_upload(update: Update) -> Dict[str, Any]:
    """ Process uploaded file from update """
    # get file information
    if update.message.document:
        file = update.message.document
        file_info = {
            'file_id': file.file_id,
            'name': file.file_name if hasattr(file, 'file_name') else 'document',
            'mime_type': file.mime_type if hasattr(file, 'mime_type') else 'unknown',
            'size': file.file_size if hasattr(file, 'file_size') else 0,
            'type': 'document'
        }
    else:  # photo
        photos = update.message.photo
        file = photos[-1]  # get the largest photo
        file_info = {
            'file_id': file.file_id,
            'name': 'photo.jpg',
            'mime_type': 'image/jpeg',
            'size': file.file_size if hasattr(file, 'file_size') else 0,
            'type': 'photo'
        }

    logger.info(f"Processed file: {file_info['name']} ({file_info['type']})")
    return file_info