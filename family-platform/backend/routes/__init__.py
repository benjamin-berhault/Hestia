from .auth import router as auth_router
from .users import router as users_router
from .profiles import router as profiles_router
from .photos import router as photos_router
from .matches import router as matches_router
from .messages import router as messages_router
from .charters import router as charters_router
from .admin import router as admin_router

__all__ = [
    "auth_router",
    "users_router", 
    "profiles_router",
    "photos_router",
    "matches_router",
    "messages_router",
    "charters_router",
    "admin_router"
]