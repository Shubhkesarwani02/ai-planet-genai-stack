# GenAI Stack Backend

A FastAPI-based backend for the No-Code/Low-Code workflow builder with document intelligence.

## Features

- 🔐 **JWT Authentication** - Secure user authentication with bcrypt password hashing
- 📄 **Document Processing** - PDF text extraction, chunking, and embedding generation
- 🧠 **AI Integration** - OpenAI GPT and Google Gemini support for chat responses
- 🗃️ **Vector Storage** - ChromaDB for semantic search and retrieval
- 💾 **Database** - PostgreSQL with SQLAlchemy ORM
- 🌐 **API** - RESTful API with FastAPI and automatic OpenAPI documentation

## Quick Start

### 1. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 2. Configure Environment

Copy the `.env` file and update with your credentials:

```bash
# Update these in .env file:
OPENAI_API_KEY=your-openai-api-key-here
GEMINI_API_KEY=your-gemini-api-key-here
JWT_SECRET=your-secure-jwt-secret-here
```

### 3. Run the Application

```bash
# Development mode with auto-reload
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python directly
python app/main.py
```

### 4. Access the API

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/health

## API Endpoints

### Authentication
- `POST /api/auth/signup` - Create new account
- `POST /api/auth/login` - Login user
- `GET /api/auth/me` - Get current user info

### Workspaces
- `POST /api/workspaces/upload-document` - Upload PDF and create workspace
- `GET /api/workspaces/` - Get user's workspaces
- `GET /api/workspaces/{id}` - Get specific workspace
- `PUT /api/workspaces/{id}/workflow` - Update workflow JSON
- `GET /api/workspaces/{id}/info` - Get workspace + ChromaDB info

### Chat
- `POST /api/chat/` - Send message and get AI response
- `GET /api/chat/{workspace_id}/history` - Get chat history
- `POST /api/chat/test-llm` - Test LLM connection

## Database Schema

The application uses three main tables:

- **users** - User accounts with authentication
- **workspaces** - Document workspaces with workflow definitions
- **chat_logs** - Chat history and responses

## Environment Variables

| Variable | Description | Required |
|----------|-------------|----------|
| `DATABASE_URL` | PostgreSQL connection string | Yes |
| `JWT_SECRET` | Secret key for JWT tokens | Yes |
| `OPENAI_API_KEY` | OpenAI API key | Optional* |
| `GEMINI_API_KEY` | Google Gemini API key | Optional* |
| `FRONTEND_URL` | Frontend URL for CORS | No |

*At least one AI provider key is required for chat functionality.

## Architecture

```
backend/
├── app/
│   ├── main.py              # FastAPI application
│   ├── core/
│   │   ├── config.py        # Configuration settings
│   │   └── security.py      # JWT and password utilities
│   ├── db/
│   │   ├── database.py      # Database connection
│   │   ├── models.py        # SQLAlchemy models
│   │   ├── schemas.py       # Pydantic schemas
│   │   └── crud.py          # Database operations
│   ├── api/
│   │   ├── auth.py          # Authentication endpoints
│   │   ├── workspaces.py    # Workspace management
│   │   └── chat.py          # Chat functionality
│   ├── services/
│   │   ├── pdf_utils.py     # PDF text extraction
│   │   ├── chunking.py      # Text chunking
│   │   ├── embeddings.py    # Embedding generation
│   │   ├── chroma_client.py # ChromaDB operations
│   │   └── llm_service.py   # LLM response generation
│   └── workers/
│       └── tasks.py         # Background task processing
├── requirements.txt
└── .env
```

## Development

### Running Tests
```bash
# Install test dependencies
pip install pytest pytest-asyncio

# Run tests
pytest
```

### Code Formatting
```bash
# Install formatting tools
pip install black isort

# Format code
black app/
isort app/
```

## Deployment

### Using Docker (Optional)
```bash
# Build image
docker build -t genai-stack-backend .

# Run container
docker run -p 8000:8000 --env-file .env genai-stack-backend
```

### Production Settings
- Set `JWT_SECRET` to a secure random string
- Use environment variables for all secrets
- Enable HTTPS
- Set up proper logging and monitoring

## Troubleshooting

### Common Issues

1. **Import Errors**: Make sure all dependencies are installed
   ```bash
   pip install -r requirements.txt
   ```

2. **Database Connection**: Verify DATABASE_URL is correct and PostgreSQL is running

3. **ChromaDB Permissions**: Ensure write permissions for `chroma_data` directory

4. **API Key Errors**: Verify OpenAI/Gemini API keys are valid and have sufficient credits

### Logs
The application logs to stdout. Check logs for detailed error information:
```bash
# View logs in development
uvicorn app.main:app --reload --log-level debug
```