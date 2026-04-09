#!/usr/bin/env python3
"""
StudyBridge — Intelligent Resource Seeding Script

Purpose: Populate your Supabase resources table with real web resources
         that match the topics extracted from student curriculum uploads.

Workflow:
1. Fetch curriculum topics from your database (not hardcoded!)
2. For each topic, search multiple sources (YouTube, arXiv, web)
3. Generate S-BERT embeddings for semantic similarity
4. Save to Supabase with embeddings for pgvector matching

This ensures when a student uploads a syllabus with "Linear Algebra",
pgvector can find matching 3Blue1Brown videos, MIT lectures, arXiv papers, etc.

Requirements:
  pip install sentence-transformers supabase google-api-python-client arxiv requests

API Keys (set as env vars):
  YOUTUBE_API_KEY      - Get from Google Cloud Console
  SUPABASE_URL         - Your Supabase project URL
  SUPABASE_SERVICE_KEY - Service account key (not public key!)
"""

import os
import time
import requests
import uuid
from typing import Optional, List, Dict
from pathlib import Path

try:
    import arxiv
except ImportError:
    arxiv = None

from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from supabase import create_client

# Load environment variables from .env file
env_path = Path(__file__).parent / '.env'
load_dotenv(dotenv_path=env_path)

# ================================================================
# CONFIGURATION
# ================================================================

YOUTUBE_API_KEY = os.getenv("YOUTUBE_API_KEY", "")
SUPABASE_URL = os.getenv("SUPABASE_URL", "")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY", "")

# Initialize clients
if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    print("❌ Error: SUPABASE_URL and SUPABASE_SERVICE_KEY env vars required")
    print(f"   SUPABASE_URL: {SUPABASE_URL or 'NOT SET'}")
    print(f"   SUPABASE_SERVICE_KEY: {SUPABASE_SERVICE_KEY[:20]+'...' if SUPABASE_SERVICE_KEY else 'NOT SET'}")
    print(f"   Loaded from: {env_path}")
    exit(1)

supabase = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
embed_model = SentenceTransformer('all-MiniLM-L6-v2')

