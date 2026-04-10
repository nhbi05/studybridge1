"""Recommendations router."""
import os
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from models.schemas import RecommendationRequest, RecommendationResponse, Resource
from services.recommender import get_recommender
from services.embeddings import get_embedding_service
from services.auth import get_current_user
from services.collaborative import get_ncf_recommender
from db.supabase import get_supabase
from seed_resources import hybrid_search
from datetime import datetime

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


class TopicWithResources(BaseModel):
    """Topic with matching resources."""
    topic_name: str
    topic_id: str
    matching_resources: list[dict]
    match_count: int


class CurriculumRecommendationsResponse(BaseModel):
    """Response for semantic curriculum-based recommendations."""
    curriculum_id: str
    topics_with_resources: list[TopicWithResources]
    total_resources: int


@router.post("/semantic/{curriculum_id}")
async def get_semantic_recommendations(
    curriculum_id: str,
    current_user = Depends(get_current_user),
    supabase=Depends(get_supabase),
    embeddings_service=Depends(get_embedding_service),
) -> CurriculumRecommendationsResponse:
    """Get resource recommendations using HYBRID SEARCH architecture.
    
    Combines:
    1. pgvector semantic search (pre-seeded DB, fast, semantic)
    2. Live web search (YouTube + arXiv APIs, fresh results)
    3. Deduplication + relevance sorting
    
    For each topic in the curriculum:
    - Finds DB resources via pgvector semantic similarity
    - Searches live web for fresh resources
    - Combines and deduplicates by URL
    - Returns top 10 combined results
    
    Requires authentication. User must own the curriculum.
    """
    try:
        user_id = current_user.id
        
        # Verify user owns this curriculum
        curriculum = await supabase.get_curriculum(curriculum_id)
        if not curriculum or curriculum.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Get all topics for this curriculum
        topics = await supabase.get_curriculum_topics(curriculum_id)
        
        if not topics:
            raise HTTPException(status_code=400, detail="No topics found for curriculum")
        
        # For each topic, find matching resources using hybrid search
        topics_with_resources = []
        total_resources = 0
        ncf_recommender = get_ncf_recommender()
        
        for topic in topics:
            topic_id = topic.get("id")
            topic_name = topic.get("topic_name")
            embedding = topic.get("embedding")
            
            if not embedding:
                print(f"⚠️  No embedding for topic: {topic_name}")
                continue
            
            # Call HYBRID SEARCH: pgvector + live web search
            matching_resources = hybrid_search(
                topic_text=topic_name,
                topic_embedding=embedding,
                supabase=supabase,
                embeddings_service=embeddings_service,
                match_threshold=0.5,
                match_count=15,  # Fetch more from DB for hybrid
                top_k=10  # Return top 10 combined
            )
            
            # RERANK with NCF: Combine semantic search with collaborative filtering
            # This learns from user-resource interaction patterns
            if matching_resources:
                matching_resources = ncf_recommender.rerank_resources(
                    user_id=user_id,
                    resources=matching_resources,
                    top_k=10
                )
                print(f"   🤖 NCF reranked {len(matching_resources)} resources for: {topic_name}")
            
            # Format response
            topics_with_resources.append(
                TopicWithResources(
                    topic_name=topic_name,
                    topic_id=topic_id,
                    matching_resources=matching_resources,
                    match_count=len(matching_resources)
                )
            )
            
            total_resources += len(matching_resources)
        
        return CurriculumRecommendationsResponse(
            curriculum_id=curriculum_id,
            topics_with_resources=topics_with_resources,
            total_resources=total_resources
        )
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Recommendations error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.post("/get")
async def get_recommendations(
    request: RecommendationRequest,
    current_user = Depends(get_current_user),
    supabase=Depends(get_supabase),
    embeddings_service=Depends(get_embedding_service),
) -> RecommendationResponse:
    """Get personalized recommendations for authenticated user.
    
    Uses hybrid search (pgvector DB + live web APIs) + NCF collaborative filtering.
    Requires authentication. User ID is extracted from the authentication token.
    """
    try:
        user_id = current_user.id
        topic = request.topic or "general learning resources"
        
        # Get topic embedding
        topic_embedding = embeddings_service.embed_text(topic)
        
        # Use HYBRID SEARCH: pgvector + YouTube + arXiv
        print(f"🔍 Searching for resources on: {topic}")
        recommended_resources = hybrid_search(
            topic_text=topic,
            topic_embedding=topic_embedding,
            supabase=supabase,
            embeddings_service=embeddings_service,
            match_threshold=0.4,  # Lower threshold for broader results
            match_count=20,  # Get more results for reranking
            top_k=request.limit or 10
        )
        
        if not recommended_resources:
            print(f"⚠️  No resources found for topic: {topic}")
            return RecommendationResponse(
                recommendations=[],
                query_topic=topic,
                total_results=0,
                timestamp=datetime.now().isoformat(),
            )
        
        # RERANK with NCF: Apply collaborative filtering
        ncf_recommender = get_ncf_recommender()
        reranked_resources = ncf_recommender.rerank_resources(
            user_id=user_id,
            resources=recommended_resources,
            top_k=request.limit or 10
        )
        print(f"✅ Retrieved {len(reranked_resources)} resources (NCF reranked)")

        # SAVE RESOURCES TO DB: Ensure all recommended resources exist in the resources table
        # This is required for the foreign key constraint when saving recommendations
        print(f"💾 Saving {len(reranked_resources)} resources to database...")
        for resource in reranked_resources:
            try:
                # Check if resource already exists
                existing = supabase.client.table("resources").select("id").eq("id", resource.get("id")).execute()
                
                if not existing.data:  # Resource doesn't exist, insert it
                    resource_data = {
                        "id": resource.get("id"),
                        "title": resource.get("title"),
                        "type": resource.get("type", "article"),
                        "topic": resource.get("topic"),
                        "summary": resource.get("summary", ""),
                        "difficulty": resource.get("difficulty", "intermediate"),
                        "url": resource.get("url"),
                        "embedding": resource.get("embedding"),
                        "metadata": {
                            "source": resource.get("source", "web"),
                            "collaboration_score": resource.get("collaboration_score", 0.5)
                        }
                    }
                    supabase.client.table("resources").insert(resource_data).execute()
                    print(f"  ✓ Saved: {resource.get('title')[:50]}")
            except Exception as e:
                print(f"  ⚠️  Failed to save resource: {str(e)[:100]}")

        # Convert to Resource models
        resources = [
            Resource(
                id=r.get("id"),
                title=r.get("title"),
                type=r.get("type"),
                topic=r.get("topic"),
                relevance_score=r.get("relevance_score", 0.5),
                summary=r.get("summary") or "Learning resource on this topic",
                url=r.get("url"),
                metadata=r.get("metadata"),
                embedding=r.get("embedding"),
            )
            for r in reranked_resources
        ]

        # Save recommendations to database
        for resource in resources:
            try:
                await supabase.save_recommendation(
                    user_id=user_id,
                    resource_id=resource.id,
                    score=resource.relevance_score,
                )
            except Exception as e:
                print(f"⚠️  Failed to save recommendation: {str(e)}")
                # Don't fail entire request if one save fails

        return RecommendationResponse(
            recommendations=resources,
            query_topic=topic,
            total_results=len(resources),
            timestamp=datetime.now().isoformat(),
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/user")
async def get_user_recommendations(
    limit: int = 20,
    current_user = Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """Get stored recommendations for authenticated user."""
    try:
        user_id = current_user.id
        recommendations = await supabase.get_user_recommendations(user_id, limit)
        return {
            "recommendations": recommendations,
            "total": len(recommendations),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.get("/similar/{resource_id}")
async def get_similar_resources(
    resource_id: str,
    limit: int = 5,
    recommender=Depends(get_recommender),
):
    """Get resources similar to a given resource."""
    try:
        similar = await recommender.get_similar_resources(resource_id, limit)

        resources = [
            Resource(
                id=r.get("id"),
                title=r.get("title"),
                type=r.get("type"),
                topic=r.get("topic"),
                relevance_score=r.get("similarity_score", 0.5),
                summary=r.get("summary"),
                metadata=r.get("metadata"),
            )
            for r in similar
        ]

        return {
            "resources": resources,
            "total": len(resources),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get similar resources: {str(e)}")


@router.post("/rerank")
async def rerank_recommendations(
    resources: list[str],
    user_context: str,
    limit: int = 10,
    recommender=Depends(get_recommender),
):
    """Rerank resources using LLM for better relevance."""
    try:
        # In production, fetch actual resource objects from DB
        reranked = await recommender.rerank_with_llm(
            resources=[],  # Would need to fetch these
            user_context=user_context,
            max_results=limit,
        )

        return {
            "reranked": reranked,
            "total": len(reranked),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Reranking failed: {str(e)}")


@router.post("/collaborative/{curriculum_id}")
async def get_collaborative_recommendations(
    curriculum_id: str,
    current_user = Depends(get_current_user),
    supabase=Depends(get_supabase),
    embeddings_service=Depends(get_embedding_service),
):
    """
    Get recommendations using Neural Collaborative Filtering (NCF).
    
    Uses the pre-trained HuggingFace model (nhbi05/studybridge-ncf) to:
    - Learn user-resource interaction patterns
    - Capture latent features of users and resources
    - Provide personalized recommendations
    
    This endpoint combines NCF scoring with semantic similarity for best results.
    """
    try:
        user_id = current_user.id
        
        # Verify user owns this curriculum
        curriculum = await supabase.get_curriculum(curriculum_id)
        if not curriculum or curriculum.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Unauthorized")
        
        # Get all topics for this curriculum
        topics = await supabase.get_curriculum_topics(curriculum_id)
        
        if not topics:
            raise HTTPException(status_code=400, detail="No topics found for curriculum")
        
        # Get NCF recommender
        ncf_recommender = get_ncf_recommender()
        
        # Collect all resources from all topics using hybrid search
        all_resources = []
        for topic in topics:
            topic_name = topic.get("topic_name")
            embedding = topic.get("embedding")
            
            if not embedding:
                continue
            
            # Get resources for this topic
            resources = hybrid_search(
                topic_text=topic_name,
                topic_embedding=embedding,
                supabase=supabase,
                embeddings_service=embeddings_service,
                match_threshold=0.5,
                match_count=20,  # Get more for comprehensive reranking
                top_k=20
            )
            
            all_resources.extend(resources)
        
        # Remove duplicates by URL
        seen_urls = set()
        unique_resources = []
        for resource in all_resources:
            url = resource.get("url", resource.get("id"))
            if url not in seen_urls:
                seen_urls.add(url)
                unique_resources.append(resource)
        
        # RERANK using NCF model
        if unique_resources:
            reranked = ncf_recommender.rerank_resources(
                user_id=user_id,
                resources=unique_resources,
                top_k=15
            )
            print(f"🤖 NCF reranked {len(reranked)} collaborative recommendations")
        else:
            reranked = []
        
        return {
            "curriculum_id": curriculum_id,
            "recommendations": reranked,
            "total": len(reranked),
            "method": "neural_collaborative_filtering",
            "model": "nhbi05/studybridge-ncf",
        }
    
    except HTTPException:
        raise
    except Exception as e:
        print(f"❌ Collaborative recommendations error: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get collaborative recommendations: {str(e)}")
