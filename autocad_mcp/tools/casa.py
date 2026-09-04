from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.drawings import AmericanHousePlan
from autocad_mcp.core.autocad import AutoCADError


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="generar_casa")
    def tool_generar_casa(origin_x: float = 0.0, origin_y: float = 0.0) -> dict:
        try:
            plan = AmericanHousePlan(origin_x, origin_y)
            return plan.draw()
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
