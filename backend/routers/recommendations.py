"""Recommendations router."""
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import RecommendationRequest, RecommendationResponse, Resource
from services.recommender import get_recommender
from services.embeddings import get_embedding_service
from services.auth import get_current_user
from db.supabase import get_supabase
from datetime import datetime

router = APIRouter(prefix="/api/recommendations", tags=["recommendations"])


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
