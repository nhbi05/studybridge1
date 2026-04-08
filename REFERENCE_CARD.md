# StudyBridge - Integration Reference Card

## 📊 Database Schema at a Glance

```sql
┌─────────────────────────────────────────────────────────┐
│                      SUPABASE DATABASE                  │
│                   (PostgreSQL + pgvector)               │
└─────────────────────────────────────────────────────────┘

┌──────────────────┐          ┌──────────────────┐
│     USERS        │          │  CURRICULUMS     │
├──────────────────┤          ├──────────────────┤
│ id (UUID, PK)    │◄─────────├─ user_id (FK)    │
│ email (UNIQUE)   │  1 to *  │ file_name        │
│ name             │          │ topics (JSONB)   │
│ preferences      │          │ summary          │
│ created_at       │          │ created_at       │
└──────────────────┘          └──────────────────┘
        ▲                             ▲
        │                             │
        │                 (user uploads)
        │
        └─────────────┬──────────────────────────┐
                      │                          │
        ┌─────────────▼──┐        ┌──────────────▼──┐
        │ RECOMMENDATIONS│        │  CHAT_MESSAGES  │
        ├────────────────┤        ├─────────────────┤
        │ user_id (FK)   │        │ user_id (FK)    │
        │ resource_id    │────┐   │ session_id      │
        │ relevance_score│    │   │ role            │
        │ created_at     │    │   │ content         │
        └────────────────┘    │   │ filters_applied │
                              │   │ created_at      │
                              │   └─────────────────┘
                              │
                    ┌─────────▼────────────┐
                    │    RESOURCES         │
                    ├──────────────────────┤
                    │ id (UUID, PK)        │
                    │ title                │
                    │ type                 │
                    │ topic                │
                    │ summary              │
                    │ difficulty           │
                    │ embedding (VECTOR)◄──┼───────┐
                    │ metadata (JSONB)     │       │
                    │ created_at           │       │
                    └──────────────────────┘       │
                                                   │
                    ┌──────────────────────┐       │
                    │    EMBEDDINGS        │       │
                    ├──────────────────────┤       │
                    │ text_id (UNIQUE)     │       │
                    │ text_type            │       │
                    │ embedding (VECTOR)───┼◄──────┘
                    │ created_at           │
                    └──────────────────────┘

INDEXES:
- users: email
- curriculums: user_id, created_at
- resources: topic, type, difficulty, embedding (ivfflat)
- recommendations: user_id, relevance_score DESC
- chat_messages: session_id, created_at DESC
- embeddings: text_id
```

---

## 🔄 Data Flow: End-to-End

