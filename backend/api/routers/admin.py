from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy import func, select, and_
from sqlalchemy.ext.asyncio import AsyncSession

from database.base import get_db
from database.models import User, Session, Message, MessageTemplate
from api.deps import get_current_active_user, get_current_admin_user

router = APIRouter()


@router.get("/stats/overview")
async def get_overview_stats(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get overview statistics for the admin dashboard.

    Returns:
        Dict containing various system statistics
    """
    # Get user statistics
    total_users = await db.scalar(select(func.count(User.id)))
    active_users = await db.scalar(
        select(func.count(User.id)).where(User.is_active == True)
    )

    # Get session statistics
    total_sessions = await db.scalar(select(func.count(Session.id)))
    active_sessions = await db.scalar(
        select(func.count(Session.id)).where(Session.is_active == True)
    )

    # Get message statistics
    total_messages = await db.scalar(select(func.count(Message.id)))

    # Get template statistics
    total_templates = await db.scalar(select(func.count(MessageTemplate.id)))
    active_templates = await db.scalar(
        select(func.count(MessageTemplate.id)).where(MessageTemplate.is_active == True)
    )

    return {
        "users": {
            "total": total_users or 0,
            "active": active_users or 0,
        },
        "sessions": {
            "total": total_sessions or 0,
            "active": active_sessions or 0,
        },
        "messages": {
            "total": total_messages or 0,
        },
        "templates": {
            "total": total_templates or 0,
            "active": active_templates or 0,
        },
    }


@router.get("/stats/activity")
async def get_activity_stats(
    days: int = 30,
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, List[Dict[str, Any]]]:
    """
    Get activity statistics over time.

    Args:
        days: Number of days to look back

    Returns:
        Dict containing activity data points
    """
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)

    # Get daily new users
    new_users = await db.execute(
        select(
            func.date_trunc("day", User.created_at).label("date"),
            func.count(User.id).label("count"),
        )
        .where(User.created_at >= start_date)
        .group_by(func.date_trunc("day", User.created_at))
        .order_by(func.date_trunc("day", User.created_at))
    )

    # Get daily active sessions
    active_sessions = await db.execute(
        select(
            func.date_trunc("day", Session.created_at).label("date"),
            func.count(Session.id).label("count"),
        )
        .where(Session.created_at >= start_date)
        .group_by(func.date_trunc("day", Session.created_at))
        .order_by(func.date_trunc("day", Session.created_at))
    )

    # Get daily messages
    messages = await db.execute(
        select(
            func.date_trunc("day", Message.created_at).label("date"),
            func.count(Message.id).label("count"),
        )
        .where(Message.created_at >= start_date)
        .group_by(func.date_trunc("day", Message.created_at))
        .order_by(func.date_trunc("day", Message.created_at))
    )

    return {
        "new_users": [{"date": str(row[0]), "count": row[1]} for row in new_users],
        "active_sessions": [
            {"date": str(row[0]), "count": row[1]} for row in active_sessions
        ],
        "messages": [{"date": str(row[0]), "count": row[1]} for row in messages],
    }


@router.get("/stats/templates")
async def get_template_stats(
    current_user: User = Depends(get_current_admin_user),
    db: AsyncSession = Depends(get_db),
) -> Dict[str, Any]:
    """
    Get statistics about message templates.

    Returns:
        Dict containing template statistics
    """
    try:
        # Get total templates
        total_templates = await db.scalar(select(func.count(MessageTemplate.id)))

        # Get active templates
        active_templates = await db.scalar(
            select(func.count(MessageTemplate.id)).where(
                MessageTemplate.is_active == True
            )
        )

        # Get templates by category
        templates_by_category_result = await db.execute(
            select(
                MessageTemplate.category, func.count(MessageTemplate.id).label("count")
            )
            .group_by(MessageTemplate.category)
            .order_by(func.count(MessageTemplate.id).desc())
        )

        # Get recent templates
        recent_templates_result = await db.execute(
            select(MessageTemplate).order_by(MessageTemplate.updated_at.desc()).limit(5)
        )

        return {
            "total_templates": total_templates or 0,
            "active_templates": active_templates or 0,
            "templates_by_category": [
                {"category": category or "Uncategorized", "count": count}
                for category, count in templates_by_category_result.all()
            ],
            "recent_templates": [
                {
                    "id": str(t.id),
                    "name": t.name,
                    "category": t.category or "Uncategorized",
                    "updated_at": t.updated_at.isoformat() if t.updated_at else None,
                }
                for t in recent_templates_result.scalars().all()
            ],
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error retrieving template statistics: {str(e)}",
        )
