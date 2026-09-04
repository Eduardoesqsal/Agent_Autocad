from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from autocad_mcp.drawings import FrontElevation
from autocad_mcp.core.autocad import AutoCADError


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="generar_alzado")
    def tool_generar_alzado(
        origin_x: float = 0.0,
        origin_y: float = 0.0,
        ancho: float = 10.8,
        altura_muro: float = 3.0,
        altura_loseta: float = 0.3,
    ) -> dict:
        try:
            plan = FrontElevation(origin_x, origin_y, ancho, altura_muro, altura_loseta)
            return plan.draw()
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
