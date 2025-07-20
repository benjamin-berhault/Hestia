from fastapi import APIRouter

router = APIRouter()

@router.get("/")
async def get_photos():
    """Get photos endpoint - placeholder"""
    return {"message": "Photos endpoint - coming soon"}