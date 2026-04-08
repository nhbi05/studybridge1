# 🚀 StudyBridge Full Stack - Complete Setup Guide

## Overview

StudyBridge is a complete AI-powered learning platform with:
- **Frontend**: Next.js + Tailwind CSS (http://localhost:3000)
- **Backend**: FastAPI + Claude AI (http://localhost:8000)
- **Database**: Supabase + PostgreSQL (cloud)

---

## Prerequisites

- **Node.js** 18+ (for frontend)
- **Python** 3.9+ (for backend)
- **Supabase Account** (https://supabase.com - free tier works)
- **Anthropic API Key** (https://console.anthropic.com)

---

## Quick Start (5 minutes)

### 1️⃣ Supabase Setup

1. Go to https://supabase.com and create account
2. Create new project (name: "studybridge")
3. Go to SQL Editor
4. Copy entire script from `SUPABASE_SCHEMA.sql`
5. Paste and execute
6. Go to Settings → API:
   - Copy `Project URL` → save as `SUPABASE_URL`
   - Copy `anon/public key` → save as `SUPABASE_KEY`

### 2️⃣ Backend Configuration

```bash
cd backend

# Create .env file
cat > .env << EOF
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_KEY=your-anon-key
ANTHROPIC_API_KEY=sk-ant-xxxxx
PORT=8000
EOF

# Install & run
pip install -r requirements.txt
python main.py
```

**Expected output:**
```
🚀 StudyBridge Backend Starting...
✓ Initializing AI services...
Uvicorn running on http://0.0.0.0:8000
```

### 3️⃣ Frontend Configuration

```bash
cd frontend

# Create .env.local
cat > .env.local << EOF
NEXT_PUBLIC_API_URL=http://localhost:8000
EOF

# Install & run
npm install  # if not already installed
npm run dev
```

**Expected output:**
```
▲ Next.js 16.2.2 (Turbopack)

  - Local:        http://localhost:3000
  - Network:      http://...
✓ Ready in 856ms
```

### 4️⃣ Test Everything

1. Open http://localhost:3000
2. Upload a curriculum (PDF/TXT)
3. See recommendations appear
4. Chat with AI advisor

---

## Full Setup Breakdown

### Backend - What's Running

**Port:** 8000
**Process:** FastAPI + Uvicorn

**API Endpoints:**
- `POST /api/curriculum/upload` - Upload curriculum
- `GET /api/curriculum/list/{user_id}` - List curriculums
- `POST /api/recommendations/get` - Get recommendations
- `POST /api/chat/message` - Chat with AI
- `GET /docs` - Interactive API documentation

**Services:**
- **parser.py** - Parses PDFs, extracts topics with Claude
- **recommender.py** - ML-based recommendations with embeddings
- **embeddings.py** - Vector similarity search
- **supabase.py** - Database client

**External APIs:**
- Supabase PostgreSQL (vector search with pgvector)
- Anthropic Claude 3.5 Sonnet

### Frontend - What's Running

**Port:** 3000
**Process:** Next.js dev server with Turbopack

**Pages:**
- `/` - Dashboard with recommendations
- `/curriculum` - Upload curriculum
- `/recommendations` - Browse all recommendations
- `/progress` - See your learning progress
- `/settings` - User preferences

**API Client:**
- `lib/api.ts` - Centralized API calls to backend

**Components:**
- `Sidebar` - Navigation
- `CurriculumUpload` - File upload with API integration
- `ChatInterface` - Real-time chat
- `ResourceCard` - Display resources
- `MetricCard` - Learning metrics

### Database - What's Stored

**Tables:**
1. **users** - User profiles
2. **curriculums** - Uploaded syllabi
3. **resources** - Learning materials (with embeddings)
4. **recommendations** - User-resource pairs with scores
5. **embeddings** - Vector cache
6. **chat_sessions** - Conversation sessions
7. **chat_messages** - Individual messages

**Features:**
- Vector search on resource embeddings
- Automatic timestamps
- Referential integrity with CASCADE delete
- Indexes for fast queries

---

## File Structure

```
studybridge1/
├── backend/
│   ├── main.py (FastAPI app)
│   ├── requirements.txt
│   ├── .env (YOUR API KEYS)
│   ├── routers/
│   │   ├── curriculum.py
│   │   ├── recommendations.py
│   │   └── chat.py
│   ├── services/
│   │   ├── parser.py (Claude)
│   │   ├── recommender.py (ML)
│   │   └── embeddings.py (Vectors)
│   ├── models/
│   │   └── schemas.py (Pydantic)
│   ├── db/
│   │   └── supabase.py (Database)
│   └── README.md
│
├── frontend/
│   ├── app/
│   │   ├── page.tsx (Dashboard)
│   │   ├── layout.tsx
│   │   ├── components/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── ChatInterface.tsx
│   │   │   ├── CurriculumUpload.tsx
│   │   │   ├── ResourceCard.tsx
│   │   │   └── MetricCard.tsx
│   │   ├── curriculum/
│   │   ├── recommendations/
│   │   ├── progress/
│   │   └── settings/
│   ├── lib/
│   │   └── api.ts (API CLIENT)
│   ├── .env.local (NEXT_PUBLIC_API_URL)
│   ├── next.config.ts
│   └── package.json
│
├── SUPABASE_SCHEMA.sql (DATABASE SETUP)
├── INTEGRATION_GUIDE.md (YOU ARE HERE)
├── start.sh (Linux/Mac startup)
└── start.bat (Windows startup)
```

---

## Environment Variables

### Backend (backend/.env)

```env
# Supabase Database
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIs...

# AI Services
ANTHROPIC_API_KEY=sk-ant-abc123xyz...

# Server
PORT=8000
```

### Frontend (frontend/.env.local)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
```

---

## Troubleshooting

### Backend Issues

| Error | Solution |
|-------|----------|
| `ModuleNotFoundError: No module named 'fastapi'` | Run `pip install -r requirements.txt` |
| `SUPABASE_URL and SUPABASE_KEY required` | Check `.env` file exists with valid keys |
| `Port 8000 already in use` | Kill process: `lsof -ti:8000 \| xargs kill -9` |
| `Anthropic API error` | Check `ANTHROPIC_API_KEY` is valid |
| `pgvector not available` | Supabase schema not run - execute SQL in Supabase UI |

### Frontend Issues

| Error | Solution |
|-------|----------|
| `Cannot find module '@/lib/api'` | Path alias issue - check `tsconfig.json` |
| `NEXT_PUBLIC_API_URL is undefined` | Create `.env.local` with API URL |
| `API call returns 404` | Ensure backend is running on 8000 |
| `CORS error` | Backend has CORS enabled - check browser console |

### Integration Issues

| Problem | Fix |
|---------|-----|
| Upload returns 500 | Backend Claude API key invalid or rate limited |
| Recommendations empty | No sample resources in Supabase (add from SQL) |
| Chat not responding | Backend connection issue or ANTHROPIC_API_KEY invalid |
| Database connection fails | SUPABASE_URL/KEY mismatch or wrong permissions |

---

## Testing the Integration

### Test Backend

```bash
# Health check
curl http://localhost:8000/health

# Get API docs
open http://localhost:8000/docs
```

### Test Frontend

```bash
# Check if running
curl http://localhost:3000

# Dev console shows API calls
# Open browser DevTools → Network tab
```

### Test Database

In Supabase Dashboard:
1. Go to SQL Editor
2. Run: `SELECT COUNT(*) FROM users;`
3. Should return count or 0

---

## Adding Sample Data

### Insert Sample Resources

In Supabase SQL Editor:

```sql
INSERT INTO resources (title, type, topic, summary, difficulty, duration_minutes)
VALUES 
  ('Linear Algebra Basics', 'video', 'Mathematics', 'Introduction to matrices and vectors', 'beginner', 120),
  ('Advanced Python', 'course', 'Computer Science', 'Master Python for data science', 'advanced', 480),
  ('Web Dev Fundamentals', 'article', 'Web Development', 'HTML, CSS, JavaScript basics', 'beginner', NULL)
ON CONFLICT DO NOTHING;
```

### View Uploaded Data

```sql
SELECT * FROM curriculums LIMIT 5;
SELECT * FROM recommendations LIMIT 10;
SELECT * FROM embeddings LIMIT 5;
```

---

## Production Deployment

When ready to deploy:

1. **Backend** → Deploy to Render, Railway, or Heroku
2. **Frontend** → Deploy to Vercel, Netlify
3. **Database** → Already on Supabase (hosted)

Update environment variables:
- Backend: `NEXT_PUBLIC_API_URL=https://your-api.herokuapp.com`
- Frontend: Update API URL in deployment settings

---

## Performance Tips

- Backend uses async/await for non-blocking I/O
- Frontend uses React hooks for efficient rendering
- Embeddings cached in database for faster search
- CORS enabled locally, disable sensitive origins in production
- Rate limiting recommended for production

---

## Security Checklist

Before production:

- [ ] Hide API keys in environment variables
- [ ] Enable Supabase RLS (Row Level Security)
- [ ] Add authentication/JWT tokens
- [ ] Rate limit API endpoints
- [ ] Validate file uploads (size, type)
- [ ] Sanitize user inputs
- [ ] Enable CORS only for your domain
- [ ] Use HTTPS (automatic on Vercel/Render)
- [ ] Monitor API usage and costs
- [ ] Regular database backups

---

## Support & Documentation

- **Backend README**: `backend/README.md`
- **API Spec**: `backend/API_SPECIFICATION.md`
- **Quick Start**: `backend/QUICKSTART.md`
- **Integration Guide**: `INTEGRATION_GUIDE.md`
- **Database Schema**: `SUPABASE_SCHEMA.sql`

---

## Next Steps

1. ✅ Set up Supabase project
2. ✅ Configure backend .env
3. ✅ Configure frontend .env.local
4. ✅ Run both servers
5. ✅ Test with sample data
6. Add authentication
7. Deploy to production
8. Monitor and optimize

---

## Quick Commands

```bash
# Start everything (from root)
# Windows:
start.bat

# macOS/Linux:
./start.sh

# Individual start:
# Backend
cd backend && python main.py

# Frontend
cd frontend && npm run dev

# Stop backend (Ctrl+C in terminal)
# Stop frontend (Ctrl+C in terminal)
```

---

## Key Features Working

✅ Upload curriculum (PDF/DOCX/TXT)
✅ Parse with Claude AI
✅ Extract topics automatically
✅ Get AI recommendations
✅ Semantic search with embeddings
✅ Chat with AI advisor
✅ Real-time API integration
✅ Responsive design

---

**You're all set! Happy learning! 🎓**
