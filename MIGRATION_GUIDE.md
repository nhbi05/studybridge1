# Database Migration Guide - Add Topic Metadata to curriculum_topics

## Issue
The `curriculum_topics` table is missing columns for storing topic metadata:
- `description` - Topic description text
- `subtopics` - Array of subtopics (JSONB)  
- `difficulty_level` - beginner/intermediate/advanced

This prevents the backend from saving and retrieving topic details.

## Solution

### Step 1: Open Supabase SQL Editor
1. Go to https://app.supabase.com
2. Select your StudyBridge project
3. Navigate to **SQL Editor** in the left sidebar
4. Click **New Query**

### Step 2: Run the Migration
Copy and paste this SQL into the editor:

```sql
-- Add missing columns to curriculum_topics
ALTER TABLE curriculum_topics
ADD COLUMN IF NOT EXISTS description TEXT DEFAULT '',
ADD COLUMN IF NOT EXISTS subtopics JSONB DEFAULT '[]',
ADD COLUMN IF NOT EXISTS difficulty_level TEXT DEFAULT 'intermediate' CHECK (difficulty_level IN ('beginner', 'intermediate', 'advanced'));

-- Create index for difficulty filtering
CREATE INDEX IF NOT EXISTS idx_curriculum_topics_difficulty_level ON curriculum_topics(difficulty_level);
```

### Step 3: Execute the Query
- Click the **Run** button (or press `Ctrl+Enter`)
- You should see "Success" with the number of rows affected

### Step 4: Verify the Schema
To confirm the columns were added, run:

```sql
SELECT column_name, data_type FROM information_schema.columns 
WHERE table_name='curriculum_topics' 
ORDER BY ordinal_position;
```

You should see these columns:
- `id` (uuid)
- `curriculum_id` (uuid)
- `topic_name` (text)
- `description` (text) ← NEW
- `subtopics` (jsonb) ← NEW  
- `difficulty_level` (text) ← NEW
- `embedding` (vector)
- `created_at` (timestamp)

## After Migration

Once the migration is applied:
1. **Upload a new curriculum** - Topics will now be saved with metadata
2. **View Topics modal** - Will display all topic details (name, description, subtopics, difficulty)
3. **Re-analyze button** - Can now re-extract topics while preserving metadata
4. **API endpoints** - GET /list and GET /{curriculum_id} will return complete topic data

## Troubleshooting

**Issue: "Column already exists" error**
- This is safe to ignore - means the column was already added
- The `IF NOT EXISTS` prevents duplicates

**Issue: "Vector extension missing" error**
- The `vector` extension should already be enabled
- If not, run: `CREATE EXTENSION IF NOT EXISTS "vector";`

**Issue: Check constraint failed**
- Only `beginner`, `intermediate`, or `advanced` are valid difficulty levels
- The default is `intermediate` if not specified

## Related Files
- Backend implementation: `backend/db/supabase.py` (save_curriculum_topics method)
- API endpoint: `backend/routers/curriculum.py` (POST /upload, GET /list)
- Frontend display: `frontend/app/curriculum/page.tsx` (View Topics modal)
- Main schema: `SUPABASE_SCHEMA.sql` (updated with new columns)
