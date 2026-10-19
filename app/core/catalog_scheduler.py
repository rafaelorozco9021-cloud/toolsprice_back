"""Scheduler del crawl nocturno a las 00:00.

Se activa solo si ENABLE_NIGHTLY_CRAWL=1 (activado en docker-compose, apagado
en dev por defecto). Usa un único task asyncio: duerme hasta la próxima
medianoche y ejecuta run_catalog_crawl. Sin dependencia de Celery.
"""
import asyncio
from datetime import datetime, timedelta


async def _nightly_loop():
    from app.services.catalog_crawler import run_catalog_crawl

    while True:
        now = datetime.now()
        # próxima medianoche (00:00:05 para no chocar con el cambio de día)
        run_at = (now + timedelta(days=1)).replace(hour=0, minute=0, second=5, microsecond=0)
        seconds = (run_at - now).total_seconds()
        print(f"[catalog_scheduler] próximo crawl nocturno: {run_at} (duerme {seconds/3600:.1f}h)")
        await asyncio.sleep(seconds)
        print("[catalog_scheduler] iniciando crawl nocturno del catálogo...")
        try:
            summary = await run_catalog_crawl()
            print(f"[catalog_scheduler] crawl terminado: {summary.get('status')} — {summary.get('products', 0)} productos")
        except Exception as e:
            print(f"[catalog_scheduler] error en crawl nocturno: {e}")


def start_nightly_crawler() -> asyncio.Task | None:
    import os

    if os.environ.get("ENABLE_NIGHTLY_CRAWL", "0").lower() not in ("1", "true", "yes"):
        return None
    task = asyncio.create_task(_nightly_loop())
    print("[catalog_scheduler] crawl nocturno habilitado (12:00 AM)")
    return task
