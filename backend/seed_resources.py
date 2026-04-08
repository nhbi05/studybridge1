"""
Fast-Seed Script: Populate resources table with S-BERT embeddings.

This script generates embeddings using the same model as the backend (all-MiniLM-L6-v2)
and inserts sample resources into Supabase. Run this once to populate the database for
semantic matching.

Usage:
    python seed_resources.py
"""

import os
import asyncio
from typing import List, Dict, Any
from sentence_transformers import SentenceTransformer
from supabase import create_client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize clients
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_KEY = os.getenv("SUPABASE_KEY")

if not SUPABASE_URL or not SUPABASE_KEY:
    raise ValueError("SUPABASE_URL and SUPABASE_KEY environment variables required")

supabase = create_client(SUPABASE_URL, SUPABASE_KEY)
model = SentenceTransformer("all-MiniLM-L6-v2")  # 384 dimensions (same as backend)

# Sample academic resources covering common CS/software topics
SAMPLE_RESOURCES: List[Dict[str, Any]] = [
    # Data Structures
    {
        "title": "Mastering Linked Lists",
        "type": "video",
        "topic": "Data Structures",
        "url": "https://youtu.be/dQw4w9WgXcQ",
        "difficulty": "intermediate",
    },
    {
        "title": "Arrays vs Linked Lists Performance",
        "type": "article",
        "topic": "Data Structures",
        "url": "https://medium.com/basecs/linked-lists-as-a-step-up-1f6",
        "difficulty": "beginner",
    },
    {
        "title": "Binary Search Trees Implementation",
        "type": "exercise",
        "topic": "Data Structures",
        "url": "https://leetcode.com/problems/binary-search-tree-node/",
        "difficulty": "intermediate",
    },
    # Algorithms
    {
        "title": "Big O Notation for Beginners",
        "type": "video",
        "topic": "Algorithms",
        "url": "https://youtu.be/v4cd1O4zkGw",
        "difficulty": "beginner",
    },
    {
        "title": "Sorting Algorithms Comparison",
        "type": "article",
        "topic": "Algorithms",
        "url": "https://en.wikipedia.org/wiki/Sorting_algorithm",
        "difficulty": "intermediate",
    },
    {
        "title": "LeetCode Sorting Challenges",
        "type": "exercise",
        "topic": "Algorithms",
        "url": "https://leetcode.com/explore/learn/card/sorting/",
        "difficulty": "intermediate",
    },
    # Design Patterns
    {
        "title": "SOLID Principles Explained",
        "type": "article",
        "topic": "Design Patterns",
        "url": "https://medium.com/@dharmesh.kadiya/s-o-l-i-d-principles",
        "difficulty": "intermediate",
    },
    {
        "title": "Singleton Pattern Tutorial",
        "type": "video",
        "topic": "Design Patterns",
        "url": "https://youtu.be/DedWcsQjfDM",
        "difficulty": "beginner",
    },
    {
        "title": "Design Patterns: Elements of Reusable Object-Oriented Software",
        "type": "article",
        "topic": "Design Patterns",
        "url": "https://en.wikipedia.org/wiki/Design_Patterns",
        "difficulty": "advanced",
    },
    # Web Development
    {
        "title": "Introduction to React Hooks",
        "type": "video",
        "topic": "Web Development",
        "url": "https://react.dev/reference/react/hooks",
        "difficulty": "beginner",
    },
    {
        "title": "Next.js App Router Guide",
        "type": "article",
        "topic": "Web Development",
        "url": "https://nextjs.org/docs/app",
        "difficulty": "intermediate",
    },
    {
        "title": "Building RESTful APIs with FastAPI",
        "type": "video",
        "topic": "Web Development",
        "url": "https://youtu.be/SORiTsvnU28",
        "difficulty": "intermediate",
    },
    # Database
    {
        "title": "SQL Fundamentals",
        "type": "article",
        "topic": "Database",
        "url": "https://www.postgresql.org/docs/current/tutorial.html",
        "difficulty": "beginner",
    },
    {
        "title": "Vector Embeddings with pgvector",
        "type": "article",
        "topic": "Database",
        "url": "https://github.com/pgvector/pgvector",
        "difficulty": "advanced",
    },
    {
        "title": "Normalizing Database Design",
        "type": "video",
        "topic": "Database",
        "url": "https://youtu.be/UrYLlVt-_KB",
        "difficulty": "intermediate",
    },
    # Software Engineering
    {
        "title": "Introduction to Microservices",
        "type": "article",
        "topic": "Software Engineering",
        "url": "https://microservices.io/",
        "difficulty": "intermediate",
    },
    {
        "title": "Test-Driven Development",
        "type": "video",
        "topic": "Software Engineering",
        "url": "https://youtu.be/B-WJm7scFI0",
        "difficulty": "intermediate",
    },
    {
        "title": "Refactoring: Improving the Design of Existing Code",
        "type": "article",
        "topic": "Software Engineering",
        "url": "https://refactoring.guru/refactoring",
        "difficulty": "advanced",
    },
]


async def seed_resources():
    """Seed resources table with sample data and S-BERT embeddings."""
    print("🌱 Starting resource seeding...")
    print(f"📊 Total resources to seed: {len(SAMPLE_RESOURCES)}")
    print(f"🧠 Using embedding model: all-MiniLM-L6-v2 (384 dimensions)")
    print()

    inserted_count = 0
    error_count = 0

    for idx, resource in enumerate(SAMPLE_RESOURCES, 1):
        try:
            # Generate embedding from title + topic for better semantic matching
            text_to_embed = f"{resource['title']} {resource['topic']}"
            embedding = model.encode(text_to_embed).tolist()

            # Prepare insert data
            insert_data = {
                "title": resource["title"],
                "type": resource["type"],
                "topic": resource["topic"],
                "url": resource["url"],
                "difficulty": resource.get("difficulty", "intermediate"),
                "embedding": embedding,
            }

            # Insert into Supabase
            response = supabase.table("resources").insert(insert_data).execute()

            print(f"✅ [{idx}/{len(SAMPLE_RESOURCES)}] {resource['title']}")
            inserted_count += 1

        except Exception as e:
            print(f"❌ [{idx}/{len(SAMPLE_RESOURCES)}] {resource['title']}")
            print(f"   Error: {str(e)}")
            error_count += 1

    print()
    print(f"=" * 60)
    print(f"✨ Seeding complete!")
    print(f"📌 Successfully inserted: {inserted_count}")
    print(f"⚠️  Errors encountered: {error_count}")
    print(f"=" * 60)

    if error_count == 0:
        print("\n🎉 All resources seeded successfully!")
        print("📚 Your database now has semantic search capabilities.")
        print("🚀 Ready to test recommendations endpoint!")


if __name__ == "__main__":
    try:
        asyncio.run(seed_resources())
    except KeyboardInterrupt:
        print("\n\n⛔ Seeding interrupted by user.")
    except Exception as e:
        print(f"\n\n💥 Fatal error: {str(e)}")
        import traceback

        traceback.print_exc()
