"""SGC agent runtime package."""

__all__ = ["build_orchestrator"]


def build_orchestrator():
    from .orchestrator import build_orchestrator as _build_orchestrator

    return _build_orchestrator()