# Sample academic resources covering common CS/software topics
CURATED_RESOURCES = [
    # Computer Science - Algorithms
    {
        'title': 'Sorting Algorithms Visualized - VisuAlgo',
        'summary': 'Interactive visualization of sorting algorithms including bubble sort, merge sort, quick sort, heap sort. Shows complexity analysis and step-by-step execution.',
        'url': 'https://visualgo.net/en/sorting',
        'type': 'video',
        'topic': 'sorting algorithms',
        'difficulty': 'beginner',
    },
    {
        'title': 'MIT OpenCourseWare - Introduction to Algorithms',
        'summary': 'Full MIT lecture series on algorithms covering sorting, searching, graph algorithms, dynamic programming with proofs and complexity analysis.',
        'url': 'https://ocw.mit.edu/courses/6-006-introduction-to-algorithms-spring-2020/',
        'type': 'course',
        'topic': 'algorithms',
        'difficulty': 'intermediate',
    },
    # Data Structures
    {
        'title': 'Data Structures - Full Course for Beginners',
        'summary': 'Complete data structures tutorial covering arrays, linked lists, stacks, queues, trees, graphs with implementations and complexity analysis.',
        'url': 'https://www.youtube.com/watch?v=RBSGKlAvoiM',
        'type': 'video',
        'topic': 'data structures',
        'difficulty': 'beginner',
    },
    # Mathematics - Linear Algebra
    {
        'title': 'Essence of Linear Algebra - 3Blue1Brown',
        'summary': 'Visual intuition for linear algebra concepts: vectors, matrices, matrix multiplication, determinants, eigenvalues, and their geometric meaning.',
        'url': 'https://www.youtube.com/playlist?list=PLZHQObOWTQDPD3MizzM2xVFitgF8hE_ab',
        'type': 'video',
        'topic': 'linear algebra',
        'difficulty': 'beginner',
    },
    # Mathematics - Calculus
    {
        'title': 'Essence of Calculus - 3Blue1Brown',
        'summary': 'Visual explanation of calculus fundamentals: derivatives, integrals, chain rule, fundamental theorem, and applications in physics and optimization.',
        'url': 'https://www.youtube.com/playlist?list=PLZHQObOWTQDMsr9K-rj53DwVRMYO3t5Yr',
        'type': 'video',
        'topic': 'calculus',
        'difficulty': 'beginner',
    },
    # Machine Learning
    {
        'title': 'Machine Learning - Andrew Ng (Stanford)',
        'summary': 'Foundational machine learning course: supervised learning, neural networks, unsupervised learning, best practices, and applications.',
        'url': 'https://www.coursera.org/learn/machine-learning',
        'type': 'course',
        'topic': 'machine learning',
        'difficulty': 'intermediate',
    },
    # Discrete Math
    {
        'title': 'Discrete Mathematics - Full Course',
        'summary': 'Complete discrete mathematics: logic, sets, relations, functions, graph theory, combinatorics, and proof techniques essential for computer science.',
        'url': 'https://www.youtube.com/watch?v=rdXw7Ps9vxc',
        'type': 'video',
        'topic': 'discrete mathematics',
        'difficulty': 'intermediate',
    },
    # Database Systems
    {
        'title': 'SQL Tutorial - Full Database Course',
        'summary': 'Complete SQL and database course: database design, SQL queries, joins, indexes, normalization, transactions, and performance optimization.',
        'url': 'https://www.youtube.com/watch?v=HXV3zeQKqGY',
        'type': 'video',
        'topic': 'database systems',
        'difficulty': 'beginner',
    },
    # Networks
    {
        'title': 'Computer Networking - Full Course',
        'summary': 'Complete networking course: OSI model, TCP/IP protocols, routing, switching, DNS, HTTP, security, and network design principles.',
        'url': 'https://www.youtube.com/watch?v=IPvYjXCsTg8',
        'type': 'video',
        'topic': 'computer networks',
        'difficulty': 'intermediate',
    },
    # Operating Systems
    {
        'title': 'Operating Systems - Neso Academy',
        'summary': 'Full OS course: processes, threads, scheduling, synchronization, deadlocks, memory management, file systems, and virtual memory.',
        'url': 'https://www.youtube.com/playlist?list=PLBlnK6fEyqRiVhbXDGLXDk_OQAeuVcp2O',
        'type': 'video',
        'topic': 'operating systems',
        'difficulty': 'intermediate',
    },
    # OOP
    {
        'title': 'Object Oriented Programming - Complete Course',
        'summary': 'Complete OOP: classes, objects, inheritance, polymorphism, encapsulation, abstraction, and design patterns with practical examples.',
        'url': 'https://www.youtube.com/watch?v=SiBw7os-_zI',
        'type': 'video',
        'topic': 'object oriented programming',
        'difficulty': 'beginner',
    },
    # Probability & Statistics
    {
        'title': 'Statistics and Probability - Khan Academy',
        'summary': 'Full statistics course: probability distributions, hypothesis testing, confidence intervals, regression, and statistical inference.',
        'url': 'https://www.khanacademy.org/math/statistics-probability',
        'type': 'course',
        'topic': 'probability and statistics',
        'difficulty': 'beginner',
    },
]

# Add IDs to curated resources
for r in CURATED_RESOURCES:
    r['id'] = str(uuid.uuid4())


# ================================================================
# FETCH FROM SOURCES
# ================================================================

def fetch_youtube_resources(query: str, max_results: int = 5) -> List[Dict]:
    """Fetch educational YouTube videos for a query."""
    if not YOUTUBE_API_KEY:
        return []

    try:
        from googleapiclient.discovery import build
        youtube = build('youtube', 'v3', developerKey=YOUTUBE_API_KEY)

        # Simplified query to avoid API errors
        search_response = youtube.search().list(
            q=f"{query} tutorial",
            part='snippet',
            maxResults=max_results,
            type='video',
            relevanceLanguage='en',
            safeSearch='moderate',
        ).execute()

        resources = []
        for item in search_response.get('items', []):
            snippet = item['snippet']
            video_id = item['id']['videoId']

            resources.append({
                'id': str(uuid.uuid4()),
                'title': snippet['title'],
                'summary': snippet['description'][:500],
                'url': f"https://www.youtube.com/watch?v={video_id}",
                'type': 'video',
                'topic': query,
                'difficulty': 'intermediate',
            })

        return resources

    except Exception as e:
        print(f"  ✗ YouTube error: {type(e).__name__}: {str(e)[:80]}")
        return []


def fetch_arxiv_resources(query: str, max_results: int = 3) -> List[Dict]:
    """Fetch academic papers from arXiv."""
    if not arxiv:
        return []

    try:
        search = arxiv.Search(
            query=query,
            max_results=max_results,
            sort_by=arxiv.SortCriterion.Relevance,
        )

        resources = []
        for paper in search.results():
            resources.append({
                'id': str(uuid.uuid4()),
                'title': paper.title,
                'summary': paper.summary[:500],
                'url': paper.pdf_url or paper.entry_id,
                'type': 'article',
                'topic': query,
                'difficulty': 'advanced',
            })

        return resources

    except Exception as e:
        print(f"  ✗ arXiv error: {str(e)[:80]}")
        return []


