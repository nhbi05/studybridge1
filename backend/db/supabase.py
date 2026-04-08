"""Supabase database client and operations."""
import os
from typing import Optional
from supabase import create_client, Client


class SupabaseClient:
    """Manages Supabase database connections and operations."""

    def __init__(
        self,
        url: Optional[str] = None,
        key: Optional[str] = None,
    ):
        """Initialize Supabase client."""
        self.url = url or os.getenv("SUPABASE_URL")
        self.key = key or os.getenv("SUPABASE_KEY")

        if not self.url or not self.key:
            raise ValueError(
                "SUPABASE_URL and SUPABASE_KEY environment variables required"
            )

        self.client: Client = create_client(self.url, self.key)

    # ============ Storage Operations ============

    async def upload_curriculum_file(
        self, user_id: str, file_name: str, file_content: bytes
    ) -> Optional[str]:
        """Upload curriculum file to storage and return public URL."""
        try:
            # Create storage path: curriculums/user_id/filename
            bucket_name = "curriculums"
            file_path = f"{user_id}/{file_name}"
            
            # Upload file to Supabase storage
            response = self.client.storage.from_(bucket_name).upload(
                file_path, file_content
            )
            
            # Generate public URL
            file_url = self.client.storage.from_(bucket_name).get_public_url(file_path)
            return file_url
        except Exception as e:
            raise ValueError(f"Failed to upload file to storage: {str(e)}")

    # ============ Curriculum Operations ============

    async def save_curriculum(
        self, user_id: str, file_name: str, file_url: str, summary: str
    ) -> dict:
        """Save curriculum to database (topics saved separately)."""
        data = {
            "user_id": user_id,
            "file_name": file_name,
            "file_url": file_url,
            "summary": summary,
        }
        response = self.client.table("curriculums").insert(data).execute()
        return response.data[0] if response.data else None

    async def save_curriculum_topics(
        self, curriculum_id: str, topics: list[dict]
    ) -> list:
        """Batch save curriculum topics with embeddings.
        
        Args:
            curriculum_id: ID of the curriculum
            topics: List of dicts with keys: topic_name, embedding (list[float])
        
        Returns:
            List of inserted topic records
        """
        try:
            # Format data for insertion
            data = [
                {
                    "curriculum_id": curriculum_id,
                    "topic_name": t["topic_name"],
                    "embedding": t["embedding"],
                }
                for t in topics
            ]
            
            response = self.client.table("curriculum_topics").insert(data).execute()
            return response.data or []
        except Exception as e:
            raise ValueError(f"Failed to save curriculum topics: {str(e)}")

    async def get_curriculum(self, curriculum_id: str) -> Optional[dict]:
        """Retrieve curriculum by ID."""
        response = (
            self.client.table("curriculums")
            .select("*")
            .eq("id", curriculum_id)
            .single()
            .execute()
        )
        return response.data

    async def get_curriculum_topics(self, curriculum_id: str) -> list:
        """Get all topics for a curriculum."""
        response = (
            self.client.table("curriculum_topics")
            .select("*")
            .eq("curriculum_id", curriculum_id)
            .execute()
        )
        return response.data or []

    async def get_user_curriculums(self, user_id: str) -> list:
        """Get all curriculums for a user."""
        response = (
            self.client.table("curriculums")
            .select("*")
            .eq("user_id", user_id)
            .execute()
        )
        return response.data or []

    # ============ Resources Operations ============

    async def save_resource(self, resource_data: dict) -> dict:
        """Save a learning resource to database."""
        response = self.client.table("resources").insert(resource_data).execute()
        return response.data[0] if response.data else None

    async def get_resources_by_topic(self, topic: str, limit: int = 20) -> list:
        """Get resources by topic."""
        response = (
            self.client.table("resources")
            .select("*")
            .eq("topic", topic)
            .limit(limit)
            .execute()
        )
        return response.data or []

    async def search_resources(self, query: str, limit: int = 20) -> list:
        """Search resources by full text search."""
        response = (
            self.client.table("resources")
            .select("*")
            .ilike("title", f"%{query}%")
            .limit(limit)
            .execute()
        )
        return response.data or []

    async def get_resource_by_id(self, resource_id: str) -> Optional[dict]:
        """Get a specific resource."""
        response = (
            self.client.table("resources")
            .select("*")
            .eq("id", resource_id)
            .single()
            .execute()
        )
        return response.data

    # ============ Embeddings Operations ============

    async def save_embedding(
        self, text_id: str, text_type: str, embedding: list[float]
    ) -> dict:
        """Save text embedding."""
        data = {
            "text_id": text_id,
            "text_type": text_type,  # topic, resource, query
            "embedding": embedding,
        }
        response = self.client.table("embeddings").insert(data).execute()
        return response.data[0] if response.data else None

    async def get_embedding(self, text_id: str) -> Optional[list[float]]:
        """Get embedding for a text ID."""
        response = (
            self.client.table("embeddings")
            .select("embedding")
            .eq("text_id", text_id)
            .single()
            .execute()
        )
        return response.data["embedding"] if response.data else None

    async def match_resources(
        self,
        query_embedding: list[float],
        match_threshold: float = 0.5,
        match_count: int = 10,
    ) -> list:
        """Call RPC function to find similar resources via pgvector."""
        try:
            response = self.client.rpc(
                "match_resources",
                {
                    "query_embedding": query_embedding,
                    "match_threshold": match_threshold,
                    "match_count": match_count,
                },
            ).execute()
            return response.data or []
        except Exception as e:
            raise ValueError(f"Failed to match resources: {str(e)}")

    async def match_curriculum_topics(
        self,
        query_embedding: list[float],
        curriculum_id: Optional[str] = None,
        match_threshold: float = 0.5,
        match_count: int = 10,
    ) -> list:
        """Call RPC function to find similar curriculum topics via pgvector."""
        try:
            response = self.client.rpc(
                "match_curriculum_topics",
                {
                    "query_embedding": query_embedding,
                    "curriculum_id_filter": curriculum_id,
                    "match_threshold": match_threshold,
                    "match_count": match_count,
                },
            ).execute()
            return response.data or []
        except Exception as e:
            raise ValueError(f"Failed to match curriculum topics: {str(e)}")

    # ============ User Operations ============

    async def save_user_profile(self, user_data: dict) -> dict:
        """Save or update user profile."""
        response = self.client.table("users").insert(user_data).execute()
        return response.data[0] if response.data else None

    async def get_user_profile(self, user_id: str) -> Optional[dict]:
        """Get user profile."""
        response = (
            self.client.table("users")
            .select("*")
            .eq("id", user_id)
            .single()
            .execute()
        )
        return response.data

    async def update_user_profile(self, user_id: str, profile_data: dict) -> Optional[dict]:
        """Update user profile."""
        response = (
            self.client.table("users")
            .update(profile_data)
            .eq("id", user_id)
            .execute()
        )
        return response.data[0] if response.data else None

    async def update_user_preferences(self, user_id: str, preferences: dict) -> dict:
        """Update user preferences."""
        response = (
            self.client.table("users")
            .update({"preferences": preferences})
            .eq("id", user_id)
            .execute()
        )
        return response.data[0] if response.data else None

    # ============ Recommendations Operations ============

    async def save_recommendation(
        self, user_id: str, resource_id: str, score: float
    ) -> dict:
        """Save a recommendation for user."""
        data = {
            "user_id": user_id,
            "resource_id": resource_id,
            "relevance_score": score,
        }
        response = self.client.table("recommendations").insert(data).execute()
        return response.data[0] if response.data else None

    async def get_user_recommendations(self, user_id: str, limit: int = 20) -> list:
        """Get recommendations for a user."""
        response = (
            self.client.table("recommendations")
            .select("*")
            .eq("user_id", user_id)
            .order("relevance_score", desc=True)
            .limit(limit)
            .execute()
        )
        return response.data or []

    async def save_user(self, user_data: dict) -> Optional[dict]:
        """Save a new user."""
        try:
            response = self.client.table("users").insert(user_data).execute()
            return response.data[0] if response.data else None
        except Exception:
            return None

    async def get_user_by_email(self, email: str) -> Optional[dict]:
        """Get user by email."""
        try:
            response = (
                self.client.table("users")
                .select("*")
                .eq("email", email)
                .single()
                .execute()
            )
            return response.data
        except Exception:
            return None

    async def get_user_by_id(self, user_id: str) -> Optional[dict]:
        """Get user by ID."""
        try:
            response = (
                self.client.table("users")
                .select("*")
                .eq("id", user_id)
                .single()
                .execute()
            )
            return response.data
        except Exception:
            return None


# Global Supabase client instance
_supabase_client: Optional[SupabaseClient] = None


def get_supabase() -> SupabaseClient:
    """Get or create Supabase client instance."""
    global _supabase_client
    if _supabase_client is None:
        _supabase_client = SupabaseClient()
    return _supabase_client
