from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_profiles():
    """Get profiles endpoint - placeholder"""
    return {"message": "Profiles endpoint - coming soon"}