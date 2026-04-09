# 🔍 Hybrid Search Architecture

## Overview

Your recommendation system now uses a **3-layer hybrid search** combining:

1. **pgvector (DATABASE)** - Fast semantic search on pre-seeded resources
2. **Live Web Search** - Fresh results from YouTube + arXiv APIs  
3. **Deduplication + Ranking** - Smart combination of results

## Architecture

```
Student uploads PDF → Gemini extracts topics → S-BERT embeddings
                                                    ↓
                                    HYBRID SEARCH (per topic):
                                    
    ┌─────────────────────────────────────────────────┐
    │ Phase 1: pgvector DB Search (0.5-1s)           │
    │ - Query: topic embedding                        │
    │ - Match threshold: 0.5 (cosine similarity)      │
    │ - Results: Top 15 from seeded resources         │
    └─────────────┬───────────────────────────────────┘
                  │
    ┌─────────────▼───────────────────────────────────┐
    │ Phase 2: Live Web Search (2-5s)                │
    │ - YouTube API: 3 tutorial videos                │
    │ - arXiv API: 2 academic papers                  │
    │ - Deduplicate duplicates                        │
    └─────────────┬───────────────────────────────────┘
                  │
    ┌─────────────▼───────────────────────────────────┐
    │ Phase 3: Combine + Deduplicate                  │
    │ - Merge results by URL                          │
    │ - Remove duplicates                             │
    │ - Embed live results with S-BERT                │
    └─────────────┬───────────────────────────────────┘
                  │
    ┌─────────────▼───────────────────────────────────┐
    │ Phase 4: Sort by Relevance                      │
    │ - Priority: DB (3) > YouTube (2) > arXiv (1)    │
    │ - Return: Top 10 combined                       │
    └─────────────┬───────────────────────────────────┘
                  │
                  ↓
            Student sees results!
```

## Code Changes

### 1. Added hybrid_search() in seed_resources.py

```python
async def hybrid_search(
    topic_text: str,
    topic_embedding: List[float],
    supabase,
    embeddings_service,
    match_count: int = 10,
    top_k: int = 10,
) -> List[Dict]:
    """Combines pgvector + live web search + reranking."""
    
    # Phase 1: pgvector search
    db_results = await supabase.match_resources(embedding=topic_embedding)
    
    # Phase 2: Live YouTube + arXiv search
    youtube = fetch_youtube_resources(topic_text, max_results=3)
    arxiv = fetch_arxiv_resources(topic_text, max_results=2)
    
    # Phase 3: Combine + embed
    all_results = db_results + youtube + arxiv
    # Embed live results on the fly
    
    # Phase 4: Dedup + sort
    unique = dedup_by_url(all_results)
    sorted_results = sort_by_priority(unique)
    
    return sorted_results[:top_k]
```

### 2. Updated /api/recommendations/semantic/{curriculum_id}

**Before:**
```python
# Direct pgvector call only
matching_resources = await supabase.match_resources(
    query_embedding=embedding,
    match_threshold=0.5,
    match_count=10
)
```

**After:**
```python
# Hybrid search: DB + live web
matching_resources = await hybrid_search(
    topic_text=topic_name,
    topic_embedding=embedding,
    supabase=supabase,
    embeddings_service=embeddings_service,
    match_count=15,  # More from DB
    top_k=10  # Final results
)
```

### 3. Added YOUTUBE_API_KEY to .env

```bash
YOUTUBE_API_KEY=AIzaSyDXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

Fetched via:
```python
YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
```

## Benefits

| Aspect | Before | After |
|--------|--------|-------|
| **Speed** | ~0.5s (pgvector only) | 2-5s (pgvector + live) |
| **Freshness** | Pre-seeded (static) | Real-time web results |
| **Coverage** | Limited to seeded DB | Unlimited via web APIs |
| **Relevance** | Semantic similarity | Semantic + live trending |
| **Redundancy** | Single source | Multi-source fallback |

## Flow Example

**Student uploads:** "Machine Learning 101.pdf"

**Gemini extracts:**
- Topic 1: "neural networks"
- Topic 2: "gradient descent"

**For each topic, hybrid search runs:**

### "neural networks" example:

**Phase 1: pgvector**
```
✓ "3Blue1Brown Neural Networks" video
✓ "MIT 6.036 - Machine Learning" course
✓ "Deep Learning Intro" paper
(15 total from seeded DB)
```

**Phase 2: Live web**
```
✓ "PyTorch Neural Networks Tutorial 2024" (YouTube - NEW!)
✓ "TensorFlow Deep Learning" (YouTube - FRESH!)
✓ "Neural Network Optimization" (arXiv - RECENT!)
(5 total from APIs)
```

**Phase 3: Combine**
```
Total: 20 resources before dedup
Removed: 3 duplicates (same URL)
Result: 17 unique resources
```

**Phase 4: Sort & return**
```
(Priority: DB > YouTube > arXiv)
1. "3Blue1Brown Neural Networks" (DB, relevance: 0.92)
2. "MIT 6.036 Course" (DB, relevance: 0.88)
3. "PyTorch Tutorial 2024" (YouTube, relevance: 0.85) ← FRESH!
4. "Deep Learning Intro" (DB, relevance: 0.83)
5. "TensorFlow Tutorial" (YouTube, relevance: 0.81) ← FRESH!
... (top 10 selected)
```

## Configuration

### .env Variables

```bash
# Required
SUPABASE_URL=https://xxxxx.supabase.co
SUPABASE_KEY=eyJhbGc...
SUPABASE_SERVICE_KEY=eyJhbGc...  # For hybrid_search
GEMINI_API_KEY=AIzaSy...

