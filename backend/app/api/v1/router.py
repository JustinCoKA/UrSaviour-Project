from fastapi import APIRouter
from app.api.v1.endpoints import products_new as products, auth, user, watchlist, assistant, admin

api_router = APIRouter()
api_router.include_router(products.router,  prefix="/products",   tags=["Products"])
api_router.include_router(auth.router,      prefix="/auth",       tags=["Authentication"])
api_router.include_router(user.router,      prefix="/users",      tags=["Users"])
api_router.include_router(watchlist.router, prefix="/watchlist",  tags=["Watchlist"])
api_router.include_router(assistant.router, prefix="/assistant",  tags=["AI Assistant"])
api_router.include_router(admin.router,     prefix="/admin",      tags=["Admin"])

# Add auth endpoints also to the root path (for /register etc.)
api_router.include_router(auth.router, prefix="", tags=["Auth"])