```
USER WORKFLOW
═════════════════════════════════════════════════════════

1. CURRICULUM UPLOAD
   ┌─────────────┐
   │ User opens  │
   │ frontend    │
   └──────┬──────┘
          │
   ┌──────▼──────────────────────┐
   │ Drag & drop PDF/DOCX file   │
   └──────┬──────────────────────┘
          │
   ┌──────▼──────────────────────────────┐
   │ Frontend calls:                      │
   │ api.curriculum.upload(userId, file) │
   └──────┬──────────────────────────────┘
          │
   ┌──────▼──────────────────────────────┐
   │ POST /api/curriculum/upload         │
   │ Content-Type: multipart/form-data   │
   └──────┬──────────────────────────────┘
          │
   ┌──────▼──────────────────────────────────┐
   │ Backend (curriculum.py):                │
   │ 1. Parse PDF/DOCX → extract text       │
   │ 2. Call Claude API → extract topics    │
   │ 3. Generate summary                    │
   │ 4. Save to DB (curriculums table)      │
   └──────┬──────────────────────────────────┘
          │
   ┌──────▼──────────────────────────────┐
   │ Database stores:                     │
   │ - curriculum_id                      │
   │ - topics (JSONB array)               │
   │ - summary                            │
   │ - file_name                          │
   └──────┬──────────────────────────────┘
          │
   ┌──────▼──────────────────────────────────┐
   │ Frontend receives response:             │
   │ {                                       │
   │   "curriculum_id": "uuid",              │
   │   "total_topics": 12,                   │
   │   "topics_extracted": [...]             │
   │   "summary": "..."                      │
   │ }                                       │
   └──────┬──────────────────────────────────┘
          │
   ┌──────▼──────────────────────┐
   │ Display success message    │
   │ "Topics extracted!"        │
   └────────────────────────────┘

2. GET RECOMMENDATIONS
   ┌─────────────────────────────┐
   │ Show recommendations page   │
   └──────┬──────────────────────┘
          │
   ┌──────▼──────────────────────────────────┐
   │ Frontend calls:                         │
   │ api.recommendations.get({               │
   │   user_id: "user-123",                  │
   │   topic: "Mathematics",                 │
   │   limit: 10                             │
   │ })                                      │
   └──────┬──────────────────────────────────┘
          │
   ┌──────▼──────────────────────────────┐
   │ POST /api/recommendations/get       │
   │ Content-Type: application/json      │
   └──────┬──────────────────────────────┘
          │
   ┌──────▼──────────────────────────────────────────┐
   │ Backend (recommender.py):                       │
   │ 1. Get all resources from DB                    │
   │ 2. For each, calculate similarity:              │
   │    - Convert topic to embedding                 │
   │    - Compare with resource embedding           │
   │    - Calculate cosine similarity                │
   │ 3. Filter by difficulty/type                    │
   │ 4. Sort by relevance score                      │
   │ 5. Save recommendations to recommendations table│
   │ 6. Return top-10                                │
   └──────┬──────────────────────────────────────────┘
          │
   ┌──────▼──────────────────────────────┐
   │ Database queries:                    │
   │ - SELECT * FROM resources            │
   │ - WHERE topic = 'Mathematics'        │
   │ - INSERT INTO recommendations        │
   └──────┬──────────────────────────────┘
          │
   ┌──────▼──────────────────────────────────────┐
   │ Frontend receives response:                 │
   │ {                                           │
   │   "recommendations": [                      │
   │     {                                       │
   │       "title": "Linear Algebra",            │
   │       "type": "video",                      │
   │       "relevance_score": 0.95               │
   │     }                                       │
   │   ],                                        │
   │   "total_results": 8                        │
   │ }                                           │
   └──────┬──────────────────────────────────────┘
          │
   ┌──────▼──────────────────┐
   │ Display resource cards  │
   │ with relevance scores   │
   └────────────────────────┘

3. CHAT WITH AI ADVISOR
   ┌────────────────────────────────────────┐
   │ User types in chat: "I want harder"    │
   └──────┬─────────────────────────────────┘
          │
   ┌──────▼──────────────────────────────────┐
   │ Frontend calls:                         │
   │ api.chat.sendMessage({                  │
   │   user_id: "user-123",                  │
   │   user_message: "I want harder",        │
   │   conversation_history: [...]           │
   │ })                                      │
   └──────┬──────────────────────────────────┘
          │
   ┌──────▼──────────────────────────────────┐
   │ POST /api/chat/message                  │
   │ Content-Type: application/json          │
   └──────┬──────────────────────────────────┘
          │
   ┌──────▼──────────────────────────────────────┐
   │ Backend (chat.py):                          │
   │ 1. Prepare conversation history             │
   │ 2. Call Claude API with system prompt       │
   │ 3. Parse response for intent ("harder")     │
   │ 4. Generate filter recommendations          │
   │ 5. Return response + filters                │
   └──────┬──────────────────────────────────────┘
          │
   ┌──────▼──────────────────────────────────────┐
   │ Claude API returns message:                 │
   │ "Since you want harder resources, I've      │
   │  updated your filters to advanced level..."│
   └──────┬──────────────────────────────────────┘
          │
   ┌──────▼──────────────────────────────────────┐
   │ Frontend receives response:                 │
   │ {                                           │
   │   "assistant_message": "...",               │
   │   "updated_filters": {                      │
   │     "difficulty": "advanced"                │
   │   }                                         │
   │ }                                           │
   └──────┬──────────────────────────────────────┘
          │
   ┌──────▼──────────────────────────┐
   │ Display message                 │
   │ Auto-refetch recommendations    │
   │ with new filters                │
   └────────────────────────────────┘
```

---

## 🌍 Network Architecture

```
┌─────────────────────────────────────┐
│         USER'S BROWSER              │
│  http://localhost:3000              │
│  ┌──────────────────────────────┐  │
│  │      Next.js Frontend         │  │
│  │  - Dashboard (page.tsx)       │  │
│  │  - Curriculum Upload          │  │
│  │  - Chat Interface             │  │
│  │  - Recommendations            │  │
│  │  - API Client (lib/api.ts)    │  │
│  └──────────────────────────────┘  │
└────────────┬────────────────────────┘
             │ HTTP Requests
             │ JSON payloads
             │
   ┌─────────▼──────────────────────────┐
   │   FASTAPI BACKEND SERVER           │
   │   http://localhost:8000            │
   │  ┌────────────────────────────┐   │
   │  │  API Routes                │   │
   │  │  /api/curriculum/upload    │   │
   │  │  /api/recommendations/get  │   │
   │  │  /api/chat/message         │   │
   │  └────────────┬───────────────┘   │
   │               │                   │
   │  ┌────────────▼───────────────┐   │
   │  │  Services                  │   │
   │  │  - parser.py               │   │
   │  │  - recommender.py          │   │
   │  │  - embeddings.py           │   │
   │  └────────────┬───────────────┘   │
   │               │                   │
   │     ┌─────────┴──────────┐        │
   │     │                    │        │
   │  ┌──▼──┐           ┌─────▼────┐ │
   │  │Claude├──────────►Supabase   │ │
   │  │API   │ embedding Postgres   │ │
   │  │(LLM) │ requests client      │ │
   │  └──────┘           └──────────┘ │
   │                                   │
   └─────────────────────────────────────┘
             │ API Calls
             │ SQL Queries
             │
   ┌─────────▼──────────────────────────┐
   │     SUPABASE CLOUD (Remote)        │
   │  https://your-project.supabase.co  │
   │                                    │
   │  ┌──────────────────────────────┐ │
   │  │   PostgreSQL Database        │ │
   │  │  - users                     │ │
   │  │  - curriculums               │ │
   │  │  - resources                 │ │
   │  │  - recommendations           │ │
   │  │  - embeddings (VECTOR)       │ │
   │  │  - chat_sessions/messages    │ │
   │  └──────────────────────────────┘ │
   │                                    │
   └────────────────────────────────────┘
```

