# StudyBridge API Topic Retrieval - Complete Implementation Guide

## Overview
The backend API is now fully set up to fetch and return topics from extracted curriculums. This guide explains the complete flow and what needs to be done.

## Implementation Status

### ✅ COMPLETED

**1. Database Schema Updated**
- Added `description` column to `curriculum_topics` table
- Added `subtopics` column (JSONB) to `curriculum_topics` table  
- Added `difficulty_level` column to `curriculum_topics` table
- Updated `SUPABASE_SCHEMA.sql` with all changes

**2. Backend Methods Fixed**
- `supabase.py::get_curriculum()` - Now returns topics in `topics_extracted` format
- `supabase.py::get_user_curriculums()` - Already returns topics in `topics_extracted` format
- `supabase.py::get_curriculum_topics()` - Fetches raw topics for backend operations

**3. API Endpoints Ready**
- `POST /api/curriculum/upload` - Extracts topics + saves with metadata + returns topics immediately
- `GET /api/curriculum/list` - Lists all curriculums with associated topics
- `GET /api/curriculum/{curriculum_id}` - Gets specific curriculum with all topics

**4. Frontend Components Ready**
- View Topics modal - Displays topic name, description, subtopics, difficulty level
- Re-analyze button - Ready to re-extract topics
- API client - Configured to call backend endpoints

---

## Required Next Steps

### Step 1: Apply Database Migration ⚠️ CRITICAL

The migration MUST be applied before uploading new curriculums. Old data will work fine, but new uploads need the schema.

**Location**: See `MIGRATION_GUIDE.md` for step-by-step instructions

**Quick SQL**:
```sql
ALTER TABLE curriculum_topics
ADD COLUMN IF NOT EXISTS description TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS subtopics JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS difficulty_level TEXT DEFAULT 'intermediate' CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced'));

CREATE INDEX IF NOT EXISTS idx_curriculum_topics_difficulty_level ON curriculum_topics(difficulty_level);
```

### Step 2: Test the Complete Flow

After migration, test this sequence:

1. **Start backend & frontend**:
   ```bash
   # Terminal 1: Backend
   cd backend
   python main.py

   # Terminal 2: Frontend
   cd frontend  
   npm run dev
   ```

2. **Login to frontend** at `http://localhost:3000`

3. **Upload a curriculum** at `/curriculum` page
   - Select any PDF, DOCX, or TXT file
   - Backend will extract topics automatically

4. **View extracted topics**
   - Click "View Topics" button
   - Should show complete topic details (name, description, subtopics, difficulty)

5. **Test get endpoints**
   - Frontend automatically calls them to populate the curriculum list
   - Each curriculum shows "X topics extracted"

### Step 3: Verify API Response Format

The API now returns responses like this:

**GET /api/curriculum/list Response**:
```json
{
  "curriculums": [
    {
      "id": "uuid...",
      "user_id": "uuid...",
      "file_name": "Math101.pdf",
      "file_url": "https://...",
      "summary": "Curriculum containing 8 core topics...",
      "topics_extracted": [
        {
          "id": "uuid...",
          "name": "Calculus",
          "description": "Study of rates of change...",
          "subtopics": ["Derivatives", "Integrals"],
          "difficulty_level": "intermediate"
        },
        ...
      ],
      "total_topics": 8,
      "created_at": "2024-01-15T..."
    }
  ],
  "total": 1
}
```

**GET /api/curriculum/{id} Response**:
Same structure as individual curriculum from list

---

## Architecture Diagram

```
Frontend (Next.js)
    ↓ api.curriculum.list()
    ↓ api.curriculum.get(id)
    ↓
Backend API (FastAPI)
    ↓ curriculum.py routes
    ↓
Supabase Client (supabase.py)
    ↓ get_user_curriculums()
    ↓ get_curriculum()
    ↓
Supabase PostgreSQL
    ↓
curriculum_topics table
(with description, subtopics, difficulty_level)
```

---

## Data Flow: Upload → Extract → Display

### 1. Upload Phase
```
User uploads file
  → POST /api/curriculum/upload
  → parser.extract_topics_from_file() [Gemini multimodal]
  → parser.embed_topics() [S-BERT]
  → supabase.save_curriculum() [saves metadata]
  → supabase.save_curriculum_topics() [saves topics with embeddings]
  → Returns CurriculumAnalysisResponse with topics_extracted
```

### 2. Retrieval Phase  
```
User views curriculum list
  → GET /api/curriculum/list
  → supabase.get_user_curriculums() [queries all curriculum + their topics]
  → Returns list with topics_extracted for each
  → Frontend displays in card list
```

### 3. Display Phase
```
User clicks "View Topics"
  → Frontend shows modal with topics from curriculum["topics_extracted"]
  → Displays: name, description, subtopics array, difficulty badge
  → User can see full extracted structure
```

---

## File Locations Reference

| Purpose | File | Key Method/Endpoint |
|---------|------|-------------------|
| Database setup | `SUPABASE_SCHEMA.sql` | curriculum_topics table |
| Migration guide | `MIGRATION_GUIDE.md` | SQL commands to run |
| Migration SQL | `MIGRATION_ADD_TOPIC_METADATA.sql` | Quick reference |
| Backend routes | `backend/routers/curriculum.py` | POST /upload, GET /list, GET /{id} |
| Database service | `backend/db/supabase.py` | get_curriculum, get_user_curriculums |
| Response schema | `backend/models/schemas.py` | CurriculumAnalysisResponse, TopicExtraction |
| Frontend page | `frontend/app/curriculum/page.tsx` | View Topics modal |
| Frontend API | `frontend/lib/api.ts` | curriculum.list(), curriculum.get() |

---

## Troubleshooting

### Issue: "Column doesn't exist" error when uploading
**Cause**: Migration hasn't been applied yet  
**Solution**: Run the migration SQL in Supabase (see MIGRATION_GUIDE.md)

### Issue: Topics show as empty in View Topics modal
**Cause**: Old curriculums uploaded before schema update  
**Solution**: Upload a new curriculum after migration is applied

### Issue: "Vector serialization error" in API response
**Cause**: Trying to serialize embedding vectors in JSON  
**Solution**: Backend now excludes embeddings from response (already fixed)

### Issue: Difficulty level not showing
**Cause**: Topic extracted without difficulty (defaults to "intermediate")  
**Solution**: Gemini parser should extract difficulty; check parser output

---

## What Happens Next

Once Step 1 (Migration) is complete, the system is fully operational:
- ✅ Upload curriculums → extracts topics with metadata
- ✅ List curriculums → shows all topics
- ✅ View topics modal → displays all details
- ✅ Re-analyze button → can re-extract topics
- ✅ Resources linked → can find resources by topic

## Validation Checklist

- [ ] Applied migration SQL to Supabase
- [ ] Backend server running (`python main.py`)
- [ ] Frontend dev server running (`npm run dev`)
- [ ] Logged in to frontend
- [ ] Uploaded a test curriculum file
- [ ] View Topics modal shows complete topic data
- [ ] Total topics count matches count in modal
- [ ] Subtopics display as bulleted list
- [ ] Difficulty level shows correct badge

Once all checked, the API topic retrieval is complete! 🎉
