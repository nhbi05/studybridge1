"""Recommendation engine with ML-based filtering."""
import json
from typing import Optional, List
import anthropic
from models.schemas import Resource
from services.embeddings import get_embedding_service
from db.supabase import get_supabase


class RecommendationEngine:
    """ML-based recommendation system using embeddings and LLM."""

    def __init__(self):
        """Initialize recommendation engine."""
        self.embedding_service = get_embedding_service()
        self.supabase = get_supabase()
        self.client = anthropic.Anthropic()
        self.model = "claude-3-5-sonnet-20241022"

    async def get_recommendations(
        self,
        user_id: str,
        curriculum_id: Optional[str] = None,
        topic: Optional[str] = None,
        difficulty: Optional[str] = None,
        resource_types: Optional[List[str]] = None,
        limit: int = 10,
    ) -> List[dict]:
        """Get personalized recommendations for a user.
        
        Uses a combination of:
        - Semantic similarity via embeddings
        - Topic matching
        - User preferences
        """
        try:
            # Get resources filtered by topic
            if topic:
                resources = await self.supabase.get_resources_by_topic(topic, limit=50)
            else:
                # Get all resources (in production, paginate this)
                resources = []

            if not resources:
                return []

            # Filter by resource type if specified
            if resource_types:
                resources = [
                    r for r in resources if r.get("type") in resource_types
                ]

            # Filter by difficulty if specified
            if difficulty:
                resources = [
                    r for r in resources if r.get("difficulty") == difficulty
                ]

            # Score resources using embeddings if topic specified
            if topic:
                topic_embedding = self.embedding_service.embed_text(topic)

                scored_resources = []
                for resource in resources:
                    # Get or generate resource embedding
                    resource_embedding = resource.get("embedding")
                    if not resource_embedding:
                        resource_text = f"{resource.get('title')} {resource.get('summary')}"
                        resource_embedding = self.embedding_service.embed_text(
                            resource_text
                        )

                    similarity_score = self.embedding_service.similarity(
                        topic_embedding, resource_embedding
                    )

                    scored_resources.append(
                        {
                            **resource,
                            "relevance_score": min(0.95, max(0.5, similarity_score)),
                        }
                    )

                # Sort by relevance
                scored_resources.sort(
                    key=lambda x: x["relevance_score"], reverse=True
                )
                resources = scored_resources

            return resources[:limit]

        except Exception as e:
            print(f"Recommendation error: {str(e)}")
            return []

    async def rerank_with_llm(
        self,
        resources: List[dict],
        user_context: str,
        max_results: int = 10,
    ) -> List[dict]:
        """Rerank resources using Claude for better relevance."""
        try:
            resources_text = "\n".join(
                [
                    f"- {r.get('title')} ({r.get('type')}): {r.get('summary')}"
                    for r in resources[:20]
                ]
            )

            prompt = f"""Given the following learning resources and user context, 
rerank them by relevance. Return a JSON array of the top {max_results} resource titles 
in order from most to least relevant.

User Context: {user_context}

Resources:
{resources_text}

Return only a JSON array of strings (resource titles), no other text."""

            message = self.client.messages.create(
                model=self.model,
                max_tokens=1000,
                messages=[{"role": "user", "content": prompt}],
            )

            response_text = message.content[0].text

            # Parse JSON response
            try:
                ranked_titles = json.loads(response_text)
            except json.JSONDecodeError:
                start = response_text.find("[")
                end = response_text.rfind("]") + 1
                ranked_titles = json.loads(response_text[start:end])

            # Reorder resources based on ranking
            ranked_resources = []
            for title in ranked_titles:
                for resource in resources:
                    if resource.get("title") == title:
                        ranked_resources.append(resource)
                        break

            return ranked_resources

        except Exception as e:
            print(f"LLM reranking error: {str(e)}")
            return resources

    async def get_similar_resources(
        self,
        resource_id: str,
        limit: int = 5,
    ) -> List[dict]:
        """Find resources similar to a given resource."""
        try:
            # Get the resource
            resource = await self.supabase.get_resource_by_id(resource_id)
            if not resource:
                return []

            # Get resource embedding
            resource_embedding = resource.get("embedding")
            if not resource_embedding:
                resource_text = f"{resource.get('title')} {resource.get('summary')}"
                resource_embedding = self.embedding_service.embed_text(resource_text)

            # Get all resources in same topic
            topic_resources = await self.supabase.get_resources_by_topic(
                resource.get("topic"), limit=50
            )

            # Score by similarity
            scored = []
            for r in topic_resources:
                if r.get("id") == resource_id:
                    continue

                r_embedding = r.get("embedding")
                if not r_embedding:
                    r_text = f"{r.get('title')} {r.get('summary')}"
                    r_embedding = self.embedding_service.embed_text(r_text)

                similarity = self.embedding_service.similarity(
                    resource_embedding, r_embedding
                )
                scored.append({**r, "similarity_score": similarity})

            # Return top similar
            scored.sort(key=lambda x: x["similarity_score"], reverse=True)
            return scored[:limit]

        except Exception as e:
            print(f"Similar resources error: {str(e)}")
            return []


# Global recommender instance
_recommender: Optional[RecommendationEngine] = None


def get_recommender() -> RecommendationEngine:
    """Get or create recommender instance."""
    global _recommender
    if _recommender is None:
        _recommender = RecommendationEngine()
    return _recommender
