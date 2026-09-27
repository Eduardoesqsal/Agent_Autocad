from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.core.autocad import AutoCADError
from autocad_mcp.drawings import BlockPlan


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="generar_planta_bloques")
    def tool_planta_bloques(
        origin_x: float = 0.0, origin_y: float = 0.0, limpiar: bool = False
    ) -> dict:
        try:
            plan = BlockPlan(origin_x, origin_y, limpiar=limpiar)
            return plan.draw()
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
