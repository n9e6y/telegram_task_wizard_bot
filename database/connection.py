import logging
from pymongo import MongoClient
from pymongo.database import Database
from pymongo.collection import Collection

from config import MONGODB_URI, DB_NAME, PROJECTS_COLLECTION

logger = logging.getLogger(__name__)


class DatabaseConnection:
    """ Singleton class for database connection and access """
    _instance = None
    _client = None
    _db = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super(DatabaseConnection, cls).__new__(cls)
            cls._connect()
        return cls._instance

    @classmethod
    def _connect(cls):
        """ Establish connection to MongoDB """
        try:
            logger.info(f"Connecting to database at {MONGODB_URI}")
            cls._client = MongoClient(MONGODB_URI)
            cls._db = cls._client[DB_NAME]
            logger.info("Database connection established")
        except Exception as e:
            logger.error(f"Failed to connect to database: {e}")
            raise

    @property
    def client(self) -> MongoClient:
        """ Return MongoDB client """
        return self._client

    @property
    def db(self) -> Database:
        """ Return database instance """
        return self._db

    @property
    def projects_collection(self) -> Collection:
        """Return projects collection"""
        return self._db[PROJECTS_COLLECTION]

    def close(self):
        """ Close database connection """
        if self._client:
            self._client.close()
            logger.info("Database connection closed")


db_connection = DatabaseConnection() # global instance for easy importing