"""
Admin Panel Router
All routes are protected by the get_current_admin dependency.
"""
import logging
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.ext.asyncio import AsyncSession
from passlib.context import CryptContext

from app.database import get_db
from app.models import User
from app.dependencies.admin_auth import get_current_admin

from app.services.admin_user_service import (
    get_all_users,
    get_user_by_id,
    block_user,
    unblock_user,
    reset_user_password,
)
from app.services.admin_feedback_service import (
    get_feedback_logs,
    get_support_tickets,
    update_ticket_status,
)
from app.services.admin_counsellor_service import (
    get_pending_counsellors,
    get_all_counsellors,
    approve_counsellor,
    reject_counsellor,
    block_counsellor,
    unblock_counsellor,
    get_counsellor_session_analytics,
)
from app.services.admin_payment_service import (
    get_payment_analytics,
    get_recent_payment_logs,
)
from app.services.admin_analytics_service import (
    get_recent_appointments,
    get_moderation_flags,
    resolve_moderation_flag,
)

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["Admin"])
templates = Jinja2Templates(directory="frontend/templates")
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# ─── Main Dashboard ───────────────────────────────────────────────────────────

@router.get("/", response_class=HTMLResponse)
async def admin_dashboard(
    request: Request,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
    user_page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    user_search: str = Query(None),
):
    """Main admin dashboard — fetches all modules and renders template."""
    try:
        # Parallel-ish fetches (sequential but separated for clarity)
        users_data = await get_all_users(db, page=user_page, page_size=page_size, search=user_search)
        feedback_data = await get_feedback_logs(db)
        tickets_data = await get_support_tickets(db)
        pending_counsellors = await get_pending_counsellors(db)
        counsellors_data = await get_all_counsellors(db)
        counsellor_analytics = await get_counsellor_session_analytics(db)
        appointments = await get_recent_appointments(db)
        payment_analytics = await get_payment_analytics(db)
        payment_logs = await get_recent_payment_logs(db)
        mod_flags = await get_moderation_flags(db)        
      
        return templates.TemplateResponse(
        request=request,
        name="admin_dashboard.html",
        context={
            "request": request,
            "admin": admin,
            "users": users_data["users"],
            "users_pagination": {
                "page": users_data["page"],
                "page_size": users_data["page_size"],
                "total": users_data["total"],
                "total_pages": users_data["total_pages"],
            },
            "feedback_logs": feedback_data["feedback_logs"],
            "support_tickets": tickets_data["support_tickets"],
            "pending_counsellors": pending_counsellors,
            "counsellors": counsellors_data["counsellors"],
            "counsellor_session_analytics": counsellor_analytics,
            "appointments": appointments,
            "payment_logs": payment_logs,
            "session_revenue": payment_analytics["session_revenue"],
            "simulation_revenue": payment_analytics["simulation_revenue"],
            "sim_revenue": payment_analytics["simulation_revenue"],
            "total_revenue": payment_analytics["total_revenue"],
            "counsellor_payouts": payment_analytics["counsellor_payouts"],
            "platform_commission": payment_analytics["platform_commission"],
            "pending_payouts": payment_analytics["pending_payouts"],
            "failed_payouts": payment_analytics["failed_payouts"],
            "moderation_flags": mod_flags,
            "sim_revenue": payment_analytics["simulation_revenue"],
            "total_counselor_payouts": payment_analytics["counsellor_payouts"],
            "platform_commission": payment_analytics["platform_commission"],
            "pending_transfers": payment_analytics["pending_payouts"],
            "failed_transfers": payment_analytics["failed_payouts"],
            "all_payments": payment_logs,
            "all_appointments": appointments,
            "all_counsellors": counsellors_data["counsellors"],
            "user_search": "",
            "counsellor_search": "",
            "user_page": 1,
            "feedback_page": 1,
            "ticket_page": 1,
            "page_size": 20,
            "total_users": users_data["total"],
            "total_feedback": len(feedback_data["feedback_logs"]),
            "total_tickets": len(tickets_data["support_tickets"]),
            "feedbacks": feedback_data["feedback_logs"],
            "tickets": tickets_data["support_tickets"],
            "simulation_payments": [],
            "captured_payments_count": 0,
            "sim_payments_count": 0,
        }
    )
    except Exception as e:
        import traceback
        print(f"ADMIN ERROR DETAIL: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=str(e))


# ─── User Management APIs ─────────────────────────────────────────────────────

@router.post("/users/{user_id}/block")
async def api_block_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = await block_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": f"User {user.full_name} blocked successfully.", "user_id": user_id}


@router.post("/users/{user_id}/unblock")
async def api_unblock_user(
    user_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    user = await unblock_user(db, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": f"User {user.full_name} unblocked.", "user_id": user_id}


@router.post("/users/{user_id}/reset-password")
async def api_reset_user_password(
    user_id: int,
    new_password: str,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    if len(new_password) < 8:
        raise HTTPException(status_code=400, detail="Password must be at least 8 characters.")
    hashed = pwd_context.hash(new_password)
    user = await reset_user_password(db, user_id, hashed)
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")
    return {"message": f"Password reset for user {user.full_name}.", "user_id": user_id}


# ─── Ticket Management APIs ───────────────────────────────────────────────────

@router.post("/tickets/{ticket_id}/status")
async def api_update_ticket_status(
    ticket_id: int,
    status: str,
    admin_reply: str = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        ticket = await update_ticket_status(db, ticket_id, status, admin_reply)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found.")
    return {"message": f"Ticket {ticket_id} updated to '{status}'.", "ticket_id": ticket_id}


# ─── Counsellor Management APIs ───────────────────────────────────────────────

@router.post("/counsellors/{profile_id}/approve")
async def api_approve_counsellor(
    profile_id: int,
    remarks: str = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    profile = await approve_counsellor(db, profile_id, remarks)
    if not profile:
        raise HTTPException(status_code=404, detail="Counsellor profile not found.")
    return {"message": "Counsellor approved.", "profile_id": profile_id}


@router.post("/counsellors/{profile_id}/reject")
async def api_reject_counsellor(
    profile_id: int,
    remarks: str = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    profile = await reject_counsellor(db, profile_id, remarks)
    if not profile:
        raise HTTPException(status_code=404, detail="Counsellor profile not found.")
    return {"message": "Counsellor rejected.", "profile_id": profile_id, "remarks": remarks}


@router.post("/counsellors/{profile_id}/block")
async def api_block_counsellor(
    profile_id: int,
    reason: str = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    profile = await block_counsellor(db, profile_id, reason)
    if not profile:
        raise HTTPException(status_code=404, detail="Counsellor profile not found.")
    return {"message": "Counsellor blocked.", "profile_id": profile_id}


@router.post("/counsellors/{profile_id}/unblock")
async def api_unblock_counsellor(
    profile_id: int,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    profile = await unblock_counsellor(db, profile_id)
    if not profile:
        raise HTTPException(status_code=404, detail="Counsellor profile not found.")
    return {"message": "Counsellor unblocked.", "profile_id": profile_id}


# ─── Moderation Flag APIs ─────────────────────────────────────────────────────

@router.post("/moderation/{flag_id}/resolve")
async def api_resolve_flag(
    flag_id: int,
    status: str,
    admin_note: str = None,
    db: AsyncSession = Depends(get_db),
    admin: User = Depends(get_current_admin),
):
    try:
        flag = await resolve_moderation_flag(db, flag_id, status, admin_note)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    if not flag:
        raise HTTPException(status_code=404, detail="Moderation flag not found.")
    return {"message": f"Flag {flag_id} marked as '{status}'.", "flag_id": flag_id}