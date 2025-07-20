from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_matches():
    """Get matches endpoint - placeholder"""
    return {"message": "Matches endpoint - coming soon"}