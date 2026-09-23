import asyncio
import json
import logging

from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import StreamingResponse

from app.config import get_settings
from app.services.live_simulator import get_simulator, reset_simulator
from app.services.machines import get_machine

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/api/live", tags=["live"])


async def _event_stream(machine_id: str, interval: float):
    sim = get_simulator(machine_id)
    while True:
        try:
            payload = sim.tick()
            yield f"data: {json.dumps(payload)}\n\n"
        except Exception as exc:  # noqa: BLE001
            logger.exception("Live stream tick failed for %s", machine_id)
            yield f"event: error\ndata: {json.dumps({'error': str(exc)})}\n\n"
        await asyncio.sleep(interval)


@router.get("/stream")
async def live_stream(
    machine_id: str = Query(..., description="Active machine ID"),
    interval: float | None = Query(default=None, ge=0.2, le=5.0),
):
    if not get_machine(machine_id):
        raise HTTPException(status_code=404, detail=f"Unknown machine ID: {machine_id}")

    settings = get_settings()
    tick_interval = interval or settings.stream_interval_seconds

    return StreamingResponse(
        _event_stream(machine_id, tick_interval),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "X-Accel-Buffering": "no",
        },
    )


@router.post("/reset/{machine_id}")
def reset_live_state(machine_id: str):
    if not get_machine(machine_id):
        raise HTTPException(status_code=404, detail=f"Unknown machine ID: {machine_id}")
    reset_simulator(machine_id)
    return {"status": "reset", "machine_id": machine_id}