---

## 📦 Request/Response Examples

### Example 1: Upload Curriculum

**Request:**
```
POST /api/curriculum/upload?user_id=user-123
Content-Type: multipart/form-data

[binary PDF file]
```

**Response (200):**
```json
{
  "curriculum_id": "123e4567-e89b-12d3-a456-426614174000",
  "user_id": "user-123",
  "file_name": "Calculus_Syllabus.pdf",
  "topics_extracted": [
    {
      "name": "Limits and Continuity",
      "description": "Fundamental concepts...",
      "subtopics": ["One-sided limits", "Continuous functions"],
      "difficulty_level": "beginner"
    }
  ],
  "total_topics": 8,
  "summary": "Comprehensive calculus course..."
}
```

### Example 2: Get Recommendations

**Request:**
```json
POST /api/recommendations/get
{
  "user_id": "user-123",
  "topic": "Linear Algebra",
  "difficulty": "intermediate",
  "limit": 5
}
```

**Response (200):**
```json
{
  "recommendations": [
    {
      "id": "resource-456",
      "title": "Linear Algebra Fundamentals",
      "type": "video",
      "topic": "Linear Algebra",
      "relevance_score": 0.95,
      "summary": "Comprehensive introduction to vectors and matrices...",
      "metadata": {
        "url": "https://example.com/video",
        "duration_minutes": 120,
        "difficulty": "intermediate"
      }
    }
  ],
  "query_topic": "Linear Algebra",
  "total_results": 7,
  "timestamp": "2024-04-07T12:34:56Z"
}
```

### Example 3: Chat Message

**Request:**
```json
POST /api/chat/message
{
  "user_id": "user-123",
  "user_message": "I already know basic linear algebra, give me advanced content",
  "conversation_history": [
    {"role": "assistant", "content": "Hi! How can I help?"}
  ]
}
```

**Response (200):**
```json
{
  "assistant_message": "Great! Since you have a solid foundation in linear algebra, I'd recommend advanced topics like eigenvalues, matrix decomposition, and applications to machine learning.",
  "confidence_score": 0.92,
  "updated_filters": {
    "difficulty": "advanced",
    "resource_types": ["research_paper", "advanced_course"]
  },
  "suggested_resources": ["resource-789", "resource-790"]
}
```

---

## 🔗 Connection Points

### Frontend → Backend
```typescript
// lib/api.ts
const API_BASE_URL = 'http://localhost:8000'

// When user uploads:
await fetch(`${API_BASE_URL}/api/curriculum/upload?user_id=...`, {
  method: 'POST',
  body: formData
})

// When getting recommendations:
await fetch(`${API_BASE_URL}/api/recommendations/get`, {
  method: 'POST',
  body: JSON.stringify(request)
})
```

### Backend → Database
```python
# db/supabase.py
async def save_curriculum(user_id, file_name, topics, summary):
    data = {...}
    response = self.client.table("curriculums").insert(data).execute()
    return response.data
```

### Backend → Claude API
```python
# services/parser.py
from anthropic import Anthropic

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[{"role": "user", "content": prompt}]
)
topics = json.loads(message.content[0].text)
```

### Database → Vector Search
```python
# services/embeddings.py
similarities = batch_similarities(query_emb, doc_embeddings)
# Powered by pgvector in Supabase
```

---

## ✅ Quick Checklist

- [ ] Supabase project created
- [ ] SUPABASE_SCHEMA.sql executed
- [ ] backend/.env configured
- [ ] frontend/.env.local configured
- [ ] `pip install -r requirements.txt`
- [ ] `npm install` (if needed)
- [ ] Backend running on 8000
- [ ] Frontend running on 3000
- [ ] Can upload curriculum
- [ ] Can see recommendations
- [ ] Chat responds to messages

---

**Ready to rock! 🚀**
