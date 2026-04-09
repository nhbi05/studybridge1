"""Pydantic models for request/response validation."""
from typing import Optional
from pydantic import BaseModel, Field


# ============ Curriculum Models ============

class CurriculumUploadRequest(BaseModel):
    """Request model for curriculum upload."""
    user_id: str
    file_name: str
    content: str
    file_type: str = Field(default="text", description="pdf, docx, or text")


class TopicExtraction(BaseModel):
    """Extracted topic from curriculum."""
    name: str
    description: str
    subtopics: Optional[list[str]] = None
    difficulty_level: Optional[str] = None


class CurriculumAnalysisResponse(BaseModel):
    """Response after analyzing curriculum."""
    curriculum_id: str
    user_id: str
    file_name: str
    file_url: str
    topics_extracted: list[TopicExtraction]
    total_topics: int
    summary: str
    milestones: Optional[list[str]] = None


# ============ Resource Models ============

class ResourceMetadata(BaseModel):
    """Metadata for a learning resource."""
    url: Optional[str] = None
    duration_minutes: Optional[int] = None
    difficulty: Optional[str] = None
    language: Optional[str] = "en"


class Resource(BaseModel):
    """A single learning resource."""
    id: str
    title: str
    type: str = Field(description="video, article, exercise, book, course")
    topic: str
    relevance_score: float = Field(ge=0, le=1)
    summary: str
    metadata: Optional[ResourceMetadata] = None
    embedding: Optional[list[float]] = None


# ============ Recommendation Models ============

class RecommendationRequest(BaseModel):
    """Request for personalized recommendations.
    
    User ID is extracted from authentication token, not from request body.
    """
    curriculum_id: Optional[str] = None
    topic: Optional[str] = None
    difficulty: Optional[str] = None
    resource_types: Optional[list[str]] = None
    limit: int = Field(default=10, le=50)


class RecommendationResponse(BaseModel):
    """Response with recommended resources."""
    recommendations: list[Resource]
    query_topic: Optional[str]
    total_results: int
    timestamp: str


# ============ Chat Models ============

class ChatMessage(BaseModel):
    """A single message in chat conversation."""
    role: str = Field(description="user or assistant")
    content: str


class ChatRequest(BaseModel):
    """Request for AI advisor chat.
    
    User ID is extracted from authentication token, not from request body.
    """
    curriculum_id: Optional[str] = None
    current_recommendations: Optional[list[str]] = None
    conversation_history: Optional[list[ChatMessage]] = None
    user_message: str


class ChatResponse(BaseModel):
    """AI advisor response."""
    assistant_message: str
    confidence_score: Optional[float] = None
    updated_filters: Optional[dict] = None
    suggested_resources: Optional[list[str]] = None


# ============ Authentication Models ============

class SignupRequest(BaseModel):
    """Request for user signup."""
    email: str
    password: str
    name: str
    year_of_study: int = Field(default=1, ge=1, le=4)
    semester: int = Field(default=1, ge=1, le=2)
    course: str = Field(default="CS", description="CS, ENG, MED, BUS, LAW")


class LoginRequest(BaseModel):
    """Request for user login."""
    email: str
    password: str


class AuthResponse(BaseModel):
    """Response after authentication."""
    success: bool
    message: str
    user_id: Optional[str] = None
    email: Optional[str] = None
    name: Optional[str] = None
    token: Optional[str] = None
    token_type: str = "bearer"


class UserProfile(BaseModel):
    """User profile information."""
    user_id: str
    email: str
    name: str
    year_of_study: int
    semester: int
    course: str
    created_at: Optional[str] = None


class UserProfileUpdate(BaseModel):
    """User profile update request (from authenticated user).
    
    User ID and email are extracted from authentication token.
    """
    name: str
    year_of_study: int
    semester: int
    course: str


# ============ Parsing Models ============

class ParseResult(BaseModel):
    """Result of parsing curriculum file."""
    success: bool
    topics: list[TopicExtraction]
    raw_text: Optional[str] = None
    error: Optional[str] = None
    summary: Optional[str] = None
    milestones: Optional[list[str]] = None


class EmbeddingRequest(BaseModel):
    """Request to generate embeddings for text."""
    texts: list[str]
    model: str = Field(default="sentence-transformers")


class EmbeddingResponse(BaseModel):
    """Response with text embeddings."""
    embeddings: list[list[float]]
    model: str
    dimension: int
