from __future__ import annotations

from collections.abc import Callable
from typing import Any, TypeVar

from autocad_mcp.core.autocad import AutoCADConnection, AutoCADError

T = TypeVar("T")


def connected(action: Callable[[AutoCADConnection], T]) -> dict[str, Any]:
    try:
        conn = AutoCADConnection.get_instance()
        conn.connect()
        return {"ok": True, "data": action(conn)}
    except AutoCADError as exc:
        return {"ok": False, "error": str(exc)}


def run_tool(action: Callable[[AutoCADConnection], dict[str, Any]]) -> dict[str, Any]:
    try:
        conn = AutoCADConnection.get_instance()
        conn.connect()
        return action(conn)
    except AutoCADError as exc:
        return {"ok": False, "error": str(exc)}

