from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_admin():
    """Get admin endpoint - placeholder"""
    return {"message": "Admin endpoint - coming soon"}