from __future__ import annotations

from typing import Any

from mcp.server.fastmcp import FastMCP

from autocad_mcp.tools._common import connected, run_tool


def register_tools(mcp: FastMCP) -> None:
    @mcp.tool(name="obtener_bloques")
    def tool_obtener_bloques() -> dict:
        return connected(lambda conn: conn.list_blocks())

    @mcp.tool(name="insertar_bloque")
    def tool_insertar_bloque(
        nombre: str,
        x: float,
        y: float,
        escala: float = 1.0,
        rotacion: float = 0.0,
        capa: str | None = None,
    ) -> dict[str, Any]:
        def insert(conn):
            result = conn.insert_block(nombre, x, y, escala, rotacion, layer=capa)
            conn.zoom_extents()
            return {"ok": True, "data": result}

        return run_tool(insert)
