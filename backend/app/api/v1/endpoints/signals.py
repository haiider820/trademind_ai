from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.deps import AuthUser, get_current_user, require_admin
from app.schemas.signal import SignalCreate, SignalUpdate
from app.services.notification_service import NotificationService
from app.services.supabase_service import SupabaseService

router = APIRouter()
notification_service = NotificationService()


@router.get("")
async def list_signals(
    status: str | None = Query(default=None),
    limit: int = Query(default=20, ge=1, le=100),
    _: AuthUser = Depends(get_current_user),
) -> dict:
    service = SupabaseService()
    query = "select=id,pair,trade_type,entry,sl,tp,status,pnl,risk_level,created_at&order=created_at.desc"
    if status:
        query += f"&status=eq.{status}"
    query += f"&limit={limit}"
    rows = await service.select("signals", query=query, use_service_key=True)
    return {"success": True, "data": rows}


@router.get("/{signal_id}")
async def get_signal(signal_id: str, _: AuthUser = Depends(get_current_user)) -> dict:
    service = SupabaseService()
    rows = await service.select(
        "signals",
        query=(
            f"id=eq.{signal_id}&"
            "select=id,pair,trade_type,entry,sl,tp,status,pnl,risk_level,created_at&limit=1"
        ),
        use_service_key=True,
    )
    if not rows:
        raise HTTPException(status_code=404, detail="Signal not found")
    return {"success": True, "data": rows[0]}


@router.post("")
async def create_signal(payload: SignalCreate, admin: AuthUser = Depends(require_admin)) -> dict:
    service = SupabaseService()
    try:
        row = await service.insert(
            "signals",
            payload={
                "pair": payload.pair,
                "trade_type": payload.trade_type,
                "entry": payload.entry,
                "sl": payload.sl,
                "tp": payload.tp,
                "status": "open",
                "pnl": 0.0,
                "risk_level": payload.risk_level,
                "created_by": admin.id,
            },
            use_service_key=True,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to create signal: {exc}") from exc

    try:
        await _broadcast_signal_notification(
            service,
            title=f"New Signal: {row.get('pair', payload.pair)}",
            body=f"{payload.trade_type.upper()} Entry {payload.entry} TP {payload.tp} SL {payload.sl}",
            data={"type": "signal_created", "signal_id": str(row.get("id", ""))},
        )
    except Exception:
        pass

    return {"success": True, "data": row}


@router.patch("/{signal_id}")
async def update_signal(
    signal_id: str,
    payload: SignalUpdate,
    _: AuthUser = Depends(require_admin),
) -> dict:
    service = SupabaseService()
    update_payload = payload.model_dump(exclude_none=True)
    if not update_payload:
        raise HTTPException(status_code=400, detail="No fields to update")
    normalized_payload = dict(update_payload)
    if "status" in normalized_payload and normalized_payload["status"] is not None:
        normalized_payload["status"] = str(normalized_payload["status"]).lower()
    try:
        row = await service.update(
            "signals",
            payload=normalized_payload,
            query=f"id=eq.{signal_id}",
            use_service_key=True,
        )
    except Exception as exc:
        raise HTTPException(status_code=500, detail=f"Unable to update signal: {exc}") from exc
    if not row:
        raise HTTPException(status_code=404, detail="Signal not found")

    if payload.status in {"tp_hit", "sl_hit", "closed"}:
        await _broadcast_signal_notification(
            service,
            title=f"Signal Update: {row.get('pair', '')}",
            body=f"Status changed to {payload.status}",
            data={"type": "signal_status", "signal_id": str(signal_id), "status": str(payload.status)},
        )
    return {"success": True, "data": row, "status": payload.status}


async def _broadcast_signal_notification(
    service: SupabaseService,
    *,
    title: str,
    body: str,
    data: dict[str, str],
) -> None:
    if not notification_service.enabled:
        return
    try:
        rows = await service.select(
            "device_tokens",
            query="is_active=eq.true&select=token",
            use_service_key=True,
        )
    except Exception:
        return
    tokens = [r.get("token", "") for r in rows if r.get("token")]
    try:
        notification_service.send_signal_alert(tokens=tokens, title=title, body=body, data=data)
    except Exception:
        return
