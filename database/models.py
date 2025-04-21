import uuid
import logging
import datetime
from typing import Dict, Any, List, Optional

from database.connection import db_connection

logger = logging.getLogger(__name__)


class ProjectModel:
    """ Project data model and operations """

    @staticmethod
    def create_project(user_id: int, username: Optional[str] = None) -> Dict[str, Any]:
        """ Create a new project entry """
        project = {
            'project_id': str(uuid.uuid4()),
            'user_id': user_id,
            'username': username,
            'files': [],
            'status': 'new',
            'created_at': datetime.datetime.utcnow()
        }

        return project

    @staticmethod
    def save_project(project_data: Dict[str, Any]) -> str:
        """ Save project to database """
        try:
            result = db_connection.projects_collection.insert_one(project_data)
            logger.info(f"Project saved with ID: {result.inserted_id}")
            return str(result.inserted_id)
        except Exception as e:
            logger.error(f"Error saving project: {e}")
            raise

    @staticmethod
    def get_project(project_id: str) -> Optional[Dict[str, Any]]:
        """ Retrieve project by ID """
        try:
            project = db_connection.projects_collection.find_one({'project_id': project_id})
            return project
        except Exception as e:
            logger.error(f"Error retrieving project {project_id}: {e}")
            return None

    @staticmethod
    def update_project_status(project_id: str, status: str) -> bool:
        """ Update project status """
        try:
            result = db_connection.projects_collection.update_one(
                {'project_id': project_id},
                {'$set': {'status': status, 'updated_at': datetime.datetime.utcnow()}}
            )
            return result.modified_count > 0
        except Exception as e:
            logger.error(f"Error updating project {project_id}: {e}")
            return False