# For hybrid search (optional but recommended)
YOUTUBE_API_KEY=AIzaSyDXXX...  # Get from Google Cloud Console
```

### Endpoint Parameters

```python
# In /semantic/{curriculum_id}:
await hybrid_search(
    topic_text=topic_name,           # "neural networks"
    topic_embedding=embedding,       # [0.12, -0.45, ...]
    supabase=supabase,               # DB connection
    embeddings_service=embeddings,   # S-BERT for live results
    match_threshold=0.5,             # Cosine similarity threshold
    match_count=15,                  # Results from pgvector
    top_k=10                         # Final return count
)
```

## Performance Considerations

### Latency
- pgvector: 100-500ms (indexed search)
- YouTube API: 1-2s
- arXiv API: 1-2s
- Deduplication: 10-50ms
- **Total: 2-5 seconds per topic**

### Optimization Tips
```python
# Reduce latency:
- match_count=10 (was 15) → Faster pgvector
- max_results=2 (was 3) in fetch_youtube_resources() → Fewer API calls
- Use caching for frequently searched topics

# Improve quality:
- Increase top_k=15 → More results
- Lower match_threshold=0.3 → Broader matches
- Add custom ranking weights
```

### API Rate Limits
- YouTube: 10,000 units/day (default quota)
- arXiv: ~3 req/sec recommended
- Supabase: Depends on plan

## Monitoring & Logging

Current logging in hybrid_search():
```python
print(f"  🔍 Phase 1: pgvector search for '{topic_text}'...")
print(f"    ✓ Found {len(db_results)} resources in seeded database")
print(f"  🌐 Phase 2: Live web search for '{topic_text}'...")
print(f"    ✓ Found {len(live_results)} fresh resources from web")
print(f"  🔄 Phase 3: Deduplicating {len(combined_results)} results...")
print(f"  ⭐ Phase 4: Sorting by relevance...")
```

**Output example:**
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

## Troubleshooting

### "0 personalized resources"
**Cause:** No seeded resources + YouTube API key invalid
**Fix:** Run seed_resources.py first, verify YOUTUBE_API_KEY

### YouTube API quota exceeded
**Cause:** Hit 10,000 units/day limit
**Solution:** Falls back to pgvector only (graceful degradation)

### Slow recommendations (>10s)
**Cause:** Both YouTube and arXiv timing out
**Solution:** Reduce match_count or skip live search

### Embedding mismatch error  
**Cause:** Different embedding model in hybrid_search vs backend
**Fix:** Ensure all use 'all-MiniLM-L6-v2' (384-dim)

## Next Steps

1. **Test hybrid search:**
   ```bash
   # Upload curriculum
   # Check recommendations page
   # Should see YouTube + arXiv results mixed with DB results
   ```

2. **Add NCF reranking:**
   ```python
   # In Phase 4, could add ML reranking:
   # ranked = ncf_model.rerank(unique_results, user_context)
   ```

3. **Implement caching:**
   ```python
   # Cache results for same topic (24h TTL)
   @cache(ttl=86400)
   async def hybrid_search(...):
   ```

4. **Add analytics:**
   ```python
   # Track which resources students click
   # Use for feedback to ML ranking model
   ```

5. **Scale to more sources:**
   - Coursera API
   - edX API
   - GitHub trending repos
   - Stack Overflow tags

---

**Architecture Summary:** Your system is now a **360° recommendation engine** combining database efficiency, web freshness, and semantic relevance! 🚀
