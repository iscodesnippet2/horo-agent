"""Disabled memory OAuth routes for the lite build."""

try:
    from fastapi import APIRouter
except Exception:  # pragma: no cover - optional dashboard dependency
    APIRouter = None

router = APIRouter() if APIRouter else None
