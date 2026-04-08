"""Curriculum upload and parsing router."""
from fastapi import APIRouter, File, UploadFile, HTTPException, Depends
from fastapi.responses import JSONResponse
import uuid
from models.schemas import CurriculumUploadRequest, CurriculumAnalysisResponse
from services.parser import get_parser
from services.auth import get_current_user
from db.supabase import get_supabase

router = APIRouter(prefix="/api/curriculum", tags=["curriculum"])


@router.post("/upload")
async def upload_curriculum(
    file: UploadFile = File(...),
    current_user = Depends(get_current_user),
    parser=Depends(get_parser),
    supabase=Depends(get_supabase),
) -> CurriculumAnalysisResponse:
    """Upload and parse a curriculum file (PDF, DOCX, or TXT).
    
    Flow:
    1. Upload file to Supabase Storage
    2. Parse file and extract topics with Gemini
    3. Generate S-BERT embeddings for each topic
    4. Save curriculum metadata
    5. Batch save curriculum topics with embeddings
    
    Requires authentication. User ID is extracted from the authentication token.
    """
    try:
        user_id = current_user.id
        
        # 1. Read file content
        content = await file.read()

        # 2. Upload file to Supabase Storage
        file_url = await supabase.upload_curriculum_file(
            user_id=user_id,
            file_name=file.filename,
            file_content=content,
        )

        # 3. Determine file type and parse
        if file.filename.endswith(".pdf"):
            curriculum_text = await parser.parse_pdf(content)
        elif file.filename.endswith(".docx"):
            curriculum_text = content.decode("utf-8")
        else:
            curriculum_text = await parser.parse_text_file(content)

        # 4. Extract topics with Gemini
        parse_result = await parser.extract_topics(curriculum_text)

        if not parse_result.success:
            raise HTTPException(status_code=400, detail=parse_result.error)

        # 5. Generate S-BERT embeddings for each topic
        topics_with_embeddings = await parser.embed_topics(parse_result.topics)

        # 6. Generate summary
        summary = await parser.generate_curriculum_summary(curriculum_text)

        # 7. Save curriculum metadata (WITHOUT topics)
        saved_curriculum = await supabase.save_curriculum(
            user_id=user_id,
            file_name=file.filename,
            file_url=file_url,
            summary=summary,
        )

        if not saved_curriculum:
            raise HTTPException(status_code=500, detail="Failed to save curriculum")

        curriculum_id = saved_curriculum.get("id")

        # 8. Batch save topics with embeddings to curriculum_topics table
        await supabase.save_curriculum_topics(
            curriculum_id=curriculum_id,
            topics=topics_with_embeddings,
        )

        return CurriculumAnalysisResponse(
            curriculum_id=curriculum_id,
            user_id=user_id,
            file_name=file.filename,
            file_url=file_url,
            topics_extracted=parse_result.topics,
            total_topics=len(parse_result.topics),
            summary=summary,
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Upload failed: {str(e)}")


@router.get("/list")
async def list_curriculums(
    current_user = Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """Get all curriculums for authenticated user."""
    try:
        user_id = current_user.id
        curriculums = await supabase.get_user_curriculums(user_id)
        return {"curriculums": curriculums, "total": len(curriculums)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to list curriculums: {str(e)}")


@router.get("/{curriculum_id}")
async def get_curriculum(
    curriculum_id: str,
    current_user = Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """Get a specific curriculum. User can only access their own curriculums."""
    try:
        user_id = current_user.id
        curriculum = await supabase.get_curriculum(curriculum_id)
        if not curriculum:
            raise HTTPException(status_code=404, detail="Curriculum not found")
        
        # Ensure user owns this curriculum
        if curriculum.get("user_id") != user_id:
            raise HTTPException(status_code=403, detail="Access denied to this curriculum")
        
        return curriculum
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get curriculum: {str(e)}")