# ================================================================
# EMBED + SAVE
# ================================================================

def embed_resource(resource: Dict) -> List[float]:
    """Generate S-BERT embedding for resource."""
    text = f"{resource['title']} {resource.get('summary', '')} {resource.get('topic', '')}"
    return embed_model.encode(text).tolist()


def save_resource_to_db(resource: Dict, embedding: List[float]) -> bool:
    """Save resource + embedding to Supabase."""
    try:
        data = {
            'id': resource['id'],
            'title': resource['title'],
            'summary': resource.get('summary', ''),
            'url': resource['url'],
            'type': resource['type'],
            'topic': resource.get('topic', ''),
            'difficulty': resource.get('difficulty', 'intermediate'),
            'embedding': embedding,
        }
        
        result = supabase.table('resources').upsert(data).execute()
        return True
        
    except Exception as e:
        import traceback
        print(f"    ✗ Save error: {str(e)}")
        traceback.print_exc()
        return False


# ================================================================
# MAIN SEEDING PIPELINE
# ================================================================

def get_topics_from_database() -> List[Dict]:
    """Fetch all curriculum topics from Supabase."""
    try:
        response = supabase.table('curriculum_topics').select('*').execute()
        topics = response.data if response.data else []
        
        print(f"📚 Found {len(topics)} topics in database")
        
        # Group by topic name to avoid duplicates
        unique_topics = {}
        for topic in topics:
            topic_name = topic.get('topic_name', '').lower().strip()
            if topic_name and topic_name not in unique_topics:
                unique_topics[topic_name] = topic
        
        return list(unique_topics.values())
        
    except Exception as e:
        print(f"⚠️  Error fetching topics: {e}")
        print("   Using fallback topics...")
        
        # Fallback topics
        return [
            {'topic_name': 'linear algebra'},
            {'topic_name': 'calculus'},
            {'topic_name': 'data structures'},
            {'topic_name': 'algorithms'},
        ]


async def hybrid_search(
    topic_text: str,
    topic_embedding: List[float],
    supabase,
    embeddings_service,
    match_threshold: float = 0.5,
    match_count: int = 10,
    top_k: int = 10,
) -> List[Dict]:
    """HYBRID SEARCH — Combines pgvector + live web search + reranking.
    
    Architecture:
    1. pgvector semantic search (pre-seeded DB, fast)
    2. Live web search (YouTube + arXiv, fresh)
    3. Deduplication + reranking by relevance
    4. Return top_k combined results
    
    Args:
        topic_text: Topic name (e.g., "linear algebra")
        topic_embedding: S-BERT embedding vector (384-dim)
        supabase: Supabase client
        embeddings_service: Service to generate embeddings
        match_threshold: Cosine similarity threshold
        match_count: Results to fetch from pgvector
        top_k: Final results to return
        
    Returns:
        List of combined resources from DB + web, top_k sorted by relevance
    """
    combined_results = []
    
    try:
        # ── Phase 1: pgvector Search (Fast, Semantic) ─────────────────
        print(f"  🔍 Phase 1: pgvector search for '{topic_text}'...")
        db_results = await supabase.match_resources(
            query_embedding=topic_embedding,
            match_threshold=match_threshold,
            match_count=match_count
        )
        print(f"    ✓ Found {len(db_results)} resources in seeded database")
        
        # Add source tag for deduplication
        for result in db_results:
            result['source'] = 'database'
            combined_results.append(result)
        
        # ── Phase 2: Live Web Search (Fresh Results) ──────────────────
        print(f"  🌐 Phase 2: Live web search for '{topic_text}'...")
        live_results = []
        
        # Search YouTube
        youtube_resources = fetch_youtube_resources(topic_text, max_results=3)
        for resource in youtube_resources:
            resource['source'] = 'youtube'
            live_results.append(resource)
        
        # Search arXiv
        arxiv_resources = fetch_arxiv_resources(topic_text, max_results=2)
        for resource in arxiv_resources:
            resource['source'] = 'arxiv'
            live_results.append(resource)
        
        print(f"    ✓ Found {len(live_results)} fresh resources from web")
        
        # Embed live results on the fly
        for result in live_results:
            text = f"{result['title']} {result.get('summary', '')}"
            result['embedding'] = embeddings_service.encode(text).tolist()
            result['relevance_score'] = 0.7  # Default before reranking
            combined_results.append(result)
        
        # ── Phase 3: Deduplication by URL ────────────────────────────
        print(f"  🔄 Phase 3: Deduplicating {len(combined_results)} results...")
        seen_urls = {}
        unique_results = []
        
        for result in combined_results:
            url = result.get('url', '')
            if url not in seen_urls:
                seen_urls[url] = result
                unique_results.append(result)
        
        print(f"    ✓ {len(unique_results)} unique results after dedup")
        
        # ── Phase 4: Sort by Relevance (simple: database > youtube > arxiv) ──
        print(f"  ⭐ Phase 4: Sorting by relevance...")
        source_priority = {'database': 3, 'youtube': 2, 'arxiv': 1}
        
        unique_results.sort(
            key=lambda x: (
                source_priority.get(x.get('source', 'arxiv'), 1),
                x.get('relevance_score', 0.5)
            ),
            reverse=True
        )
        
        # Return top_k
        final_results = unique_results[:top_k]
        print(f"    ✓ Returning top {len(final_results)} results")
        
        return final_results
        
    except Exception as e:
        print(f"  ✗ Hybrid search error: {str(e)}")
        # Fallback: return empty list or DB results only
        return combined_results[:top_k]


