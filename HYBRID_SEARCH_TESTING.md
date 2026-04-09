# 🧪 Testing the Hybrid Search Architecture

## Prerequisites

✅ Backend running: `python -m uvicorn main:app --reload`
✅ Supabase seeded with resources: `python seed_resources.py`
✅ .env configured with API keys

## Step-by-Step Test

### 1. Get YouTube API Key

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create project → APIs & Services → Library
3. Search "YouTube Data API v3" → Enable
4. Create API Key in Credentials
5. Add to `.env`:
   ```bash
   YOUTUBE_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
   ```

### 2. Verify Database Setup

```sql
-- Connect to your Supabase database
SELECT COUNT(*) FROM resources;           -- Should be 50+
SELECT COUNT(*) FROM curriculum_topics;   -- Should have topics

-- Check embeddings exist
SELECT id, title, embedding FROM resources LIMIT 1;  -- embedding should have 384 values
```

### 3. Upload a Curriculum (via Web UI)

1. Open http://localhost:3000/curriculum
2. Upload a sample PDF (or use test file)
3. Watch Chat Sidebar show events:
   ```
   📥 File received: sample.pdf
   🔄 Confirming topics...
   🧠 Topics extracted: [Linear Algebra, Calculus, ...]
   ⚙️ Creating embeddings...
   ✅ Upload complete!
   ```

### 4. Test Hybrid Search (Direct API Call)

```bash
# Get curriculum_id from web UI or database
curl -X POST http://localhost:8000/api/recommendations/semantic/{curriculum_id} \
  -H "Authorization: Bearer {access_token}" \
  -H "Content-Type: application/json"
```

### 5. View Results on Recommendations Page

Navigate to: http://localhost:3000/recommendations/{curriculum_id}

**Expected output:**
```
📊 Personalized Recommendations
  23 Topics extracted
  75-100 Resources matched

[Topic: Linear Algebra]
  ✓ 3 results from pre-seeded DB
  ✓ 2 results from YouTube (fresh 2024 videos)
  ✓ 2 results from arXiv (recent papers)
  
  Results shown:
  1. "Essence of Linear Algebra" - 3Blue1Brown (DB) ⭐⭐⭐
  2. "MIT 18.06 Linear Algebra" - MIT OCW (DB) ⭐⭐
  3. "Linear Algebra in Python" - YouTube 2024 (YouTube) ✨ FRESH
  4. "Matrix Theory Fundamentals" - arXiv (arXiv)
  5. "Linear Algebra Deep Dive" - YouTube 2024 (YouTube) ✨ FRESH
  ... (top 10 returned)

[Topic: Calculus]
  ... (same pattern)
```

## Debugging

### Enable Verbose Logging

In `seed_resources.py`, increase print statements:

```python
print(f"  🔍 Phase 1: pgvector search for '{topic_text}'...")
print(f"    Topics: {len(db_results)} from DB")
print(f"  🌐 Phase 2: Live web for '{topic_text}'...")
print(f"    YouTube: {youtube_resources}")
print(f"    arXiv: {arxiv_resources}")
```

### Check Backend Logs

Terminal running backend should show:
```
🔍 Phase 1: pgvector search for 'linear algebra'...
  ✓ Found 12 resources in seeded database
🌐 Phase 2: Live web search for 'linear algebra'...
  ✓ Found 5 fresh resources from web
🔄 Phase 3: Deduplicating 17 results...
  ✓ 15 unique results after dedup
⭐ Phase 4: Sorting by relevance...
  ✓ Returning top 10 results
```

### Test Individual Components

#### Test pgvector alone:
```python
# In Python shell
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('all-MiniLM-L6-v2')
embedding = model.encode("linear algebra").tolist()

# Then in Supabase:
# SELECT * FROM resources ORDER BY embedding <-> embedding LIMIT 10
```

#### Test YouTube API:
```python
from googleapiclient.discovery import build
import os

youtube = build('youtube', 'v3', developerKey=os.getenv("YOUTUBE_API_KEY"))
results = youtube.search().list(
    q="linear algebra tutorial",
    part='snippet',
    maxResults=3
).execute()

print(results['items'])
```

#### Test arXiv API:
```python
import arxiv

search = arxiv.Search(
    query="linear algebra",
    max_results=3
)

for paper in search.results():
    print(f"{paper.title}: {paper.pdf_url}")
```

