from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.core.autocad import AutoCADError
from autocad_mcp.drawings import ProfessionalPlan


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="generar_planta")
    def tool_planta(origin_x: float = 0.0, origin_y: float = 0.0) -> dict:
        try:
            plan = ProfessionalPlan(origin_x, origin_y)
            return plan.draw()
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
