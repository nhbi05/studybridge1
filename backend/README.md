# StudyBridge Backend

AI-powered curriculum-based resource recommendation system built with FastAPI, Claude AI, and Supabase.

## Features

- **Curriculum Upload & Analysis**: Parse PDFs, DOCX, and text files to extract topics
- **AI-Powered Recommendations**: Use embeddings and LLM for intelligent resource suggestions
- **Smart Chat Interface**: AI advisor helps refine recommendations in real-time
- **Semantic Search**: Find similar resources using embeddings
- **User Preferences**: Track and personalize recommendations per user

## Architecture

```
backend/
├── main.py                 # FastAPI app entry point
├── routers/
│   ├── curriculum.py      # Upload & parse endpoints
│   ├── recommendations.py # Resource recommendation endpoints
│   └── chat.py            # AI advisor conversation endpoints
├── services/
│   ├── parser.py          # LLM curriculum parsing logic
│   ├── recommender.py     # ML recommendation engine
│   └── embeddings.py      # Vector embedding service
├── models/
│   └── schemas.py         # Pydantic request/response models
└── db/
    └── supabase.py        # Supabase client & database ops
```

## Setup

### 1. Prerequisites

- Python 3.9+
- [Supabase Project](https://supabase.com/)
- [Anthropic API Key](https://console.anthropic.com/) (for Claude)

### 2. Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

### 3. Configure Environment

Create a `.env` file in the `backend/` directory:

```env
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key

# AI Services
ANTHROPIC_API_KEY=your-claude-api-key

# Server
PORT=8000
```

### 4. Database Setup (Supabase)

Create the following tables in your Supabase project:

**users** table:
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  preferences JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**curriculums** table:
```sql
CREATE TABLE curriculums (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  file_name TEXT NOT NULL,
  topics JSONB NOT NULL,
  summary TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**resources** table:
```sql
CREATE TABLE resources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  type TEXT NOT NULL, -- 'video', 'article', 'exercise', 'book', 'course'
  topic TEXT NOT NULL,
  summary TEXT,
  url TEXT,
  difficulty TEXT,
  duration_minutes INTEGER,
  embedding VECTOR(384),
  metadata JSONB,
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create index for vector search
CREATE INDEX ON resources USING ivfflat (embedding vector_cosine_ops);
```

**recommendations** table:
```sql
CREATE TABLE recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id),
  resource_id UUID REFERENCES resources(id),
  relevance_score FLOAT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

**embeddings** table:
```sql
CREATE TABLE embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  text_id TEXT UNIQUE NOT NULL,
  text_type TEXT NOT NULL, -- 'topic', 'resource', 'query'
  embedding VECTOR(384) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### 5. Run the Server

```bash
python main.py
# or
uvicorn main:app --reload
```

The API will be available at `http://localhost:8000`

## API Endpoints

### Curriculum Management

- **POST** `/api/curriculum/upload` - Upload and parse a curriculum file
- **GET** `/api/curriculum/list/{user_id}` - List user's curriculums
- **GET** `/api/curriculum/{curriculum_id}` - Get curriculum details

### Recommendations

- **POST** `/api/recommendations/get` - Get personalized recommendations
- **GET** `/api/recommendations/user/{user_id}` - Get user's saved recommendations
- **GET** `/api/recommendations/similar/{resource_id}` - Find similar resources
- **POST** `/api/recommendations/rerank` - Rerank resources using LLM

### Chat

- **POST** `/api/chat/message` - Send message to AI advisor
- **POST** `/api/chat/session` - Create new chat session
- **GET** `/api/chat/history/{session_id}` - Get chat history

## Example Usage

### Upload Curriculum

```bash
curl -X POST "http://localhost:8000/api/curriculum/upload?user_id=user123" \
  -F "file=@syllabus.pdf"
```

### Get Recommendations

```bash
curl -X POST "http://localhost:8000/api/recommendations/get" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "curriculum_id": "curr456",
    "topic": "Linear Algebra",
    "limit": 10
  }'
```

### Chat with AI Advisor

```bash
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{
    "user_id": "user123",
    "user_message": "I already know basic linear algebra, can you recommend advanced resources?",
    "conversation_history": []
  }'
```

## API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## Services

### Parser Service
- Extracts topics from curriculum documents (PDF, DOCX, TXT)
- Uses Claude to identify topics, subtopics, and difficulty levels
- Generates curriculum summaries

### Embedding Service
- Generates vector embeddings using sentence-transformers
- Supports semantic similarity search
- Batch embedding operations

### Recommender Service
- Finds recommendations using semantic similarity
- Combines embeddings with metadata filtering
- Reranks results using Claude for improved relevance

## Environment Variables

| Variable | Required | Description |
|----------|----------|-------------|
| `SUPABASE_URL` | Yes | Your Supabase project URL |
| `SUPABASE_KEY` | Yes | Supabase anon/public key |
| `ANTHROPIC_API_KEY` | Yes | Claude API key |
| `PORT` | No | Server port (default: 8000) |

## Development

### Run with auto-reload

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### Run tests (when added)

```bash
pytest
```

## Troubleshooting

### ModuleNotFoundError

Make sure your working directory is the `backend/` folder when running:
```bash
cd backend
python main.py
```

### Supabase Connection Issues

1. Verify `SUPABASE_URL` and `SUPABASE_KEY` in `.env`
2. Check your Supabase project is active
3. Ensure your API key has the correct permissions

### API Key Issues

- Verify your `ANTHROPIC_API_KEY` is valid
- Check API key quotas and usage limits
- Ensure keys are not accidentally committed to git

## License

Proprietary - StudyBridge Platform

## Support

For issues and questions, please refer to the documentation or contact the development team.
