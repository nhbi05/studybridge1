# StudyBridge Backend - Quick Start Guide

## STEP 1: Install Dependencies

```bash
cd backend
pip install -r requirements.txt
```

## STEP 2: Set Up Supabase

1. Create a project at https://supabase.com
2. Go to SQL Editor and run these commands:

### Create users table
```sql
CREATE TABLE users (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  email TEXT UNIQUE NOT NULL,
  name TEXT,
  preferences JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Create curriculums table
```sql
CREATE TABLE curriculums (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  file_name TEXT NOT NULL,
  topics JSONB NOT NULL,
  summary TEXT,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Create resources table
```sql
CREATE TABLE resources (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  title TEXT NOT NULL,
  type TEXT NOT NULL,
  topic TEXT NOT NULL,
  summary TEXT,
  url TEXT,
  difficulty TEXT,
  duration_minutes INTEGER,
  embedding VECTOR(384),
  metadata JSONB DEFAULT '{}',
  created_at TIMESTAMP DEFAULT NOW()
);

-- Create vector index for semantic search
CREATE INDEX ON resources USING ivfflat (embedding vector_cosine_ops);
```

### Create recommendations table
```sql
CREATE TABLE recommendations (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  user_id UUID REFERENCES users(id) ON DELETE CASCADE,
  resource_id UUID REFERENCES resources(id) ON DELETE CASCADE,
  relevance_score FLOAT NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

### Create embeddings table
```sql
CREATE TABLE embeddings (
  id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  text_id TEXT UNIQUE NOT NULL,
  text_type TEXT NOT NULL,
  embedding VECTOR(384) NOT NULL,
  created_at TIMESTAMP DEFAULT NOW()
);
```

## STEP 3: Get API Keys

### Supabase Keys:
- Go to Settings → API in your Supabase project
- Copy: Project URL, anon/public key

### Anthropic API Key:
- Visit https://console.anthropic.com/
- Create API key in account settings

## STEP 4: Create .env File

Create `backend/.env`:

```env
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key-here
ANTHROPIC_API_KEY=your-claude-key-here
PORT=8000
```

## STEP 5: Run the Server

```bash
python main.py
```

The API will start at `http://localhost:8000`

Open `http://localhost:8000/docs` for interactive API documentation

## STEP 6: Test Endpoints

### Health check
```bash
curl http://localhost:8000/health
```

### Upload curriculum
```bash
curl -X POST "http://localhost:8000/api/curriculum/upload?user_id=test-user" \
  -F "file=@your-syllabus.pdf"
```

### Get recommendations
```bash
curl -X POST "http://localhost:8000/api/recommendations/get" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test-user","topic":"Mathematics","limit":5}'
```

### Chat with AI
```bash
curl -X POST "http://localhost:8000/api/chat/message" \
  -H "Content-Type: application/json" \
  -d '{"user_id":"test-user","user_message":"I want harder resources"}'
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError` | cd into `backend/` folder before running |
| Supabase connection error | Check `SUPABASE_URL` and `SUPABASE_KEY` |
| API key error | Verify `ANTHROPIC_API_KEY` is valid and has quota |
| CORS error | Frontend should be at localhost:3000 or 3001 |
| Vector search error | Enable pgvector extension in Supabase SQL Editor |

## Next Steps

1. Connect frontend at localhost:3000 to this API
2. Add test resources to resources table
3. Populate sample curriculums
4. Monitor API logs in terminal
5. Check Supabase dashboard for data
