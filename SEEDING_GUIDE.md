# 🌱 StudyBridge Resource Seeding Guide

## Overview

The new `seed_resources.py` intelligently populates your Supabase resources table with real web resources that **match topics extracted from student curriculum uploads**.

Instead of hardcoded topics, it:
1. **Fetches actual curriculum topics** from your database
2. **Searches multiple sources** (YouTube, arXiv, curated)
3. **Generates S-BERT embeddings** for semantic similarity
4. **Saves to pgvector** for fast semantic search

## Why This Matters

**Before:** Hardcoded resources like "Mathematics", "Physics"
```python
TOPICS = ['Calculus', 'Linear Algebra', 'Data Structures']
```

**Now:** Dynamic resources from actual student curriculums
```
Student uploads: "CS101 - Intro to Programming"
  → Gemini extracts: "object-oriented programming", "data types", "loops"
  → Seeding searches for resources matching these EXACT topics
  → Semantic search finds relevant videos, papers, courses
```

## Setup (5 minutes)

### 1. Install Dependencies

```bash
cd backend
pip install sentence-transformers arxiv requests google-api-python-client
```

### 2. Set Environment Variables

Create or update `.env` in the `backend/` directory:

```bash
# Supabase credentials (use SERVICE account key, not public key!)
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_SERVICE_KEY=eyJhbGc...

# Optional: YouTube API key (for live video search)
YOUTUBE_API_KEY=AIzaSyDxx...
```

**Get YouTube API Key:**
1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → Enable "YouTube Data API v3"
3. Create API key in Credentials
4. Add to `.env`

**Get Supabase Keys:**
1. Go to your Supabase project Settings
2. Copy "URL" and "service_role key" (NOT anon key)
3. Add to `.env`

### 3. Verify Database Schema

Ensure your `resources` table has:
```sql
CREATE TABLE resources (
  id UUID PRIMARY KEY,
  title TEXT NOT NULL,
  description TEXT,
  url TEXT UNIQUE,
  type TEXT,  -- 'video', 'paper', 'course', 'interactive'
  topic TEXT,
  difficulty_level TEXT,  -- 'beginner', 'intermediate', 'advanced'
  embedding vector(384),  -- S-BERT embeddings
  created_at TIMESTAMP DEFAULT now()
);

CREATE INDEX resources_embedding_idx ON resources USING ivfflat (embedding vector_cosine_ops);
```

## Running the Seeder

### Quick Start

```bash
cd backend
python seed_resources.py
```

### Output Example

```
======================================================================
🌱 StudyBridge — Resource Seeding Pipeline
======================================================================

[1/4] Adding 12 curated fallback resources...
  ✓ Added curated resources

[2/4] Fetching topics from database...
📚 Found 23 topics in database

[3/4] Searching for resources across 23 topics...

  [1/23] Object Oriented Programming
  ✓ Found 3 YouTube videos for 'object oriented programming'
  ✓ Found 2 arXiv papers for 'object oriented programming'

  [2/23] Linear Algebra
  ✓ Found 3 YouTube videos for 'linear algebra'
  ✓ Found 2 arXiv papers for 'linear algebra'

[4/4] Deduplicating 127 resources...
  ✓ 98 unique resources (29 duplicates removed)

Embedding and saving to Supabase...
  ✓ Saved 10/98
  ✓ Saved 20/98
  ✓ Saved 30/98
  ... (continues)

======================================================================
✅ Seeding Complete!
   Saved:       98 resources
   Duplicates:  29
   Total:       127
======================================================================

✨ Resources indexed in pgvector
   Semantic search ready for student curriculums!
```

## How It Works

### Phase 1: Fetch Database Topics

```python
def get_topics_from_database():
    # Queries curriculum_topics table
    # Groups by topic_name to deduplicate
    # Returns: [
    #   {'topic_name': 'linear algebra', 'id': '...'},
    #   {'topic_name': 'sorting algorithms', 'id': '...'},
    #   ...
    # ]
```

**Why:** Uses REAL topics from student uploads, not hardcoded guesses.

### Phase 2: Search Multiple Sources

For each topic, the seeder searches:

#### YouTube
- Query: `"{topic} tutorial lecture education"`
- Returns: Educational videos (4-20 min duration)
- Metadata: title, description, video ID

#### arXiv
- Query: `"{topic}"` with relevance sorting
- Returns: Academic papers and preprints
- Metadata: title, abstract, PDF URL

#### Curated Fallback
- Always included 12 high-quality resources
- Examples: 3Blue1Brown videos, MIT OCW courses, Khan Academy
- Ensures search succeeds even if APIs fail

### Phase 3: Deduplicate

```python
seen_urls = set()
for resource in all_resources:
    if resource['url'] not in seen_urls:
        unique_resources.append(resource)
```

Prevents duplicate resources from being saved.

### Phase 4: Embed + Save

```python
for resource in unique_resources:
    # Generate S-BERT embedding
    text = f"{title} {description} {topic}"
    embedding = embed_model.encode(text).tolist()  # 384 dimensions
    
    # Save to Supabase with embedding
    supabase.table('resources').upsert({
        'id': resource['id'],
        'title': resource['title'],
        'embedding': embedding,  # Used for pgvector search
        ...
    })
```

