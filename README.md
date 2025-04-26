# Telegram Task Wizard Bot

A modular, scalable Telegram bot designed to collect and manage project submissions with file handling capabilities.

**⚠️ Under Development and will complete soon**

## Features

- Guided conversation flow for project submissions
- File upload and management system
- MongoDB data storage
- Modular architecture for extensibility
- Comprehensive logging
- Error handling and validation


## Architecture

```
telegram_task_wizard_bot/
│
├── main.py                    # bot initialization
├── config.py                  # Configuration, environment variables
├── database/
│   ├── __init__.py
│   ├── connection.py          # db connection setup
│   └── models.py              # Data models and operations
│
├── handlers/
│   ├── __init__.py
│   ├── start_handler.py       # Basic commands
│   ├── project_handlers.py    # Project submission flow handlers
│   └── file_handlers.py       # File processing handlers
│
├── utils/
│   ├── __init__.py
│   ├── logger.py              # Logging configuration
│   └── helpers.py             # Helper functions
│
└── requirements.txt           # Dependencies
```


## Installation

1. Clone the repository:
   ```bash
   gh repo clone n9e6y/telegram_task_wizard_bot.git
   cd telegram_task_wizard_bot
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Configure environment variables by creating a `.env` file:
   ```
   TELEGRAM_TOKEN=your_telegram_bot_token
   MONGODB_URI=mongodb://localhost:27017/
   DB_NAME=project_bot_db
   UPLOAD_FOLDER=uploads
   MAX_FILE_SIZE=10485760 
   LOG_LEVEL=INFO
   ```

## Usage

### Starting the Bot

```bash
python main.py
```

### Bot Commands

- `/start` - Initialize the bot
- `/help` - Display help information
- `/newproject` - Begin project submission process
- `/basicinfo` - Provide project name and summary
- `/brieffile` - Upload project brief documents
- `/skipadditionalbrief` - Skip uploading additional files
- `/getintouch` - Provide contact information
- `/cancel` - Cancel current submission process

### Conversation Flow

1. User starts with `/newproject`
2. Bot requests basic project information
3. User provides info with `/basicinfo [Project Name] - [Summary]`
4. Bot requests brief files with `/brieffile`
5. User uploads document(s)
6. Bot asks if user wants to upload more files
7. User provides contact details with `/getintouch [Email] - [Phone]`
8. Bot confirms submission and stores data

## Data Storage

Projects are stored in MongoDB with the following schema:

```javascript
{
  "project_id": "uuid-string",
  "user_id": 123456789,
  "username": "username",
  "name": "Project Name",
  "summary": "Project Summary",
  "files": [
    {
      "file_id": "telegram-file-id",
      "name": "filename.ext",
      "mime_type": "application/pdf",
      "size": 1024,
      "type": "document",
      "local_path": "uploads/123456789/uuid-string/filename.ext",
      "download_success": true
    }
  ],
  "contact": {
    "email": "user@example.com",
    "phone": "123-456-7890",
    "submitted_at": "2025-04-22T14:30:00.000Z"
  },
  "status": "new",
  "created_at": "2025-04-22T14:00:00.000Z",
  "updated_at": "2025-04-22T14:30:00.000Z"
}
```

## Extending the Bot

### Adding New Commands

1. Create appropriate handler function in relevant module
2. Register handler in `main.py` or respective module's registration function
3. Update help documentation

### Creating New Conversation Flows

1. Define conversation states
2. Implement handler functions
3. Create a `ConversationHandler` and register with application

### Database Schema Updates

1. Modify the model in `database/models.py`
2. Add migration script if necessary
3. Update relevant handlers

## Security Considerations

- File validation prevents malicious uploads
- Size limits prevent DoS attacks
- MongoDB validation ensures data integrity
- Proper error handling prevents information leakage

## License

MIT License - See LICENSE file for details
