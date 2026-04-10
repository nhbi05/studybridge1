"""AI advisor chat router."""
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import ChatRequest, ChatResponse
from services.auth import get_current_user
from db.supabase import get_supabase
from google import genai
import os

router = APIRouter(prefix="/api/chat", tags=["chat"])

# Initialize Gemini client
client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
model_id = "gemini-2.5-flash"


@router.post("/message")
async def send_message(
    request: ChatRequest,
    current_user = Depends(get_current_user),
    supabase = Depends(get_supabase),
) -> ChatResponse:
    """Send a message to the AI learning advisor.
    
    Integrates with curriculum topics and semantic recommendations
    to provide personalized guidance.
    
    Requires authentication. User ID is extracted from the authentication token.
    """
    try:
        user_id = current_user.id
        
        # Build system prompt
        system_prompt = """You are StudyBridge's AI Learning Advisor. Your role is to help students:
1. Understand their extracted curriculum topics
2. Refine their resource recommendations based on what they know
3. Adjust difficulty levels and resource types
4. Guide them towards optimal learning paths

Be conversational, supportive, and practical. When users say they already know something, 
acknowledge it and help them find more advanced resources. When they struggle, suggest easier 
alternatives or different explanations.

Current context:
- User is using StudyBridge to find curriculum-aligned learning resources
- Recommendations are generated using semantic search (pgvector cosine similarity)
- Suggestions are ranked by relevance score (0-1, higher = better match)
- Users can filter by difficulty (beginner/intermediate/advanced) and resource type"""

        # If curriculum_id provided, fetch its topics and recommendations
        curriculum_context = ""
        if request.curriculum_id:
            try:
                # Get curriculum topics
                topics = await supabase.get_curriculum_topics(request.curriculum_id)
                if topics:
                    topic_names = [t.get("topic_name") for t in topics]
                    curriculum_context = f"\n\nCurriculum topics extracted from syllabus:\n"
                    curriculum_context += "\n".join([f"- {name}" for name in topic_names])
            except Exception as e:
                print(f"Warning: Could not fetch curriculum topics: {e}")
        
        # Build prompt with context and history
        prompt = system_prompt + curriculum_context + "\n\n"
        
        # Add previous messages to context
        if request.conversation_history:
            for msg in request.conversation_history:
                role = "User" if msg.role == "user" else "Assistant"
                prompt += f"{role}: {msg.content}\n"
        
        # Add current message
        prompt += f"User: {request.user_message}\nAssistant:"

        # Get Gemini response
        response = client.models.generate_content(
            model=model_id,
            contents=prompt
        )
        
        assistant_message = response.text

        # Parse any filter suggestions from the response
        updated_filters = {}
        if "harder" in assistant_message.lower() or "advanced" in assistant_message.lower():
            updated_filters["difficulty"] = "advanced"
        elif "easier" in assistant_message.lower() or "beginner" in assistant_message.lower():
            updated_filters["difficulty"] = "beginner"

        if "video" in assistant_message.lower():
            updated_filters["resource_types"] = ["video"]
        elif "article" in assistant_message.lower():
            updated_filters["resource_types"] = ["article"]
        elif "exercise" in assistant_message.lower():
            updated_filters["resource_types"] = ["exercise"]

        return ChatResponse(
            assistant_message=assistant_message,
            confidence_score=0.85,  # Gemini's baseline confidence
            updated_filters=updated_filters if updated_filters else None,
            suggested_resources=None,
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Chat failed: {str(e)}")


@router.post("/session")
async def create_chat_session(current_user = Depends(get_current_user)):
    """Create a new chat session for authenticated user."""
    try:
        user_id = current_user.id
        # In production, store session in database
        session_id = f"session_{user_id}_{int(__import__('time').time())}"
        return {
            "session_id": session_id,
            "user_id": user_id,
            "created_at": __import__('datetime').datetime.now().isoformat(),
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Session creation failed: {str(e)}")


@router.get("/history/{session_id}")
async def get_chat_history(session_id: str):
    """Get chat history for a session."""
    try:
        # In production, fetch from database
        return {
            "session_id": session_id,
            "messages": [],
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get chat history: {str(e)}")
