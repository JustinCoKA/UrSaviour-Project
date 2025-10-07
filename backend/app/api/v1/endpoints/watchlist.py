from fastapi import APIRouter

router = APIRouter()


@router.get("/watchlist/health")
def watchlist_health():
	return {"status": "ok"}
