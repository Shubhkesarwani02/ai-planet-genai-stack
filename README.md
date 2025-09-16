# GenAI Stack 🚀

<div align="center">
  <h3>No-Code/Low-Code Workflow Builder with Document Intelligence</h3>
  <p>A powerful platform that combines AI-driven document processing with visual workflow building capabilities</p>

  ![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)
  ![License](https://img.shields.io/badge/license-MIT-green.svg)
  ![Python](https://img.shields.io/badge/python-3.13-blue.svg)
  ![Next.js](https://img.shields.io/badge/next.js-14.2.16-black.svg)
  ![FastAPI](https://img.shields.io/badge/fastapi-0.104.1-009688.svg)
</div>

## 📋 Table of Contents

- [Overview](#overview)
- [Features](#features)
- [Architecture](#architecture)
- [Tech Stack](#tech-stack)
- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Usage](#usage)
- [API Documentation](#api-documentation)
- [Project Structure](#project-structure)
- [Contributing](#contributing)
- [License](#license)

## 🌟 Overview

GenAI Stack is a comprehensive no-code/low-code platform that enables users to create intelligent workflows with document processing capabilities. The platform combines the power of modern AI models (OpenAI GPT, Google Gemini) with an intuitive visual workflow builder, allowing users to process documents, extract insights, and build automated workflows without writing code.

**Platform Workflow (high-level):**

```mermaid
flowchart LR
   A[User] --> B[Upload Document]
   B --> C[Document Processing]
   C --> D[Generate Embeddings]
   D --> E[Store in ChromaDB]
   E --> F[Build Workflow]
   F --> G[Run Workflow]
   G --> H[Results / Export]
```

### Key Capabilities

- **Visual Workflow Builder**: Drag-and-drop interface for creating complex workflows
- **Document Intelligence**: Upload and process PDFs with AI-powered analysis
- **Multi-LLM Support**: Integration with OpenAI GPT-4 and Google Gemini models
- **Vector Search**: Advanced document search using ChromaDB
- **User Management**: Secure authentication and workspace management
- **Real-time Chat**: Interactive chat interface for querying document knowledge base

## ✨ Features

### 🎨 Frontend Features
- **Modern UI/UX**: Built with Next.js 14 and shadcn/ui components
- **Responsive Design**: Mobile-first approach with Tailwind CSS
- **Real-time Interactions**: Dynamic workflow canvas with drag-and-drop
- **Authentication**: Secure login/signup with protected routes
- **Workspace Management**: Multi-workspace support for organizing projects
- **Dark/Light Theme**: Toggle between themes for better user experience

**Frontend Workflow:**

```mermaid
flowchart LR
   U[User] --> S[Login / Signup]
   S --> W[Select Workspace]
   W --> C[Open Workflow Canvas]
   C --> D[Drag & Drop Nodes]
   D --> R[Save / Run Workflow]
   R --> V[View Results]
```

### ⚡ Backend Features
- **High-Performance API**: FastAPI with async/await support
- **Database Integration**: PostgreSQL with SQLAlchemy ORM
- **Document Processing**: PDF parsing and chunking with intelligent text extraction
- **Vector Database**: ChromaDB integration for semantic search
- **Background Tasks**: Celery for handling long-running operations
- **Security**: JWT authentication with password hashing
- **CORS Support**: Cross-origin resource sharing for frontend integration

**Backend Workflow:**

```mermaid
flowchart LR
   CR[Client Request] --> A[Auth (JWT)]
   A --> AR[API Route]
   AR --> S[Service Layer]
   S --> DB[DB / ChromaDB]
   S --> BT[Background Task (Celery)]
   BT --> RESP[Return Response]
   DB --> RESP
```

### 🤖 AI/ML Features
- **Multi-Model Support**: OpenAI GPT-4o-mini and Google Gemini integration
- **Embedding Generation**: Multiple embedding providers (OpenAI, Google)
- **Contextual Responses**: RAG (Retrieval-Augmented Generation) implementation
- **Intelligent Chunking**: Smart document segmentation for better retrieval

**AI/ML Workflow:**

```mermaid
flowchart LR
   P[PDF] --> PC[Parse & Chunk]
   PC --> CN[Clean / Text Normalize]
   CN --> GE[Generate Embeddings]
   GE --> Q[Query LLMs (OpenAI / Gemini)]
   Q --> AG[Aggregate & Rank]
   AG --> RR[Return Contextual Response]
```

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Frontend      │    │     Backend      │    │   AI Services   │
│   (Next.js)     │◄──►│   (FastAPI)      │◄──►│   (OpenAI/      │
│                 │    │                  │    │    Gemini)      │
└─────────────────┘    └──────────────────┘    └─────────────────┘
         │                       │                       │
         │                       │                       │
         ▼                       ▼                       ▼
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   UI Components │    │   PostgreSQL     │    │   ChromaDB      │
│   shadcn/ui     │    │   Database       │    │   Vector Store  │
└─────────────────┘    └──────────────────┘    └─────────────────┘
```

## 🛠️ Tech Stack

### Frontend
- **Framework**: Next.js 14.2.16
- **Language**: TypeScript
- **Styling**: Tailwind CSS
- **UI Components**: Radix UI + shadcn/ui
- **State Management**: React Context API
- **Icons**: Lucide React
- **Fonts**: Geist Sans & Mono

### Backend
- **Framework**: FastAPI 0.104.1
- **Language**: Python 3.13
- **Database**: PostgreSQL with SQLAlchemy 2.0+
- **Authentication**: JWT with python-jose
- **Password Hashing**: passlib with bcrypt
- **Async Support**: uvicorn with async/await
- **Database Driver**: psycopg3 (Python 3.13 compatible)

### AI/ML Stack
- **LLM Models**: OpenAI GPT-4o-mini, Google Gemini
- **Vector Database**: ChromaDB
- **Embeddings**: OpenAI Embeddings, Google Embeddings
- **Document Processing**: Custom PDF parsing and chunking
- **Task Queue**: Background task processing

### Infrastructure
- **Web Server**: Uvicorn (ASGI)
- **Database**: PostgreSQL
- **Environment**: Python virtual environments
- **Package Management**: pip (backend), pnpm (frontend)

## 📋 Prerequisites

### System Requirements
- **Node.js**: 18.x or higher
- **Python**: 3.13
- **PostgreSQL**: 12.x or higher
- **pnpm**: Latest version (recommended over npm)

### API Keys Required
- **OpenAI API Key** (optional): For GPT-4 integration
- **Google AI API Key** (optional): For Gemini integration
- At least one AI provider is required for full functionality

## 🚀 Installation

### 1. Clone the Repository
```bash
git clone https://github.com/Shubhkesarwani02/ai-planet-genai-stack.git
cd ai-planet-genai-stack
```

### 2. Backend Setup

#### Navigate to backend directory
```bash
cd backend
```

#### Create and activate virtual environment
```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

#### Install dependencies
```bash
pip install -r requirements.txt
```

#### Setup database
```bash
# Run database initialization
python init_database.py
```

### 3. Frontend Setup

#### Navigate to frontend directory
```bash
cd ../frontend
```

#### Install dependencies
```bash
pnpm install
```

## ⚙️ Configuration

### Backend Configuration

Create a `.env` file in the `backend` directory:

```bash
# Database Configuration (Required)
DATABASE_URL=postgresql://username:password@localhost:5432/genai_stack

# For Supabase (add SSL mode for production)
# DATABASE_URL=postgresql://postgres:password@db.xxxxx.supabase.co:5432/postgres?sslmode=require

# Security (Required)
SECRET_KEY=your-super-secret-jwt-key-here-minimum-32-characters
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Service API Keys (At least one required)
OPENAI_API_KEY=sk-your-openai-api-key-here
GEMINI_API_KEY=your-google-ai-api-key-here

# Application Settings
DEBUG=False
CORS_ORIGINS=["http://localhost:3000"]

# For production deployment
# CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]
```

**Important Notes:**
- For **Render deployment**: Add `?sslmode=require` to your DATABASE_URL
- For **Supabase**: Ensure your database is not paused and has proper access settings
- **SECRET_KEY**: Must be at least 32 characters for JWT security

### Frontend Configuration

Create a `.env.local` file in the `frontend` directory:

```bash
# API Configuration
NEXT_PUBLIC_API_URL=http://localhost:8000

# Optional: Analytics
NEXT_PUBLIC_VERCEL_ANALYTICS=true
```

## 🎯 Usage

### Starting the Development Environment

#### 1. Start the Backend Server
```bash
cd backend
# Activate virtual environment if not already active
# Windows: venv\Scripts\activate
# macOS/Linux: source venv/bin/activate

# Start the server
python main_simple.py
# or for full features:
python -m app.main
```

The backend API will be available at `http://localhost:8000`

#### 2. Start the Frontend Development Server
```bash
cd frontend
pnpm dev
```

The frontend application will be available at `http://localhost:3000`

### Basic Workflow

**End-to-end Basic Workflow:**

```mermaid
flowchart LR
   SU[Sign Up / Login] --> CW[Create Workspace]
   CW --> UD[Upload Document]
   UD --> PE[Process & Embed]
   PE --> BW[Build Workflow]
   BW --> RQ[Run / Query]
   RQ --> ES[Export / Save Results]
```

## 📚 API Documentation

### Authentication Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/auth/register` | Register a new user |
| `POST` | `/auth/login` | User login |
| `GET` | `/auth/me` | Get current user info |

### Workspace Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `GET` | `/workspaces/` | List user workspaces |
| `POST` | `/workspaces/` | Create new workspace |
| `GET` | `/workspaces/{id}` | Get workspace details |
| `PUT` | `/workspaces/{id}` | Update workspace |
| `DELETE` | `/workspaces/{id}` | Delete workspace |

### Chat Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/chat/` | Send chat message |
| `GET` | `/chat/history/{workspace_id}` | Get chat history |

### Document Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| `POST` | `/documents/upload` | Upload document |
| `GET` | `/documents/{workspace_id}` | List workspace documents |
| `DELETE` | `/documents/{id}` | Delete document |

### API Documentation URLs

- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

## 📁 Project Structure

```
genai-stack/
├── backend/                    # FastAPI backend
│   ├── app/
│   │   ├── api/               # API route handlers
│   │   │   ├── auth.py        # Authentication routes
│   │   │   ├── chat.py        # Chat functionality
│   │   │   └── workspaces.py  # Workspace management
│   │   ├── core/              # Core configuration
│   │   │   ├── config.py      # App configuration
│   │   │   └── security.py    # Security utilities
│   │   ├── db/                # Database layer
│   │   │   ├── crud.py        # Database operations
│   │   │   ├── database.py    # Database connection
│   │   │   ├── models.py      # SQLAlchemy models
│   │   │   └── schemas.py     # Pydantic schemas
│   │   ├── services/          # Business logic
│   │   │   ├── chroma_client.py    # Vector database
│   │   │   ├── chunking.py         # Document chunking
│   │   │   ├── embeddings.py       # Embedding generation
│   │   │   ├── llm_service.py      # LLM integration
│   │   │   └── pdf_utils.py        # PDF processing
│   │   └── workers/           # Background tasks
│   │       └── tasks.py       # Async task definitions
│   ├── requirements.txt       # Python dependencies
│   ├── main_simple.py        # Simplified entry point
│   └── init_database.py      # Database initialization
│
├── frontend/                  # Next.js frontend
│   ├── app/                  # App router (Next.js 13+)
│   │   ├── builder/         # Workflow builder pages
│   │   ├── chat/           # Chat interface pages
│   │   ├── login/          # Authentication pages
│   │   ├── signup/
│   │   └── layout.tsx      # Root layout
│   ├── components/          # React components
│   │   ├── ui/             # shadcn/ui components
│   │   ├── workflow-canvas.tsx    # Main workflow editor
│   │   ├── workflow-node.tsx      # Workflow node component
│   │   └── ProtectedRoute.tsx     # Route protection
│   ├── contexts/           # React contexts
│   │   └── AuthContext.tsx # Authentication context
│   ├── hooks/             # Custom React hooks
│   ├── lib/               # Utility libraries
│   │   ├── api.ts         # API client
│   │   └── utils.ts       # Helper functions
│   └── package.json       # Node.js dependencies
│
└── README.md              # This file
```

## 🤝 Contributing

We welcome contributions to GenAI Stack! Please follow these guidelines:

### Development Workflow

1. **Fork the Repository**
   ```bash
   git fork https://github.com/Shubhkesarwani02/ai-planet-genai-stack.git
   ```

2. **Create Feature Branch**
   ```bash
   git checkout -b feature/your-feature-name
   ```

3. **Make Changes**
   - Follow existing code style and conventions
   - Add tests for new functionality
   - Update documentation as needed

4. **Test Your Changes**
   ```bash
   # Backend tests
   cd backend
   python -m pytest

   # Frontend tests
   cd frontend
   pnpm test
   ```

5. **Submit Pull Request**
   - Provide clear description of changes
   - Reference any related issues
   - Ensure all tests pass

### Code Style Guidelines

- **Python**: Follow PEP 8 guidelines
- **TypeScript**: Use ESLint and Prettier configurations
- **Commit Messages**: Use conventional commit format

## � Deployment

### Deploying to Render

#### Backend Deployment

1. **Connect your GitHub repository** to Render
2. **Create a new Web Service** with these settings:
   ```
   Build Command: pip install -r requirements.txt
   Start Command: uvicorn app.main:app --host 0.0.0.0 --port $PORT
   ```
3. **Set Environment Variables** in Render dashboard:
   ```
   DATABASE_URL=your-supabase-or-postgres-url
   SECRET_KEY=your-secret-key
   OPENAI_API_KEY=your-openai-key
   GEMINI_API_KEY=your-gemini-key
   ```

#### Frontend Deployment

1. **Deploy to Vercel** (recommended):
   ```bash
   # Install Vercel CLI
   npm i -g vercel
   
   # Deploy from frontend directory
   cd frontend
   vercel --prod
   ```

2. **Set Environment Variables** in Vercel:
   ```
   NEXT_PUBLIC_API_URL=https://your-render-backend-url.onrender.com
   ```

### Environment Variables Reference

#### Backend (.env)
```bash
# Database (Required)
DATABASE_URL=postgresql://user:password@host:port/database

# Security (Required)
SECRET_KEY=your-super-secret-jwt-key-min-32-chars
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30

# AI Services (At least one required)
OPENAI_API_KEY=sk-your-openai-key
GEMINI_API_KEY=your-google-ai-key

# Optional
DEBUG=False
CORS_ORIGINS=["https://your-frontend-domain.vercel.app"]
```

#### Frontend (.env.local)
```bash
NEXT_PUBLIC_API_URL=https://your-backend.onrender.com
```

## 🔧 Troubleshooting

### Common Issues

#### Database Connection Issues

**Supabase/PostgreSQL Connection Error**
```
Error: connection to server failed: Network is unreachable
```

**Solutions:**
1. **Check Database URL format:**
   ```bash
   # Correct format for Supabase
   DATABASE_URL=postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres
   ```

2. **Verify Supabase settings:**
   - Ensure database is not paused
   - Check if IP restrictions are configured
   - Verify SSL mode is enabled

3. **Test connection locally:**
   ```bash
   psql "postgresql://postgres:[password]@db.[ref].supabase.co:5432/postgres"
   ```

4. **For Render deployment:**
   - Add `?sslmode=require` to DATABASE_URL
   - Ensure outbound connections are allowed

**Local PostgreSQL Issues**
```bash
# Check PostgreSQL is running
pg_isready -h localhost -p 5432

# Verify database exists
psql -h localhost -p 5432 -l

# Start PostgreSQL service
# Windows: net start postgresql-x64-13
# macOS: brew services start postgresql
# Linux: sudo systemctl start postgresql
```

#### Deployment Issues

**Render Build Failures**
- Ensure `requirements.txt` is in the root or specify correct path
- Check Python version compatibility (3.13)
- Verify all environment variables are set

**Port Binding Issues**
```bash
# Ensure your app uses PORT environment variable
port = int(os.environ.get("PORT", 8000))
uvicorn.run("app.main:app", host="0.0.0.0", port=port)
```

**CORS Issues**
- Add your frontend domain to `CORS_ORIGINS`
- For development: `["http://localhost:3000"]`
- For production: `["https://your-app.vercel.app"]`

#### Frontend Issues

**API Connection Errors**
```bash
# Check NEXT_PUBLIC_API_URL is correct
echo $NEXT_PUBLIC_API_URL

# Verify backend is accessible
curl https://your-backend.onrender.com/health
```

**Build Errors**
```bash
# Clear cache and reinstall
rm -rf .next node_modules
pnpm install
pnpm build
```

#### AI Service Issues

**OpenAI API Errors**
- Verify API key is valid and has credits
- Check rate limits and usage quotas
- Ensure correct model names (gpt-4o-mini)

**Gemini API Errors**
- Verify API key is enabled for Gemini Pro
- Check regional availability
- Ensure Google AI Studio access

### Performance Optimization

**Database Performance**
- Use connection pooling
- Implement database indexes
- Consider read replicas for high traffic

**API Performance**
- Enable response caching
- Use background tasks for heavy operations
- Implement rate limiting

**Frontend Performance**
- Enable Next.js image optimization
- Use dynamic imports for large components
- Implement proper loading states

### Getting Help

- **Issues**: [GitHub Issues](https://github.com/Shubhkesarwani02/ai-planet-genai-stack/issues)
- **Discussions**: [GitHub Discussions](https://github.com/Shubhkesarwani02/ai-planet-genai-stack/discussions)

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🙏 Acknowledgments

- **OpenAI** for GPT-4 API
- **Google** for Gemini AI API
- **Vercel** for Next.js framework
- **FastAPI** team for the excellent Python framework
- **shadcn/ui** for beautiful UI components
- **ChromaDB** for vector database capabilities

---

<div align="center">
  <p>Built with ❤️ by the GenAI Stack team</p>
  <p>
    <a href="#genai-stack-">Back to Top</a>
  </p>
</div>