**Key:** Same S-BERT model as your backend (`all-MiniLM-L6-v2`), so embeddings are compatible.

## Semantic Search Flow

After seeding:

```
1. Student uploads PDF → Gemini extracts topics → S-BERT embeddings
   Example: topic_name="Linear Algebra", embedding=[0.12, -0.45, ...]

2. Backend calls pgvector:
   SELECT * FROM resources
   ORDER BY embedding <-> topic_embedding
   LIMIT 10

3. Database performs cosine similarity search:
   - "Essence of Linear Algebra" video: similarity 0.89 ✓
   - "Matrix Computations" paper: similarity 0.87 ✓
   - "Linear Algebra Fundamentals" course: similarity 0.85 ✓
   ...returned to student

4. Student sees personalized resources!
```

## Troubleshooting

### Error: "SUPABASE_URL and SUPABASE_SERVICE_KEY env vars required"

**Solution:** Check your `.env` file:
```bash
# Must be in backend/.env
echo $SUPABASE_URL  # Should print your URL
echo $SUPABASE_SERVICE_KEY  # Should print private key
```

### Error: "No topics found"

**Reason:** No curriculums uploaded yet.
**Solution:** Upload at least one curriculum first via the UI.

### Error: "YouTube error 403"

**Reason:** Invalid API key or quota exceeded.
**Solution:**
1. Verify key in [Google Cloud Console](https://console.cloud.google.com/)
2. Check quota: "YouTube Data API v3" → Quotas
3. Fallback: Script still works with arXiv + curated resources

### "0 personalized resources selected for you"

**Reason:** Resources table is empty or no topics match.
**Solution:**
```bash
# Run seeding again
python seed_resources.py

# Verify in Supabase
SELECT COUNT(*) FROM resources;  -- Should be > 0
SELECT COUNT(*) FROM curriculum_topics;  -- Check topics exist
```

## Customization

### Add More Curated Resources

Edit `CURATED_RESOURCES` list:
```python
CURATED_RESOURCES = [
    {
        'title': 'Your Resource Title',
        'description': 'Your resource description',
        'url': 'https://...',
        'type': 'video',  # 'video', 'paper', 'course', 'interactive'
        'topic': 'linear algebra',  # Must match student topics
        'difficulty_level': 'beginner',  # 'beginner', 'intermediate', 'advanced'
    },
    ...
]
```

### Adjust Search Parameters

```python
# In fetch_youtube_resources():
search_response = youtube.search().list(
    q=f"{query} tutorial lecture",  # Search query
    maxResults=5,  # Results per topic (↑ = more resources, slower)
    videoDuration='medium',  # 'short', 'medium', 'long'
)

# In fetch_arxiv_resources():
search = arxiv.Search(
    query=topic,
    max_results=3,  # Results per topic
)
```

### Add New Source (e.g., Khan Academy)

```python
def fetch_khan_academy_resources(query: str) -> List[Dict]:
    """Fetch Khan Academy resources for topic."""
    # Use Khan Academy API or webscraping
    resources = []
    # ... search logic ...
    return resources

# Then in seed_resources():
resources = fetch_khan_academy_resources(topic_name)
all_resources.extend(resources)
```

## Performance Notes

- **First run:** 2-5 minutes (depends on API response times)
- **Subsequent runs:** ~1 minute (updates existing resources)
- **Embeddings:** Generated locally on your machine (fast)
- **pgvector:** Indexes created automatically, searches <100ms

## Best Practices

1. **Run after first curriculum upload**
   ```bash
   # Student uploads "CS101_Syllabus.pdf"
   # Wait for Gemini to extract topics
   # Then run:
   python seed_resources.py
   ```

2. **Re-run periodically** to capture new topics
   ```bash
   # Weekly or after every 5-10 new curriculum uploads
   python seed_resources.py
   ```

3. **Monitor resource growth**
   ```sql
   -- Check resource count
   SELECT COUNT(*) FROM resources;
   
   -- Check coverage by topic
   SELECT topic, COUNT(*) as count 
   FROM resources 
   GROUP BY topic 
   ORDER BY count DESC;
   ```

4. **Backup resources**
   ```bash
   # Export before updating database schema
   supabase db pull
   ```

## Next Steps

✅ **After seeding:**
1. Upload a curriculum via the web UI
2. Check "Recommendations" page
3. Should see 5-10 matching resources per topic
4. Test Chat sidebar shows upload progress
5. Test pgvector search latency

📊 **Monitor:**
- Resource count in DB: `SELECT COUNT(*) FROM resources;`
- Topic distribution: `SELECT DISTINCT topic FROM resources;`
- Embedding quality: Check similarity scores in recommendations

🚀 **Scale up:**
- Add more sources (Coursera, edX, Udacity APIs)
- Implement topic clustering
- Add user feedback for ranking improvements
- Build recommendation history

---

**Questions?** Check logs or test semantically similar topics:
```python
# Test if embeddings work:
from sentence_transformers import SentenceTransformer
model = SentenceTransformer('all-MiniLM-L6-v2')
e1 = model.encode("linear algebra")
e2 = model.encode("matrix theory")
print(f"Similarity: {np.dot(e1, e2)}")  # Should be ~0.85+
```