def seed_resources():
    """Main seeding pipeline."""
    print("\n" + "="*70)
    print("🌱 StudyBridge — Resource Seeding Pipeline")
    print("="*70)
    
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        print("❌ Error: Set SUPABASE_URL and SUPABASE_SERVICE_KEY env vars")
        return

    all_resources = []
    saved_count = 0
    duplicate_count = 0

    # ── Step 1: Add curated resources ─────────────────────────
    print(f"\n[1/4] Adding {len(CURATED_RESOURCES)} curated fallback resources...")
    all_resources.extend(CURATED_RESOURCES)
    print(f"  ✓ Added curated resources")

    # ── Step 2: Fetch topics from database ────────────────────
    print(f"\n[2/4] Fetching topics from database...")
    topics = get_topics_from_database()

    # ── Step 3: Search for resources per topic ───────────────
    print(f"\n[3/4] Searching for resources across {len(topics)} topics...")
    for i, topic in enumerate(topics, 1):
        topic_name = topic.get('topic_name', '').strip()
        if not topic_name:
            continue

        print(f"\n  [{i}/{len(topics)}] {topic_name.title()}")
        
        # Search YouTube
        resources = fetch_youtube_resources(topic_name, max_results=3)
        all_resources.extend(resources)
        time.sleep(0.5)
        
        # Search arXiv
        resources = fetch_arxiv_resources(topic_name, max_results=2)
        all_resources.extend(resources)
        time.sleep(0.3)

    # ── Step 4: Deduplicate ──────────────────────────────────
    print(f"\n[4/4] Deduplicating {len(all_resources)} resources...")
    seen_urls = set()
    unique_resources = []
    
    for resource in all_resources:
        url = resource['url']
        if url not in seen_urls:
            seen_urls.add(url)
            unique_resources.append(resource)
        else:
            duplicate_count += 1

    print(f"  ✓ {len(unique_resources)} unique resources ({duplicate_count} duplicates removed)")

    # ── Step 5: Embed + Save ────────────────────────────────────
    print(f"\nEmbedding and saving to Supabase...")
    for i, resource in enumerate(unique_resources, 1):
        try:
            embedding = embed_resource(resource)
            if save_resource_to_db(resource, embedding):
                saved_count += 1
                if saved_count % 10 == 0:
                    print(f"  ✓ Saved {saved_count}/{len(unique_resources)}")
        except Exception as e:
            print(f"  ✗ Error: {str(e)[:80]}")

    # ── Summary ─────────────────────────────────────────────────
    print("\n" + "="*70)
    print("✅ Seeding Complete!")
    print(f"   Saved:       {saved_count} resources")
    print(f"   Duplicates:  {duplicate_count}")
    print(f"   Total:       {len(unique_resources)}")
    print("="*70)
    print("\n✨ Resources indexed in pgvector")
    print("   Semantic search ready for student curriculums!")
    print()


if __name__ == "__main__":
    try:
        seed_resources()
    except KeyboardInterrupt:
        print("\n\n⛔ Seeding interrupted by user")
    except Exception as e:
        print(f"\n\n💥 Fatal error: {str(e)}")
        import traceback
        traceback.print_exc()

