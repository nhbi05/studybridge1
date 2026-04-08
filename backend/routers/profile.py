"""User profile and authentication router."""
import os
from datetime import datetime
from fastapi import APIRouter, HTTPException, Depends
from models.schemas import SignupRequest, AuthResponse, UserProfile, UserProfileUpdate
from services.auth import get_current_user
from db.supabase import get_supabase

router = APIRouter(prefix="/api/auth", tags=["auth"])


@router.post("/profile", response_model=UserProfile)
async def create_or_update_profile(
    profile: UserProfileUpdate,
    current_user = Depends(get_current_user),
    supabase=Depends(get_supabase),
) -> UserProfile:
    """Create or update user profile in the users table.
    
    Accepts profile data without user_id (extracted from auth token).
    """
    try:
        user_id = current_user.id
        email = current_user.email

        # Prepare profile data
        profile_data = {
            "id": user_id,
            "email": email,
            "name": profile.name,
            "year_of_study": profile.year_of_study,
            "semester": profile.semester,
            "course": profile.course,
            "updated_at": datetime.utcnow().isoformat(),
        }

        # Try to update, if not exists, insert
        # First check if user exists
        existing = await supabase.get_user_by_id(user_id)
        
        if existing:
            # Update existing profile
            await supabase.update_user_profile(user_id, profile_data)
        else:
            # Create new profile
            profile_data["created_at"] = datetime.utcnow().isoformat()
            await supabase.save_user_profile(profile_data)

        return UserProfile(
            user_id=user_id,
            email=email,
            name=profile.name,
            year_of_study=profile.year_of_study,
            semester=profile.semester,
            course=profile.course,
            created_at=profile_data.get("created_at"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Profile update failed: {str(e)}")


@router.get("/profile", response_model=UserProfile)
async def get_user_profile(
    current_user = Depends(get_current_user),
    supabase=Depends(get_supabase),
) -> UserProfile:
    """Get user profile from the users table."""
    try:
        user_id = current_user.id
        email = current_user.email

        # Get profile from users table
        user_profile = await supabase.get_user_by_id(user_id)

        if not user_profile:
            # Return basic profile if not in table yet
            return UserProfile(
                user_id=user_id,
                email=email,
                name=email.split("@")[0],
                year_of_study=1,
                semester=1,
                course="CS",
            )

        return UserProfile(
            user_id=user_profile.get("id"),
            email=user_profile.get("email"),
            name=user_profile.get("name", ""),
            year_of_study=user_profile.get("year_of_study", 1),
            semester=user_profile.get("semester", 1),
            course=user_profile.get("course", "CS"),
            created_at=user_profile.get("created_at"),
        )

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get profile: {str(e)}")


@router.delete("/profile")
async def delete_user_profile(
    current_user = Depends(get_current_user),
    supabase=Depends(get_supabase),
):
    """Delete user profile from the users table."""
    try:
        user_id = current_user.id
        
        # Delete from users table
        supabase.table("users").delete().eq("id", user_id).execute()
        
        # Delete auth user (optional - requires service role key)
        # For now, just delete from users table
        
        return {"success": True, "message": "Profile deleted successfully"}

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Delete failed: {str(e)}")


@router.post("/logout")
async def logout(current_user = Depends(get_current_user)):
    """Logout user (client-side token invalidation with Supabase)."""
    return {"success": True, "message": "Logged out successfully"}
