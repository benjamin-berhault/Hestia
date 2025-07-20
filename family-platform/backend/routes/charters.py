from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_charters():
    """Get charters endpoint - placeholder"""
    return {"message": "Charters endpoint - coming soon"}