## Performance Testing

### Measure latency:

```bash
# Test recommendations endpoint timing
time curl -X POST http://localhost:8000/api/recommendations/semantic/{curriculum_id} \
  -H "Authorization: Bearer {token}"

# Expected: 2-5 seconds per topic
```

### Breakdown:
```
pgvector search:     ~0.5s (indexed query)
YouTube API call:    ~1s    (network latency)
arXiv API call:      ~1s    (network latency)
Embedding overhead:  ~0.5s  (S-BERT encoding)
Dedup + sorting:     ~0.2s
─────────────────────────────
Total per topic:     ~3.2s
```

## Expected Results Matrix

| Scenario | pgvector | YouTube | arXiv | Total | Status |
|----------|----------|---------|-------|-------|--------|
| Cold start (no seeding) | 0 | 3 | 2 | 5 | ⚠️ Limited |
| After seeding | 12 | 3 | 2 | 17 | ✅ Full |
| YouTube API down | 12 | 0 | 2 | 14 | ✅ Degraded |
| All APIs down | 12 | 0 | 0 | 12 | ✅ Fallback |

## Validation Checklist

- [ ] Database has resources: `SELECT COUNT(*) FROM resources;` → 50+
- [ ] Embeddings exist: `SELECT COUNT(*) FROM resources WHERE embedding IS NOT NULL;` → 50+
- [ ] Topics extracted: Student sees chat messages during upload
- [ ] Hybrid search runs: Backend logs show 4 phases
- [ ] Results visible: Recommendations page shows resources
- [ ] Fresh results: See "2024" videos from YouTube
- [ ] Deduplication works: No duplicate URLs in results
- [ ] Fallback works: Results even without YouTube API key

## Comparison: Before vs After

### Before (pgvector only):
```
GET /api/recommendations/semantic/abc123
↓
pgvector search → 10 static results from DB → Response

Issues:
- No fresh content
- Always same results
- Limited if DB empty
- Cold start problem
```

### After (Hybrid):
```
GET /api/recommendations/semantic/abc123
↓
Phase 1: pgvector search → 15 DB results
Phase 2: YouTube API → 3 videos (2024 content!)
Phase 3: arXiv API → 2 papers (recent!)
Phase 4: Combine + dedup + sort → Top 10 → Response

Improvements:
✓ Fresh content included
✓ Diverse sources
✓ Graceful degradation
✓ Better coverage
```

## Example Output

**Recommendations API Response:**
```json
{
  "curriculum_id": "550e8400-e29b-41d4-a716-446655440000",
  "topics_with_resources": [
    {
      "topic_name": "Linear Algebra",
      "topic_id": "topic_123",
      "match_count": 10,
      "matching_resources": [
        {
          "id": "res_001",
          "title": "Essence of Linear Algebra - 3Blue1Brown",
          "url": "https://www.youtube.com/playlist?list=...",
          "type": "video",
          "difficulty_level": "beginner",
          "source": "database",
          "relevance_score": 0.92
        },
        {
          "id": "res_002",
          "title": "Linear Algebra Fundamentals - MIT 18.06",
          "url": "https://ocw.mit.edu/courses/...",
          "type": "course",
          "difficulty_level": "intermediate",
          "source": "database",
          "relevance_score": 0.88
        },
        {
          "id": "res_003",
          "title": "Learn Linear Algebra in Python - 2024",
          "url": "https://www.youtube.com/watch?v=...",
          "type": "video",
          "difficulty_level": "beginner",
          "source": "youtube",
          "relevance_score": 0.85
        },
        ...
      ]
    },
    ...
  ],
  "total_resources": 75
}
```

## Monitoring

Track metrics in logs:

```python
# In hybrid_search():
import time

start = time.time()
db_results = await supabase.match_resources(...)
print(f"pgvector: {time.time()-start:.2f}s, {len(db_results)} results")

start = time.time()
youtube = fetch_youtube_resources(...)
print(f"YouTube: {time.time()-start:.2f}s, {len(youtube)} results")

# Monitor in production for:
# - API response times
# - Number of results per source
# - Dedup effectiveness
# - Source distribution (80% DB, 15% YouTube, 5% arXiv)
```

---

**Ready to launch!** Your hybrid search system combines database efficiency with web freshness 🚀
