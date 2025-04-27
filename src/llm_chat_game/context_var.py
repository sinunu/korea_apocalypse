"""Context variables."""

from contextvars import ContextVar


DEBUG_MODE: ContextVar[bool] = ContextVar("debug_mode", default=False)
