"""Shared API dependencies"""
from app.core.database import get_db
from app.core.security import get_current_user, get_current_teacher

__all__ = ["get_db", "get_current_user", "get_current_teacher"]


