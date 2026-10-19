"""Rutas del catálogo pre-scrapeado de Homecenter."""
from fastapi import APIRouter, BackgroundTasks

router = APIRouter(prefix="/catalog", tags=["catalog"])

# estado simple del último crawl en background (por proceso)
_last_run: dict = {}


@router.post("/crawl")
async def trigger_crawl(background: BackgroundTasks, max_pages: int = 300):
    """Dispara el crawl del catálogo manualmente (no bloquea la respuesta)."""
    from app.services.catalog_crawler import run_catalog_crawl

    if _last_run.get("running"):
        return {"status": "already_running", "detail": _last_run}
    _last_run["running"] = True

    async def _job():
        try:
            summary = await run_catalog_crawl(max_pages=max_pages)
            _last_run["summary"] = summary
        finally:
            _last_run["running"] = False

    background.add_task(_job)
    return {"status": "started", "max_pages": max_pages}


@router.get("/crawl/status")
async def crawl_status():
    from app.services.catalog_crawler import get_crawl_stats

    stats = await get_crawl_stats()
    stats["last_run"] = {k: v for k, v in _last_run.items() if k != "summary"} or {
        "running": False
    }
    return stats
