from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from autocad_mcp.core.autocad import AutoCADConnection, AutoCADError


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="obtener_bloques")
    def tool_obtener_bloques() -> dict:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            return {"ok": True, "data": conn.list_blocks()}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}

    @mcp.tool(name="insertar_bloque")
    def tool_insertar_bloque(
        nombre: str,
        x: float,
        y: float,
        escala: float = 1.0,
        rotacion: float = 0.0,
        capa: str | None = None,
    ) -> dict[str, Any]:
        try:
            conn = AutoCADConnection.get_instance()
            conn.connect()
            result = conn.insert_block(nombre, x, y, escala, rotacion, layer=capa)
            conn.zoom_extents()
            return {"ok": True, "data": result}
        except AutoCADError as exc:
            return {"ok": False, "error": str(exc)}
