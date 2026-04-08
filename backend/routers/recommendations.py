"""Recommendations router."""
from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from models.schemas import RecommendationRequest, RecommendationResponse, Resource
from services.recommender import get_recommender
from services.embeddings import get_embedding_service
from services.auth import get_current_user
from db.supabase import get_supabase
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
) -> CurriculumRecommendationsResponse:
    """Get resource recommendations using pgvector semantic search.
    
    For each topic in the curriculum, finds semantically similar resources
    using cosine similarity on S-BERT embeddings.
    
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
        
        # For each topic, find matching resources using pgvector
        topics_with_resources = []
        total_resources = 0
        
        for topic in topics:
            topic_id = topic.get("id")
            topic_name = topic.get("topic_name")
            embedding = topic.get("embedding")
            
            # Call RPC: match_resources with this topic's embedding
            matching_resources = await supabase.match_resources(
                query_embedding=embedding,
                match_threshold=0.5,
                match_count=10
            )
            
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
        raise HTTPException(status_code=500, detail=f"Failed to get recommendations: {str(e)}")


@router.post("/get")
async def get_recommendations(
    request: RecommendationRequest,
    current_user = Depends(get_current_user),
    recommender=Depends(get_recommender),
    supabase=Depends(get_supabase),
) -> RecommendationResponse:
    """Get personalized recommendations for authenticated user.
    
    Requires authentication. User ID is extracted from the authentication token.
    """
    try:
        user_id = current_user.id
        
        # Get recommendations from engine
        recommended_resources = await recommender.get_recommendations(
            user_id=user_id,
            curriculum_id=request.curriculum_id,
            topic=request.topic,
            difficulty=request.difficulty,
            resource_types=request.resource_types,
            limit=request.limit,
        )

        # Convert to Resource models
        resources = [
            Resource(
                id=r.get("id"),
                title=r.get("title"),
                type=r.get("type"),
                topic=r.get("topic"),
                relevance_score=r.get("relevance_score", 0.5),
                summary=r.get("summary"),
                metadata=r.get("metadata"),
                embedding=r.get("embedding"),
            )
            for r in recommended_resources
        ]

        # Save recommendations to database
        for resource in resources:
            await supabase.save_recommendation(
                user_id=user_id,
                resource_id=resource.id,
                score=resource.relevance_score,
            )

        return RecommendationResponse(
            recommendations=resources,
            query_topic=request.topic,
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
