from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.drawings import TopoPlan
from autocad_mcp.core.autocad import AutoCADError


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="generar_plano_topo")
    def tool_generar_plano(origin_x: float = 0.0, origin_y: float = 0.0) -> dict:
        try:
            plan = TopoPlan(origin_x, origin_y)
            return plan.draw()
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
